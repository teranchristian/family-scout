"""Small contract checks for the new three-agent Family Scout flow."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "hermes-skill" / "SKILL.md").read_text()
PROFILE = (ROOT / "hermes-skill" / "references" / "profile.md").read_text()
RESEARCH = (ROOT / "hermes-skill" / "references" / "research.md").read_text()


class FamilyScoutWorkflowTest(unittest.TestCase):
    def test_only_three_runtime_markdown_files(self):
        installed = sorted(p.relative_to(ROOT / "hermes-skill").as_posix()
                           for p in (ROOT / "hermes-skill").rglob("*.md"))
        self.assertEqual(installed, ["SKILL.md", "references/profile.md",
                                     "references/research.md"])

    def test_parallel_agents_share_discovery_and_weather_is_separate(self):
        for phrase in ("one `delegate_task` call", "Agent 1", "Agent 2", "Agent 3",
                       "same discovery instructions", "weather", "nearby suburbs",
                       "if delegation", "private profile"):
            self.assertIn(phrase.casefold(), SKILL.casefold())
        self.assertIn("Shared instructions for Agent 1 and Agent 2", RESEARCH)
        self.assertIn("Agent 3: weather only", RESEARCH)
        self.assertIn("each requested date", RESEARCH)
        self.assertIn("do **not** research events", RESEARCH.casefold())

    def test_child_ages_and_location_are_profile_driven(self):
        for phrase in ("discovery_context.py", "ages-on --date YYYY-MM-DD",
                       "group_members", "travel/home", "explicit request",
                       "private", "date_of_birth"):
            if phrase == "date_of_birth":
                self.assertIn("Birthdate-derived ages", PROFILE)
            else:
                self.assertIn(phrase.casefold(), PROFILE.casefold())
        for personal_example in ("Randwick", "Sydney", "Ema", "Haru", "2026-11-14"):
            self.assertNotIn(personal_example, SKILL + PROFILE + RESEARCH)

    def test_direct_telegram_response_with_live_evidence(self):
        for phrase in ("top five", "direct official", "Google Maps",
                       "child-by-child", "weather", "Never invent",
                       "Fresh discovery", "No mandatory saving"):
            self.assertIn(phrase.casefold(), (SKILL + RESEARCH).casefold())
        self.assertIn("official/organiser page", RESEARCH)
        self.assertIn("Needs checking", RESEARCH)


if __name__ == "__main__":
    unittest.main()
