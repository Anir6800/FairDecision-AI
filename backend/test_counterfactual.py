import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.services.counterfactual import run_counterfactual


class CounterfactualTests(unittest.IsolatedAsyncioTestCase):
    async def test_location_change_ahmedabad_to_mumbai_returns_positive_score_delta(self):
        evaluation = {
            "_id": "eval-1",
            "evaluation_id": "eval-1",
            "candidate_id": "cand-1",
            "jd_id": "jd-1",
            "overall_score": 80.0,
            "bias_flags": [
                {"factor": "location", "candidate_value": "ahmedabad -> mumbai", "influence_pct": 12.0, "severity": "MEDIUM"},
                {"factor": "college", "candidate_value": "IIT_NIT", "influence_pct": 0.0, "severity": "NONE"},
                {"factor": "employment_gap", "candidate_value": "0 months", "influence_pct": 0.0, "severity": "NONE"},
            ],
            "fairness_score": 88.0,
        }
        candidate = {
            "candidate_id": "cand-1",
            "location": "ahmedabad",
            "education": [{"tier": "IIT_NIT"}],
            "employment_gaps": [],
        }
        jd = {"jd_id": "jd-1", "location": "mumbai"}

        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = evaluation

        with patch("app.services.counterfactual.get_evaluations", return_value=mock_collection), \
            patch("app.services.counterfactual.get_candidate", new=AsyncMock(return_value=candidate)), \
            patch("app.services.counterfactual.get_jd", new=AsyncMock(return_value=jd)):
            result = await run_counterfactual("eval-1", "location", "mumbai")

        self.assertGreater(result["score_delta"], 0)

    async def test_gap_change_high_to_none_returns_positive_fairness_delta(self):
        evaluation = {
            "_id": "eval-2",
            "evaluation_id": "eval-2",
            "candidate_id": "cand-2",
            "jd_id": "jd-2",
            "overall_score": 70.0,
            "bias_flags": [
                {"factor": "location", "candidate_value": "mumbai -> mumbai", "influence_pct": 0.0, "severity": "NONE"},
                {"factor": "college", "candidate_value": "IIT_NIT", "influence_pct": 0.0, "severity": "NONE"},
                {"factor": "employment_gap", "candidate_value": "14 months", "influence_pct": 14.0, "severity": "HIGH"},
            ],
            "fairness_score": 81.33,
        }
        candidate = {
            "candidate_id": "cand-2",
            "location": "mumbai",
            "education": [{"tier": "IIT_NIT"}],
            "employment_gaps": [{"months": 14, "severity": "HIGH"}],
        }
        jd = {"jd_id": "jd-2", "location": "mumbai"}

        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = evaluation

        with patch("app.services.counterfactual.get_evaluations", return_value=mock_collection), \
            patch("app.services.counterfactual.get_candidate", new=AsyncMock(return_value=candidate)), \
            patch("app.services.counterfactual.get_jd", new=AsyncMock(return_value=jd)):
            result = await run_counterfactual("eval-2", "employment_gap", "0")

        self.assertGreater(result["fairness_delta"], 0)

    async def test_location_change_within_same_tier_returns_zero_score_delta(self):
        evaluation = {
            "_id": "eval-3",
            "evaluation_id": "eval-3",
            "candidate_id": "cand-3",
            "jd_id": "jd-3",
            "overall_score": 75.0,
            "bias_flags": [
                {"factor": "location", "candidate_value": "mumbai -> delhi", "influence_pct": 0.0, "severity": "NONE"},
                {"factor": "college", "candidate_value": "IIT_NIT", "influence_pct": 0.0, "severity": "NONE"},
                {"factor": "employment_gap", "candidate_value": "0 months", "influence_pct": 0.0, "severity": "NONE"},
            ],
            "fairness_score": 100.0,
        }
        candidate = {
            "candidate_id": "cand-3",
            "location": "mumbai",
            "education": [{"tier": "IIT_NIT"}],
            "employment_gaps": [],
        }
        jd = {"jd_id": "jd-3", "location": "delhi"}

        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = evaluation

        with patch("app.services.counterfactual.get_evaluations", return_value=mock_collection), \
            patch("app.services.counterfactual.get_candidate", new=AsyncMock(return_value=candidate)), \
            patch("app.services.counterfactual.get_jd", new=AsyncMock(return_value=jd)):
            result = await run_counterfactual("eval-3", "location", "bangalore")

        self.assertEqual(result["score_delta"], 0.0)


class BiasRouteTests(unittest.TestCase):
    @patch("app.routes.bias.get_evaluations")
    def test_get_bias_returns_array_and_fairness_range(self, mock_get_evaluations):
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "_id": "eval-4",
            "evaluation_id": "eval-4",
            "bias_flags": [],
            "fairness_score": 100.0,
            "bias_severity": "NONE",
        }
        mock_get_evaluations.return_value = mock_collection

        with TestClient(app) as client:
            response = client.get("/api/bias/eval-4")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsInstance(body["bias_flags"], list)
        self.assertGreaterEqual(body["fairness_score"], 0)
        self.assertLessEqual(body["fairness_score"], 100)

    def test_invalid_variable_returns_400_not_500(self):
        with patch("app.routes.bias.run_counterfactual", new=AsyncMock(side_effect=ValueError("Unsupported counterfactual variable"))):
            with TestClient(app) as client:
                response = client.post(
                    "/api/bias/counterfactual",
                    json={
                        "evaluation_id": "eval-5",
                        "variable": "invalid_variable",
                        "new_value": "whatever",
                    },
                )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
