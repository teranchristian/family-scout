#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GenericBriefingContractTest(unittest.TestCase):
    def test_skill_routes_structured_activity_and_family_fit_rendering(self):
        skill = " ".join((ROOT / "hermes-skill" / "SKILL.md").read_text().split())
        self.assertLess(len((ROOT / "hermes-skill" / "SKILL.md").read_text().split()), 600)
        for phrase in (
            "venue being open does not prove",
            "requested-date availability",
            "what they can actually do",
            "activities",
            "family_fit",
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
