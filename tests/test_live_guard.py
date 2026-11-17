"""The live diagnostic cannot run accidentally as part of ordinary checks."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LiveOptInTests(unittest.TestCase):
    def run_guarded(self, *args):
        tool = Path(__file__).resolve().parents[1] / "tools" / "live_discovery_smoke.py"
        script = """
import runpy, sys
sys.dont_write_bytecode = True
def guard(event, args):
    if event in ("sqlite3.connect", "socket.connect", "socket.getaddrinfo", "os.mkdir"):
        raise AssertionError("Live diagnostic attempted I/O without opt-in")
sys.addaudithook(guard)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
        return subprocess.run([sys.executable, "-B", "-c", script, str(tool), *args],
                                capture_output=True, text=True, timeout=30)

    def test_live_tool_without_opt_in_refuses_before_external_io(self):
        result = self.run_guarded()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Live API calls require the explicit --live flag", result.stderr)

    def test_report_refuses_non_json_and_existing_targets_before_live_io(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("protected.db", "existing.json"):
                target = Path(directory) / name
                target.write_text("preserve sentinel", encoding="utf-8")
                result = self.run_guarded("--live", "--report", str(target))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Report must be a new .json file", result.stderr)
                self.assertEqual(target.read_text(encoding="utf-8"), "preserve sentinel")


if __name__ == "__main__":
    unittest.main()
