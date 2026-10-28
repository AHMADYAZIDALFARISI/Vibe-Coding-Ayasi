import sys
import unittest
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills/verification/scripts"))
import ui_probe  # noqa: E402

try:
    from playwright.sync_api import sync_playwright  # noqa: F401
    HAVE_PW = True
except ImportError:
    HAVE_PW = False


@unittest.skipUnless(HAVE_PW, "playwright not installed")
class UiProbeTest(unittest.TestCase):
    def run_probe(self, name):
        out = Path(tempfile.mkdtemp())
        return ui_probe.probe((ROOT / "tests/fixtures" / name).as_uri(), out, [360])["viewports"][360]

    def test_detects_problems(self):
        v = self.run_probe("sloppy.html")
        self.assertTrue(v["zoom_blocked"])
        self.assertEqual(len(v["unlabeled_inputs"]), 1)
        self.assertEqual(len(v["unnamed_controls"]), 1)
        self.assertEqual(v["duplicate_control_names"], ['2x "delete"'])
        self.assertEqual(len(v["broken_aria_refs"]), 1)
        self.assertEqual(len([p for p in v["focus_problems"] if "Delete" in p]), 2)
        self.assertEqual(len(v["images_without_alt"]), 1)
        self.assertGreater(v["horizontal_overflow_px"], 0)

    def test_clean_page(self):
        v = self.run_probe("clean.html")
        self.assertFalse(v["zoom_blocked"])
        self.assertEqual(v["focus_problems"], [])
        self.assertEqual(ui_probe.count_issues({"viewports": {360: v}}), 0)


class UiProbeCliTest(unittest.TestCase):
    @unittest.skipUnless(HAVE_PW, "playwright not installed")
    def test_unreachable_url_exits_2_without_traceback(self):
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT / "skills/verification/scripts/ui_probe.py"),
                            "http://127.0.0.1:9/", "--out", tempfile.mkdtemp()],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
