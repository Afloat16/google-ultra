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

class PasswordInputTests(unittest.TestCase):
    def test_password_does_not_need_to_be_in_arguments(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", ["ultra0.py", "--account", "tester@example.test", "--password-stdin"]))
            stack.enter_context(patch.object(sys, "stdin", io.StringIO("  synthetic password  \n")))
            stack.enter_context(patch.object(app, "REPORT_DIR", Path(temporary)))
            for name in ("find_adb", "pick_device", "ensure_root", "ensure_network", "ensure_frida_server", "ensure_module_apk"):
                stack.enter_context(patch.object(app, name))
            process = stack.enter_context(patch.object(app, "process", return_value={"email": "tester@example.test", "status": "launched"}))
            app.main()
            self.assertEqual(process.call_args.args[1], "  synthetic password  ")

    def test_empty_input_fails_before_device_access(self):
        with patch.object(sys, "argv", ["ultra0.py", "--account", "tester@example.test", "--password-stdin"]), patch.object(sys, "stdin", io.StringIO("")), patch.object(app, "find_adb") as adb:
            with self.assertRaises(SystemExit):
                app.main()
        adb.assert_not_called()

if __name__ == "__main__":
    unittest.main()
