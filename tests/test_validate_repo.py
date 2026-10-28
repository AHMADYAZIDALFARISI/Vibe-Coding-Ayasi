import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repo  # noqa: E402


class ValidateRepoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT, self.tmp / "repo", ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.repo = self.tmp / "repo"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def errors(self):
        return validate_repo.validate(self.repo)[1]

    def test_repository_is_clean(self):
        self.assertEqual(self.errors(), [])

    def test_name_folder_mismatch_is_caught(self):
        md = self.repo / "skills/verification/SKILL.md"
        md.write_text(md.read_text().replace("name: verification", "name: verify"))
        self.assertTrue(any("does not match folder" in e for e in self.errors()))

    def test_unknown_frontmatter_key_is_caught(self):
        md = self.repo / "skills/verification/SKILL.md"
        md.write_text(md.read_text().replace("name: verification", "name: verification\nversion: 1"))
        self.assertTrue(any("unexpected keys" in e for e in self.errors()))

    def test_broken_link_is_caught(self):
        (self.repo / "docs/broken.md").write_text("[x](missing.md)\n")
        self.assertTrue(any("broken link" in e for e in self.errors()))

    def test_secret_is_caught(self):
        fake = "ghp_" + "a" * 36
        (self.repo / "docs/leak.md").write_text(f"token {fake}\n")
        self.assertTrue(any("github-token" in e for e in self.errors()))

    def test_cli_exit_code(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/validate_repo.py"), str(self.repo)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
