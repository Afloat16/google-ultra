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

class ExitStatusTests(unittest.TestCase):
    def test_failed_run_is_nonzero(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", ["ultra0.py", "--account", "tester@example.test:synthetic"]))
            stack.enter_context(patch.object(app, "REPORT_DIR", Path(temporary)))
            for name in ("find_adb", "pick_device", "ensure_root", "ensure_network", "ensure_frida_server", "ensure_module_apk"):
                stack.enter_context(patch.object(app, name))
            stack.enter_context(patch.object(app, "process", return_value={"email": "tester@example.test", "status": "wrong_account"}))
            self.assertEqual(app.main(), 1)

if __name__ == "__main__":
    unittest.main()
