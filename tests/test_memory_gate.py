"""App pre-load RAM gate; measurement is read-only and never contacts a model."""

import sys
import unittest
from unittest.mock import patch

from review import memory


GIB = 1024 ** 3


class MemoryGateTests(unittest.TestCase):
    def test_gate_is_inclusive_and_never_relaxed(self):
        for available, allowed in ((4 * GIB, True), (4 * GIB - 1, False), (0, False), (8 * GIB, True)):
            with self.subTest(available=available), patch(
                    "review.memory.available_memory_bytes", return_value=available):
                if allowed:
                    self.assertEqual(memory.require_memory(), available)
                else:
                    with self.assertRaisesRegex(memory.MemoryGateError, "No model was loaded"):
                        memory.require_memory()
        self.assertEqual(memory.MIN_AVAILABLE_BYTES, 4 * GIB)

    def test_unmeasurable_memory_refuses_instead_of_assuming_enough(self):
        with patch("ctypes.windll", create=True, new=None), \
                self.assertRaisesRegex(memory.MemoryGateError, "Cannot measure available memory"):
            memory.available_memory_bytes()
        self.assertTrue(issubclass(memory.MemoryGateError, ValueError))  # The UI shows ValueErrors.

    @unittest.skipUnless(sys.platform == "win32", "Windows measurement only")
    def test_windows_measurement_reports_physical_bytes(self):
        available = memory.available_memory_bytes()
        self.assertIsInstance(available, int)
        self.assertGreater(available, 0)


if __name__ == "__main__":
    unittest.main()
