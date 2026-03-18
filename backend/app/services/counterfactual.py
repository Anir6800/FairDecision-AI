from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.db import get_evaluations
from app.services.bias_detector import build_bias_report
from app.services.candidate_service import get_candidate
from app.services.jd_service import get_jd


def _score_with_fairness(overall_score: float, fairness_score: float) -> float:
    adjusted = float(overall_score) * (float(fairness_score) / 100.0)
    return round(max(0.0, min(100.0, adjusted)), 2)


def _parse_gap_months(new_value: str) -> int:
    digits = "".join(char for char in str(new_value) if char.isdigit())
    return int(digits) if digits else 0


def _candidate_value_for_variable(candidate: dict[str, Any], variable: str) -> str:
    if variable == "location":
        return str(candidate.get("location") or "")
    if variable == "college_tier":
        education = candidate.get("education", [])
        if education and isinstance(education[0], dict):
            return str(education[0].get("tier") or "UNKNOWN")
        return "UNKNOWN"
    if variable == "employment_gap":
        gaps = candidate.get("employment_gaps", [])
        if gaps and isinstance(gaps[0], dict):
            return str(gaps[0].get("months") or 0)
        return "0"
    raise ValueError("Unsupported counterfactual variable")


def _apply_counterfactual(candidate: dict[str, Any], variable: str, new_value: str) -> dict[str, Any]:
    modified = deepcopy(candidate)

    if variable == "location":
        modified["location"] = new_value
        return modified

    if variable == "college_tier":
        education = modified.get("education") or []
        if education and isinstance(education[0], dict):
            education[0]["tier"] = new_value.strip().upper()
        else:
            education = [{"degree": None, "institution": None, "year": None, "tier": new_value.strip().upper()}]
        modified["education"] = education
        return modified

    if variable == "employment_gap":
        months = _parse_gap_months(new_value)
        if months <= 0:
            modified["employment_gaps"] = []
        else:
            modified["employment_gaps"] = [
                {
                    "start": "SIMULATED",
                    "end": "SIMULATED",
                    "months": months,
                    "severity": "HIGH" if months >= 12 else "LOW",
                }
            ]
        return modified

    raise ValueError("Unsupported counterfactual variable")


async def _get_evaluation(evaluation_id: str) -> dict[str, Any]:
    document = await get_evaluations().find_one({"_id": evaluation_id})
    if document is None:
        raise ValueError("Evaluation not found")
    return document


async def run_counterfactual(evaluation_id: str, variable: str, new_value: str) -> dict[str, Any]:
    evaluation = await _get_evaluation(evaluation_id)
    candidate = await get_candidate(evaluation["candidate_id"])
    job_description = await get_jd(evaluation["jd_id"])

    original_bias = evaluation.get("bias_flags")
    original_fairness = evaluation.get("fairness_score")
    if not isinstance(original_bias, list) or original_fairness is None:
        report = build_bias_report(candidate, job_description)
        original_bias = report["bias_flags"]
        original_fairness = report["fairness_score"]

    base_score = float(evaluation.get("overall_score") or 0.0)
    original_score = _score_with_fairness(base_score, float(original_fairness))

    original_value = _candidate_value_for_variable(candidate, variable)
    modified_candidate = _apply_counterfactual(candidate, variable, new_value)
    modified_report = build_bias_report(modified_candidate, job_description)

    new_fairness = float(modified_report["fairness_score"])
    new_score = _score_with_fairness(base_score, new_fairness)

    return {
        "variable": variable,
        "original_value": original_value,
        "new_value": new_value,
        "original_score": original_score,
        "new_score": new_score,
        "score_delta": round(new_score - original_score, 2),
        "original_fairness": round(float(original_fairness), 2),
        "new_fairness": round(new_fairness, 2),
        "fairness_delta": round(new_fairness - float(original_fairness), 2),
        "bias_before": original_bias,
        "bias_after": modified_report["bias_flags"],
    }
