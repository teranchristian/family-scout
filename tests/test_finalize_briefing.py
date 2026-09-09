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
        calendar = "https://events.example.org/calendar/2030-04-07"
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
                "exact_date_event_source_urls": [calendar],
                "finalist_date_enrichment": [
                    {"option_number": 1, "source_urls": [facts]}
                ],
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
                "consulted_sources": [
                    {"url": facts, "status": "read"},
                    {"url": calendar, "status": "read"},
                ],
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

    def assert_no_real_write(self):
        self.assertEqual((self.data / "shortlists.jsonl").read_text(), "")

    def test_incomplete_enrichment_fails_without_real_write(self):
        payload = self.payload()
        payload["discovery"]["finalist_date_enrichment"] = []
        result = self.run_finalize(payload, expected=2)
        self.assertIn("every finalist", result["error"])
        self.assert_no_real_write()

    def test_unverified_finalist_enrichment_url_fails_without_real_write(self):
        payload = self.payload()
        calendar = payload["discovery"]["exact_date_event_source_urls"][0]
        payload["discovery"]["finalist_date_enrichment"][0]["source_urls"] = [calendar]
        result = self.run_finalize(payload, expected=2)
        self.assertIn("date-enrichment URL must be saved", result["error"])
        self.assert_no_real_write()

    def test_unread_exact_date_event_source_fails_without_real_write(self):
        payload = self.payload()
        payload["discovery"]["exact_date_event_source_urls"] = [
            "https://events.example.org/not-consulted"
        ]
        result = self.run_finalize(payload, expected=2)
        self.assertIn("exact-date event source", result["error"])
        self.assert_no_real_write()

    def test_bad_render_fails_without_real_write(self):
        payload = self.payload()
        payload["render"]["cards"][0]["activities"][0]["availability"] = "unknown"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("at least one activity available", result["error"])
        self.assert_no_real_write()

    def test_japanese_descriptive_content_fails_without_real_write(self):
        payload = self.payload()
        payload["render"]["cards"][0]["activities"][0]["name"] = "屋内遊び場"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("render content must be English", result["error"])
        self.assert_no_real_write()

    def test_local_language_option_title_is_allowed(self):
        payload = self.payload()
        payload["shortlist"]["operation_id"] = "op-finalize-local-title"
        payload["shortlist"]["options"][0]["title"] = "サンプル活動"
        result = self.run_finalize(payload)
        self.assertIn("サンプル活動", result["numbered_options_markdown"])
        self.assertIn("Hands-on session", result["numbered_options_markdown"])

    def test_valid_payload_saves_renders_and_reports_research_summary(self):
        payload = self.payload()
        result = self.run_finalize(payload)
        self.assertTrue(result["ok"])
        coverage = result["research_coverage"]
        self.assertEqual(coverage["fresh_candidates"], 6)
        self.assertEqual(coverage["activity_classes_checked"], 4)
        self.assertEqual(coverage["confirmed_recommendations"], 1)
        self.assertEqual(coverage["needs_checking"], 0)
        self.assertEqual(coverage["not_shortlisted"], 5)
        self.assertEqual(coverage["exact_date_event_sources_checked"], 1)
        self.assertEqual(coverage["finalist_date_evidence_sources"], 1)
        self.assertIn("6 fresh candidates across 4 categories",
                      result["research_summary_markdown"])
        self.assertIn("1 exact-date event/calendar source(s) checked",
                      result["research_summary_markdown"])
        self.assertIn("Hands-on session", result["numbered_options_markdown"])
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
