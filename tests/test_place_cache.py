#!/usr/bin/env python3
"""Focused boundaries for Family Scout's stable-place verification cache."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
HELPER = REPO / "scripts" / "family_scout.py"
SETUP = REPO / "scripts" / "setup.py"


class PlaceCacheTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="family-scout-places-")
        self.root = Path(self.temporary.name)
        self.hermes = self.root / "hermes"
        self.data = self.root / "data"
        self.hermes.mkdir()
        completed = subprocess.run(
            [PYTHON, SETUP, "install", "--hermes-home", str(self.hermes),
             "--data-dir", str(self.data)],
            text=True,
            capture_output=True,
            cwd=REPO,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)

    def tearDown(self):
        self.temporary.cleanup()

    def cli(self, command, payload, expected=0):
        completed = subprocess.run(
            [PYTHON, HELPER, "--data-dir", str(self.data), command, "--input", "-"],
            input=json.dumps(payload),
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
        return json.loads(completed.stdout if expected == 0 else completed.stderr)

    @staticmethod
    def place_payload(name="Example Discovery Centre", area="Example City",
                      address="1 Public Road, Example City",
                      observed_at="2030-04-06T09:00:00Z"):
        official_url = "https://places.example.org/discovery-centre"
        calendar_url = "https://places.example.org/discovery-centre/calendar"
        return {
            "observed_at": observed_at,
            "evidence_urls": [official_url, calendar_url],
            "place": {
                "name": name,
                "area": area,
                "categories": ["museum", "indoor"],
                "official_url": official_url,
                "calendar_url": calendar_url,
                "address": address,
                "latitude": 1.25,
                "longitude": 2.5,
            },
        }

    def test_exact_discovered_place_reuses_stable_pointers_as_leads_only(self):
        payload = self.place_payload()
        first = self.cli("place-cache-upsert", payload)
        retry = self.cli("place-cache-upsert", payload)
        self.assertFalse(first["duplicate"])
        self.assertTrue(retry["duplicate"])
        self.assertEqual(first["place_id"], retry["place_id"])
        self.assertEqual(len((self.data / "places.jsonl").read_text().splitlines()), 1)

        lookup = self.cli("place-cache-lookup", {"candidates": [{
            "name": "Example Discovery Centre",
            "area": "Example City",
        }]})
        self.assertEqual(lookup["cache_role"], "verification_leads_only")
        self.assertTrue(lookup["requires_current_verification"])
        self.assertEqual(lookup["results"][0]["status"], "hit")
        place = lookup["results"][0]["place"]
        self.assertEqual(place["official_url"], payload["place"]["official_url"])
        self.assertEqual(place["calendar_url"], payload["place"]["calendar_url"])
        self.assertEqual(place["address"], payload["place"]["address"])
        self.assertNotIn("open_today", place)
        self.assertNotIn("price", place)

    def test_same_name_locations_stay_distinct_and_weak_lookup_is_ambiguous(self):
        first = self.place_payload(
            name="Shared Hall", area="Example Borough", address="1 North Road"
        )
        second = self.place_payload(
            name="Shared Hall", area="Example Borough", address="9 South Road",
            observed_at="2030-04-06T10:00:00Z",
        )
        third = self.place_payload(
            name="Shared Hall", area="Other Borough", address="9 South Road",
            observed_at="2030-04-06T11:00:00Z",
        )
        self.cli("place-cache-upsert", first)
        self.cli("place-cache-upsert", second)
        self.cli("place-cache-upsert", third)
        self.assertEqual(len((self.data / "places.jsonl").read_text().splitlines()), 3)

        ambiguous = self.cli("place-cache-lookup", {"candidates": [{
            "name": "Shared Hall", "area": "Example Borough",
        }]})
        self.assertEqual(ambiguous["results"][0]["status"], "ambiguous")

        exact = self.cli("place-cache-lookup", {"candidates": [{
            "name": "Shared Hall",
            "area": "Example Borough",
            "address": "9 South Road",
        }]})
        self.assertEqual(exact["results"][0]["status"], "hit")
        self.assertEqual(exact["results"][0]["place"]["address"], "9 South Road")

    def test_date_sensitive_fields_and_name_only_matching_are_refused(self):
        payload = self.place_payload()
        payload["place"]["open_today"] = True
        rejected = self.cli("place-cache-upsert", payload, expected=2)
        self.assertIn("date-sensitive", rejected["error"])
        self.assertEqual((self.data / "places.jsonl").read_text(), "")

        lookup = self.cli("place-cache-lookup", {
            "candidates": [{"name": "Example Discovery Centre"}],
        }, expected=2)
        self.assertIn("name-only matching is unsafe", lookup["error"])

    def test_older_observation_cannot_replace_newer_stable_pointers(self):
        newer = self.place_payload(observed_at="2030-04-07T09:00:00Z")
        newer["place"]["official_url"] = "https://places.example.org/current-centre"
        newer["evidence_urls"][0] = newer["place"]["official_url"]
        self.cli("place-cache-upsert", newer)

        older = self.place_payload(observed_at="2030-04-06T09:00:00Z")
        response = self.cli("place-cache-upsert", older)
        self.assertTrue(response["duplicate"])
        lookup = self.cli("place-cache-lookup", {"candidates": [{
            "name": "Example Discovery Centre",
            "address": "1 Public Road, Example City",
        }]})
        place = lookup["results"][0]["place"]
        self.assertEqual(place["official_url"], "https://places.example.org/current-centre")
        self.assertEqual(place["last_seen_at"], "2030-04-07T09:00:00Z")

    def test_weaker_identity_cannot_replace_pointers_for_known_address(self):
        original = self.place_payload()
        self.cli("place-cache-upsert", original)
        weaker = self.place_payload(observed_at="2030-04-07T09:00:00Z")
        del weaker["place"]["address"]
        weaker["place"]["official_url"] = "https://places.example.org/ambiguous-centre"
        weaker["evidence_urls"][0] = weaker["place"]["official_url"]
        rejected = self.cli("place-cache-upsert", weaker, expected=2)
        self.assertIn("stronger address", rejected["error"])

        stored = json.loads((self.data / "places.jsonl").read_text())
        self.assertEqual(stored["official_url"], original["place"]["official_url"])
        self.assertEqual(stored["address"], original["place"]["address"])

    def test_malformed_cache_is_preserved_on_failed_update(self):
        malformed = b'{"schema_version":1,"place_id":"broken"\n'
        (self.data / "places.jsonl").write_bytes(malformed)
        rejected = self.cli("place-cache-upsert", self.place_payload(), expected=2)
        self.assertIn("malformed", rejected["error"])
        self.assertEqual((self.data / "places.jsonl").read_bytes(), malformed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
