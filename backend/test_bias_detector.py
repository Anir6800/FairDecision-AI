import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.bias_detector import (
    calculate_fairness_score,
    college_bias_score,
    gap_bias_score,
    location_bias_score,
)


class BiasDetectorTests(unittest.TestCase):
    def test_location_bias_tier2_to_metro_is_at_least_ten(self):
        result = location_bias_score("ahmedabad", "mumbai")

        self.assertGreaterEqual(result["influence_pct"], 10)
        self.assertEqual(result["severity"], "MEDIUM")

    def test_location_bias_same_metro_is_zero_and_none(self):
        result = location_bias_score("mumbai", "mumbai")

        self.assertEqual(result["influence_pct"], 0.0)
        self.assertEqual(result["severity"], "NONE")

    def test_college_bias_iit_nit_is_zero(self):
        result = college_bias_score(
            [
                {
                    "degree": "B.Tech",
                    "institution": "IIT Bombay",
                    "year": "2022",
                    "tier": "IIT_NIT",
                }
            ]
        )

        self.assertEqual(result["influence_pct"], 0.0)
        self.assertEqual(result["severity"], "NONE")

    def test_gap_bias_fourteen_months_is_high(self):
        result = gap_bias_score(
            [
                {
                    "start": "2021-01",
                    "end": "2022-02",
                    "months": 14,
                    "severity": "HIGH",
                }
            ]
        )

        self.assertEqual(result["severity"], "HIGH")
        self.assertEqual(result["influence_pct"], 14.0)

    def test_calculate_fairness_score_empty_is_hundred(self):
        self.assertEqual(calculate_fairness_score([]), 100.0)

    def test_calculate_fairness_score_three_high_bias_flags_is_below_sixty(self):
        fairness = calculate_fairness_score(
            [
                {"factor": "location", "candidate_value": "tier3->metro", "influence_pct": 18.0, "severity": "HIGH"},
                {"factor": "college", "candidate_value": "STATE", "influence_pct": 10.0, "severity": "MEDIUM"},
                {"factor": "employment_gap", "candidate_value": "24 months", "influence_pct": 14.0, "severity": "HIGH"},
            ]
        )

        self.assertLess(fairness, 60)


if __name__ == "__main__":
    unittest.main()
