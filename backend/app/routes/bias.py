from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import get_evaluations
from app.services.bias_detector import build_bias_report
from app.services.candidate_service import get_candidate
from app.services.counterfactual import run_counterfactual
from app.services.jd_service import get_jd


router = APIRouter(tags=["bias"])


class CounterfactualRequest(BaseModel):
    evaluation_id: str
    variable: str
    new_value: str


@router.post("/bias/counterfactual")
async def create_counterfactual(payload: CounterfactualRequest):
    try:
        return await run_counterfactual(
            evaluation_id=payload.evaluation_id,
            variable=payload.variable,
            new_value=payload.new_value,
        )
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message) from exc


@router.get("/bias/{evaluation_id}")
async def get_bias_report(evaluation_id: str):
    evaluation = await get_evaluations().find_one({"_id": evaluation_id})
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if "bias_flags" in evaluation and "fairness_score" in evaluation and "bias_severity" in evaluation:
        return {
            "evaluation_id": evaluation["evaluation_id"],
            "bias_flags": evaluation["bias_flags"],
            "fairness_score": evaluation["fairness_score"],
            "bias_severity": evaluation["bias_severity"],
        }

    try:
        candidate = await get_candidate(evaluation["candidate_id"])
        job_description = await get_jd(evaluation["jd_id"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    report = build_bias_report(candidate, job_description)
    return {
        "evaluation_id": evaluation["evaluation_id"],
        "bias_flags": report["bias_flags"],
        "fairness_score": report["fairness_score"],
        "bias_severity": report["bias_severity"],
    }
