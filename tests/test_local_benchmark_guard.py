"""The real local inference diagnostic must never run with ordinary tests."""

import subprocess
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class LocalBenchmarkGuardTests(unittest.TestCase):
    def benchmark_module(self):
        path = Path(__file__).resolve().parents[1] / "tools" / "local_analysis_benchmark.py"
        spec = importlib.util.spec_from_file_location("synthetic_benchmark", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def guarded(self, *args):
        tool = Path(__file__).resolve().parents[1] / "tools" / "local_analysis_benchmark.py"
        script = """
import runpy, sys
sys.dont_write_bytecode = True
def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'sqlite3.connect', 'os.mkdir'):
        raise AssertionError('Local inference diagnostic attempted I/O without valid opt-in')
sys.addaudithook(guard)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
        return subprocess.run([sys.executable, "-B", "-c", script, str(tool), *args],
                              capture_output=True, text=True, timeout=30)

    def test_no_opt_in_refuses_before_network_storage_or_memory_probe(self):
        result = self.guarded()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("requires explicit --live-local", result.stderr)

    def test_existing_or_non_json_report_refused_before_live_io(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("research.db", "existing.json"):
                target = Path(directory) / name
                target.write_text("preserve sentinel", encoding="utf-8")
                result = self.guarded("--live-local", "--report", str(target))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Report must be a new .json", result.stderr)
                self.assertEqual(target.read_text(), "preserve sentinel")

    def test_memory_wait_never_relaxes_the_approved_gate(self):
        module = self.benchmark_module()
        with patch.object(module, "available_memory", return_value=module.MIN_AVAILABLE_BYTES-1), patch.object(module.time, "sleep") as sleep:
            self.assertLess(module.wait_for_memory_gate(seconds=0), module.MIN_AVAILABLE_BYTES)
            sleep.assert_not_called()

    def test_memory_wait_allows_asynchronous_unload_to_finish(self):
        module = self.benchmark_module()
        with patch.object(module, "available_memory", side_effect=[module.MIN_AVAILABLE_BYTES-1,module.MIN_AVAILABLE_BYTES+1]), patch.object(module.time, "sleep") as sleep:
            self.assertGreater(module.wait_for_memory_gate(), module.MIN_AVAILABLE_BYTES)
            sleep.assert_called_once_with(0.25)


if __name__ == "__main__":
    unittest.main()
