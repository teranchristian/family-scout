"""Privacy-preserving date-of-birth support with legacy static-age fallback."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import family_scout as scout  # noqa: E402


class BirthdateAgeTests(unittest.TestCase):
    def profile(self, members):
        p = deepcopy(scout.DEFAULT_PROFILE)
        p["group_members"] = members
        return p

    def test_birthdate_used_over_stale_saved_age(self):
        profile = self.profile([{
            "id": "member-alpha", "age": 4, "date_of_birth": "2023-11-15"
        }])
        scout.validate_profile(profile)
        from datetime import date
        self.assertEqual(
            scout.member_ages_on(profile, date(2026, 11, 14)),
            [{"id": "member-alpha", "age": 2, "age_basis": "date_of_birth"}],
        )
        self.assertEqual(
            scout.member_ages_on(profile, date(2026, 11, 15))[0]["age"], 3
        )
        self.assertEqual(profile["group_members"][0]["age"], 4)

    def test_legacy_age_still_works_without_birthdate(self):
        from datetime import date
        p = self.profile([{"id": "member-alpha", "age": 5},
                          {"id": "member-beta"}])
        self.assertEqual(scout.member_ages_on(p, date(2029, 1, 1)), [
            {"id": "member-alpha", "age": 5, "age_basis": "saved_age"},
            {"id": "member-beta", "age": None, "age_basis": "unknown"},
        ])

    def test_leap_day_birthday_in_nonleap_year(self):
        from datetime import date
        p = self.profile([{"id": "member-alpha",
                           "date_of_birth": "2024-02-29"}])
        self.assertEqual(scout.member_ages_on(p, date(2025, 2, 28))[0]["age"], 0)
        self.assertEqual(scout.member_ages_on(p, date(2025, 3, 1))[0]["age"], 1)
        self.assertEqual(scout.member_ages_on(p, date(2028, 2, 29))[0]["age"], 4)

    def test_not_born_at_requested_date(self):
        from datetime import date
        p = self.profile([{"id": "member-alpha", "date_of_birth": "2030-02-03"}])
        self.assertEqual(scout.member_ages_on(p, date(2030, 2, 2)), [
            {"id": "member-alpha", "age": None, "age_basis": "not_born_yet"}
        ])

    def test_invalid_birthdates_are_rejected(self):
        for value in ("2026-02-30", "2026/02/03", "20260203", "not-a-date", 123):
            p = self.profile([{"id": "member-alpha", "date_of_birth": value}])
            with self.subTest(value=value), self.assertRaises(scout.ScoutError):
                scout.validate_profile(p)

    def test_cli_computes_ages_without_leaking_birthdates_or_changing_profile(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            home = root / "hermes"
            data = root / "data"
            home.mkdir()
            setup = subprocess.run([
                sys.executable, str(ROOT / "scripts" / "setup.py"),
                "install", "--hermes-home", str(home), "--data-dir", str(data)
            ], capture_output=True, text=True)
            self.assertEqual(setup.returncode, 0, setup.stderr)
            update = {
                "operation_id": "op-birthdate-example",
                "reviewed_at": "2030-01-01T00:00:00Z",
                "source": "explicit_user",
                "changes": {
                    "group_members": [{
                        "id": "member-alpha", "age": 4,
                        "date_of_birth": "2023-11-15"
                    }]
                },
            }
            helper = ROOT / "scripts" / "family_scout.py"
            saved = subprocess.run([
                sys.executable, str(helper), "--data-dir", str(data),
                "profile-update"
            ], input=json.dumps(update), capture_output=True, text=True)
            self.assertEqual(saved.returncode, 0, saved.stderr)
            original = (data / "profile.yaml").read_bytes()
            ages = subprocess.run([
                sys.executable, str(helper), "--data-dir", str(data),
                "ages-on", "--date", "2030-11-15"
            ], capture_output=True, text=True)
            self.assertEqual(ages.returncode, 0, ages.stderr)
            result = json.loads(ages.stdout)
            self.assertEqual(result["age_as_of"], "2030-11-15")
            self.assertEqual(result["effective_member_ages"], [
                {"id": "member-alpha", "age": 7, "age_basis": "date_of_birth"}
            ])
            self.assertNotIn("2023-11-15", ages.stdout)
            self.assertEqual((data / "profile.yaml").read_bytes(), original)

            discovery = subprocess.run([
                sys.executable, str(ROOT / "scripts" / "discovery_context.py"),
                "--data-dir", str(data), "--at", "2030-11-14T13:00:00+00:00"
            ], capture_output=True, text=True)
            self.assertEqual(discovery.returncode, 0, discovery.stderr)
            context = json.loads(discovery.stdout)
            self.assertEqual(context["age_as_of"], "2030-11-14")
            self.assertEqual(context["effective_member_ages"][0]["age"], 6)


if __name__ == "__main__":
    unittest.main()
