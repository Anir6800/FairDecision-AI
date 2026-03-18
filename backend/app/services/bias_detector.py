from __future__ import annotations

from typing import Any


METRO = ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", "pune", "kolkata"]
TIER2 = ["ahmedabad", "surat", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "bhopal"]

LOCATION_TIERS = {
    "METRO": set(METRO),
    "TIER2": set(TIER2),
}

COLLEGE_INFLUENCE = {
    "IIT_NIT": 0.0,
    "PRIVATE_TIER1": 5.0,
    "STATE": 10.0,
    "UNKNOWN": 6.0,
}

SEVERITY_WEIGHTS = {
    "NONE": 0.0,
    "LOW": 2.0,
    "MEDIUM": 3.0,
    "HIGH": 4.0,
}


def _severity_for_influence(influence_pct: float) -> str:
    if influence_pct <= 0:
        return "NONE"
    if influence_pct <= 8:
        return "LOW"
    if influence_pct <= 14:
        return "MEDIUM"
    return "HIGH"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().casefold()


def _city_only(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text.split(",", maxsplit=1)[0].strip()


def _location_tier(location: Any) -> str:
    city = _normalize_text(_city_only(location))
    if city in LOCATION_TIERS["METRO"]:
        return "METRO"
    if city in LOCATION_TIERS["TIER2"]:
        return "TIER2"
    return "TIER3"


def location_bias_score(candidate_location, job_location) -> dict:
    candidate_city = _city_only(candidate_location)
    job_city = _city_only(job_location)
    candidate_tier = _location_tier(candidate_location)
    job_tier = _location_tier(job_location)

    influence = 0.0
    if candidate_tier == job_tier:
        influence = 0.0
    elif candidate_tier == "TIER2" and job_tier == "METRO":
        influence = 12.0
    elif candidate_tier == "TIER3" and job_tier == "METRO":
        influence = 18.0

    return {
        "factor": "location",
        "candidate_value": f"{candidate_city or 'UNKNOWN'} -> {job_city or 'UNKNOWN'}",
        "influence_pct": influence,
        "severity": _severity_for_influence(influence),
    }


def college_bias_score(education: list) -> dict:
    highest_influence = 0.0
    selected_tier = "IIT_NIT"

    if not education:
        selected_tier = "UNKNOWN"
        highest_influence = COLLEGE_INFLUENCE[selected_tier]
    else:
        for item in education:
            if not isinstance(item, dict):
                continue
            tier = str(item.get("tier") or "UNKNOWN").strip().upper()
            influence = COLLEGE_INFLUENCE.get(tier, COLLEGE_INFLUENCE["UNKNOWN"])
            if influence >= highest_influence:
                highest_influence = influence
                selected_tier = tier if tier in COLLEGE_INFLUENCE else "UNKNOWN"

    return {
        "factor": "college",
        "candidate_value": selected_tier,
        "influence_pct": highest_influence,
        "severity": _severity_for_influence(highest_influence),
    }


def gap_bias_score(employment_gaps: list) -> dict:
    max_months = 0
    for gap in employment_gaps:
        if not isinstance(gap, dict):
            continue
        try:
            months = int(gap.get("months") or 0)
        except (TypeError, ValueError):
            months = 0
        if months > max_months:
            max_months = months

    if max_months == 0:
        influence = 0.0
        severity = "NONE"
    elif max_months < 6:
        influence = 4.0
        severity = "LOW"
    elif max_months < 12:
        influence = 8.0
        severity = "LOW"
    else:
        influence = 14.0
        severity = "HIGH"

    return {
        "factor": "employment_gap",
        "candidate_value": f"{max_months} months",
        "influence_pct": influence,
        "severity": severity,
    }


def calculate_fairness_score(bias_flags: list) -> float:
    weighted_total = 0.0
    total_weight = 0.0

    for flag in bias_flags:
        if not isinstance(flag, dict):
            continue
        try:
            influence = float(flag.get("influence_pct", 0.0))
        except (TypeError, ValueError):
            continue
        severity = str(flag.get("severity") or _severity_for_influence(influence)).upper()
        weight = SEVERITY_WEIGHTS.get(severity, 1.0)
        if weight <= 0:
            continue
        weighted_total += influence * weight
        total_weight += weight

    counted_flags = len([flag for flag in bias_flags if isinstance(flag, dict)])
    if total_weight <= 0 or counted_flags == 0:
        return 100.0

    fairness = 100.0 - (weighted_total / counted_flags)
    return round(max(0.0, min(100.0, fairness)), 2)


def bias_severity_from_flags(bias_flags: list[dict[str, Any]]) -> str:
    severity_rank = {
        "NONE": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }
    highest = "NONE"
    for flag in bias_flags:
        if not isinstance(flag, dict):
            continue
        severity = str(flag.get("severity") or "NONE").upper()
        if severity_rank.get(severity, 0) > severity_rank[highest]:
            highest = severity
    return highest


def build_bias_report(candidate: dict[str, Any], job_description: dict[str, Any]) -> dict[str, Any]:
    bias_flags = [
        location_bias_score(candidate.get("location"), job_description.get("location")),
        college_bias_score(candidate.get("education", [])),
        gap_bias_score(candidate.get("employment_gaps", [])),
    ]
    fairness_score = calculate_fairness_score(bias_flags)
    return {
        "bias_flags": bias_flags,
        "fairness_score": fairness_score,
        "bias_severity": bias_severity_from_flags(bias_flags),
    }
