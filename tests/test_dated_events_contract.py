"""Checks for the date-specific local-event route and safe default routing."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "hermes-skill" / "SKILL.md").read_text(encoding="utf-8")
EVENTS = (ROOT / "hermes-skill" / "references" / "dated-events.md").read_text(
    encoding="utf-8"
)
RECOMMENDATION = (
    ROOT / "hermes-skill" / "references" / "recommendation.md"
).read_text(encoding="utf-8")


class DatedEventsContractTests(unittest.TestCase):
    def test_main_skill_routes_dated_events_but_preserves_undated_menu(self):
        self.assertIn("references/dated-events.md", SKILL)
        self.assertIn("this/next weekend", SKILL)
        self.assertIn("undated general outings", SKILL)
        self.assertIn("one-pass verified shortlist", SKILL)
        self.assertIn("two-stage", RECOMMENDATION)
        self.assertIn("dated-events.md", RECOMMENDATION)

    def test_dates_and_places_are_resolved_at_runtime_not_fixed(self):
        for required in (
            "activity location's IANA timezone",
            "explicit location and radius",
            "saved **home/travel** profile",
            "never assume a particular country, city, suburb",
            "requested date window",
            "resolved anchor",
        ):
            self.assertIn(required, EVENTS)
        for forbidden in ("Randwick", "Sydney", "November 2026", "2026-11-14"):
            self.assertNotIn(forbidden, EVENTS)
            self.assertNotIn(forbidden, SKILL)

    def test_local_first_coverage_and_unverified_evidence(self):
        for required in (
            "Priority 1", "Priority 2", "Priority 3",
            "general events calendars AND library/event-program calendars",
            "day by day", "actively", "source URL",
            "Unknown hard", "verified", "link_checks",
        ):
            self.assertIn(required, EVENTS)

    def test_validated_one_pass_five_picks_and_shared_budget(self):
        for required in (
            'effort_mode: "deep"', 'result_mode = "verified"',
            "up to five", "six searches and twenty-four",
            "shared budget", "at most **ten retained",
            "finalize_briefing.py", "numbered_options_markdown",
            "one", "delegation", "never serialize",
        ):
            self.assertIn(required, EVENTS)

    def test_summary_requires_evidence_not_made_up_counts(self):
        for required in (
            "Subagents completed", "Distinct candidate events actually discovered",
            "Priority 1 / 2 / 3", "actually checked", "not tracked",
            "verification gaps", "retained for validation",
        ):
            self.assertIn(required, EVENTS)


if __name__ == "__main__":
    unittest.main()
