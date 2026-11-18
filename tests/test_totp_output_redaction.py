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

class TotpPrivacyTests(unittest.TestCase):
    def test_live_code_is_not_printed(self):
        text = '<hierarchy><node text="两步验证" class="android.widget.EditText" bounds="[1,1][10,10]"/></hierarchy>'
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), patch.object(app, "accounts_on_device", side_effect=[[], [], ["account"]]), patch.object(app, "sh"), patch.object(app.time, "sleep"), patch.object(app, "tap_text", return_value=False), patch.object(app, "find_edit", side_effect=[None, None, (1, 1), (1, 1)]), patch.object(app, "ui_xml", return_value=text), patch.object(app, "totp", return_value="867530"), patch.object(app, "type_text") as write:
            self.assertTrue(app.add_account("tester@example.test", "synthetic", "synthetic"))
        write.assert_called_once_with("867530")
        self.assertNotIn("867530", buffer.getvalue())

if __name__ == "__main__":
    unittest.main()
