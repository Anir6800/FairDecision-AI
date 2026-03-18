import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.resume_parser import parse_jd, parse_resume


SAMPLE_RESUME_TEXT = """
ANIRUDDH RATHOD
Rajkot
anir6800@gmail.com
+91-9624519644

Skills: Python, FastAPI, React, PostgreSQL, Machine Learning

Education:
- B.Tech in Computer Engineering, State University, 2024

Experience:
- AI Engineer Intern at FairDecision Labs (2024-01 to PRESENT)

Certifications:
- AWS Certified Cloud Practitioner
""".strip()

SAMPLE_RESUME_JSON = """
{
  "name": "Aniruddh Rathod",
  "email": "anir6800@gmail.com",
  "phone": "+91-9624519644",
  "location": "Rajkot",
  "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Machine Learning"],
  "education": [
    {
      "degree": "B.Tech in Computer Engineering",
      "institution": "State University",
      "year": "2024",
      "tier": "STATE"
    }
  ],
  "experience": [
    {
      "company": "FairDecision Labs",
      "role": "AI Engineer Intern",
      "start": "2024-01",
      "end": "PRESENT"
    }
  ],
  "certifications": ["AWS Certified Cloud Practitioner"],
  "total_experience_years": 1.5
}
""".strip()

SAMPLE_JD_TEXT = """
AI Engineer
Required skills: Python, FastAPI, NLP, SQL
Preferred skills: React, Docker
Minimum experience: 2 years
Education: Bachelor's in Computer Science
Location: Bangalore
""".strip()

SAMPLE_JD_JSON = """
{
  "title": "AI Engineer",
  "required_skills": ["Python", "FastAPI", "NLP", "SQL"],
  "preferred_skills": ["React", "Docker"],
  "min_experience_years": 2,
  "education_requirement": "Bachelor's in Computer Science",
  "location": "Bangalore"
}
""".strip()


class ResumeParserTests(unittest.TestCase):
    @patch("app.services.resume_parser.LMStudioClient.chat", return_value=SAMPLE_RESUME_JSON)
    def test_parse_resume_returns_valid_dict_with_required_keys(self, mock_chat):
        parsed = parse_resume(SAMPLE_RESUME_TEXT)

        self.assertIsInstance(parsed, dict)
        self.assertEqual(
            set(parsed.keys()),
            {
                "name",
                "email",
                "phone",
                "location",
                "skills",
                "education",
                "experience",
                "certifications",
                "total_experience_years",
            },
        )
        self.assertGreaterEqual(len(parsed["skills"]), 1)
        self.assertIn(parsed["education"][0]["tier"], {"IIT_NIT", "PRIVATE_TIER1", "STATE", "UNKNOWN"})
        mock_chat.assert_called_once()

    @patch(
        "app.services.resume_parser.LMStudioClient.chat",
        return_value='Here is the JSON you asked for:\n{"name":"A","email":null,"phone":null,"location":"Rajkot","skills":["Python"],"education":[{"degree":"B.Tech","institution":"State University","year":"2024","tier":"STATE"}],"experience":[],"certifications":[],"total_experience_years":1}\nThanks.',
    )
    def test_parse_resume_handles_extra_text_around_json(self, mock_chat):
        parsed = parse_resume(SAMPLE_RESUME_TEXT)

        self.assertEqual(parsed["name"], "A")
        self.assertEqual(parsed["skills"], ["Python"])
        self.assertEqual(parsed["education"][0]["tier"], "STATE")
        mock_chat.assert_called_once()

    @patch("app.services.resume_parser.LMStudioClient.chat", return_value=SAMPLE_JD_JSON)
    def test_parse_jd_returns_non_empty_required_skills(self, mock_chat):
        parsed = parse_jd(SAMPLE_JD_TEXT)

        self.assertIsInstance(parsed, dict)
        self.assertIsInstance(parsed["required_skills"], list)
        self.assertGreaterEqual(len(parsed["required_skills"]), 1)
        mock_chat.assert_called_once()


if __name__ == "__main__":
    unittest.main()
