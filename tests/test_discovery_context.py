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

    def test_preferred_urls_available_only_at_home_and_preserve_suburb_label(self):
        urls = ["https://events.example.org/city", "https://events.example.org/library"]
        update = {
            "operation_id": "op-preferred-home-urls",
            "reviewed_at": "2030-04-01T00:00:00Z",
            "source": "explicit_user",
            "changes": {
                "home": {
                    "label": "Example Suburb",
                    "latitude": 1.0,
                    "longitude": 2.0,
                    "timezone": "Etc/UTC",
                    "preferred_event_urls": urls,
                },
                "travel": {
                    "label": "Example Travel Town",
                    "latitude": 3.0,
                    "longitude": 4.0,
                    "timezone": "Etc/UTC",
                    "expires_at": "2030-04-08T23:59:59+00:00",
                },
            },
        }
        input_path = self.root / "profile-update.json"
        input_path.write_text(json.dumps(update), encoding="utf-8")
        saved = self.run_script(FULL_CONTEXT, "profile-update", "--input", str(input_path))
        self.assertEqual(saved.returncode, 0, msg=saved.stderr)

        travel = self.run_script(DISCOVERY_CONTEXT, "--at", "2030-04-06T10:00:00Z")
        self.assertEqual(travel.returncode, 0, msg=travel.stderr)
        travel_data = json.loads(travel.stdout)
        self.assertEqual(travel_data["resolved_location"]["origin_ref"], "travel")
        self.assertEqual(travel_data["preferred_event_urls"], [])

        home = self.run_script(DISCOVERY_CONTEXT, "--at", "2030-04-10T10:00:00Z")
        self.assertEqual(home.returncode, 0, msg=home.stderr)
        home_data = json.loads(home.stdout)
        self.assertEqual(home_data["resolved_location"]["origin_ref"], "home")
        self.assertEqual(home_data["preferred_event_urls"], urls)
        self.assertEqual(home_data["resolved_location"]["location"]["label"], "Example Suburb")
        self.assertEqual(home_data["resolved_location"]["location"]["latitude"], 1.0)
        self.assertEqual(home_data["profile"]["home"]["preferred_event_urls"], urls)

    def test_preferred_urls_optional_clearable_and_validated(self):
        empty = self.run_script(DISCOVERY_CONTEXT)
        self.assertEqual(empty.returncode, 0, msg=empty.stderr)
        self.assertEqual(json.loads(empty.stdout)["preferred_event_urls"], [])

        input_path = self.root / "url-update.json"
        cases = [
            "https://events.example.org",
            ["file:///tmp/calendar"],
            ["https://events.example.org", "https://events.example.org"],
        ]
        for index, bad_urls in enumerate(cases):
            payload = {
                "operation_id": f"op-invalid-urls-{index}",
                "source": "explicit_user",
                "changes": {"home": {"preferred_event_urls": bad_urls}},
            }
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            failed = self.run_script(FULL_CONTEXT, "profile-update", "--input", str(input_path))
            self.assertEqual(failed.returncode, 2, msg=failed.stdout)
            self.assertIn("preferred_event_urls", failed.stderr)
        for operation_id, urls in [
            ("op-add-valid-home-urls", ["https://events.example.org"]),
            ("op-clear-home-urls", []),
        ]:
            payload = {
                "operation_id": operation_id,
                "source": "explicit_user",
                "changes": {"home": {
                    "label": "Example Suburb",
                    "preferred_event_urls": urls,
                }},
            }
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            saved = self.run_script(FULL_CONTEXT, "profile-update", "--input", str(input_path))
            self.assertEqual(saved.returncode, 0, msg=saved.stderr)
            found = self.run_script(DISCOVERY_CONTEXT)
            self.assertEqual(found.returncode, 0, msg=found.stderr)
            result = json.loads(found.stdout)
            self.assertEqual(result["preferred_event_urls"], urls)
            self.assertEqual(result["resolved_location"]["location"]["latitude"], None)

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
        self.assertNotIn("recent_shortlists", payload)
        self.assertNotIn("effective_feedback", payload)
        self.assertNotIn("places", payload)
        self.assertNotIn("place_cache", payload)

        full = self.run_script(FULL_CONTEXT, "context")
        self.assertEqual(full.returncode, 2)
        self.assertIn("malformed", full.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
