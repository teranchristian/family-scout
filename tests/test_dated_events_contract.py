"""Contract tests for day-independent dated Family Scout discovery."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "hermes-skill" / "SKILL.md").read_text(encoding="utf-8")
EVENTS = (ROOT / "hermes-skill" / "references" / "dated-events.md").read_text(encoding="utf-8")
RECOMMENDATION = (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")


class DatedEventsContractTests(unittest.TestCase):
    def test_every_named_day_uses_same_route(self):
        self.assertIn("references/dated-events.md", SKILL)
        self.assertIn("references/recommendation.md", SKILL)
        for phrase in ("today", "tomorrow", "a named weekday", "Saturday",
                       "Sunday", "this weekend", "next weekend", "specific dates"):
            self.assertIn(phrase, EVENTS)
        self.assertIn("not a separate", EVENTS)
        self.assertIn("two-stage", RECOMMENDATION)

    def test_no_weekend_only_or_mandatory_agent_workflow(self):
        for phrase in ("no fixed candidate minimum", "required\nthree-agent delegation",
                       "Search directly", "date range"):
            self.assertIn(phrase, EVENTS)
        self.assertNotIn("parallel-research.md", SKILL + EVENTS + RECOMMENDATION)
        self.assertNotIn("delegate_task", SKILL + EVENTS)
        self.assertIn("no weekend-only logic", README.lower())

    def test_location_privacy_and_age(self):
        compact = " ".join(EVENTS.split())
        for phrase in ("activity location's IANA timezone", "explicit location and radius",
                       "home/travel", "birthdates", "age", "private"):
            self.assertIn(phrase, compact)
        for example in ("Randwick", "Sydney", "Ema", "Haru", "2026-11-14"):
            self.assertNotIn(example, SKILL + EVENTS)

    def test_local_discovery_with_current_evidence(self):
        for phrase in ("general event calendars", "library/event-program calendars",
                       "adjacent", "small events", "Fresh discovery comes before",
                       "Search snippets alone", "One trustworthy source",
                       "Search the actual requested dates"):
            self.assertIn(phrase, EVENTS)

    def test_decision_ready_answer_and_optional_saving(self):
        for phrase in ("Both children", "total family price",
                       "Needs checking", "closures", "Weather",
                       "Google Maps", "official source", "Saving is optional",
                       "Respond directly from the source evidence",
                       "shortlist-save", "saved search ID"):
            self.assertIn(phrase, EVENTS)


if __name__ == "__main__":
    unittest.main()
