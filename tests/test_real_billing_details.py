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

class BillingDetailsTests(unittest.TestCase):
    def test_card_setup_does_not_fill_invented_address(self):
        card = {"number": "4242424242424242", "exp": "10/29", "cvc": "000", "holder": "", "zip": ""}
        with patch.object(app, "sh"), patch.object(app.time, "sleep"), patch.object(app, "tap_text", return_value=True), patch.object(app, "nodes", return_value=[{"cls": "EditText", "x": 1, "y": 1}] * 7), patch.object(app, "ui_xml", return_value=""), patch.object(app, "type_text") as write, patch.object(app, "wait_human", return_value=True) as human:
            self.assertTrue(app.add_card(card))
        write.assert_not_called()
        human.assert_called_once()

    def test_declined_confirmation_is_not_success(self):
        with patch.object(app, "sh"), patch.object(app, "wait_human", return_value=False):
            self.assertFalse(app.add_card({"number": "synthetic"}))

if __name__ == "__main__":
    unittest.main()
