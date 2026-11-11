"""Integration checks for optional Hermes skill lock during installation."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup.py"


class InstallerLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="family-scout-lock-test-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.bin = self.path / "bin"
        self.bin.mkdir()
        self.profile = self.path / "selected hermes profile"
        self.profile.mkdir()
        self.private = self.path / "private data"

    def run_install(self):
        environment = os.environ.copy()
        environment["PATH"] = str(self.bin)
        # Deliberately point the shell at another profile. --hermes-home must win.
        environment["HERMES_HOME"] = str(self.path / "wrong profile")
        return subprocess.run(
            [sys.executable, str(SETUP), "install",
             "--hermes-home", str(self.profile),
             "--data-dir", str(self.private)],
            cwd=ROOT, env=environment, text=True, capture_output=True,
            check=False,
        )

    def test_installer_locks_selected_hermes_home(self):
        cli = self.bin / "hermes"
        cli.write_text(
            "#!/bin/sh\n"
            'printf "%s\\n" "$1 $2 $3" > "$HERMES_HOME/lock-command.txt"\n'
            "exit 0\n", encoding="utf-8",
        )
        cli.chmod(0o755)
        result = self.run_install()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("LOCKED: Family Scout", result.stdout)
        self.assertEqual(
            (self.profile / "lock-command.txt").read_text().strip(),
            "curator lock family-scout",
        )
        self.assertFalse((self.path / "wrong profile").exists())
        self.assertTrue((self.profile / "skills" / "family-scout" / "SKILL.md").exists())

    def test_missing_hermes_warns_but_keeps_installation(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("LOCK NOT APPLIED: Hermes CLI is not on PATH", result.stdout)
        self.assertTrue((self.profile / "skills" / "family-scout" / "SKILL.md").exists())

    def test_unsupported_lock_warns_and_does_not_corrupt_existing_state(self):
        cli = self.bin / "hermes"
        cli.write_text("#!/bin/sh\nexit 2\n", encoding="utf-8")
        cli.chmod(0o755)
        result = self.run_install()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("LOCK NOT APPLIED:", result.stdout)
        self.assertTrue((self.profile / "skills" / "family-scout" / "SKILL.md").exists())
        self.assertTrue((self.private / "profile.yaml").exists())


if __name__ == "__main__":
    unittest.main()
