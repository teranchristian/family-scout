"""Contract checks for the optional parallel-research delegation recipe."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATION = (ROOT / "hermes-skill" / "references" / "recommendation.md").read_text(
    encoding="utf-8"
)


class ParallelDelegationContractTests(unittest.TestCase):
    def test_documented_batch_is_valid_three_task_json(self):
        start_marker = "<!-- begin single-batch-example -->"
        end_marker = "<!-- end single-batch-example -->"
        self.assertIn(start_marker, RECOMMENDATION)
        self.assertIn(end_marker, RECOMMENDATION)
        block = RECOMMENDATION.split(start_marker, 1)[1].split(end_marker, 1)[0]
        payload = json.loads("{" + block.split("{", 1)[1].rsplit("}", 1)[0] + "}")
        self.assertEqual(set(payload), {"tasks"})
        self.assertEqual(len(payload["tasks"]), 3)
        self.assertLess(len(json.dumps(payload, separators=(",", ":"))), 8000)
        goals = set()
        for task in payload["tasks"]:
            self.assertEqual(set(task), {"goal", "context"})
            self.assertTrue(task["goal"].strip())
            self.assertTrue(task["context"].strip())
            self.assertNotIn("\n", task["context"])
            self.assertLessEqual(len(task["context"].encode("utf-8")), 1500)
            goals.add(task["goal"])
        self.assertEqual(len(goals), 3)

    def test_fallback_does_not_serialize_three_delegations(self):
        self.assertIn("Never recover by launching the three", RECOMMENDATION)
        self.assertIn("subagents separately.", RECOMMENDATION)
        self.assertIn("Three children do **not** create three fresh budgets", RECOMMENDATION)
        self.assertIn("Do not modify Hermes configuration", RECOMMENDATION)


if __name__ == "__main__":
    unittest.main()
