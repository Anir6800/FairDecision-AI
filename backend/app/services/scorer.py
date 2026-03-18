from __future__ import annotations

from typing import Any


DEGREE_SCORES = {
    "phd": 100.0,
    "masters": 85.0,
    "bachelors": 70.0,
    "diploma": 50.0,
    "other": 30.0,
}


def _normalize_skill(value: Any) -> str:
    return str(value).strip().casefold()


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def _classify_degree(degree_text: str | None) -> str:
    text = (degree_text or "").strip().casefold()
    if "phd" in text or "doctor" in text:
        return "phd"
    if "master" in text or "mba" in text or "m.tech" in text or "mtech" in text or "m.sc" in text or "msc" in text:
        return "masters"
    if (
        "bachelor" in text
        or "b.tech" in text
        or "btech" in text
        or "b.e" in text
        or "be " in f"{text} "
        or "b.sc" in text
        or "bsc" in text
        or "bca" in text
    ):
        return "bachelors"
    if "diploma" in text:
        return "diploma"
    return "other"


def score_skills(candidate_skills: list, required_skills: list, preferred_skills: list) -> dict:
    candidate_lookup = {
        _normalize_skill(skill): str(skill).strip()
        for skill in candidate_skills
        if str(skill).strip()
    }

    matched_required: list[str] = []
    missing_required: list[str] = []
    for skill in required_skills:
        original = str(skill).strip()
        normalized = _normalize_skill(original)
        if not original:
            continue
        if normalized in candidate_lookup:
            matched_required.append(candidate_lookup[normalized])
        else:
            missing_required.append(original)

    matched_preferred: list[str] = []
    for skill in preferred_skills:
        original = str(skill).strip()
        normalized = _normalize_skill(original)
        if original and normalized in candidate_lookup:
            matched_preferred.append(candidate_lookup[normalized])

    base_score = (len(matched_required) / max(len(required_skills), 1)) * 100.0
    bonus_score = len(_dedupe_preserve_order(matched_preferred)) * 5.0
    total_score = min(100.0, base_score + bonus_score)

    return {
        "score": round(total_score, 2),
        "matched": _dedupe_preserve_order(matched_required),
        "missing": _dedupe_preserve_order(missing_required),
        "matched_preferred": _dedupe_preserve_order(matched_preferred),
    }


def score_experience(candidate_years: float, required_years: float) -> dict:
    candidate_value = float(candidate_years or 0.0)
    required_value = float(required_years or 0.0)

    if candidate_value >= required_value:
        denominator = required_value if required_value > 0 else 1.0
        score = min(100.0, 70.0 + (candidate_value / denominator) * 30.0)
    else:
        score = (candidate_value / max(required_value, 1.0)) * 70.0

    return {
        "score": round(score, 2),
        "candidate_years": candidate_value,
        "required_years": required_value,
    }


def score_education(candidate_edu: list, required_level: str) -> dict:
    del required_level

    highest_degree = "other"
    highest_score = DEGREE_SCORES["other"]

    for item in candidate_edu:
        degree_value = item.get("degree") if isinstance(item, dict) else item
        classified = _classify_degree(str(degree_value) if degree_value is not None else None)
        score = DEGREE_SCORES[classified]
        if score > highest_score:
            highest_score = score
            highest_degree = classified

    return {
        "score": highest_score,
        "highest_degree": highest_degree,
    }


def aggregate_score(skill_s, exp_s, edu_s, cert_count) -> dict:
    skill_score = float(skill_s.get("score", 0.0))
    experience_score = float(exp_s.get("score", 0.0))
    education_score = float(edu_s.get("score", 0.0))
    certification_score = min(float(cert_count or 0) * 20.0, 100.0)

    overall = (
        (0.45 * skill_score)
        + (0.30 * experience_score)
        + (0.15 * education_score)
        + (0.10 * certification_score)
    )

    return {
        "overall_score": round(overall, 2),
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "certification_score": round(certification_score, 2),
    }
