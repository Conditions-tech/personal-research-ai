"""Isolated model-specific pilot boundaries; no live runtime or production data."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import qwen3_pilot as pilot
from review.analysis import CURRENT_PROMPT_VERSION, MODEL, OPTIONS, evidence_context
from review.workspace import create_review
from test_review import fixture_run


class Qwen3PilotTests(unittest.TestCase):
    def setUp(self):
        self.http = self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP blocked")))
        self.enterContext(patch("sqlite3.connect", side_effect=AssertionError("SQLite blocked")))
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.ledger = self.tmp / "ledger.json"
        self.ledger.write_text(json.dumps({"kind":"c2-coverage-budget-v1", "cap":12, "used":0, "entries":[]}))
        self.review = create_review(fixture_run(), "Synthetic question", "Synthetic inclusion", "Private research")
        self.key = next(iter(self.review["papers"]))
        self.context = evidence_context(self.review, self.key)

    def test_model_specific_request_does_not_change_legacy_configuration_or_work(self):
        before = copy.deepcopy(self.review)
        request = pilot.build(self.context)
        self.assertEqual(request["options"], pilot.OPTIONS)
        self.assertEqual(request["options"]["num_ctx"], 6144)
        self.assertIs(request["think"], False)
        self.assertEqual(request["keep_alive"], 0)
        self.assertEqual(CURRENT_PROMPT_VERSION, "abstract-quotes-v3")
        self.assertEqual(MODEL, "qwen2.5:1.5b-instruct-q4_K_M")
        self.assertEqual(OPTIONS["num_ctx"], 8192)
        self.assertEqual(self.review, before)
        for abstract in ("", "x" * 4001):
            context=copy.deepcopy(self.context);context["record"]["abstract"]=abstract
            with self.assertRaises(ValueError):pilot.build(context)

    def test_inspection_requires_explicit_thinking_control_and_pinned_local_identity(self):
        backend = pilot.Backend(self.ledger, "synthetic")
        model={"name":pilot.MODEL, "digest":pilot.DIGEST, "size":123}
        show={"details":{"format":"gguf", "quantization_level":"Q4_K_M", "family":"qwen3"},
              "capabilities":["completion", "thinking"], "thinking":{"values":[True,False], "default":True}}
        for change in (lambda s:s.pop("thinking"), lambda s:s.update(thinking={"values":[True]}),
                       lambda s:s.update(thinking={"values":[0]}), lambda s:s.update(remote_host="cloud")):
            bad=copy.deepcopy(show);change(bad)
            with patch.object(backend,"request",side_effect=[{"version":pilot.RUNTIME},{"models":[model]},bad]):
                with self.assertRaises(pilot.PilotBlocked):backend.inspect()
        with patch.object(backend,"request",side_effect=[{"version":pilot.RUNTIME},{"models":[model]},show]):
            self.assertEqual(backend.inspect()["model_digest"],pilot.DIGEST)
        for bad in ({**model,"digest":"0"*64},{**model,"remote_model":"remote"}):
            with patch.object(backend,"request",return_value={"models":[bad]}):
                with self.assertRaises(pilot.PilotBlocked):backend.inventory()

    def test_below_gate_or_changed_settings_cannot_debit_or_send_generation(self):
        backend=pilot.Backend(self.ledger,"synthetic")
        body={**pilot.build(self.context),"model":pilot.MODEL}
        with patch("local_analysis_benchmark.available_memory",return_value=pilot.MIN_AVAILABLE-1):
            with self.assertRaises(pilot.PilotBlocked):backend.request("/api/generate",body)
        body["think"]=True
        with self.assertRaises(pilot.PilotBlocked):backend.request("/api/generate",body)
        self.assertEqual(json.loads(self.ledger.read_text())["used"],0)
        self.http.assert_not_called()

    def test_failed_http_retains_bounded_body_and_debits_exactly_once_without_retry(self):
        backend=pilot.Backend(self.ledger,"synthetic")
        response=Mock(status_code=429)
        response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.iter_content.return_value=[b'{"error":"Synthetic rate limit"}']
        self.http.side_effect=None;self.http.return_value=response
        with patch("local_analysis_benchmark.available_memory",return_value=pilot.MIN_AVAILABLE):
            with self.assertRaises(pilot.PilotBlocked):backend.request("/api/generate",{**pilot.build(self.context),"model":pilot.MODEL})
            with self.assertRaisesRegex(pilot.PilotBlocked,"duplicate trial"):backend.request("/api/generate",{**pilot.build(self.context),"model":pilot.MODEL})
        self.assertEqual(self.http.call_count,1)
        self.assertEqual(json.loads(self.ledger.read_text())["used"],1)
        self.assertEqual(backend.events[0]["http_status"],429)
        self.assertIn("Synthetic rate limit",backend.events[0]["raw_body"])
        self.assertFalse(self.http.call_args.kwargs["allow_redirects"])
        self.assertTrue(self.http.call_args.kwargs["stream"])

    def test_blocked_evaluation_never_checks_backend_and_preserves_fresh_budget(self):
        manifest=self.tmp/"manifest.json";report=self.tmp/"report.json"
        manifest.write_text(json.dumps({"protocol":pilot.VERSION,"partition":"synthetic","cases":[{"id":"synthetic"}]}))
        with patch("local_analysis_benchmark.available_memory",return_value=pilot.MIN_AVAILABLE-1):
            pilot.evaluate(manifest,self.ledger,report)
        value=json.loads(report.read_text())
        self.assertEqual(value["state"],"blocked");self.assertEqual(value["cases"],[])
        self.assertEqual(json.loads(self.ledger.read_text())["used"],0)
        self.http.assert_not_called()

    def test_first_smoke_selection_rejects_unknown_or_duplicate_frozen_case_ids(self):
        manifest=self.tmp/"manifest.json";report=self.tmp/"report.json"
        manifest.write_text(json.dumps({"protocol":pilot.VERSION,"partition":"synthetic","cases":[{"id":"synthetic"}]}))
        for selected in (["other"],["synthetic","synthetic"],[]):
            with self.assertRaises(ValueError):pilot.evaluate(manifest,self.ledger,report,selected)
        self.assertFalse(report.exists());self.http.assert_not_called()

    def test_cli_requires_explicit_opt_in_and_new_report(self):
        for extra in ([],["--live-local"]):
            report=self.tmp/"report.json"
            if extra:report.write_text('{}')
            with patch.object(sys,"argv",["qwen3_pilot", "--manifest","fixture.json","--ledger",str(self.ledger),"--report",str(report),*extra]),patch.object(pilot,"evaluate") as evaluate:
                with self.assertRaises(SystemExit):pilot.main()
                evaluate.assert_not_called()
        self.http.assert_not_called()


if __name__ == "__main__":
    unittest.main()
