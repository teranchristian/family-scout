#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
RENDERER = ROOT / "scripts" / "render_briefing.py"


class RenderBriefingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="family-scout-render-")
        self.data = Path(self.temp.name)
        self.search_id = "search-example-render"
        self.member_ids = ["member-alpha", "member-beta", "member-adult"]
        urls = [
            "https://example.org/one",
            "https://example.org/two",
            "https://example.org/three",
        ]
        options = []
        for number, url in enumerate(urls, 1):
            options.append({
                "number": number,
                "title": f"Example Option {number}",
                "source_urls": [url],
                "link_checks": [{
                    "url": url,
                    "purposes": ["facts"],
                    "result": "content_verified",
                    "checked_at": "2030-04-06T09:00:00Z",
                }],
            })
        record = {
            "schema_version": 1,
            "search_id": self.search_id,
            "request": {"attending_member_ids": self.member_ids},
            "options": options,
        }
        (self.data / "shortlists.jsonl").write_text(
            json.dumps(record) + "\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def run_renderer(self, payload, expected=0):
        completed = subprocess.run(
            [sys.executable, RENDERER, "--data-dir", self.data,
             "--search-id", self.search_id, "--input", "-"],
            input=json.dumps(payload), text=True, capture_output=True, check=False,
        )
        self.assertEqual(
            completed.returncode, expected,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
        return json.loads(completed.stdout if expected == 0 else completed.stderr)

    def card(self, number, availability="available"):
        word = ["one", "two", "three"][number - 1]
        activity = f"Activity {number}"
        return {
            "number": number,
            "body": f"Practical details for option {number}.",
            "activities": [{
                "name": activity,
                "kind": "sub_facility",
                "availability": availability,
                "detail": "A concrete evidenced thing the family can do.",
                "source_url": f"https://example.org/{word}",
            }],
            "family_fit": [
                {
                    "member_id": "member-alpha",
                    "label": "younger child",
                    "fit": "good",
                    "activity_names": [activity] if availability == "available" else [],
                    "limitations": [],
                },
                {
                    "member_id": "member-beta",
                    "label": "older child",
                    "fit": "strong",
                    "activity_names": [activity] if availability == "available" else [],
                    "limitations": [],
                },
                {
                    "member_id": "member-adult",
                    "label": "adult",
                    "fit": "guardian",
                    "activity_names": [],
                    "limitations": [],
                },
            ],
        }

    def valid_payload(self):
        return {"cards": [self.card(1), self.card(2), self.card(3)]}

    def test_verified_links_activities_and_member_fit_are_rendered(self):
        result = self.run_renderer(self.valid_payload())
        rendered = result["numbered_options_markdown"]
        for number in range(1, 4):
            heading = f"**{number}. Example Option {number}**"
            url = f"https://example.org/{['one', 'two', 'three'][number - 1]}"
            self.assertIn(heading, rendered)
            self.assertIn(f"**Activity {number}**", rendered)
            self.assertIn("Fit for each attending family member", rendered)
            self.assertIn("younger child", rendered)
            self.assertIn("older child", rendered)
            self.assertNotIn("**adult**", rendered)
            self.assertIn(url, rendered)
            self.assertLess(rendered.index(heading), rendered.index(url))
        self.assertEqual(result["option_count"], 3)

    def test_missing_option_card_is_rejected(self):
        payload = self.valid_payload()
        payload["cards"].pop()
        error = self.run_renderer(payload, expected=2)
        self.assertIn("exactly one card", error["error"])

    def test_manual_urls_in_body_are_rejected(self):
        payload = self.valid_payload()
        payload["cards"][0]["body"] = "See https://unverified.example.org"
        error = self.run_renderer(payload, expected=2)
        self.assertIn("must not contain URLs", error["error"])

    def test_activity_must_use_verified_factual_source(self):
        payload = self.valid_payload()
        payload["cards"][0]["activities"][0]["source_url"] = "https://wrong.example.org"
        error = self.run_renderer(payload, expected=2)
        self.assertIn("content-verified factual link", error["error"])

    def test_unavailable_activity_cannot_be_used_for_member_fit(self):
        payload = self.valid_payload()
        payload["cards"][0]["activities"].append({
            "name": "Closed feature",
            "kind": "sub_facility",
            "availability": "unavailable",
            "detail": "Closed on the requested date.",
            "source_url": "https://example.org/one",
        })
        payload["cards"][0]["family_fit"][0]["activity_names"] = ["Closed feature"]
        error = self.run_renderer(payload, expected=2)
        self.assertIn("only activities available on the requested date", error["error"])

    def test_every_attending_member_requires_separate_fit_entry(self):
        payload = self.valid_payload()
        payload["cards"][0]["family_fit"] = payload["cards"][0]["family_fit"][:-1]
        error = self.run_renderer(payload, expected=2)
        self.assertIn("exactly one entry for every attending member", error["error"])

    def test_confirmed_option_needs_at_least_one_available_activity(self):
        payload = self.valid_payload()
        card = payload["cards"][0]
        card["activities"][0]["availability"] = "unavailable"
        for fit in card["family_fit"]:
            if fit["fit"] != "guardian":
                fit["activity_names"] = []
        error = self.run_renderer(payload, expected=2)
        self.assertIn("at least one activity available", error["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
