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

class PrivateReportTests(unittest.TestCase):
    def run_main(self, directory):
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", ["ultra0.py", "--account", "tester@example.test:synthetic"]))
            stack.enter_context(patch.object(app, "REPORT_DIR", directory))
            for name in ("find_adb", "pick_device", "ensure_root", "ensure_network", "ensure_frida_server", "ensure_module_apk"):
                stack.enter_context(patch.object(app, name))
            stack.enter_context(patch.object(app, "process", return_value={"email": "tester@example.test", "status": "launched"}))
            app.main()

    @unittest.skipIf(os.name == "nt", "POSIX permissions")
    def test_report_is_owner_only_even_with_permissive_umask(self):
        with tempfile.TemporaryDirectory() as temporary:
            previous = os.umask(0)
            try:
                self.run_main(Path(temporary))
            finally:
                os.umask(previous)
            self.assertEqual((Path(temporary) / "tester.json").stat().st_mode & 0o777, 0o600)

    @unittest.skipIf(os.name == "nt", "symlink privilege varies on Windows")
    def test_existing_symlink_does_not_overwrite_another_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "preserved.txt"
            original.write_text("preserve")
            (root / "tester.json").symlink_to(original)
            self.run_main(root)
            self.assertEqual(original.read_text(), "preserve")
            self.assertFalse((root / "tester.json").is_symlink())

if __name__ == "__main__":
    unittest.main()
