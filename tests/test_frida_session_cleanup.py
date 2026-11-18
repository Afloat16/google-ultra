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

class FridaCleanupTests(unittest.TestCase):
    def test_session_is_released_on_success_and_load_failure(self):
        for failure in (None, RuntimeError("load failed")):
            with self.subTest(failure=failure):
                script, session = MagicMock(), MagicMock()
                session.create_script.return_value = script
                script.load.side_effect = failure
                fake = types.SimpleNamespace(get_usb_device=MagicMock())
                fake.get_usb_device.return_value.attach.return_value = session
                with patch.dict(sys.modules, {"frida": fake}), patch.object(app.time, "sleep"):
                    if failure:
                        with self.assertRaisesRegex(RuntimeError, "load failed"):
                            app.run_trial(123, wait=0)
                    else:
                        app.run_trial(123, wait=0)
                script.unload.assert_called_once()
                session.detach.assert_called_once()

    def test_script_creation_failure_still_detaches(self):
        session = MagicMock()
        session.create_script.side_effect = RuntimeError("create failed")
        fake = types.SimpleNamespace(get_usb_device=MagicMock())
        fake.get_usb_device.return_value.attach.return_value = session
        with patch.dict(sys.modules, {"frida": fake}):
            with self.assertRaisesRegex(RuntimeError, "create failed"):
                app.run_trial(123, wait=0)
        session.detach.assert_called_once()

if __name__ == "__main__":
    unittest.main()
