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

class ConfirmationClickTests(unittest.TestCase):
    def test_missing_button_is_not_confirmation(self):
        for text in ("Ultra 订阅 US$0.00", "Ultra 订阅 免费试用 12 个月"):
            with self.subTest(text=text), patch.object(app, "ui_xml", return_value=""), patch.object(app, "nodes", return_value=[{"text": text}]), patch.object(app, "tap_text", return_value=False):
                self.assertFalse(app.confirm_zero(wait=2)["confirmed"])

    def test_matched_button_is_recorded(self):
        with patch.object(app, "ui_xml", return_value=""), patch.object(app, "nodes", return_value=[{"text": "Ultra 订阅 US$0.00"}]), patch.object(app, "tap_text", return_value=True):
            self.assertTrue(app.confirm_zero(wait=2)["confirmed"])

if __name__ == "__main__":
    unittest.main()
