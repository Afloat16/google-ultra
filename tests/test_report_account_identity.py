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

class ReportIdentityTests(unittest.TestCase):
    def test_same_local_part_preserves_both_reports(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", ["ultra0.py", "accounts.txt"]))
            stack.enter_context(patch.object(app, "REPORT_DIR", Path(temporary)))
            for name in ("find_adb", "pick_device", "ensure_root", "ensure_network", "ensure_frida_server", "ensure_module_apk"):
                stack.enter_context(patch.object(app, name))
            emails = ["tester@example.test", "tester@another.test"]
            stack.enter_context(patch.object(app, "parse_accounts", return_value=[[email, "", "", ""] for email in emails]))
            stack.enter_context(patch.object(app, "process", side_effect=lambda email, *args, **kwargs: {"email": email, "status": "launched"}))
            app.main()
            paths = list(Path(temporary).glob("*.json"))
            self.assertEqual(len(paths), 2)
            self.assertEqual({json.loads(p.read_text())["email"] for p in paths}, set(emails))
            for path in paths:
                self.assertRegex(path.name, r"^[0-9a-f]{64}\.json$")

if __name__ == "__main__":
    unittest.main()
