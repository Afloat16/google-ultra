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

class ShellInputTests(unittest.TestCase):
    def test_password_quote_is_not_shell_syntax(self):
        import shlex
        for value in ("a'b", "a'b; c", "plain-text"):
            with self.subTest(value=value), patch.object(app, "sh") as shell:
                app.type_text(value)
                tokens = shlex.split(shell.call_args.args[1])
                self.assertEqual(tokens, ["input", "text", value.replace(" ", "%s")])

    def test_account_argument_is_one_shell_value(self):
        import shlex
        email = "o'brien@example.test"
        with patch.object(app, "sh") as shell, patch.object(app.time, "sleep"), patch.object(app, "current_play_account", return_value=email):
            self.assertTrue(app.switch_play(email))
        command = next(c.args[1] for c in shell.call_args_list if "authAccount" in c.args[1])
        self.assertEqual(shlex.split(command)[-1], email)

if __name__ == "__main__":
    unittest.main()
