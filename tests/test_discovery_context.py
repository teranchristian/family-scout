#!/usr/bin/env python3
"""Tests for history-free Family Scout discovery context."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
SETUP = REPO / "scripts" / "setup.py"
DISCOVERY_CONTEXT = REPO / "scripts" / "discovery_context.py"
FULL_CONTEXT = REPO / "scripts" / "family_scout.py"


class DiscoveryContextTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-discovery-")
        self.root = Path(self.temporary.name)
        self.hermes = self.root / "hermes"
        self.data = self.root / "data"
        self.hermes.mkdir()
        completed = subprocess.run(
            [PYTHON, SETUP, "install", "--hermes-home", str(self.hermes),
             "--data-dir", str(self.data)],
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, script):
        return subprocess.run(
            [PYTHON, script, "--data-dir", str(self.data)],
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )

    def test_discovery_context_does_not_read_or_expose_history(self):
        (self.data / "shortlists.jsonl").write_text("{malformed shortlist\n")
        (self.data / "feedback.jsonl").write_text("{malformed feedback\n")

        discovery = self.run_script(DISCOVERY_CONTEXT)
        self.assertEqual(discovery.returncode, 0, msg=discovery.stderr)
        payload = json.loads(discovery.stdout)
        self.assertEqual(payload["scope"], "discovery")
        self.assertIn("profile", payload)
        self.assertIn("resolved_location", payload)
        self.assertIn("enabled_sources", payload)
        self.assertNotIn("recent_shortlists", payload)
        self.assertNotIn("effective_feedback", payload)

        full = self.run_script(FULL_CONTEXT)
        self.assertEqual(full.returncode, 2)
        self.assertIn("malformed", full.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
