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

class AdbProbeTests(unittest.TestCase):
    def test_failed_candidate_does_not_hide_working_adb(self):
        fail = types.SimpleNamespace(returncode=1, stdout=b"", stderr=b"failed")
        good = types.SimpleNamespace(returncode=0, stdout=b"Android Debug Bridge version 1.0.41")
        with patch.object(app, "ADB_CANDIDATES", ["/bad/adb", "adb"]), patch.object(app.Path, "exists", return_value=True), patch.object(app.subprocess, "run", side_effect=[fail, good]):
            self.assertEqual(app.find_adb(), "adb")

    def test_unrelated_command_is_rejected(self):
        fake = types.SimpleNamespace(returncode=0, stdout=b"unrelated utility")
        with patch.object(app, "ADB_CANDIDATES", ["adb"]), patch.object(app.subprocess, "run", return_value=fake):
            with self.assertRaises(SystemExit):
                app.find_adb()

if __name__ == "__main__":
    unittest.main()
