"""Contract tests for the simple dated-weekend Family Scout workflow."""

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
    def test_routes_stay_distinct(self):
        self.assertIn("references/dated-events.md", SKILL)
        self.assertIn("this/next weekend", SKILL)
        self.assertIn("three local-to-wide research subagents", SKILL)
        self.assertIn("references/recommendation.md", SKILL)
        self.assertIn("two-stage", RECOMMENDATION)
        self.assertIn("dated-events.md", RECOMMENDATION)

    def test_request_not_hardcoded_to_example_family(self):
        compact = " ".join(EVENTS.split())
        for phrase in (
            "activity location's IANA timezone",
            "explicit location and radius",
            "saved **home/travel**",
            "never assume a particular country, city, suburb",
            "date window",
            "age bands",
        ):
            self.assertIn(phrase, compact)
        for example in ("Randwick", "Sydney", "Ema", "Haru",
                        "November 2026", "2026-11-14"):
            self.assertNotIn(example, SKILL)
            self.assertNotIn(example, EVENTS)

    def test_local_council_events_before_big_venues(self):
        compact = " ".join(EVENTS.split())
        for phrase in (
            "Priority 1", "Priority 2", "Priority 3",
            "general event calendars", "library/event-program calendars",
            "community centres", "sustainability/environment hubs",
            "small one-off community events", "swaps",
            "Search **Saturday and Sunday separately**",
            "wider", "famous",
        ):
            self.assertIn(phrase, compact)

    def test_geographic_preflight_is_model_first_with_conditional_lookup(self):
        for phrase in (
            "Hermes's existing AI model knowledge",
            "public suburb/town and city",
            "not a new subagent, tool call or mandatory web search",
            "search-area plan",
            "search leads, not",
            "user's explicitly specified tiers",
            "exact event venue",
            "at most one quick web search",
            "If the lookup fails",
            "specific area names and assigned tier",
            "no separate council",
        ):
            self.assertIn(phrase, EVENTS)
        self.assertNotIn("Before the three research agents start, make **one quick web search**", EVENTS)
        for phrase in (
            "model-first geographic preflight",
            "before** calling `delegate_task`",
            "one web lookup only when needed",
            "specific local suburbs",
            "assigned scope",
            "nearby",
            "local only",
            "adjacent only",
            "wider exceptional options and weather only",
            "Each agent finds its own official council calendars",
        ):
            self.assertIn(phrase, PARALLEL)
        for example in ("Randwick", "Sydney", "Ema", "Haru"):
            self.assertNotIn(example, EVENTS)
            self.assertNotIn(example, PARALLEL)

    def test_three_parallel_specialists_and_broader_discovery(self):
        compact = " ".join(EVENTS.split())
        for phrase in (
            "three parallel research specialists",
            "once as one three-task batch",
            "discover about 10–15 distinct relevant candidates",
            "before final ranking",
            "Do not stop when you have found five",
            "5–8 distinct worthwhile choices",
            "If delegation is unavailable",
        ):
            self.assertIn(phrase, compact)
        self.assertIn("Agent 1 — local specialist", PARALLEL)
        self.assertIn("Agent 2 — adjacent-area specialist", PARALLEL)
        self.assertIn("Agent 3 — wider-area and weather specialist", PARALLEL)

    def test_child_engagement_and_local_event_verification_beat_duration(self):
        # Guard the decision principle, not a particular location or example.
        compact = " ".join(EVENTS.lower().split())
        for idea in (
            "duration is not a proxy for child engagement",
            "before replacing a promising",
            "specific session and booking details",
            "needs checking",
            "rain changes practicality, not discovery",
        ):
            self.assertIn(idea, compact)

    def test_official_source_once_and_honest_uncertainty(self):
        for phrase in (
            "One trustworthy source is sufficient",
            "current official council, organiser, venue or booking page",
            "Search snippets alone",
            "what each child can actively do",
            "total family", "Needs checking",
            "exact ticket slot",
            "Rain changes", "outdoor",
            "free council/community",
            "local one-off value",
        ):
            self.assertIn(phrase, EVENTS)

    def test_save_not_required_for_dated_event_delivery(self):
        for phrase in (
            "Never discard a researched answer",
            "do not call `evaluate`",
            "`finalize_briefing.py`",
            "`shortlist-save`",
            "as a prerequisite",
            "Respond directly from the source evidence",
            "explicitly requests **saving**",
            "show the useful shortlist regardless",
            "same conversation",
            "do not demand a saved",
        ):
            self.assertIn(phrase, EVENTS)
        self.assertNotIn("Run `finalize_briefing.py` with the JSON input, once", EVENTS)
        self.assertNotIn("paste `numbered_options_markdown` verbatim", EVENTS)

    def test_preserve_profile_and_new_discovery(self):
        compact = " ".join(EVENTS.split()).casefold()
        for phrase in (
            "Fresh discovery comes before history or feedback",
            "Saved preferences are gentle ranking signals",
            "hard constraint",
            "Do not invent",
        ):
            self.assertIn(phrase.casefold(), compact)


if __name__ == "__main__":
    unittest.main()
