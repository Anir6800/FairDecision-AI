from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import get_evaluations
from app.services.bias_detector import build_bias_report
from app.services.candidate_service import get_candidate
from app.services.explainer import generate_explanation, is_valid_explanation
from app.services.jd_service import get_jd
from app.services.scorer import (
    aggregate_score,
    score_education,
    score_experience,
    score_skills,
)


router = APIRouter(tags=["evaluate"])


class EvaluateRequest(BaseModel):
    candidate_id: str
    jd_id: str


def _recommendation_for_score(overall_score: float) -> str:
    if overall_score >= 80:
        return "STRONG_FIT"
    if overall_score >= 65:
        return "GOOD_FIT"
    if overall_score >= 50:
        return "REVIEW"
    return "NOT_FIT"


async def _get_evaluation_or_404(evaluation_id: str) -> dict[str, Any]:
    document = await get_evaluations().find_one({"_id": evaluation_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return document


@router.post("/evaluate")
async def evaluate_candidate(payload: EvaluateRequest):
    try:
        candidate = await get_candidate(payload.candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        jd = await get_jd(payload.jd_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    skill_result = score_skills(
        candidate.get("skills", []),
        jd.get("required_skills", []),
        jd.get("preferred_skills", []),
    )
    experience_result = score_experience(
        float(candidate.get("total_experience_years") or 0.0),
        float(jd.get("min_experience_years") or 0.0),
    )
    education_result = score_education(
        candidate.get("education", []),
        jd.get("education_requirement") or "",
    )
    aggregate_result = aggregate_score(
        skill_result,
        experience_result,
        education_result,
        len(candidate.get("certifications", [])),
    )

    recommendation = _recommendation_for_score(aggregate_result["overall_score"])
    evaluation_id = str(uuid4())
    bias_report = build_bias_report(candidate, jd)
    sub_scores = {
        "skills": skill_result,
        "experience": experience_result,
        "education": education_result,
        "aggregate": aggregate_result,
    }
    document = {
        "_id": evaluation_id,
        "evaluation_id": evaluation_id,
        "candidate_id": payload.candidate_id,
        "jd_id": payload.jd_id,
        "overall_score": aggregate_result["overall_score"],
        "recommendation": recommendation,
        "sub_scores": sub_scores,
        "bias_flags": bias_report["bias_flags"],
        "fairness_score": bias_report["fairness_score"],
        "bias_severity": bias_report["bias_severity"],
        "created_at": datetime.now(timezone.utc),
    }
    await get_evaluations().insert_one(document)

    return {
        "evaluation_id": evaluation_id,
        "overall_score": aggregate_result["overall_score"],
        "recommendation": recommendation,
        "sub_scores": sub_scores,
    }


@router.get("/evaluate/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    return await _get_evaluation_or_404(evaluation_id)


@router.get("/evaluate/{evaluation_id}/score")
async def get_evaluation_score(evaluation_id: str):
    document = await _get_evaluation_or_404(evaluation_id)
    return {
        "evaluation_id": document["evaluation_id"],
        "overall_score": document["overall_score"],
        "recommendation": document["recommendation"],
        "sub_scores": document["sub_scores"],
    }


@router.get("/evaluate/{evaluation_id}/explanation")
async def get_evaluation_explanation(evaluation_id: str):
    evaluation = await _get_evaluation_or_404(evaluation_id)

    cached_explanation = evaluation.get("explanation")
    if is_valid_explanation(cached_explanation, evaluation.get("bias_flags", [])):
        return cached_explanation

    try:
        candidate = await get_candidate(evaluation["candidate_id"])
        jd = await get_jd(evaluation["jd_id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    explanation = generate_explanation(
        evaluation=evaluation,
        bias_flags=evaluation.get("bias_flags", []),
        candidate=candidate,
        jd=jd,
    )
    await get_evaluations().update_one(
        {"_id": evaluation_id},
        {"$set": {"explanation": explanation}},
    )
    return explanation
