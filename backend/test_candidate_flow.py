import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.services.gap_detector import detect_gaps


class CandidateFlowTests(unittest.TestCase):
    def test_detect_gaps_reports_high_severity_for_two_year_gap(self):
        experience = [
            {
                "company": "First Co",
                "role": "Engineer",
                "start": "2020-01",
                "end": "2020-12",
            },
            {
                "company": "Second Co",
                "role": "Senior Engineer",
                "start": "2023-01",
                "end": "PRESENT",
            },
        ]

        gaps = detect_gaps(experience)

        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["start"], "2021-01")
        self.assertEqual(gaps[0]["end"], "2022-12")
        self.assertEqual(gaps[0]["months"], 24)
        self.assertEqual(gaps[0]["severity"], "HIGH")

    @patch("app.routes.upload.get_candidate", new_callable=AsyncMock)
    def test_get_parse_resume_returns_full_document_with_employment_gaps(self, mock_get_candidate):
        candidate_document = {
            "_id": "candidate-123",
            "candidate_id": "candidate-123",
            "session_id": "session-456",
            "file_url": "uploads/candidate-123_resume.pdf",
            "name": "Aniruddh Rathod",
            "email": "anir6800@gmail.com",
            "phone": "+91-9624519644",
            "location": "Rajkot",
            "skills": ["Python", "FastAPI"],
            "education": [
                {
                    "degree": "B.Tech",
                    "institution": "State University",
                    "year": "2024",
                    "tier": "STATE",
                }
            ],
            "experience": [
                {
                    "company": "First Co",
                    "role": "Engineer",
                    "start": "2020-01",
                    "end": "2020-12",
                }
            ],
            "certifications": ["AWS CCP"],
            "total_experience_years": 2.0,
            "employment_gaps": [],
        }
        mock_get_candidate.return_value = candidate_document

        with TestClient(app) as client:
            response = client.get("/api/parse/resume/candidate-123")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["_id"], "candidate-123")
        self.assertEqual(body["candidate_id"], "candidate-123")
        self.assertIn("employment_gaps", body)
        self.assertEqual(body["employment_gaps"], [])
        self.assertEqual(body["name"], "Aniruddh Rathod")


if __name__ == "__main__":
    unittest.main()
