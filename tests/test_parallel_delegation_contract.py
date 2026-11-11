"""Contract checks for one-batch local-first weekend discovery."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATION = (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text(
    encoding="utf-8"
)
PARALLEL = (ROOT / "hermes-skill" / "references" / "parallel-research.md").read_text(
    encoding="utf-8"
)


class ParallelDelegationContractTests(unittest.TestCase):
    def test_single_batch_with_three_distinct_roles(self):
        start = "<!-- begin single-batch-example -->"
        end = "<!-- end single-batch-example -->"
        block = PARALLEL.split(start, 1)[1].split(end, 1)[0]
        payload = json.loads(block.split("```json", 1)[1].split("```", 1)[0])
        self.assertEqual(set(payload), {"tasks"})
        self.assertEqual(len(payload["tasks"]), 3)
        self.assertLess(len(json.dumps(payload, separators=(",", ":"))), 8000)
        for task in payload["tasks"]:
            self.assertEqual(set(task), {"goal", "context"})
            self.assertTrue(task["goal"])
            self.assertTrue(task["context"])
            self.assertNotIn("\n", task["context"])
            self.assertLessEqual(len(task["context"].encode("utf-8")), 1500)
        goals = [task["goal"] for task in payload["tasks"]]
        self.assertEqual(len(set(goals)), 3)
        # Check responsibilities, not exact editorial phrasing in the example.
        contexts = [task["context"].lower() for task in payload["tasks"]]
        self.assertIn("calendar", contexts[0])
        self.assertIn("library", contexts[0])
        self.assertIn("adjacent", contexts[1])
        self.assertIn("council", contexts[1])
        self.assertIn("library programs", contexts[1])
        self.assertIn("for each date", contexts[1])
        self.assertIn("recurring weekend sessions", contexts[1])
        self.assertIn("forecast", contexts[2])
        self.assertIn("indoor", contexts[2])

    def test_weekend_delegates_but_undated_menu_is_direct(self):
        self.assertIn("Do not delegate routine requests", RECOMMENDATION)
        self.assertIn("broad dated weekend search", PARALLEL)
        self.assertIn("once with three tasks in one batch", PARALLEL)
        self.assertIn("not as three", PARALLEL)
        self.assertIn("serial calls", PARALLEL)
        self.assertIn("10–15 across all three agents", PARALLEL)

    def test_failed_delegation_must_not_block_reply(self):
        self.assertIn("search the missing", PARALLEL)
        self.assertIn("return a useful answer", PARALLEL)
        self.assertIn("Never recover by launching the three", PARALLEL)
        self.assertIn("Do not modify", PARALLEL)
        self.assertIn("Present the findings first", PARALLEL)


if __name__ == "__main__":
    unittest.main()
