from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.db import get_candidates
from app.models.candidate import CandidateModel


def _model_dump(model: CandidateModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


async def save_candidate(parsed_data: dict[str, Any], file_url: str, session_id: str) -> str:
    candidate_id = str(uuid4())
    candidate = CandidateModel(
        candidate_id=candidate_id,
        session_id=session_id,
        file_url=file_url,
        name=parsed_data.get("name"),
        email=parsed_data.get("email"),
        phone=parsed_data.get("phone"),
        location=parsed_data.get("location"),
        skills=parsed_data.get("skills") or [],
        education=parsed_data.get("education") or [],
        experience=parsed_data.get("experience") or [],
        certifications=parsed_data.get("certifications") or [],
        total_experience_years=float(parsed_data.get("total_experience_years") or 0.0),
        employment_gaps=parsed_data.get("employment_gaps") or [],
    )

    document = _model_dump(candidate)
    document["_id"] = candidate_id

    await get_candidates().insert_one(document)
    return candidate_id


async def get_candidate(candidate_id: str) -> dict[str, Any]:
    candidate = await get_candidates().find_one({"_id": candidate_id})
    if candidate is None:
        raise ValueError("Candidate not found")
    return candidate
