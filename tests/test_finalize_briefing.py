#!/usr/bin/env python3
"""Regression tests for atomic Family Scout recommendation finalization."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
SETUP = REPO / "scripts" / "setup.py"
FINALIZE = REPO / "scripts" / "finalize_briefing.py"


class FinalizeBriefingTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-finalize-test-")
        self.root = Path(self.temporary.name)
        self.hermes = self.root / "hermes"
        self.data = self.root / "data"
        self.hermes.mkdir()
        completed = subprocess.run(
            [PYTHON, SETUP, "install", "--hermes-home", str(self.hermes),
             "--data-dir", str(self.data)],
            text=True, capture_output=True, cwd=REPO, check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def payload():
        facts = "https://events.example.org/activity"
        map_url = "https://maps.example.org/?q=example"
        checked = "2030-04-06T09:00:00Z"
        return {
            "discovery": {
                "fresh_discovery_completed": True,
                "candidates_considered": 6,
                "activity_classes_searched": [
                    "dated_events", "play", "culture", "commercial"
                ],
                "exact_date_event_searched": True,
                "finalist_numbers_date_enriched": [1],
            },
            "shortlist": {
                "operation_id": "op-finalize-example",
                "created_at": checked,
                "conversation_ref": "conversation-example",
                "effort_mode": "normal",
                "request": {
                    "origin_ref": "explicit",
                    "place_label": "Example City",
                    "date_start": "2030-04-07",
                    "date_end": "2030-04-07",
                    "timezone": "Etc/UTC",
                    "radius_km": 10,
                    "attending_member_ids": [],
                },
                "weather": {"status": "unknown", "reason": "fixture"},
                "options": [{
                    "title": "Example Activity",
                    "venue": "Example Hall",
                    "date_start": "2030-04-07T10:00:00+00:00",
                    "date_end": "2030-04-07T11:00:00+00:00",
                    "checked_at": checked,
                    "source_urls": [facts],
                    "link_checks": [
                        {"url": facts, "purposes": ["facts"],
                         "result": "content_verified", "checked_at": checked},
                        {"url": map_url, "purposes": ["map"],
                         "result": "reachable", "checked_at": checked},
                    ],
                    "distance_km": 1.2,
                    "cost": {"status": "known", "amount": 0,
                             "currency": "XXX", "basis": "attending group"},
                    "indoor_status": "indoor",
                    "booking": {"required": False, "availability": "not_applicable"},
                    "why": "Current evidence confirms the session.",
                    "constraint_results": [
                        {"requirement": "radius", "status": "confirmed_match",
                         "reason": "inside inclusive boundary"},
                        {"requirement": "date", "status": "confirmed_match",
                         "reason": "usable interval overlaps"},
                    ],
                    "features": ["hands-on"],
                }],
                "needs_checking": [],
                "consulted_sources": [{"url": facts, "status": "read"}],
                "tool_usage": {"search_queries": 4, "source_fetches": 8,
                               "forecast_lookups": 0},
            },
            "render": {
                "cards": [{
                    "number": 1,
                    "body": "A verified indoor activity with a checked address and map.",
                    "activities": [{
                        "name": "Hands-on session",
                        "kind": "scheduled_activity",
                        "availability": "available",
                        "detail": "The dated listing confirms this session.",
                        "source_url": facts,
                    }],
                    "family_fit": [{
                        "member_id": "member-example",
                        "label": "Example child",
                        "fit": "strong",
                        "activity_names": ["Hands-on session"],
                        "limitations": [],
                    }],
                }]
            },
        }

    def run_finalize(self, payload, expected=0):
        input_path = self.root / "payload.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run(
            [PYTHON, FINALIZE, "--source-dir", str(REPO),
             "--data-dir", str(self.data), "--input", str(input_path)],
            text=True, capture_output=True, cwd=REPO, check=False,
        )
        self.assertEqual(completed.returncode, expected,
                         msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
        return json.loads(completed.stdout if expected == 0 else completed.stderr)

    def test_incomplete_enrichment_fails_without_real_write(self):
        payload = self.payload()
        payload["discovery"]["finalist_numbers_date_enriched"] = []
        result = self.run_finalize(payload, expected=2)
        self.assertIn("every finalist", result["error"])
        self.assertEqual((self.data / "shortlists.jsonl").read_text(), "")

    def test_bad_render_fails_without_real_write(self):
        payload = self.payload()
        payload["render"]["cards"][0]["activities"][0]["availability"] = "unknown"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("at least one activity available", result["error"])
        self.assertEqual((self.data / "shortlists.jsonl").read_text(), "")

    def test_valid_payload_saves_and_renders_once(self):
        # No attending IDs in the saved request means the renderer does not require
        # a specific private family member fixture, so omit the synthetic fit row.
        payload = self.payload()
        payload["render"]["cards"][0]["family_fit"] = [{
            "member_id": "member-example",
            "label": "Example child",
            "fit": "strong",
            "activity_names": ["Hands-on session"],
            "limitations": [],
        }]
        result = self.run_finalize(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["research_coverage"]["candidates_considered"], 6)
        self.assertIn("Hands-on session", result["numbered_options_markdown"])
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
