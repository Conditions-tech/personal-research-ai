"""Isolated budget/resource/fixture guards; no real inference or production data."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from coverage_evaluation import debit, evaluate, make_review


class CoverageEvaluationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="coverage-tests-")
        self.addCleanup(directory.cleanup); self.root = Path(directory.name)
        self.ledger = self.root / "budget.json"
        self.ledger.write_text(json.dumps({"kind": "c2-coverage-budget-v1", "cap": 12, "used": 0, "entries": []}), encoding="utf-8")
        self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("Live HTTP blocked")))
        self.enterContext(patch("sqlite3.connect", side_effect=AssertionError("SQLite blocked")))

    def case(self):
        return {"id": "synthetic", "kind": "synthetic", "title": "Synthetic fixture", "authors": "Synthetic author",
                "year": None, "doi": "", "source_url": "", "license": "synthetic fixture", "abstract": "Our objective was to test a protocol.",
                "expected": {"objective": ["Our objective was to test a protocol."]}}

    def manifest(self):
        path = self.root / "tuning.json"
        path.write_text(json.dumps({"partition": "tuning", "cases": [self.case()]}), encoding="utf-8")
        return path

    def test_hard_budget_is_debited_twelve_times_then_refuses_without_overwrite(self):
        for i in range(12): debit(self.ledger, str(i), "abstract-quotes-v2")
        before = self.ledger.read_bytes()
        with self.assertRaisesRegex(ValueError, "budget is exhausted"):
            debit(self.ledger, "extra", "abstract-quotes-v2")
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertFalse(self.ledger.with_suffix(".lock").exists())

    def test_malformed_budget_is_not_replaced(self):
        for change in [{"cap": 100}, {"used": 1}, {"cap": 12.0}, {"entries": {}}, {"kind": "unrelated"}]:
            value = {"kind": "c2-coverage-budget-v1", "cap": 12, "used": 0, "entries": [], **change}
            self.ledger.write_text(json.dumps(value)); before = self.ledger.read_bytes()
            with self.assertRaises(ValueError): debit(self.ledger, "case", "v2")
            self.assertEqual(self.ledger.read_bytes(), before)

    def test_existing_lock_prevents_concurrent_debit(self):
        lock = self.ledger.with_suffix(".lock"); lock.write_text("owned by another worker")
        with self.assertRaises(FileExistsError): debit(self.ledger, "case", "v2")
        self.assertEqual(json.loads(self.ledger.read_text())["used"], 0)
        self.assertEqual(lock.read_text(), "owned by another worker")

    def guarded_cli(self, *args):
        script = """
import runpy,sys
sys.dont_write_bytecode=True
def guard(event,args):
 if event in ('socket.connect','socket.getaddrinfo','sqlite3.connect','os.mkdir'):
  raise AssertionError('Unapproved evaluation I/O')
sys.addaudithook(guard)
sys.argv=sys.argv[1:]
runpy.run_path(sys.argv[0],run_name='__main__')
"""
        return subprocess.run([sys.executable,"-B","-c",script,str(TOOLS/"coverage_evaluation.py"),*args],capture_output=True,text=True,timeout=30)

    def test_cli_requires_opt_in_before_any_external_io(self):
        result = self.guarded_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Explicit --live-local", result.stderr)

    def test_cli_refuses_existing_or_non_json_report_before_live_io(self):
        for name in ["research.db", "existing.json"]:
            path = self.root/name; path.write_text("preserve")
            result = self.guarded_cli("--live-local", "--report", str(path))
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(path.read_text(), "preserve")

    def test_low_memory_blocks_before_backend_health_or_generation(self):
        output = self.root/"low-memory.json"
        with patch("local_analysis_benchmark.wait_for_memory_gate", return_value=1), patch("review.local_backend.OllamaLocal.inspect") as inspect:
            evaluate(self.manifest(), "abstract-quotes-v2", self.ledger, output)
        inspect.assert_not_called()
        self.assertEqual(json.loads(output.read_text())["state"], "blocked")
        self.assertEqual(json.loads(self.ledger.read_text())["used"], 0)

    def test_backend_failure_is_saved_without_budget_debit_or_traceback(self):
        output = self.root/"backend-failure.json"
        with patch("local_analysis_benchmark.wait_for_memory_gate", return_value=5*1024**3), patch("review.local_backend.OllamaLocal.inspect", side_effect=ValueError("Local backend unavailable")):
            evaluate(self.manifest(), "abstract-quotes-v2", self.ledger, output)
        saved = json.loads(output.read_text())
        self.assertEqual(saved["state"], "blocked"); self.assertEqual(saved["cases"], [])
        self.assertEqual(json.loads(self.ledger.read_text())["used"], 0)

    def test_gold_labels_are_not_captured_as_model_evidence(self):
        case = self.case(); review = make_review([case], "tuning")
        record = review["run"]["records"][0]
        self.assertNotIn("expected", record)
        self.assertEqual(record["abstract"], case["abstract"])
        self.assertEqual(review["run"]["manifest"]["settings"]["not_a_provider_search"], True)


if __name__ == "__main__": unittest.main()
