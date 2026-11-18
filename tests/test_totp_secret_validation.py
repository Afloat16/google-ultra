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

class TotpSecretTests(unittest.TestCase):
    def test_invalid_characters_are_not_silently_removed(self):
        for secret in ("MZXW6!!!", "MZXW60", "MZXW6=YQ"):
            with self.subTest(secret=secret), self.assertRaises(ValueError):
                app.totp(secret)

    def test_rfc6238_vector_and_whitespace(self):
        secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        with patch.object(app.time, "time", return_value=59):
            self.assertEqual(app.totp(secret, digits=8), "94287082")
            self.assertEqual(app.totp(" "+secret.lower()+"\n", digits=8), "94287082")

if __name__ == "__main__":
    unittest.main()
