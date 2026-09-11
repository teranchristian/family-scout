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
                "run_started_at": checked,
                "fresh_discovery_completed": True,
                "activity_classes_searched": [
                    "dated_events", "play", "culture", "commercial"
                ],
                "candidate_ledger": [
                    {"title": "Example Activity", "primary_class": "commercial",
                     "discovery_origin": "fresh", "disposition": "shown"},
                    {"title": "Example Event", "primary_class": "dated_events",
                     "discovery_origin": "fresh", "disposition": "not_shortlisted"},
                    {"title": "Example Playground", "primary_class": "play",
                     "discovery_origin": "fresh", "disposition": "not_shortlisted"},
                    {"title": "Example Museum", "primary_class": "culture",
                     "discovery_origin": "fresh", "disposition": "not_shortlisted"},
                    {"title": "Example Workshop", "primary_class": "commercial",
                     "discovery_origin": "fresh", "disposition": "not_shortlisted"},
                    {"title": "Example Library", "primary_class": "culture",
                     "discovery_origin": "fresh", "disposition": "not_shortlisted"},
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
                "result_mode": "verified",
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
        payload["discovery"]["candidate_ledger"][0]["title"] = "サンプル活動"
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

    def test_explore_mode_saves_and_renders_a_six_option_menu(self):
        payload = self.payload()
        payload["shortlist"]["operation_id"] = "op-explore-menu"
        payload["shortlist"]["result_mode"] = "explore"
        payload["discovery"]["cache_lookup_performed"] = True
        payload["shortlist"]["options"] = []
        payload["render"]["cards"] = []
        classes = ["dated_events", "play", "culture", "commercial", "play", "culture"]
        payload["discovery"]["candidate_ledger"] = []
        for index, candidate_class in enumerate(classes, 1):
            title = f"Example Possibility {index}"
            venue = f"Example Venue {index}"
            payload["discovery"]["candidate_ledger"].append({
                "title": title,
                "primary_class": candidate_class,
                "discovery_origin": "fresh",
                "disposition": "shown",
            })
            payload["shortlist"]["options"].append({
                "title": title,
                "venue": venue,
                "candidate_class": candidate_class,
                "discovery_origin": "fresh",
                "checked_at": "2030-04-06T09:00:00Z",
                "source_urls": ["https://events.example.org/activity"],
                "link_checks": [{
                    "url": "https://events.example.org/activity",
                    "purposes": ["facts"],
                    "result": "content_verified",
                    "checked_at": "2030-04-06T09:00:00Z",
                }],
                "why": "A distinct possibility for the family to consider.",
                "known": ["Listed by the current source."],
                "needs_verification": ["Requested-date details"],
            })
            payload["render"]["cards"].append({
                "number": index,
                "body": "A possible activity to compare before detailed verification.",
                "highlights": ["Different from the other menu choices"],
                "needs_verification": ["Requested-date details"],
            })
        result = self.run_finalize(payload)
        self.assertEqual(result["research_coverage"]["menu_options"], 6)
        self.assertEqual(result["research_coverage"]["confirmed_recommendations"], 0)
        self.assertIn("**6. Example Possibility 6**", result["numbered_options_markdown"])
        self.assertIn("Reply with the number or numbers", result["numbered_options_markdown"])
        saved = json.loads((self.data / "shortlists.jsonl").read_text().splitlines()[0])
        self.assertEqual(saved["result_mode"], "explore")
        self.assertEqual(len(saved["research"]["candidate_ledger"]), 6)
        self.assertIn("elapsed_seconds", saved["run_timing"])

    def test_explore_mode_refuses_to_collapse_to_three_options(self):
        payload = json.loads(subprocess.run(
            [PYTHON, FINALIZE, "--print-template"],
            text=True, capture_output=True, cwd=REPO, check=True,
        ).stdout)
        payload["shortlist"]["operation_id"] = "op-three-option-menu"
        payload["discovery"]["candidate_ledger"] = payload["discovery"][
            "candidate_ledger"
        ][:3]
        payload["shortlist"]["options"] = payload["shortlist"]["options"][:3]
        payload["render"]["cards"] = payload["render"]["cards"][:3]
        result = self.run_finalize(payload, expected=2)
        self.assertIn("at least four distinct options", result["error"])
        self.assert_no_real_write()

    def test_candidate_counts_cannot_be_backfilled_manually(self):
        payload = self.payload()
        payload["discovery"]["candidates_considered"] = 4
        result = self.run_finalize(payload, expected=2)
        self.assertIn("counts are derived", result["error"])
        self.assert_no_real_write()

    def test_shown_option_must_match_candidate_ledger(self):
        payload = self.payload()
        payload["discovery"]["candidate_ledger"][0]["title"] = "Different Candidate"
        result = self.run_finalize(payload, expected=2)
        self.assertIn("displayed option", result["error"])
        self.assert_no_real_write()

    def test_over_budget_finalize_preserves_actual_counts_and_warns(self):
        payload = self.payload()
        payload["shortlist"]["operation_id"] = "op-honest-over-budget"
        payload["shortlist"]["tool_usage"] = {
            "search_queries": 6,
            "source_fetches": 7,
            "forecast_lookups": 1,
            "geocode_lookups": 7,
        }
        result = self.run_finalize(payload)
        self.assertEqual(result["budget_status"], "exceeded")
        self.assertIn("21/12 external calls", result["numbered_options_markdown"])
        saved = json.loads((self.data / "shortlists.jsonl").read_text().splitlines()[0])
        self.assertEqual(saved["tool_usage"]["external_calls"], 21)
        self.assertEqual(saved["tool_usage"]["search_queries"], 6)

    def test_print_template_needs_no_state_or_source_reads(self):
        completed = subprocess.run(
            [PYTHON, FINALIZE, "--print-template"],
            text=True, capture_output=True, cwd=REPO, check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        template = json.loads(completed.stdout)
        self.assertEqual(template["shortlist"]["effort_mode"], "normal")
        self.assertEqual(template["shortlist"]["result_mode"], "explore")
        self.assertIn("candidate_ledger", template["discovery"])
        self.assertEqual(len(template["discovery"]["candidate_ledger"]), 6)
        self.assertEqual(len(template["shortlist"]["options"]), 6)
        self.assertIn("place", template["shortlist"]["options"][0])
        self.assertNotIn("finalist_date_enrichment", template["discovery"])

    def test_verified_template_is_self_contained_and_finalizes(self):
        completed = subprocess.run(
            [PYTHON, FINALIZE, "--print-template", "--template-mode", "verified"],
            text=True, capture_output=True, cwd=REPO, check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        template = json.loads(completed.stdout)
        template["shortlist"]["operation_id"] = "op-verified-template"
        result = self.run_finalize(template)
        self.assertEqual(result["research_coverage"]["result_mode"], "verified")
        self.assertIn("Example activity", result["numbered_options_markdown"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
