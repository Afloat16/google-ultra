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

class HumanConfirmationTests(unittest.TestCase):
    def test_timeout_does_not_resume(self):
        with self.assertRaises(TimeoutError):
            app.wait_human("Confirm", timeout=0)
        self.assertFalse(app.WAITING["on"])

    def test_eof_does_not_acknowledge(self):
        with patch.object(app.select, "select", return_value=([object()], [], [])), patch.object(app.sys, "stdin", io.StringIO("")):
            with self.assertRaises(EOFError):
                app.wait_human("Confirm", timeout=2)
        self.assertFalse(app.WAITING["on"])

    def test_enter_acknowledges(self):
        with patch.object(app.select, "select", return_value=([object()], [], [])), patch.object(app.sys, "stdin", io.StringIO("\n")):
            self.assertTrue(app.wait_human("Confirm", timeout=2))

    def test_interruption_clears_waiting(self):
        with patch.object(app.select, "select", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                app.wait_human("Confirm", timeout=2)
        self.assertFalse(app.WAITING["on"])

    def test_card_confirmation_error_stops_before_checkout(self):
        with patch.object(app, "add_card", side_effect=TimeoutError), patch.object(app, "switch_play") as switch:
            result = app.process("tester@example.test", add=False, card={"number": "synthetic"})
        self.assertEqual(result["status"], "add_card_error")
        switch.assert_not_called()

if __name__ == "__main__":
    unittest.main()
