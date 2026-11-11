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
PARALLEL = (
    ROOT / "hermes-skill" / "references" / "parallel-research.md"
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
        compact = " ".join(EVENTS.split())
        for required in (
            "activity location's IANA timezone",
            "explicit location and radius",
            "saved **home/travel** profile",
            "never assume a particular country, city, suburb",
            "date window",
            "resolved anchor",
        ):
            self.assertIn(required, compact)
        for forbidden in ("Randwick", "Sydney", "November 2026", "2026-11-14"):
            self.assertNotIn(forbidden, EVENTS)
            self.assertNotIn(forbidden, SKILL)

    def test_local_first_coverage_and_unverified_evidence(self):
        for required in (
            "Priority 1", "Priority 2", "Priority 3",
            "general events calendars AND library/event-program calendars",
            "day by day", "active participation", "source URL",
            "Unknown hard", "verified", "link_checks",
        ):
            self.assertIn(required, EVENTS)

    def test_validated_one_pass_five_picks_and_shared_budget(self):
        for required in (
            'effort_mode: "deep"', 'result_mode = "verified"',
            "up to five", "six searches and twenty-four",
            "shared budget", "at most **ten retained",
            "finalize_briefing.py", "numbered_options_markdown",
            "one", "delegation", "three serial calls",
        ):
            self.assertIn(required, EVENTS)

    def test_weekend_uses_three_parallel_agents_and_booking_is_checked(self):
        self.assertIn("three parallel subagents by default", EVENTS)
        self.assertIn("once with three tasks in one batch", EVENTS)
        self.assertIn("do not add more by", EVENTS)
        self.assertIn("narrow venue check", EVENTS)
        self.assertIn("Booking matters even when entry is free", EVENTS)
        self.assertIn("fallback_markdown", EVENTS)

    def test_weekend_discovery_rejects_three_and_done_regression(self):
        compact = " ".join(EVENTS.split())
        for required in (
            "not events-only",
            "6–8 plausible distinct leads",
            "at least four useful experience classes",
            "general attractions/experiences sweep",
            "not framed only around children",
            "separate discovery sources",
            "Do not stop after three good leads",
            "fresh pool before loading history or feedback",
            "meaningful age-appropriate activity for each child",
            "Weather affects ranking and backups, not discovery coverage",
            "choices, not a fixed itinerary",
            "state which calendars/classes were missed",
        ):
            self.assertIn(required, compact)
        self.assertNotIn("Stop early if the shortlist is useful", EVENTS)

    def test_weekend_ranks_complete_pool_before_saving(self):
        compact = " ".join(EVENTS.split())
        for required in (
            "cinema screenings",
            "examples, never required picks",
            "actual date/time, price and age fit",
            "Finish discovery before choosing or saving",
            "complete fresh pool",
            "Never run a residual discovery sweep after finalization",
            'unsaved "bonus find"',
            "strong nearby find from the last search",
            "free or low-cost preference",
            "free-only",
        ):
            self.assertIn(required, compact)
        parallel = " ".join(PARALLEL.split())
        for required in (
            "Wait for the entire batch",
            "before final ranking and saving",
            'post-save "bonus" discovery',
        ):
            self.assertIn(required, parallel)

    def test_saved_preferences_reorder_without_filtering_novel_options(self):
        dated = " ".join(EVENTS.split())
        undated = " ".join(RECOMMENDATION.split())
        for required in (
            "Saved profile preferences are ranking signals, not discovery filters",
            "profile.preferences",
            "after fresh discovery and initial ranking",
            "Keep genuinely new options visible",
            "clear hard constraint",
            "profile.constraints",
            "A current user request takes precedence",
        ):
            self.assertIn(required, dated)
        for required in (
            "profile.preferences",
            "soft ranking signals, not search or candidate filters",
            "preserve unfamiliar categories and novel options",
            "profile.constraints",
        ):
            self.assertIn(required, undated)

    def test_parallel_example_keeps_budget_for_parent_discovery(self):
        markers = ("<!-- begin single-batch-example -->", "<!-- end single-batch-example -->")
        block = PARALLEL.split(markers[0], 1)[1].split(markers[1], 1)[0]
        payload = json.loads(block.split("```json", 1)[1].split("```", 1)[0])
        contexts = [task["context"] for task in payload["tasks"]]
        self.assertEqual(len(contexts), 3)
        self.assertIn("budget: 2 searches", contexts[0])
        self.assertIn("budget: 1 search", contexts[1])
        self.assertIn("budget: 1 search", contexts[2])
        compact = " ".join(PARALLEL.split())
        for required in (
            "two local searches, one neighbouring, one wider, and up to two parent searches",
            "twenty-four total external calls",
            "calendars actually inspected",
            "rather than selecting the final top three",
        ):
            self.assertIn(required, compact)

    def test_summary_requires_evidence_not_made_up_counts(self):
        for required in (
            "Subagents completed", "Distinct candidate events actually discovered",
            "Priority 1 / 2 / 3", "actually checked", "not tracked",
            "verification gaps", "retained for validation",
        ):
            self.assertIn(required, EVENTS)


if __name__ == "__main__":
    unittest.main()
