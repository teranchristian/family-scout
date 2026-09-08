#!/usr/bin/env python3
"""Deterministic Phase 1 acceptance checks using invented fixtures only."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
HELPER = REPO / "scripts" / "family_scout.py"
SETUP = REPO / "scripts" / "setup.py"


class Phase1Test(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-test-")
        self.root = Path(self.temporary.name)
        self.hermes = self.root / "hermes home"
        self.hermes.mkdir()
        self.data = self.root / "private state"
        self.setup("install")

    def tearDown(self):
        self.temporary.cleanup()

    def run_process(self, command, payload=None, expected=0):
        completed = subprocess.run(
            [str(value) for value in command],
            input=None if payload is None else json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        return completed

    def setup(self, action, expected=0):
        return self.run_process(
            [PYTHON, SETUP, action, "--hermes-home", self.hermes,
             *(["--data-dir", self.data] if action == "install" else [])],
            expected=expected,
        )

    def cli(self, *arguments, payload=None, expected=0):
        completed = self.run_process(
            [PYTHON, HELPER, "--data-dir", self.data, *arguments],
            payload=payload,
            expected=expected,
        )
        stream = completed.stdout if expected == 0 else completed.stderr
        return json.loads(stream)

    @staticmethod
    def example_profile_update(operation_id="op-profile-example"):
        return {
            "operation_id": operation_id,
            "reviewed_at": "2030-04-06T09:00:00Z",
            "source": "explicit_user",
            "changes": {
                "home": {
                    "label": "Example City",
                    "latitude": 0,
                    "longitude": 0,
                    "timezone": "Etc/UTC",
                },
                "group_members": [
                    {"id": "member-alpha", "age": 8},
                    {"id": "member-beta", "age": 12},
                ],
                "travel": {
                    "label": "Sample Town",
                    "latitude": 1,
                    "longitude": 1,
                    "timezone": "Etc/UTC",
                    "expires_at": "2030-04-08T23:59:59+00:00",
                },
            },
        }

    @staticmethod
    def example_option(title="Example Activity", start="2030-04-07T10:00:00+00:00"):
        return {
            "title": title,
            "venue": "Example Hall",
            "date_start": start,
            "date_end": "2030-04-07T11:00:00+00:00",
            "checked_at": "2030-04-06T09:00:00Z",
            "source_urls": ["https://events.example.org/example-activity"],
            "distance_km": 1.2,
            "cost": {
                "status": "known",
                "amount": 0,
                "currency": "XXX",
                "basis": "attending group",
            },
            "indoor_status": "indoor",
            "booking": {"required": False, "availability": "not_applicable"},
            "why": "The current listing confirms a free, hands-on session.",
            "constraint_results": [
                {"requirement": "radius", "status": "confirmed_match",
                 "reason": "inside inclusive boundary"},
                {"requirement": "date", "status": "confirmed_match",
                 "reason": "usable interval overlaps"},
                {"requirement": "free_only", "status": "confirmed_match",
                 "reason": "mandatory group cost is zero"},
            ],
            "features": ["hands-on"],
        }

    @classmethod
    def shortlist_payload(cls, operation_id="op-search-example",
                          conversation_ref="conversation-example"):
        return {
            "operation_id": operation_id,
            "created_at": "2030-04-06T09:00:00Z",
            "conversation_ref": conversation_ref,
            "effort_mode": "normal",
            "request": {
                "origin_ref": "explicit",
                "place_label": "Example City",
                "date_start": "2030-04-07",
                "date_end": "2030-04-07",
                "timezone": "Etc/UTC",
                "radius_km": 10,
                "attending_member_ids": [],
                "free_only": True,
            },
            "weather": {"status": "unknown", "reason": "outside forecast coverage"},
            "options": [cls.example_option()],
            "needs_checking": [],
            "consulted_sources": [
                {"url": "https://events.example.org/example-activity", "status": "read"}
            ],
            "tool_usage": {
                "search_queries": 1,
                "source_fetches": 1,
                "forecast_lookups": 0,
            },
        }

    def test_install_upgrade_copy_ownership_and_preservation(self):
        target = self.hermes / "skills" / "family-scout"
        record = json.loads((target / "installation.json").read_text())
        self.assertEqual(record["schema_version"], 2)
        self.assertEqual(
            set(record["skill_files"]),
            {
                "SKILL.md",
                "references/briefing.md",
                "references/cli.md",
                "references/discovery.md",
                "references/memory.md",
                "references/runtime-tools.md",
                "references/venue-status.md",
            },
        )
        for relative in record["skill_files"]:
            self.assertTrue((target / relative).is_file())
        self.assertEqual(stat.S_IMODE(self.data.stat().st_mode), 0o700)
        for name in ("profile.yaml", "sources.yaml", "shortlists.jsonl", "feedback.jsonl"):
            self.assertEqual(stat.S_IMODE((self.data / name).stat().st_mode), 0o600)

        opaque = b"synthetic bytes preserved\n"
        (self.data / "shortlists.jsonl").write_bytes(opaque)
        self.setup("install")
        self.assertEqual((self.data / "shortlists.jsonl").read_bytes(), opaque)

        reference = target / "references" / "briefing.md"
        reference.write_text(reference.read_text() + "\nlocal edit\n")
        self.setup("install", expected=1)
        self.setup("uninstall", expected=1)
        self.assertTrue(reference.read_text().endswith("local edit\n"))
        self.assertEqual((self.data / "shortlists.jsonl").read_bytes(), opaque)

    def test_schema_one_installation_upgrades_to_skill_tree(self):
        other_home = self.root / "legacy hermes"
        target = other_home / "skills" / "family-scout"
        target.mkdir(parents=True)
        old_skill = b"legacy setup-only skill\n"
        (target / "SKILL.md").write_bytes(old_skill)
        (target / "references").mkdir()
        (target / "references" / "cli.md").write_bytes(
            (REPO / "hermes-skill" / "references" / "cli.md").read_bytes()
        )
        other_data = self.root / "legacy data"
        marker = {
            "project": "family-scout",
            "schema_version": 1,
            "source_dir": str(REPO),
            "data_dir": str(other_data),
            "skill_sha256": hashlib.sha256(old_skill).hexdigest(),
        }
        (target / "installation.json").write_text(json.dumps(marker))
        self.run_process([PYTHON, SETUP, "install", "--hermes-home", other_home])
        upgraded = json.loads((target / "installation.json").read_text())
        self.assertEqual(upgraded["schema_version"], 2)
        self.assertTrue((target / "references" / "cli.md").is_file())

    def test_interrupted_owned_file_operations_are_recoverable(self):
        target = self.hermes / "skills" / "family-scout"
        cli_reference = target / "references" / "cli.md"
        cli_reference.unlink()
        self.setup("install")
        self.assertTrue(cli_reference.is_file())

        preserved = (self.data / "profile.yaml").read_bytes()
        cli_reference.unlink()
        self.setup("uninstall")
        self.assertFalse(target.exists())
        self.assertEqual((self.data / "profile.yaml").read_bytes(), preserved)

    def test_profile_travel_precedence_expiry_and_idempotency(self):
        update = self.example_profile_update()
        first = self.cli("profile-update", payload=update)
        retry = self.cli("profile-update", payload=update)
        self.assertFalse(first["duplicate"])
        self.assertTrue(retry["duplicate"])

        travelling = self.cli("context", "--at", "2030-04-07T12:00:00Z")
        forced_home = self.cli(
            "context", "--at", "2030-04-07T12:00:00Z", "--location", "home"
        )
        expired = self.cli("context", "--at", "2030-04-09T00:00:00Z")
        self.assertEqual(travelling["resolved_location"]["origin_ref"], "travel")
        self.assertEqual(forced_home["resolved_location"]["origin_ref"], "home")
        self.assertEqual(expired["resolved_location"]["origin_ref"], "home")
        profile = json.loads((self.data / "profile.yaml").read_text())
        self.assertEqual(len(profile["provenance"]), 1)

    def test_original_blank_yaml_is_migrated_only_on_write(self):
        legacy = (
            "# Blank template, not a configured family. No personal data belongs in Git.\n"
            "# Edit only the installed private copy of profile.yaml.\n"
            "schema_version: 1\n"
            "home:\n"
            "  label: null\n"
            "  latitude: null\n"
            "  longitude: null\n"
            "  timezone: null\n"
            "default_radius_km: 15\n"
            "# Keep stable, private identifiers; names and exact birth dates are optional.\n"
            "# Future member records include an id, age or age band, and relevant constraints.\n"
            "group_members: []\n"
            "preferences: []\n"
            "constraints: []\n"
            "# Future provenance records identify the field, source and reviewed_at date.\n"
            "provenance: []\n"
            "# A future travel context must include a location, timezone and explicit expiry.\n"
            "travel: null\n"
        ).encode()
        self.assertEqual(
            hashlib.sha256(legacy).hexdigest(),
            "6e7fa4deeda376c5e2d76d1dc9262dcab93bf27b660bfb10dcac8a3c579a8244",
        )
        (self.data / "profile.yaml").write_bytes(legacy)
        self.assertTrue(self.cli("status")["profile"]["blank"])
        self.cli("profile-update", payload=self.example_profile_update("op-profile-migrate"))
        self.assertEqual(json.loads((self.data / "profile.yaml").read_text())["schema_version"], 1)

    def test_source_lifecycle(self):
        payload = {
            "operation_id": "op-source-example",
            "source": {
                "name": "Example Events",
                "url": "https://events.example.org",
                "enabled": True,
                "scope": {"place": "Example City"},
                "query_guidance": "Use for public activity leads",
            },
        }
        added = self.cli("source-add", payload=payload)
        source_id = added["source"]["id"]
        self.assertFalse(added["duplicate"])
        self.assertTrue(self.cli("source-add", payload=payload)["duplicate"])
        disabled = self.cli(
            "source-disable", "--id", source_id, "--operation-id", "op-disable-example"
        )
        self.assertFalse(disabled["enabled"])
        self.assertTrue(self.cli(
            "source-disable", "--id", source_id, "--operation-id", "op-disable-example"
        )["duplicate"])
        self.assertTrue(self.cli(
            "source-enable", "--id", source_id, "--operation-id", "op-enable-example"
        )["enabled"])
        self.assertTrue(self.cli(
            "source-remove", "--id", source_id, "--operation-id", "op-remove-example"
        )["removed"])
        self.assertFalse(self.cli(
            "source-remove", "--id", source_id, "--operation-id", "op-remove-example"
        )["removed"])

    def test_hard_constraint_classification(self):
        request = {
            "origin": {"latitude": 0, "longitude": 0},
            "radius_km": 15,
            "date_start": "2030-04-07",
            "date_end": "2030-04-07",
            "timezone": "Etc/UTC",
            "free_only": True,
            "budget": {"amount": 0, "currency": "XXX", "basis": "attending group"},
            "indoor_only": True,
            "attending": [{"id": "member-alpha", "age": 8}],
        }
        base = {
            "title": "Example Activity",
            "coordinates": {"latitude": 0.01, "longitude": 0.01},
            "date_start": "2030-04-07T10:00:00+00:00",
            "date_end": "2030-04-07T11:00:00+00:00",
            "cost": {"status": "known", "amount": 0, "currency": "XXX",
                     "basis": "attending group"},
            "indoor_status": "indoor",
            "eligibility": {"status": "verified", "min_age": 5, "max_age": 12},
            "booking": {"required": False, "availability": "not_applicable"},
            "closure_status": "open",
        }
        cases = []
        cases.append(deepcopy(base))
        outside = deepcopy(base)
        outside.update(title="Outside Radius", coordinates={"latitude": 1, "longitude": 1})
        cases.append(outside)
        unknown_cost = deepcopy(base)
        unknown_cost.update(title="Unknown Cost", cost={"status": "unknown"})
        cases.append(unknown_cost)
        paid = deepcopy(base)
        paid.update(title="Paid Group",
                    cost={"status": "known", "amount": 20, "currency": "XXX",
                          "basis": "attending group"})
        cases.append(paid)
        old = deepcopy(base)
        old.update(title="Old Session", date_start="2030-04-01", date_end="2030-04-01")
        cases.append(old)
        restricted = deepcopy(base)
        restricted.update(title="Restricted Session",
                          eligibility={"status": "verified", "min_age": 10, "max_age": 14})
        cases.append(restricted)
        booking = deepcopy(base)
        booking.update(title="Unknown Booking",
                       booking={"required": True, "availability": "unknown"})
        cases.append(booking)
        closed = deepcopy(base)
        closed.update(title="Closed Session", closure_status="closed")
        cases.append(closed)

        results = self.cli("evaluate", payload={"request": request, "candidates": cases})["results"]
        by_title = {item["title"]: item["classification"] for item in results}
        self.assertEqual(by_title["Example Activity"], "confirmed_match")
        self.assertEqual(by_title["Outside Radius"], "confirmed_failure")
        self.assertEqual(by_title["Unknown Cost"], "unverified")
        self.assertEqual(by_title["Paid Group"], "confirmed_failure")
        self.assertEqual(by_title["Old Session"], "confirmed_failure")
        self.assertEqual(by_title["Restricted Session"], "confirmed_failure")
        self.assertEqual(by_title["Unknown Booking"], "unverified")
        self.assertEqual(by_title["Closed Session"], "confirmed_failure")

    def test_shortlist_identity_retry_privacy_budget_and_ambiguity(self):
        payload = self.shortlist_payload()
        saved = self.cli("shortlist-save", payload=payload)
        retry = self.cli("shortlist-save", payload=payload)
        self.assertFalse(saved["duplicate"])
        self.assertTrue(retry["duplicate"])
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)

        resolved = self.cli(
            "resolve-option", "--number", "1", "--search-id", saved["search_id"]
        )
        self.assertEqual(resolved["option"]["title"], "Example Activity")

        private_request = self.shortlist_payload("op-search-private")
        private_request["request"]["street_address"] = "1 Example Road"
        self.cli("shortlist-save", payload=private_request, expected=2)
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)

        excessive = self.shortlist_payload("op-search-excessive")
        excessive["tool_usage"]["source_fetches"] = 13
        self.cli("shortlist-save", payload=excessive, expected=2)

        duplicate_session = self.shortlist_payload("op-search-duplicate")
        duplicate_session["options"].append(deepcopy(duplicate_session["options"][0]))
        self.cli("shortlist-save", payload=duplicate_session, expected=2)

        unverified = self.shortlist_payload("op-search-unverified")
        unverified["options"][0]["constraint_results"][2]["status"] = "unverified"
        unverified["options"][0]["constraint_results"][2]["reason"] = "price is unknown"
        self.cli("shortlist-save", payload=unverified, expected=2)

        second = self.shortlist_payload("op-search-second")
        second["options"][0]["date_start"] = "2030-04-07T14:00:00+00:00"
        second["options"][0]["date_end"] = "2030-04-07T15:00:00+00:00"
        self.cli("shortlist-save", payload=second)
        ambiguous = self.cli(
            "resolve-option", "--number", "1", "--conversation-ref",
            "conversation-example", expected=2
        )
        self.assertIn("ambiguous", ambiguous["error"])

    def test_feedback_retry_correction_retraction_and_fresh_context(self):
        search_id = self.cli(
            "shortlist-save", payload=self.shortlist_payload()
        )["search_id"]
        feedback = {
            "operation_id": "op-feedback-example",
            "search_id": search_id,
            "option_number": 1,
            "state": "liked",
            "features": [{"feature": "hands-on", "sentiment": "positive"}],
            "member_ids": [],
            "context": None,
            "original": "We liked the hands-on part.",
        }
        first = self.cli("feedback-add", payload=feedback)
        self.assertTrue(self.cli("feedback-add", payload=feedback)["duplicate"])

        correction = {
            "operation_id": "op-feedback-correction",
            "state": "disliked",
            "features": [{"feature": "hands-on", "sentiment": "negative"}],
            "member_ids": [],
            "context": {"reason": "session-specific"},
            "original": "Correction: that session was not enjoyable.",
            "supersedes_event_id": first["event_id"],
        }
        corrected = self.cli("feedback-add", payload=correction)
        context = self.cli("context", "--at", "2030-04-07T12:00:00Z")
        self.assertEqual([item["state"] for item in context["effective_feedback"]], ["disliked"])

        retraction = {
            "operation_id": "op-feedback-retraction",
            "state": "retracted",
            "features": [],
            "member_ids": [],
            "context": None,
            "original": "Please retract that feedback.",
            "supersedes_event_id": corrected["event_id"],
        }
        self.cli("feedback-add", payload=retraction)
        fresh = self.cli("context", "--at", "2030-04-07T13:00:00Z")
        self.assertEqual(fresh["effective_feedback"], [])
        self.assertEqual(len((self.data / "feedback.jsonl").read_text().splitlines()), 3)

        invalid = deepcopy(retraction)
        invalid["operation_id"] = "op-feedback-invalid-retraction"
        invalid.pop("supersedes_event_id")
        self.cli("feedback-add", payload=invalid, expected=2)

    def test_concurrent_shortlist_retry_appends_once(self):
        encoded = json.dumps(self.shortlist_payload("op-search-concurrent"))
        command = [PYTHON, HELPER, "--data-dir", self.data,
                   "shortlist-save", "--input", "-"]
        processes = [
            subprocess.Popen(
                [str(value) for value in command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=REPO,
            )
            for _ in range(4)
        ]
        results = [process.communicate(encoded) for process in processes]
        for process, (stdout, stderr) in zip(processes, results):
            self.assertEqual(process.returncode, 0, msg=f"stdout:\n{stdout}\nstderr:\n{stderr}")
        responses = [json.loads(stdout) for stdout, _ in results]
        self.assertEqual(sum(not response["duplicate"] for response in responses), 1)
        self.assertEqual(len((self.data / "shortlists.jsonl").read_text().splitlines()), 1)

    def test_malformed_documents_and_jsonl_are_preserved(self):
        malformed_profile = b"home: [unterminated\n"
        (self.data / "profile.yaml").write_bytes(malformed_profile)
        self.cli("profile-update", payload=self.example_profile_update(), expected=2)
        self.assertEqual((self.data / "profile.yaml").read_bytes(), malformed_profile)

        (self.data / "profile.yaml").write_bytes((REPO / "examples" / "profile.example.yaml").read_bytes())
        malformed_history = b'{"schema_version":1,"search_id":"broken"\n'
        (self.data / "shortlists.jsonl").write_bytes(malformed_history)
        self.cli("shortlist-save", payload=self.shortlist_payload(), expected=2)
        self.assertEqual((self.data / "shortlists.jsonl").read_bytes(), malformed_history)

    def test_skill_routes_phase_one_behavior_contracts(self):
        skill_path = REPO / "hermes-skill" / "SKILL.md"
        skill = " ".join(skill_path.read_text().split())
        discovery = " ".join(
            (REPO / "hermes-skill" / "references" / "discovery.md").read_text().split()
        )
        briefing = " ".join(
            (REPO / "hermes-skill" / "references" / "briefing.md").read_text().split()
        )
        memory = " ".join(
            (REPO / "hermes-skill" / "references" / "memory.md").read_text().split()
        )
        venue_status = " ".join(
            (REPO / "hermes-skill" / "references" / "venue-status.md").read_text().split()
        )
        self.assertLess(len(skill_path.read_text().split()), 600)
        for phrase in (
            "Never invent a fact",
            "numerical match score",
            "references/discovery.md",
            "references/briefing.md",
            "references/memory.md",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "this weekend",
            "Unknown price does not pass",
            "straight-line distance",
            "six search queries",
            "One failed page, PDF or reader path",
            "[runtime-tools.md](runtime-tools.md)",
            "[venue-status.md](venue-status.md)",
        ):
            self.assertIn(phrase, discovery)
        for phrase in (
            "four or five genuinely useful confirmed options",
            "Needs checking",
            "What it is",
            "recommended plan for each day",
            "Final quality gate",
            "current name, address and host",
        ):
            self.assertIn(phrase, briefing)
        for phrase in (
            "explicit feedback",
            "Never attach a default party",
            "More like this",
        ):
            self.assertIn(phrase, memory)
        for phrase in (
            "exact current venue and branch name",
            "current official venue page",
            "official website is sufficient",
            "not operating-status evidence",
            "separate candidate",
            "Needs checking",
        ):
            self.assertIn(phrase, venue_status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
