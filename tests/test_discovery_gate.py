#!/usr/bin/env python3
"""Regression checks for the fresh-discovery/history boundary."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
SETUP = REPO / "scripts" / "setup.py"
HELPER = REPO / "scripts" / "family_scout.py"
GATE = REPO / "scripts" / "discovery_gate.py"


class DiscoveryGateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-discovery-")
        self.root = Path(self.temporary.name)
        self.hermes = self.root / "hermes"
        self.data = self.root / "data"
        self.hermes.mkdir()
        self.run_process([
            PYTHON, SETUP, "install", "--hermes-home", self.hermes,
            "--data-dir", self.data,
        ])

    def tearDown(self):
        self.temporary.cleanup()

    def run_process(self, command, payload=None, expected=0):
        completed = subprocess.run(
            [str(item) for item in command],
            input=None if payload is None else json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        stream = completed.stdout if expected == 0 else completed.stderr
        return json.loads(stream) if stream.strip().startswith("{") else stream

    @staticmethod
    def shortlist_payload(operation_id="op-discovery-seed"):
        return {
            "operation_id": operation_id,
            "created_at": "2030-04-06T09:00:00Z",
            "conversation_ref": "conversation-discovery",
            "effort_mode": "normal",
            "request": {
                "origin_ref": "explicit",
                "place_label": "Example City",
                "date_start": "2030-04-07",
                "date_end": "2030-04-07",
                "timezone": "Etc/UTC",
                "radius_km": 10,
                "attending_member_ids": [],
                "free_only": True,
            },
            "weather": {"status": "unknown", "reason": "outside forecast coverage"},
            "options": [{
                "title": "Example Activity",
                "venue": "Example Hall",
                "date_start": "2030-04-07T10:00:00+00:00",
                "date_end": "2030-04-07T11:00:00+00:00",
                "checked_at": "2030-04-06T09:00:00Z",
                "source_urls": ["https://events.example.org/example-activity"],
                "link_checks": [{
                    "url": "https://events.example.org/example-activity",
                    "purposes": ["facts"],
                    "result": "content_verified",
                    "checked_at": "2030-04-06T09:00:00Z",
                }],
                "distance_km": 1.2,
                "cost": {"status": "known", "amount": 0, "currency": "XXX",
                         "basis": "attending group"},
                "indoor_status": "indoor",
                "booking": {"required": False, "availability": "not_applicable"},
                "why": "Current source confirms the session.",
                "constraint_results": [
                    {"requirement": "radius", "status": "confirmed_match",
                     "reason": "inside inclusive boundary"},
                    {"requirement": "date", "status": "confirmed_match",
                     "reason": "usable interval overlaps"},
                    {"requirement": "free_only", "status": "confirmed_match",
                     "reason": "mandatory group cost is zero"},
                ],
                "features": ["hands-on"],
            }],
            "needs_checking": [],
            "consulted_sources": [
                {"url": "https://events.example.org/example-activity", "status": "read"}
            ],
            "tool_usage": {"search_queries": 1, "source_fetches": 1,
                           "forecast_lookups": 0},
        }

    def test_discovery_context_does_not_expose_history(self):
        payload = self.shortlist_payload()
        self.run_process(
            [PYTHON, HELPER, "--data-dir", self.data, "shortlist-save", "--input", "-"],
            payload=payload,
        )
        full = self.run_process([
            PYTHON, HELPER, "--data-dir", self.data, "context",
            "--at", "2030-04-06T10:00:00Z",
        ])
        self.assertEqual(len(full["recent_shortlists"]), 1)

        discovery = self.run_process([
            PYTHON, GATE, "--source-dir", REPO, "--data-dir", self.data,
            "context", "--at", "2030-04-06T10:00:00Z",
        ])
        self.assertEqual(discovery["scope"], "discovery")
        self.assertNotIn("recent_shortlists", discovery)
        self.assertNotIn("effective_feedback", discovery)
        self.assertIn("profile", discovery)
        self.assertIn("resolved_location", discovery)
        self.assertIn("enabled_sources", discovery)

    def test_broad_save_requires_real_discovery_coverage(self):
        payload = self.shortlist_payload("op-discovery-gated")
        path = self.root / "payload.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        rejected = self.run_process([
            PYTHON, GATE, "--source-dir", REPO, "--data-dir", self.data,
            "shortlist-save", "--input", path,
        ], expected=2)
        self.assertIn("discovery_telemetry", rejected["error"])

        payload["discovery_telemetry"] = {
            "candidates_considered": 9,
            "prior_shortlist_matches": 3,
            "activity_classes_searched": [
                "dated_events", "children_play", "museum_culture",
                "animals", "commercial_family", "workshops",
            ],
            "exact_date_event_searched": True,
            "finalists_date_enriched": True,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        saved = self.run_process([
            PYTHON, GATE, "--source-dir", REPO, "--data-dir", self.data,
            "shortlist-save", "--input", path,
        ])
        self.assertFalse(saved["duplicate"])
        self.assertEqual(saved["research_coverage"], {
            "candidates_considered": 9,
            "activity_classes_checked": 6,
            "prior_shortlist_matches": 3,
            "finalists_verified": 1,
        })

        # Novelty is never a quota: all fresh candidates may be familiar.
        payload["operation_id"] = "op-discovery-all-familiar"
        payload["discovery_telemetry"]["prior_shortlist_matches"] = 9
        path.write_text(json.dumps(payload), encoding="utf-8")
        saved_again = self.run_process([
            PYTHON, GATE, "--source-dir", REPO, "--data-dir", self.data,
            "shortlist-save", "--input", path,
        ])
        self.assertFalse(saved_again["duplicate"])

        invalid = self.shortlist_payload("op-discovery-too-few-classes")
        invalid["discovery_telemetry"] = {
            "candidates_considered": 4,
            "prior_shortlist_matches": 0,
            "activity_classes_searched": ["dated_events", "children_play"],
            "exact_date_event_searched": True,
            "finalists_date_enriched": True,
        }
        path.write_text(json.dumps(invalid), encoding="utf-8")
        rejected_classes = self.run_process([
            PYTHON, GATE, "--source-dir", REPO, "--data-dir", self.data,
            "shortlist-save", "--input", path,
        ], expected=2)
        self.assertIn("five activity classes", rejected_classes["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
