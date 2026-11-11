"""Keep Git-owned skill instructions distinct from writable Family Scout state."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillOwnershipContractTests(unittest.TestCase):
    def test_skill_declares_repo_ownership_and_refuses_auto_edits(self):
        skill = (ROOT / "hermes-skill" / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "Git-owned skill",
            "read-only in Hermes",
            "skill_manage",
            "background learning",
            "proposed Git change",
            "private Family Scout state commands",
        ):
            self.assertIn(required, skill)

    def test_memory_uses_private_state_not_procedural_skill_edits(self):
        memory = (
            ROOT / "hermes-skill" / "references" / "memory.md"
        ).read_text(encoding="utf-8")
        for required in (
            "Do not use Hermes's general memory",
            "profile-update",
            "feedback-add",
            "shadow skill",
            "outside Git",
        ):
            self.assertIn(required, memory)

    def test_readme_explains_lock_and_github_workflow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "hermes curator lock family-scout",
            "hermes curator status",
            "if your version supports it",
            "agent-policy guard",
            "git pull",
            "./install.sh",
            "local edits",
        ):
            self.assertIn(required, readme)


if __name__ == "__main__":
    unittest.main()
