import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


DEMO_DIR = BACKEND_DIR / "demo_data"
RESUME_PATH = DEMO_DIR / "resume_B.pdf"
JD_PATH = DEMO_DIR / "JD_senior_dev.pdf"


def parse_resume_fixture(raw_text: str) -> dict:
    if "Rahul Verma" not in raw_text:
        raise AssertionError("Unexpected resume content in E2E fixture")

    return {
        "name": "Rahul Verma",
        "email": "rahul.verma@example.com",
        "phone": "+91-9876543210",
        "location": "Ahmedabad",
        "skills": ["Python", "Django", "React", "AWS"],
        "education": [
            {
                "degree": "B.Tech in Computer Science",
                "institution": "Gujarat University",
                "year": "2018",
                "tier": "STATE",
            }
        ],
        "experience": [
            {
                "company": "Local IT Company",
                "role": "Software Engineer",
                "start": "2018-01",
                "end": "2021-04",
            },
            {
                "company": "Local IT Company",
                "role": "Senior Software Engineer",
                "start": "2022-01",
                "end": "PRESENT",
            },
        ],
        "certifications": [],
        "total_experience_years": 5.0,
    }


def parse_jd_fixture(raw_text: str) -> dict:
    if "Senior Python Developer" not in raw_text:
        raise AssertionError("Unexpected JD content in E2E fixture")

    return {
        "title": "Senior Python Developer",
        "required_skills": ["Python", "Django", "REST APIs"],
        "preferred_skills": [],
        "min_experience_years": 4.0,
        "education_requirement": "B.Tech preferred",
        "location": "Mumbai",
    }


def assert_check(label: str, condition: bool) -> None:
    print(f"{'PASS' if condition else 'FAIL'}: {label}")
    if not condition:
        raise AssertionError(label)


def main() -> int:
    if not RESUME_PATH.exists() or not JD_PATH.exists():
        print("FAIL: Demo PDFs are missing. Run backend/demo_data/generate_demo_data.py first.")
        return 1

    with patch("app.routes.upload.parse_resume", side_effect=parse_resume_fixture), patch(
        "app.routes.upload.parse_jd", side_effect=parse_jd_fixture
    ):
        with TestClient(app) as client:
            with RESUME_PATH.open("rb") as resume_file:
                resume_response = client.post(
                    "/api/upload/resume",
                    files={"file": (RESUME_PATH.name, io.BytesIO(resume_file.read()), "application/pdf")},
                )
            assert_check("resume upload succeeds", resume_response.status_code == 200)
            candidate_id = resume_response.json()["candidate_id"]

            with JD_PATH.open("rb") as jd_file:
                jd_response = client.post(
                    "/api/upload/jd",
                    files={"file": (JD_PATH.name, io.BytesIO(jd_file.read()), "application/pdf")},
                )
            assert_check("jd upload succeeds", jd_response.status_code == 200)
            jd_id = jd_response.json()["jd_id"]

            evaluation_response = client.post(
                "/api/evaluate",
                json={"candidate_id": candidate_id, "jd_id": jd_id},
            )
            assert_check("evaluation succeeds", evaluation_response.status_code == 200)
            evaluation = evaluation_response.json()
            evaluation_id = evaluation["evaluation_id"]

            overall_score = float(evaluation["overall_score"])
            assert_check("overall_score between 60 and 85", 60 <= overall_score <= 85)

            bias_response = client.get(f"/api/bias/{evaluation_id}")
            assert_check("bias endpoint succeeds", bias_response.status_code == 200)
            bias_payload = bias_response.json()
            factors = {flag["factor"] for flag in bias_payload.get("bias_flags", [])}
            assert_check("bias_flags contains location", "location" in factors)
            assert_check("bias_flags contains employment_gap", "employment_gap" in factors)

            location_counterfactual = client.post(
                "/api/bias/counterfactual",
                json={
                    "evaluation_id": evaluation_id,
                    "variable": "location",
                    "new_value": "mumbai",
                },
            )
            assert_check("location counterfactual succeeds", location_counterfactual.status_code == 200)
            location_payload = location_counterfactual.json()
            assert_check("location to Mumbai score_delta > 5", float(location_payload["score_delta"]) > 5)

            gap_counterfactual = client.post(
                "/api/bias/counterfactual",
                json={
                    "evaluation_id": evaluation_id,
                    "variable": "employment_gap",
                    "new_value": "0",
                },
            )
            assert_check("gap removal counterfactual succeeds", gap_counterfactual.status_code == 200)
            gap_payload = gap_counterfactual.json()
            assert_check("remove gap fairness_delta > 5", float(gap_payload["fairness_delta"]) > 5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
