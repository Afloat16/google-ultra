import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ultra0_under_test", ROOT / "ultra0.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class CommandIntentTests(unittest.TestCase):
    def test_no_arguments_do_not_initialize_device(self):
        with patch.object(sys, "argv", ["ultra0.py"]), patch.object(app, "find_adb", side_effect=AssertionError("device accessed")):
            self.assertEqual(app.main(), 1)

    def test_conflicting_sources_are_rejected_before_adb(self):
        with patch.object(sys, "argv", ["ultra0.py", "accounts.txt", "--account", "tester@example.test:secret"]), patch.object(app, "find_adb", side_effect=AssertionError("device accessed")):
            with self.assertRaises(SystemExit) as result:
                app.main()
        self.assertEqual(result.exception.code, 2)

if __name__ == "__main__":
    unittest.main()
