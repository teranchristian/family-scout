#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GenericBriefingContractTest(unittest.TestCase):
    def test_skill_routes_structured_activity_and_family_fit_rendering(self):
        skill = " ".join((ROOT / "hermes-skill" / "SKILL.md").read_text().split())
        self.assertLess(len((ROOT / "hermes-skill" / "SKILL.md").read_text().split()), 600)
        for phrase in (
            "references/quality.md",
            "venue being open does not prove",
            "requested-date availability",
            "what they can actually do",
            "activities",
            "family_fit",
            "Google Maps is navigation evidence only",
            "Paste the returned `numbered_options_markdown` **verbatim**",
        ):
            self.assertIn(phrase, skill)

    def test_discovery_requires_feature_date_status_child_fit_and_exact_access(self):
        discovery = " ".join(
            (ROOT / "hermes-skill" / "references" / "discovery.md").read_text().split()
        )
        for phrase in (
            "Verify the actual experience, not only the host venue",
            "everyday facility",
            "scheduled activity",
            "sub-facility",
            "available",
            "unavailable",
            "unknown",
            "Verify fit child by child",
            "what that child can actually do",
            "Verify access claims against the exact place",
            "Never reuse access wording from another nearby venue",
        ):
            self.assertIn(phrase, discovery)

    def test_broad_discovery_precedes_history_and_includes_general_attractions(self):
        skill = " ".join((ROOT / "hermes-skill" / "SKILL.md").read_text().split())
        discovery = " ".join(
            (ROOT / "hermes-skill" / "references" / "discovery.md").read_text().split()
        )
        briefing = " ".join(
            (ROOT / "hermes-skill" / "references" / "briefing.md").read_text().split()
        )
        for phrase in (
            "broad fresh discovery first",
            "general-attractions/experiences sweep",
            "initial ranking from current evidence only",
            "history only as a final adjustment",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "General-attractions sweep",
            "not framed only around children",
            "Do not inspect prior shortlists or feedback during this stage",
            "does **not** justify increasing candidate count or tool calls",
        ):
            self.assertIn(phrase, discovery)
        for phrase in (
            "Rank current evidence first",
            "without prior shortlist history or learned feedback",
            "History is a **final adjustment**",
            "This is the only stage where past recommendation repetition affects ordering",
        ):
            self.assertIn(phrase, briefing)

    def test_briefing_quality_gate_prevents_host_open_and_generic_age_fit_shortcuts(self):
        briefing = " ".join(
            (ROOT / "hermes-skill" / "references" / "briefing.md").read_text().split()
        )
        for phrase in (
            "Activity availability",
            "Fit by child",
            "both children fit",
            "at least one concrete activity confirmed available",
            "ranking reconsidered",
            "separate fit explanation",
            "exact origin, exact venue",
        ):
            self.assertIn(phrase, briefing)

    def test_quality_guardrails_cover_freshness_maps_weather_and_compact_output(self):
        quality = " ".join(
            (ROOT / "hermes-skill" / "references" / "quality.md").read_text().split()
        )
        for phrase in (
            "newest applicable date-specific official",
            "Scheduled to be open",
            "Do not make a source sound more specific",
            "Google Maps is for navigation, not status",
            "verified address",
            "straight-line distance as a compact secondary fact",
            "precipitation probability near 100%",
            "Remove repetition from the briefing",
        ):
            self.assertIn(phrase, quality)

    def test_quality_keeps_useful_venue_when_optional_feature_is_unavailable(self):
        quality = " ".join(
            (ROOT / "hermes-skill" / "references" / "quality.md").read_text().split()
        )
        for phrase in (
            "Keep a good venue when one feature is unavailable",
            "does **not** make the whole venue unavailable",
            "at least one concrete activity is confirmed available",
            "what the family **can do today**",
            "reopens 12 Sep",
            "Do not remove an otherwise strong venue",
            "reranked using only the activities that are actually available",
            "remaining verified activities no longer make it a good recommendation",
        ):
            self.assertIn(phrase, quality)


if __name__ == "__main__":
    unittest.main(verbosity=2)
