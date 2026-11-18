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

class DeviceSelectionTests(unittest.TestCase):
    def setUp(self):
        app.SERIAL = None

    def test_multiple_devices_require_selection(self):
        with patch.object(app, "sh", return_value="List of devices attached\none\tdevice\ntwo\tdevice\n"):
            with self.assertRaises(SystemExit):
                app.pick_device()

    def test_explicit_serial_is_retained(self):
        app.SERIAL = "two"
        with patch.object(app, "sh", return_value="List of devices attached\none\tdevice\ntwo\tdevice\n"):
            app.pick_device()
        self.assertEqual(app.SERIAL, "two")

    def test_unavailable_serial_is_rejected(self):
        app.SERIAL = "two"
        with patch.object(app, "sh", return_value="List of devices attached\none\tdevice\ntwo\tunauthorized\n"):
            with self.assertRaises(SystemExit):
                app.pick_device()

    def test_check_honors_serial(self):
        with patch.object(sys, "argv", ["ultra0.py", "--check", "--serial", "two"]), patch.object(app, "find_adb", return_value="adb"), patch.object(app, "do_check", side_effect=lambda: app.SERIAL):
            self.assertEqual(app.main(), "two")

if __name__ == "__main__":
    unittest.main()
