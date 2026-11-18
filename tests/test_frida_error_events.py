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

class FridaMessageTests(unittest.TestCase):
    def run_message(self, message):
        script, session = MagicMock(), MagicMock()
        session.create_script.return_value = script
        fake = types.SimpleNamespace(get_usb_device=MagicMock())
        fake.get_usb_device.return_value.attach.return_value = session
        script.load.side_effect = lambda: script.on.call_args.args[1](message, None)
        with patch.dict(sys.modules, {"frida": fake}), patch.object(app.time, "sleep"):
            return app.run_trial(123, wait=0)

    def test_javascript_error_is_retained(self):
        result = self.run_message({"type": "error", "description": "synthetic script failure"})
        self.assertEqual(result["errors"], [{"ev": "script_error", "m": "synthetic script failure"}])

    def test_non_object_payload_is_ignored(self):
        for payload in ("diagnostic text", [1], 7):
            with self.subTest(payload=payload):
                self.assertEqual(self.run_message({"type": "send", "payload": payload})["errors"], [])

if __name__ == "__main__":
    unittest.main()
