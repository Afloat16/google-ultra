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

class UISnapshotTests(unittest.TestCase):
    def test_failed_dump_never_reads_stale_screen(self):
        calls = []
        def shell(*args, **kwargs):
            calls.append(args)
            if "uiautomator" in args[1]:
                if kwargs.get("check"):
                    raise RuntimeError("dump failed")
                return ""
            return '<hierarchy><node text="Subscribe"/></hierarchy>'
        with patch.object(app, "sh", side_effect=shell):
            with self.assertRaises(RuntimeError):
                app.ui_xml()
        self.assertFalse(any("cat " in args[1] for args in calls))

    def test_non_xml_output_is_rejected(self):
        with patch.object(app, "sh", return_value="permission denied"):
            with self.assertRaises(RuntimeError):
                app.ui_xml()

    def test_success_returns_current_hierarchy(self):
        xml = '<hierarchy rotation="0"></hierarchy>'
        with patch.object(app, "sh", side_effect=["", "dumped", xml]):
            self.assertEqual(app.ui_xml(), xml)

if __name__ == "__main__":
    unittest.main()
