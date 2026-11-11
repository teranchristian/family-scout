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

    def run_script(self, script, *arguments):
        return subprocess.run(
            [PYTHON, script, "--data-dir", str(self.data), *arguments],
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )

    def test_discovery_context_does_not_read_or_expose_history_or_legacy_files(self):
        (self.data / "shortlists.jsonl").write_text("{malformed shortlist\n")
        (self.data / "feedback.jsonl").write_text("{malformed feedback\n")
        (self.data / "places.jsonl").write_text("{malformed place cache\n")

        discovery = self.run_script(DISCOVERY_CONTEXT)
        self.assertEqual(discovery.returncode, 0, msg=discovery.stderr)
        payload = json.loads(discovery.stdout)
        self.assertEqual(payload["scope"], "discovery")
        self.assertRegex(payload["run_started_at"], r"^\d{4}-\d{2}-\d{2}T")
        self.assertIn("profile", payload)
        self.assertIn("resolved_location", payload)
        self.assertIn("enabled_sources", payload)
        self.assertEqual(payload["location_sources"], {"suburb": None, "urls": []})
        self.assertNotIn("recent_shortlists", payload)
        self.assertNotIn("effective_feedback", payload)
        self.assertNotIn("places", payload)
        self.assertNotIn("place_cache", payload)

        full = self.run_script(FULL_CONTEXT, "context")
        self.assertEqual(full.returncode, 2)
        self.assertIn("malformed", full.stderr)

    def test_location_sources_match_active_home_and_explicit_suburb(self):
        profile_path = self.data / "profile.yaml"
        profile = json.loads(profile_path.read_text())
        profile["home"]["label"] = "EXAMPLETOWN, NSW, Australia"
        profile_path.write_text(json.dumps(profile))
        (self.data / "sources.yml").write_text(
            "# Public calendars only\n"
            "exampletown:\n"
            "  - https://events.example.org/home\n"
            "other suburb:\n"
            "  - https://events.example.org/other\n"
        )

        home = self.run_script(DISCOVERY_CONTEXT)
        self.assertEqual(home.returncode, 0, msg=home.stderr)
        self.assertEqual(json.loads(home.stdout)["location_sources"], {
            "suburb": "exampletown", "urls": ["https://events.example.org/home"]
        })
        explicit = self.run_script(DISCOVERY_CONTEXT, "--source-location", "Other Suburb, NSW")
        self.assertEqual(explicit.returncode, 0, msg=explicit.stderr)
        self.assertEqual(json.loads(explicit.stdout)["location_sources"], {
            "suburb": "other suburb", "urls": ["https://events.example.org/other"]
        })
        missing = self.run_script(DISCOVERY_CONTEXT, "--source-location", "Unknown")
        self.assertEqual(missing.returncode, 0, msg=missing.stderr)
        self.assertEqual(json.loads(missing.stdout)["location_sources"]["urls"], [])

    def test_location_sources_follow_active_travel_and_expiry(self):
        profile_path = self.data / "profile.yaml"
        profile = json.loads(profile_path.read_text())
        profile["home"]["label"] = "Exampletown, NSW"
        profile["travel"] = {
            "label": "Holidaytown, Region", "latitude": None, "longitude": None,
            "timezone": "Etc/UTC", "expires_at": "2030-06-10T00:00:00Z"
        }
        profile_path.write_text(json.dumps(profile))
        (self.data / "sources.yml").write_text(
            "exampletown:\n  - https://events.example.org/home\n"
            "holidaytown:\n  - https://events.example.org/travel\n"
        )
        during = self.run_script(DISCOVERY_CONTEXT, "--at", "2030-06-09T00:00:00Z")
        self.assertEqual(during.returncode, 0, msg=during.stderr)
        self.assertEqual(json.loads(during.stdout)["location_sources"]["suburb"], "holidaytown")
        after = self.run_script(DISCOVERY_CONTEXT, "--at", "2030-06-11T00:00:00Z")
        self.assertEqual(after.returncode, 0, msg=after.stderr)
        self.assertEqual(json.loads(after.stdout)["location_sources"]["suburb"], "exampletown")

    def test_invalid_location_source_file_fails_without_rewriting(self):
        path = self.data / "sources.yml"
        invalid = b"Exampletown:\n  - file:///private/path\n"
        path.write_bytes(invalid)
        result = self.run_script(DISCOVERY_CONTEXT)
        self.assertEqual(result.returncode, 2)
        self.assertIn("sources.yml line 2", result.stderr)
        self.assertEqual(path.read_bytes(), invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
