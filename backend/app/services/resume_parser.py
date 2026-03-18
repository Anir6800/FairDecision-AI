import json
from typing import Any

from app.services.lm_client import LMStudioClient


RESUME_SYSTEM_PROMPT = """You are a resume data extractor. Extract structured information from the resume text provided. You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no code fences. Just raw JSON.

The JSON must follow this exact schema:
{
  "name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string (city name only) or null",
  "skills": ["array", "of", "skill", "strings"],
  "education": [{"degree": "string", "institution": "string", "year": "string or null", "tier": "IIT_NIT or PRIVATE_TIER1 or STATE or UNKNOWN"}],
  "experience": [{"company": "string", "role": "string", "start": "YYYY-MM or null", "end": "YYYY-MM or null or PRESENT"}],
  "certifications": ["array of certification strings"],
  "total_experience_years": number
}"""

JD_SYSTEM_PROMPT = """You are a job description data extractor. Extract structured information from the job description text provided. You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no code fences. Just raw JSON.

The JSON must follow this exact schema:
{
  "title": "string or null",
  "required_skills": ["array", "of", "skill", "strings"],
  "preferred_skills": ["array", "of", "skill", "strings"],
  "min_experience_years": number or null,
  "education_requirement": "string or null",
  "location": "string (city name only) or null"
}"""


def _extract_json_object(response_text: str) -> dict[str, Any]:
    response_text = response_text.strip()
    try:
        parsed = json.loads(response_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start_index = response_text.find("{")
    if start_index == -1:
        raise ValueError("Model response did not contain a JSON object")

    depth = 0
    in_string = False
    escape = False

    for index in range(start_index, len(response_text)):
        char = response_text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = response_text[start_index : index + 1]
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
                break

    raise ValueError("Unable to parse a JSON object from model response")


def _as_string_or_null(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return str(value).strip() or None


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        string_value = _as_string_or_null(item)
        if string_value is not None:
            items.append(string_value)
    return items


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _normalize_resume(data: dict[str, Any]) -> dict[str, Any]:
    normalized_education: list[dict[str, Any]] = []
    for item in data.get("education", []):
        if not isinstance(item, dict):
            continue
        normalized_education.append(
            {
                "degree": _as_string_or_null(item.get("degree")),
                "institution": _as_string_or_null(item.get("institution")),
                "year": _as_string_or_null(item.get("year")),
                "tier": _as_string_or_null(item.get("tier")) or "UNKNOWN",
            }
        )

    normalized_experience: list[dict[str, Any]] = []
    for item in data.get("experience", []):
        if not isinstance(item, dict):
            continue
        normalized_experience.append(
            {
                "company": _as_string_or_null(item.get("company")),
                "role": _as_string_or_null(item.get("role")),
                "start": _as_string_or_null(item.get("start")),
                "end": _as_string_or_null(item.get("end")),
            }
        )

    return {
        "name": _as_string_or_null(data.get("name")),
        "email": _as_string_or_null(data.get("email")),
        "phone": _as_string_or_null(data.get("phone")),
        "location": _as_string_or_null(data.get("location")),
        "skills": _as_string_list(data.get("skills")),
        "education": normalized_education,
        "experience": normalized_experience,
        "certifications": _as_string_list(data.get("certifications")),
        "total_experience_years": _as_float(data.get("total_experience_years"), default=0.0),
    }


def _normalize_jd(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _as_string_or_null(data.get("title")),
        "required_skills": _as_string_list(data.get("required_skills")),
        "preferred_skills": _as_string_list(data.get("preferred_skills")),
        "min_experience_years": _as_float(data.get("min_experience_years"), default=0.0)
        if data.get("min_experience_years") is not None
        else None,
        "education_requirement": _as_string_or_null(data.get("education_requirement")),
        "location": _as_string_or_null(data.get("location")),
    }


def parse_resume(raw_text: str) -> dict[str, Any]:
    client = LMStudioClient()
    response_text = client.chat(
        system_prompt=RESUME_SYSTEM_PROMPT,
        user_message=f"Extract from this resume: {raw_text}",
        temperature=0,
    )
    return _normalize_resume(_extract_json_object(response_text))


def parse_jd(raw_text: str) -> dict[str, Any]:
    client = LMStudioClient()
    response_text = client.chat(
        system_prompt=JD_SYSTEM_PROMPT,
        user_message=f"Extract from this job description: {raw_text}",
        temperature=0,
    )
    return _normalize_jd(_extract_json_object(response_text))
