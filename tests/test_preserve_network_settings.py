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

class NetworkSettingsTests(unittest.TestCase):
    def test_network_probe_does_not_mutate_settings_or_stop_apps(self):
        with patch.object(app, "sh", return_value="proxy-configured") as shell:
            app.ensure_network()
        commands = [call.args[1] for call in shell.call_args_list]
        self.assertFalse(any("settings put" in command or "force-stop" in command for command in commands), commands)

    def test_proxy_value_is_not_logged(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), patch.object(app, "sh", return_value="private-proxy-value"):
            app.ensure_network()
        self.assertNotIn("private-proxy-value", buffer.getvalue())

if __name__ == "__main__":
    unittest.main()
