import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.services.explainer import generate_explanation


class ExplainerServiceTests(unittest.TestCase):
    @patch(
        "app.services.explainer.LMStudioClient.chat",
        return_value=json.dumps(
            {
                "summary": "The candidate has a mixed evaluation profile.",
                "positive_factors": "The education background is relevant.",
                "limiting_factors": "Skill alignment is weak for this role.",
                "bias_assessment": "No bias flags were identified.",
                "recommendation_reason": "The recommendation follows the weighted score.",
            }
        ),
    )
    def test_generate_explanation_mentions_specific_bias_factors(self, mock_chat):
        evaluation = {
            "overall_score": 44.5,
            "recommendation": "NOT_FIT",
            "sub_scores": {
                "aggregate": {
                    "skill_score": 0.0,
                    "experience_score": 100.0,
                    "education_score": 70.0,
                }
            },
        }
        candidate = {
            "name": "Aniruddh Rathod",
            "location": "Rajkot",
            "education": [{"degree": "B.Tech", "institution": "L.J. University", "tier": "STATE"}],
        }
        jd = {"title": "AI Engineer"}
        bias_flags = [
            {"factor": "college", "candidate_value": "STATE", "influence_pct": 10.0, "severity": "MEDIUM"},
            {"factor": "employment_gap", "candidate_value": "47 months", "influence_pct": 14.0, "severity": "HIGH"},
        ]

        explanation = generate_explanation(evaluation, bias_flags, candidate, jd)

        self.assertEqual(
            set(explanation.keys()),
            {"summary", "positive_factors", "limiting_factors", "bias_assessment", "recommendation_reason"},
        )
        self.assertTrue(all(isinstance(value, str) and value.strip() for value in explanation.values()))
        self.assertIn("college background", explanation["bias_assessment"].casefold())
        self.assertIn("employment gap history", explanation["bias_assessment"].casefold())
        self.assertNotIn("{", explanation["summary"])
        mock_chat.assert_called_once()


class ExplanationRouteTests(unittest.TestCase):
    @patch("app.routes.evaluate.get_evaluations")
    @patch("app.routes.evaluate.get_candidate", new_callable=AsyncMock)
    @patch("app.routes.evaluate.get_jd", new_callable=AsyncMock)
    @patch("app.routes.evaluate.generate_explanation")
    def test_explanation_route_returns_cached_result_without_regeneration(
        self,
        mock_generate_explanation,
        mock_get_jd,
        mock_get_candidate,
        mock_get_evaluations,
    ):
        cached = {
            "summary": "Readable summary.",
            "positive_factors": "Positive factor text.",
            "limiting_factors": "Limiting factor text.",
            "bias_assessment": "Potential bias signals were identified in college background.",
            "recommendation_reason": "Recommendation reason text.",
        }
        evaluation = {
            "_id": "eval-1",
            "evaluation_id": "eval-1",
            "candidate_id": "cand-1",
            "jd_id": "jd-1",
            "explanation": cached,
        }
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = evaluation
        mock_get_evaluations.return_value = mock_collection

        with TestClient(app) as client:
            start = time.perf_counter()
            response = client.get("/api/evaluate/eval-1/explanation")
            elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), cached)
        self.assertLess(elapsed_ms, 500)
        mock_generate_explanation.assert_not_called()
        mock_get_candidate.assert_not_called()
        mock_get_jd.assert_not_called()


if __name__ == "__main__":
    unittest.main()
