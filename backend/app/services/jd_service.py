from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db import get_jd_collection


async def save_jd(parsed_data: dict[str, Any], file_url: str) -> str:
    jd_id = str(uuid4())
    document = {
        "_id": jd_id,
        "jd_id": jd_id,
        "file_url": file_url,
        "title": parsed_data.get("title"),
        "required_skills": parsed_data.get("required_skills") or [],
        "preferred_skills": parsed_data.get("preferred_skills") or [],
        "min_experience_years": parsed_data.get("min_experience_years"),
        "education_requirement": parsed_data.get("education_requirement"),
        "location": parsed_data.get("location"),
        "created_at": datetime.now(timezone.utc),
    }
    await get_jd_collection().insert_one(document)
    return jd_id


async def get_jd(jd_id: str) -> dict[str, Any]:
    document = await get_jd_collection().find_one({"_id": jd_id})
    if document is None:
        raise ValueError("Job description not found")
    return document
