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
        record = {"schema_version": 1, "search_id": self.search_id, "options": options}
        (self.data / "shortlists.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_renderer(self, payload, expected=0):
        completed = subprocess.run(
            [sys.executable, RENDERER, "--data-dir", self.data,
             "--search-id", self.search_id, "--input", "-"],
            input=json.dumps(payload), text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, expected, completed.stderr)
        return json.loads(completed.stdout if expected == 0 else completed.stderr)

    def test_every_saved_verified_link_is_rendered_with_its_option(self):
        result = self.run_renderer({"cards": [
            {"number": 1, "body": "First body."},
            {"number": 2, "body": "Second body."},
            {"number": 3, "body": "Third body."},
        ]})
        rendered = result["numbered_options_markdown"]
        for number in range(1, 4):
            heading = f"**{number}. Example Option {number}**"
            url = f"https://example.org/{['one', 'two', 'three'][number - 1]}"
            self.assertIn(heading, rendered)
            self.assertIn(url, rendered)
            self.assertLess(rendered.index(heading), rendered.index(url))
        self.assertEqual(result["option_count"], 3)

    def test_missing_option_body_is_rejected(self):
        error = self.run_renderer({"cards": [
            {"number": 1, "body": "First body."},
            {"number": 2, "body": "Second body."},
        ]}, expected=2)
        self.assertIn("exactly one card body", error["error"])

    def test_manual_urls_in_body_are_rejected(self):
        error = self.run_renderer({"cards": [
            {"number": 1, "body": "See https://unverified.example.org"},
            {"number": 2, "body": "Second body."},
            {"number": 3, "body": "Third body."},
        ]}, expected=2)
        self.assertIn("must not contain URLs", error["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
