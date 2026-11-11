"""Regression guards for simple, credible discovery (no old finalizer contract)."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "hermes-skill" / "SKILL.md").read_text()
RESEARCH = (ROOT / "hermes-skill" / "references" / "research.md").read_text()
PROFILE = (ROOT / "hermes-skill" / "references" / "profile.md").read_text()


class SimpleResearchContractTests(unittest.TestCase):
    def test_skill_is_small_and_has_only_two_reference_links(self):
        self.assertLess(len(SKILL.split()), 650)
        self.assertIn("references/profile.md", SKILL)
        self.assertIn("references/research.md", SKILL)
        for obsolete in ("references/dated-events.md", "references/recommendation.md",
                         "references/cli.md", "references/briefing.md"):
            self.assertNotIn(obsolete, SKILL)

    def test_two_geographies_use_identical_event_criteria(self):
        self.assertIn("differing only in their assigned area", RESEARCH)
        for term in ("council", "library", "community", "free", "paid",
                     "one-off", "date/time", "age", "booking", "URL"):
            self.assertIn(term.casefold(), RESEARCH.casefold())
        self.assertIn("up to five worthwhile options per day", RESEARCH)
        self.assertIn("not a hard minimum", RESEARCH)

    def test_safety_privacy_and_optional_persistence(self):
        for phrase in ("read-only", "source_dir", "data_dir", "shortlists.jsonl",
                       "feedback.jsonl", "explicitly", "private"):
            self.assertIn(phrase.casefold(), (SKILL + PROFILE).casefold())
        self.assertIn("source page", RESEARCH)
        self.assertIn("booking required", RESEARCH)
        self.assertIn("no mandatory saving", RESEARCH.casefold())
        self.assertIn("No numeric match scores", SKILL)

    def test_no_old_two_stage_discovery_assumption(self):
        for obsolete in ("result_mode: \"explore\"", "slot_verified: true",
                         "numbered_options_markdown", "two-stage menu"):
            self.assertNotIn(obsolete, SKILL + PROFILE + RESEARCH)


if __name__ == "__main__":
    unittest.main()
