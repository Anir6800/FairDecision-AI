import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.scorer import (
    aggregate_score,
    score_education,
    score_experience,
    score_skills,
)


class ScorerTests(unittest.TestCase):
    def test_score_skills_partial_match_returns_about_sixty_seven(self):
        result = score_skills(["python", "django"], ["python", "django", "react"], [])

        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {"score", "matched", "missing", "matched_preferred"})
        self.assertAlmostEqual(result["score"], 66.67, places=2)
        self.assertEqual(result["matched"], ["python", "django"])
        self.assertEqual(result["missing"], ["react"])
        self.assertEqual(result["matched_preferred"], [])

    def test_score_skills_full_match_returns_hundred(self):
        result = score_skills(
            ["python", "django", "react"],
            ["python", "django", "react"],
            [],
        )

        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["missing"], [])

    def test_score_experience_above_requirement_returns_above_seventy(self):
        result = score_experience(5, 3)

        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {"score", "candidate_years", "required_years"})
        self.assertGreater(result["score"], 70)

    def test_score_experience_below_requirement_returns_below_forty(self):
        result = score_experience(1, 5)

        self.assertLess(result["score"], 40)

    def test_score_education_returns_expected_keys(self):
        result = score_education(
            [{"degree": "Bachelor of Engineering"}, {"degree": "Diploma in Computer Engineering"}],
            "bachelors",
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {"score", "highest_degree"})
        self.assertEqual(result["highest_degree"], "bachelors")
        self.assertEqual(result["score"], 70.0)

    def test_aggregate_score_stays_within_zero_to_hundred(self):
        result = aggregate_score(
            {"score": 100},
            {"score": 95},
            {"score": 85},
            10,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(
            set(result.keys()),
            {
                "overall_score",
                "skill_score",
                "experience_score",
                "education_score",
                "certification_score",
            },
        )
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 100)


if __name__ == "__main__":
    unittest.main()
