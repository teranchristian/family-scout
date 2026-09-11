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
                "exact_date_event_findings": [{
                    "name": "Hands-on session",
                    "source_url": calendar,
                    "date": "2030-04-07",
                    "time": "10:00-11:00",
                    "detail": "The requested-date calendar lists this session.",
                    "option_number": 1,
                }],
                "finalist_date_enrichment": [{
                    "option_number": 1,
                    "source_urls": [facts, calendar],
                    "dated_findings": [
                        {
                            "kind": "venue_availability",
                            "name": "Venue opening",
                            "status": "available",
                            "detail": "Current venue information supports opening on the requested date.",
                            "source_url": facts,
                        },
                        {
                            "kind": "scheduled_activity",
                            "name": "Hands-on session",
                            "status": "available",
                            "detail": "The requested-date calendar confirms the scheduled session.",
                            "source_url": calendar,
                        },
                    ],
                }],
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
                    "source_urls": [facts, calendar],
                    "link_checks": [
                        {"url": facts, "purposes": ["facts"],
                         "result": "content_verified", "checked_at": checked},
                        {"url": calendar, "purposes": ["facts"],
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
                "tool_usage": {"search_queries": 3, "source_fetches": 8,
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
                        "source_url": calendar,
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

    def test_finalist_requires_concrete_dated_findings(self):
        payload = self.payload()
        payload["discovery"]["finalist_date_enrichment"][0]["dated_findings"] = []
        result = self.run_finalize(payload, expected=2)
        self.assertIn("concrete dated_findings", result["error"])
        self.assert_no_real_write()

    def test_unverified_finalist_enrichment_url_fails_without_real_write(self):
        payload = self.payload()
        missing = "https://events.example.org/not-option"
        payload["shortlist"]["consulted_sources"].append({"url": missing, "status": "read"})
        payload["discovery"]["finalist_date_enrichment"][0]["source_urls"] = [missing]
        payload["discovery"]["finalist_date_enrichment"][0]["dated_findings"][0]["source_url"] = missing
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

    def test_exact_date_event_finding_must_render_for_finalist(self):
        payload = self.payload()
        payload["discovery"]["exact_date_event_findings"][0]["name"] = "Morning workshop"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("must appear as an available scheduled_activity", result["error"])
        self.assert_no_real_write()

    def test_dated_subfacility_finding_must_render(self):
        payload = self.payload()
        payload["discovery"]["finalist_date_enrichment"][0]["dated_findings"].append({
            "kind": "sub_facility",
            "name": "Planetarium",
            "status": "unavailable",
            "detail": "The sub-facility is closed on the requested date.",
            "source_url": payload["discovery"]["finalist_date_enrichment"][0]["source_urls"][0],
        })
        result = self.run_finalize(payload, expected=2)
        self.assertIn("dated sub_facility 'Planetarium' must appear", result["error"])
        self.assert_no_real_write()

    def test_bad_render_fails_without_real_write(self):
        payload = self.payload()
        payload["render"]["cards"][0]["activities"][0]["availability"] = "unknown"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("exact-date event", result["error"])
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
        self.assertEqual(coverage["exact_date_event_findings_captured"], 1)
        self.assertEqual(coverage["finalist_date_evidence_sources"], 2)
        self.assertEqual(coverage["finalist_dated_findings"], 2)
        self.assertIn("6 fresh + 0 cached lead(s) across 4 categories",
                      result["research_summary_markdown"])
        self.assertIn("1 exact-date event/calendar source(s) checked",
                      result["research_summary_markdown"])
        self.assertIn("1 exact-date event finding(s) captured",
                      result["research_summary_markdown"])
        self.assertIn("Hands-on session", result["numbered_options_markdown"])
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)

    def test_compact_payload_omits_duplicate_enrichment_structures(self):
        payload = self.payload()
        payload["shortlist"]["operation_id"] = "op-finalize-compact"
        payload["discovery"].pop("exact_date_event_findings")
        payload["discovery"].pop("finalist_date_enrichment")
        payload["shortlist"]["options"][0]["place"] = {
            "name": "Example Hall",
            "area": "Example City",
            "categories": ["hands-on"],
            "official_url": "https://events.example.org/activity",
            "address": "1 Public Road, Example City",
        }
        result = self.run_finalize(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["place_cache"]["upserted"], 1)
        self.assertEqual(len((self.data / "places.jsonl").read_text().splitlines()), 1)

    def test_print_template_needs_no_state_or_source_reads(self):
        completed = subprocess.run(
            [PYTHON, FINALIZE, "--print-template"],
            text=True, capture_output=True, cwd=REPO, check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        template = json.loads(completed.stdout)
        self.assertEqual(template["shortlist"]["effort_mode"], "normal")
        self.assertIn("place", template["shortlist"]["options"][0])
        self.assertNotIn("finalist_date_enrichment", template["discovery"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
