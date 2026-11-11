"""Keep reviewed skill instructions separate from private family state."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillOwnershipContractTests(unittest.TestCase):
    def test_skill_is_git_owned_and_read_only(self):
        skill = (ROOT / "hermes-skill" / "SKILL.md").read_text()
        for phrase in ("Git-owned skill", "read-only in Hermes", "skill_manage",
                       "background learning", "proposed Git change",
                       "private Family Scout state commands"):
            self.assertIn(phrase, skill)

    def test_profile_reference_preserves_private_state(self):
        profile = (ROOT / "hermes-skill" / "references" / "profile.md").read_text()
        for phrase in ("profile-update", "feedback-add", "shortlists.jsonl",
                       "private", "Never turn personal facts into edits"):
            self.assertIn(phrase, profile)

    def test_readme_explains_lock_upgrade_and_review(self):
        readme = (ROOT / "README.md").read_text()
        for phrase in ("hermes curator lock family-scout", "hermes curator status",
                       "LOCK NOT APPLIED", "agent-policy guard", "git pull",
                       "./install.sh", "local edits", "old ten-file skill"):
            self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
