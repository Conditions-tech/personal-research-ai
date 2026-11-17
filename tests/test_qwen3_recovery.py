"""Recovery/control tests use temporary files and no model or provider HTTP."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import qwen3_recovery as recovery


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP blocked")))
        self.enterContext(patch("sqlite3.connect", side_effect=AssertionError("SQLite blocked")))
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.budget = {"used": 7, "entries": []}
        self.backend = Mock()
        self.backend.inspect.return_value = {"model": recovery.pilot.MODEL, "runtime_version": recovery.pilot.RUNTIME}
        self.backend.request.return_value = {"models": []}
        self.sleep, self.clients, self.unload, self.popen = Mock(), Mock(return_value=True), Mock(), Mock()
        self.controller = recovery.Controller(
            directory=self.tmp, budget=lambda: copy.deepcopy(self.budget),
            memory=Mock(return_value=recovery.pilot.MIN_AVAILABLE),
            backend_factory=lambda: self.backend, sleep=self.sleep,
            birth=Mock(return_value="birth-token"), clients=self.clients,
            unload=self.unload, popen=self.popen)

    def state(self, **values):
        recovery.save(self.controller.path, {"version": 1, **values})

    def test_low_memory_wait_is_bounded_pending_and_budget_are_preserved(self):
        self.controller.memory.return_value = recovery.pilot.MIN_AVAILABLE - 1
        result = self.controller.run(generate=True)
        self.assertEqual(result["status"], "waiting_memory")
        self.assertEqual(result["pending"], list(recovery.REMAINING))
        self.assertEqual(len(result["memory_samples"]), 3)
        self.assertEqual(self.sleep.call_args_list, [((5,),), ((5,),)])
        self.assertEqual(self.budget["used"], 7)
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_default_is_recovery_only_and_never_launches_generation(self):
        self.assertEqual(self.controller.run()["status"], "ready_no_generation_requested")
        self.popen.assert_not_called()
        self.unload.assert_not_called()

    def test_empty_inventory_with_another_connected_client_is_still_busy(self):
        self.clients.return_value = False
        self.assertEqual(self.controller.run(True)["status"], "waiting_runtime_idle")
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_later_invocation_can_resume_after_memory_recovers(self):
        self.controller.memory.return_value = recovery.pilot.MIN_AVAILABLE - 1
        self.assertEqual(self.controller.run(True)["status"], "waiting_memory")
        self.controller.memory.return_value = recovery.pilot.MIN_AVAILABLE
        self.popen.return_value = Mock(pid=42, wait=Mock(return_value=0))
        self.assertEqual(self.controller.run(True)["status"], "case_finished_recheck_next_invocation")
        self.assertEqual(self.popen.call_count, 1)

    def test_allocation_exhausted_never_starts_another_worker(self):
        self.budget = {"used": 12, "entries": [{"case": c} for c in recovery.REMAINING]}
        self.assertEqual(self.controller.run(True)["status"], "allocation_finished")
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_foreign_unowned_or_busy_model_is_never_unloaded(self):
        model = {"name": recovery.pilot.MODEL, "digest": recovery.pilot.DIGEST}
        for models, owned, clients in (([model], None, True), ([model], "tracked", False),
                                       ([{**model, "digest": "foreign"}], "tracked", True),
                                       ([model, model], "tracked", True)):
            self.state(owned_finished_case=owned)
            self.backend.request.return_value = {"models": models}
            self.clients.return_value = clients
            self.assertEqual(self.controller.run(True)["status"], "waiting_runtime_idle")
        self.unload.assert_not_called(); self.popen.assert_not_called()

    def test_owned_finished_model_unload_is_verified_and_does_not_debit(self):
        self.state(owned_finished_case="tracked")
        self.backend.request.side_effect = [{"models": [{"name": recovery.pilot.MODEL, "digest": recovery.pilot.DIGEST}]}, {"models": []}]
        result = self.controller.run()
        self.assertEqual(result["status"], "ready_no_generation_requested")
        self.unload.assert_called_once_with()
        self.assertNotIn("owned_finished_case", result)
        self.assertEqual(result["recovery_controls"][0]["action"], "empty-request-unload")
        self.assertEqual(self.budget["used"], 7)
        self.popen.assert_not_called()

    def test_unload_failure_and_health_errors_preserve_queue(self):
        self.state(owned_finished_case="tracked")
        self.backend.request.return_value = {"models": [{"name": recovery.pilot.MODEL, "digest": recovery.pilot.DIGEST}]}
        self.unload.side_effect = OSError("synthetic failure")
        result = self.controller.run(True)
        self.assertEqual(result["status"], "waiting_check_failure")
        self.assertEqual(result["pending"], list(recovery.REMAINING))
        self.backend.inspect.side_effect = ValueError("synthetic health failure")
        self.assertEqual(self.controller.run(True)["status"], "waiting_runtime_identity")
        self.popen.assert_not_called()

    def test_empty_model_inventory_records_actionable_identity_block_and_clears_stale_identity(self):
        self.backend.inspect.side_effect = recovery.pilot.PilotBlocked(
            "Approved local model/digest unavailable; no fallback or download.")
        self.backend.events = [{"path": "/api/version", "http_status": 200},
                               {"path": "/api/tags", "http_status": 200}]
        self.state(runtime_identity={"model_digest": recovery.pilot.DIGEST}, loaded_model_count=1,
                   last_check_error={"reason": "stale"})
        result = self.controller.run(True)
        self.assertEqual(result["status"], "waiting_runtime_identity")
        self.assertIsNone(result["runtime_identity"])
        self.assertNotIn("loaded_model_count", result)
        self.assertEqual(result["runtime_check"]["status"], "blocked")
        self.assertEqual(result["last_check_error"], {
            "type": "PilotBlocked", "stage": "runtime_metadata_and_model_identity",
            "endpoint": "/api/tags", "http_status": 200,
            "reason": "Approved local model/digest unavailable; no fallback or download."})
        self.assertEqual(result["pending"], list(recovery.REMAINING))
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_successful_runtime_recheck_replaces_prior_failure_details(self):
        self.state(runtime_identity={"stale": True},
                   last_check_error={"reason": "old"}, error_type="PilotBlocked",
                   runtime_check={"status": "blocked"})
        result = self.controller.run()
        self.assertEqual(result["runtime_check"]["status"], "ready")
        self.assertEqual(result["runtime_check"]["stage"], "idle_verified")
        self.assertEqual(result["runtime_identity"]["runtime_version"], recovery.pilot.RUNTIME)
        self.assertNotIn("last_check_error", result)
        self.assertNotIn("error_type", result)

    def test_unload_returning_without_empty_inventory_is_not_success(self):
        self.state(owned_finished_case="tracked")
        self.backend.request.return_value = {"models": [{"name": recovery.pilot.MODEL, "digest": recovery.pilot.DIGEST}]}
        self.assertEqual(self.controller.run(True)["status"], "waiting_runtime_idle")
        self.assertEqual(self.sleep.call_count, 2)
        self.popen.assert_not_called()

    def test_active_unknown_or_launching_workers_cannot_be_replaced(self):
        for job in ({"phase": "launching"}, {"pid": 42, "birth": "birth-token"}):
            self.state(active_job=job)
            self.assertEqual(self.controller.run(True)["status"], "waiting_worker_reconciliation")
        self.controller.birth.side_effect = OSError("access denied")
        self.assertEqual(self.controller.run(True)["status"], "waiting_check_failure")
        self.popen.assert_not_called(); self.unload.assert_not_called()
        self.backend.inspect.assert_not_called()

    def test_exited_or_reused_pid_does_not_uncharge_unknown_attempt(self):
        self.budget = {"used": 8, "entries": [{"case": recovery.REMAINING[0]}]}
        for token in (None, "different-creation-token"):
            self.state(active_job={"pid": 42, "birth": "birth-token", "case": recovery.REMAINING[0], "report": str(self.tmp / "absent.json")})
            self.controller.birth.return_value = token
            result = self.controller.run()
            self.assertEqual(result["charged"], 8)
            self.assertEqual(result["pending"], list(recovery.REMAINING[1:]))
            self.assertNotIn("active_job", result)
            self.assertNotIn("owned_finished_case", result)
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_only_completed_wire_response_can_prove_idle_ownership(self):
        path = self.tmp / "report.json"
        job = {"case": recovery.REMAINING[0], "report": str(path)}
        event = {"path": "/api/generate", "http_status": 200,
                 "raw_body": json.dumps({"model": recovery.pilot.MODEL, "done": True, "done_reason": "stop"})}
        for events, expected in (([], False), ([{**event, "http_status": 500}], False), ([event], True)):
            recovery.save(path, {"cases": [{"case": {"id": job["case"]}, "events": events}]})
            state = {}
            self.controller.confirm_finished_owner(state, job)
            self.assertEqual("owned_finished_case" in state, expected)

    def test_one_child_is_awaited_and_metering_is_left_to_frozen_helper(self):
        child = Mock(pid=42)
        def finish():
            self.assertEqual(recovery.read(self.controller.path)["active_job"]["pid"], 42)
            self.budget["used"] += 1
            self.budget["entries"].append({"case": recovery.REMAINING[0]})
            return 0
        child.wait.side_effect = finish
        self.popen.return_value = child
        result = self.controller.run(True)
        self.assertEqual(result["status"], "case_finished_recheck_next_invocation")
        self.assertEqual(result["charged"], 8)
        self.assertEqual(result["pending"], list(recovery.REMAINING[1:]))
        command = self.popen.call_args.args[0]
        self.assertEqual(command.count("--case-id"), 1)
        self.assertEqual(command[-1], recovery.REMAINING[0])
        child.wait.assert_called_once_with()
        self.assertTrue(self.popen.call_args.kwargs["stdout"].closed)
        self.assertNotIn("active_job", recovery.read(self.controller.path))

    def test_spawn_failure_or_preflight_without_charge_keeps_case_pending(self):
        self.popen.side_effect = OSError("synthetic spawn failure")
        result = self.controller.run(True)
        self.assertEqual(result["status"], "waiting_check_failure")
        self.assertNotIn("active_job", result)
        self.assertEqual(result["pending"], list(recovery.REMAINING))
        self.popen.side_effect = None
        self.popen.return_value = Mock(pid=42, wait=Mock(return_value=0))
        result = self.controller.run(True)
        self.assertEqual(result["charged"], 7)
        self.assertEqual(result["pending"], list(recovery.REMAINING))

    def test_liveness_metadata_failure_still_awaits_spawned_child(self):
        child = Mock(pid=42, wait=Mock(return_value=0))
        self.popen.return_value = child
        self.controller.birth.side_effect = OSError("synthetic metadata failure")
        result = self.controller.run(True)
        self.assertEqual(result["status"], "case_finished_recheck_next_invocation")
        child.wait.assert_called_once_with()

    def test_interrupted_wait_keeps_active_worker_marker_and_does_not_kill(self):
        child = Mock(pid=42)
        child.wait.side_effect = KeyboardInterrupt()
        self.popen.return_value = child
        with self.assertRaises(KeyboardInterrupt):
            self.controller.run(True)
        self.assertEqual(recovery.read(self.controller.path)["active_job"]["pid"], 42)
        child.kill.assert_not_called(); child.terminate.assert_not_called()
        self.assertEqual(self.controller.run(True)["status"], "waiting_worker_reconciliation")
        self.assertEqual(self.popen.call_count, 1)

    def test_regression_mode_uses_same_serial_job_lease_and_no_runtime(self):
        self.popen.return_value = Mock(pid=42, wait=Mock(return_value=0))
        self.state(status="waiting_runtime_identity", runtime_identity=None,
                   runtime_check={"status": "blocked", "stage": "runtime_metadata_and_model_identity"},
                   last_check_error={"endpoint": "/api/tags"})
        result = self.controller.run(regression=True)
        self.assertEqual(result["status"], "waiting_runtime_identity")
        self.assertEqual(result["runtime_check"]["status"], "blocked")
        self.assertEqual(result["last_check_error"]["endpoint"], "/api/tags")
        self.assertEqual(result["last_regression_exit_code"], 0)
        self.assertIn("unittest", self.popen.call_args.args[0])
        self.backend.inspect.assert_not_called(); self.unload.assert_not_called()

    def test_failed_regression_is_reported_as_failure(self):
        self.popen.return_value = Mock(pid=42, wait=Mock(return_value=1))
        self.assertEqual(self.controller.run(regression=True)["status"], "regression_failed")
        self.backend.inspect.assert_not_called()

    def test_regression_cli_exit_code_tracks_suite_not_preserved_runtime_blocker(self):
        for exit_code, raises in ((0, False), (1, True)):
            with patch.object(recovery, "Controller") as factory, patch.object(sys, "argv", ["recovery", "--regression"]):
                factory.return_value.run.return_value = {
                    "status": "waiting_runtime_identity", "last_regression_exit_code": exit_code}
                if raises:
                    with self.assertRaises(SystemExit) as caught:
                        recovery.main()
                    self.assertEqual(caught.exception.code, 1)
                else:
                    recovery.main()

    def test_corrupt_state_is_preserved_and_does_not_touch_runtime(self):
        for data in ('{"version":', '[]', '{"version":2}'):
            self.controller.path.write_text(data)
            self.assertEqual(self.controller.run(True)["status"], "waiting_state_reconciliation")
            self.assertEqual(self.controller.path.read_text(), data)
        self.backend.inspect.assert_not_called(); self.popen.assert_not_called()

    def test_live_lease_blocks_other_process_without_any_recovery_or_worker(self):
        with recovery.Lease(self.tmp):
            self.assertEqual(self.controller.run(True)["status"], "busy")
            code = "import sys;sys.path.insert(0,'tools');from qwen3_recovery import Lease,Busy;from pathlib import Path\ntry:\n with Lease(Path(sys.argv[1])): sys.exit(3)\nexcept Busy: sys.exit(0)"
            result = subprocess.run([sys.executable, "-c", code, str(self.tmp)], cwd=recovery.ROOT, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.controller.run()["status"], "ready_no_generation_requested")
        self.popen.assert_not_called(); self.unload.assert_not_called()

    def test_unload_wire_contains_no_prompt_and_retains_no_budget_handle(self):
        response = Mock(status_code=200)
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.iter_content.return_value = [b'{"done":true,"response":""}']
        session = Mock(trust_env=True)
        session.__enter__ = Mock(return_value=session)
        session.__exit__ = Mock(return_value=False)
        session.post.return_value = response
        with patch("requests.Session", return_value=session):
            recovery.unload_owned_model()
        self.assertFalse(session.trust_env)
        self.assertEqual(session.post.call_args.kwargs["json"], {"model": recovery.pilot.MODEL, "keep_alive": 0})
        self.assertFalse(session.post.call_args.kwargs["allow_redirects"])
        self.assertEqual(self.budget["used"], 7)

    def test_budget_and_freeze_tampering_are_refused_without_runtime(self):
        # Fixture copies, never modifies the real ledger or frozen inputs.
        freeze = recovery.ROOT / "docs/C2_QWEN3_PROTOCOL_FREEZE_2026-10-21.json"
        (self.tmp / "docs").mkdir()
        freeze_copy = self.tmp / freeze.relative_to(recovery.ROOT)
        freeze_copy.write_bytes(freeze.read_bytes())
        values = recovery.read(freeze)
        for relative in values["source_and_evidence_sha256"]:
            dest = self.tmp / relative
            dest.parent.mkdir(exist_ok=True, parents=True)
            dest.write_bytes((recovery.ROOT / relative).read_bytes())
        ledger = self.tmp / recovery.LEDGER.relative_to(recovery.ROOT)
        ledger.write_bytes(recovery.LEDGER.read_bytes())
        self.assertGreaterEqual(recovery.verified_budget(self.tmp)["used"], 7)
        original = recovery.read(ledger)
        for mutate in (lambda v: v.update(cap=13), lambda v: v.update(used=0),
                       lambda v: v["entries"][0].update(case="changed"),
                       lambda v: (v["entries"].append({"case":"unapproved","protocol":recovery.pilot.VERSION}), v.update(used=len(v["entries"])))):
            value = copy.deepcopy(original); mutate(value); recovery.save(ledger, value)
            with self.assertRaises(ValueError): recovery.verified_budget(self.tmp)
        recovery.save(ledger, original)
        (self.tmp / "tools/qwen3_pilot.py").write_text("changed")
        with self.assertRaises(ValueError): recovery.verified_budget(self.tmp)
        freeze_copy.write_text("{}")
        with self.assertRaises(ValueError): recovery.verified_budget(self.tmp)


if __name__ == "__main__":
    unittest.main()
