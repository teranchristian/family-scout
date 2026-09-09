#!/usr/bin/env python3
"""Tests for the history-free Family Scout discovery context."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
DISCOVERY = REPO / "scripts" / "discovery_context.py"
HELPER = REPO / "scripts" / "family_scout.py"


class DiscoveryContextTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-discovery-")
        self.data = Path(self.temporary.name)
        profile = {
            "schema_version": 1,
            "home": {
                "label": "Example City",
                "latitude": 0,
                "longitude": 0,
                "timezone": "Etc/UTC",
            },
            "default_radius_km": 12,
            "group_members": [{"id": "member-alpha", "age": 4}],
            "preferences": [],
            "constraints": [],
            "provenance": [],
            "travel": {
                "label": "Example Travel Area",
                "latitude": 1,
                "longitude": 1,
                "timezone": "Etc/UTC",
                "expires_at": "2030-04-08T23:59:59+00:00",
            },
        }
        sources = {
            "schema_version": 1,
            "sources": [{
                "id": "source-example",
                "name": "Example Events",
                "url": "https://events.example.org",
                "enabled": True,
                "scope": None,
                "added_at": "2030-04-01",
                "query_guidance": None,
            }],
        }
        (self.data / "profile.yaml").write_text(json.dumps(profile), encoding="utf-8")
        (self.data / "sources.yaml").write_text(json.dumps(sources), encoding="utf-8")
        # Deliberately malformed history proves discovery context does not even read it.
        (self.data / "shortlists.jsonl").write_text("{malformed\n", encoding="utf-8")
        (self.data / "feedback.jsonl").write_text("{malformed\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(script), "--data-dir", str(self.data), *arguments],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_discovery_context_omits_and_does_not_read_history(self):
        result = self.run_script(
            DISCOVERY, "--at", "2030-04-07T12:00:00+00:00"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["scope"], "discovery")
        self.assertFalse(payload["history_loaded"])
        self.assertNotIn("recent_shortlists", payload)
        self.assertNotIn("effective_feedback", payload)
        self.assertEqual(payload["resolved_location"]["origin_ref"], "travel")
        self.assertEqual(payload["profile"]["group_members"][0]["age"], 4)
        self.assertEqual(len(payload["enabled_sources"]), 1)

        # The normal context still reads history and therefore rejects the same
        # malformed files. This guards against accidental future coupling.
        full = self.run_script(
            HELPER, "context", "--at", "2030-04-07T12:00:00+00:00"
        )
        self.assertEqual(full.returncode, 2)

    def test_discovery_context_can_explicitly_use_home(self):
        result = self.run_script(
            DISCOVERY,
            "--at", "2030-04-07T12:00:00+00:00",
            "--location", "home",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["resolved_location"]["origin_ref"], "home")
        self.assertEqual(payload["resolved_location"]["location"]["label"], "Example City")


if __name__ == "__main__":
    unittest.main(verbosity=2)
