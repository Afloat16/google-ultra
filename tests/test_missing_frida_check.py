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

class DependencyCheckTests(unittest.TestCase):
    def test_missing_frida_returns_failure_without_device_changes(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {"frida": None}))
            adb = stack.enter_context(patch.object(app, "find_adb"))
            mutations = []
            for name in ("pick_device", "ensure_root", "ensure_network", "ensure_frida_server", "ensure_module_apk"):
                mutations.append(stack.enter_context(patch.object(app, name)))
            self.assertEqual(app.do_check(), 1)
            adb.assert_not_called()
            for call in mutations:
                call.assert_not_called()

if __name__ == "__main__":
    unittest.main()
