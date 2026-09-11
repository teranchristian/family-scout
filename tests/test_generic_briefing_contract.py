#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GenericBriefingContractTest(unittest.TestCase):
    def test_skill_routes_structured_activity_and_family_fit_rendering(self):
        skill = " ".join((ROOT / "hermes-skill" / "SKILL.md").read_text().split())
        recommendation = " ".join(
            (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text().split()
        )
        self.assertLess(len((ROOT / "hermes-skill" / "SKILL.md").read_text().split()), 600)
        for phrase in (
            "references/recommendation.md",
            "venue being open does not prove",
            "Google Maps is navigation evidence only",
            "Do not inspect helper or validator source code",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "one to four decision-relevant activities",
            "child-specific fit",
            "`numbered_options_markdown` verbatim",
        ):
            self.assertIn(phrase, recommendation)

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
        recommendation = " ".join(
            (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text().split()
        )
        discovery = " ".join(
            (ROOT / "hermes-skill" / "references" / "discovery.md").read_text().split()
        )
        briefing = " ".join(
            (ROOT / "hermes-skill" / "references" / "briefing.md").read_text().split()
        )
        self.assertIn("references/recommendation.md", skill)
        for phrase in (
            "broad, local-language family activity sweep",
            "broad general attractions/experiences sweep",
            "category-based",
            "History and explicit feedback may adjust the final order only after",
        ):
            self.assertIn(phrase, recommendation)
        for phrase in (
            "General-attractions sweep",
            "not framed only around children",
            "Do not inspect prior shortlists or feedback during this stage",
            "not an extra phase or extra query allowance",
        ):
            self.assertIn(phrase, discovery)
        for phrase in (
            "Rank current evidence first",
            "without prior shortlist history or learned feedback",
            "History is a **final adjustment**",
            "This is the only stage where past recommendation repetition affects ordering",
        ):
            self.assertIn(phrase, briefing)
        standing_contract = (skill + " " + recommendation + " " + discovery).casefold()
        for overly_specific_term in ("trick-art", "optical-illusion", "3d art"):
            self.assertNotIn(overly_specific_term, standing_contract)

    def test_research_budget_stops_candidate_hunting_and_bounds_deep_effort(self):
        recommendation = " ".join(
            (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text().split()
        )
        discovery = " ".join(
            (ROOT / "hermes-skill" / "references" / "discovery.md").read_text().split()
        )
        for phrase in (
            "at most **three search queries**",
            "Keep **4–6 plausible candidates**",
            "at most **three likely finalists**",
            "**12 external calls total**",
            "returning two is better than slow padding",
        ):
            self.assertIn(phrase, recommendation)
        for phrase in (
            "stop broad candidate hunting",
            "ceilings, not targets",
            "replaces one normal discovery slot",
            "must **not** be used to discover more candidates",
            "six search queries and twenty-four external calls total",
            "put that lead under **Needs checking** or return fewer confirmed options",
        ):
            self.assertIn(phrase, discovery)

    def test_geocoding_retry_never_invents_distance(self):
        runtime_tools = " ".join(
            (ROOT / "hermes-skill" / "references" / "runtime-tools.md").read_text().split()
        )
        for phrase in (
            "one exact venue/address geocoding attempt",
            "explicit thorough/comprehensive request",
            "exact public venue/branch and locality",
            "do not invent, estimate or approximate `distance_km`",
            "Keep distance/radius unverified",
            "Needs checking",
        ):
            self.assertIn(phrase, runtime_tools)

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
