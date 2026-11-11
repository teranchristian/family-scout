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

    def test_parallel_for_all_broad_dated_discovery(self):
        for phrase in ("no fixed candidate minimum", "Focused verification",
                       "Broad discovery", "one batch", "three parallel specialists",
                       "delegate_task", "single weekday", "10–15 distinct leads",
                       "If delegation fails", "Search the actual requested dates",
                       "find activities tomorrow", "what's on Wednesday",
                       "Neither the word \"best\""):
            self.assertIn(phrase, EVENTS)
        for phrase in ("Local specialist", "Adjacent specialist",
                       "Wider/weather specialist", "council general event calendars",
                       "library calendars", "private names", "deduplicate"):
            self.assertIn(phrase, EVENTS)
        self.assertIn("one parallel three-specialist research batch", SKILL)
        self.assertIn("same research depth", README.lower())
        self.assertIn("Find activities tomorrow", README)
        self.assertIn("What's on Wednesday?", README)
        self.assertIn("no weekend-only logic", README.lower())
        self.assertNotIn("parallel-research.md", SKILL + EVENTS + RECOMMENDATION)

    def test_broad_discovery_output_is_consistent_every_day(self):
        for phrase in ("top five", "3–5 additional interesting choices",
                       "suggested", "indoor backup", "same answer depth",
                       "Focused venue checks"):
            self.assertIn(phrase, EVENTS)

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
