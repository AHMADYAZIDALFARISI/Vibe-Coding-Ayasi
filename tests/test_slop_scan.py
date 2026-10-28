import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills/interface-design/scripts"))
import slop_scan  # noqa: E402

FIXTURES = ROOT / "tests/fixtures"


class SlopScanTest(unittest.TestCase):
    def rules(self, name):
        return {h[2] for h in slop_scan.scan([str(FIXTURES / name)])}

    def test_flags_template_patterns(self):
        found = self.rules("sloppy.html")
        for rule in ("gradient", "glass", "lorem", "fake-metric", "zoom-block"):
            self.assertIn(rule, found)

    def test_clean_file_has_no_hits(self):
        self.assertEqual(self.rules("clean.html"), set())


if __name__ == "__main__":
    unittest.main()
