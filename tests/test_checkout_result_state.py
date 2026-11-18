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

class CheckoutStateTests(unittest.TestCase):
    def check_sheet(self, sheet):
        with patch.object(app, "switch_play", return_value=True), patch.object(app, "launch_app", return_value=10), patch.object(app, "run_trial", return_value={"launched": {"code": 0}}), patch.object(app, "confirm_zero", return_value=sheet), patch.object(app, "verify", return_value="Ultra existing subscription") as verify:
            record = app.process("tester@example.test", add=False)
        return record, verify

    def test_ineligible_is_not_existing_subscription(self):
        record, verify = self.check_sheet({"ineligible": True, "confirmed": False})
        self.assertEqual(record["status"], "ineligible")
        verify.assert_not_called()

    def test_unconfirmed_does_not_claim_success(self):
        record, verify = self.check_sheet({"confirmed": False})
        self.assertEqual(record["status"], "confirmation_required")
        verify.assert_not_called()

    def test_confirmed_checkout_can_be_verified(self):
        record, verify = self.check_sheet({"confirmed": True})
        self.assertEqual(record["status"], "subscribed")
        verify.assert_called_once()

if __name__ == "__main__":
    unittest.main()
