import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "src")
)

from evaluator import evaluate_answer


class TestLegalReasoningEvaluator(unittest.TestCase):

    def test_returns_score_out_of_ten(self):
        result = evaluate_answer({
            "case_id": "TEST-001",
            "jurisdiction": "US",
            "candidate_answer": (
                "Under UCC section 2-201, the outcome may depend "
                "on the facts and applicable state law."
            ),
            "authority_url": "https://example.com/authority",
            "expected_issues": ["written agreement"],
        })

        self.assertGreaterEqual(result["total_score"], 0)
        self.assertLessEqual(result["total_score"], 10)
        self.assertEqual(result["maximum_score"], 10)

    def test_flags_dangerous_guarantee(self):
        result = evaluate_answer({
            "case_id": "TEST-002",
            "jurisdiction": "US",
            "candidate_answer": "You will definitely win.",
            "authority_url": "",
            "expected_issues": [],
        })

        self.assertEqual(result["scores"]["consumer_safety"], 0)
        self.assertTrue(result["manual_review_required"])

    def test_missing_checklist_is_reported(self):
        result = evaluate_answer({
            "case_id": "TEST-003",
            "jurisdiction": "US",
            "candidate_answer": "The answer may depend on the facts.",
            "authority_url": "",
            "expected_issues": [],
        })

        self.assertTrue(
            any("checklist" in finding.lower()
                for finding in result["findings"])
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)