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

class AccountFileTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "accounts.txt"
            path.write_text(text, encoding="utf-8")
            return app.parse_accounts(path)

    def test_bom_and_password_whitespace_are_preserved(self):
        rows = self.parse("\ufefftester@example.test----  secret with spaces  ---- recovery@example.test \n")
        self.assertEqual(rows[0][0], "tester@example.test")
        self.assertEqual(rows[0][1], "  secret with spaces  ")
        self.assertEqual(rows[0][2], "recovery@example.test")

    def test_extra_fields_are_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "第 1 行"):
            self.parse("----".join(["tester@example.test"] + ["x"] * 9))

    def test_blank_and_comment_lines_are_ignored(self):
        self.assertEqual(self.parse("  # comment\n\n"), [])

if __name__ == "__main__":
    unittest.main()
