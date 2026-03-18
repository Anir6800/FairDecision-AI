from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class CandidateModel(BaseModel):
    candidate_id: str
    session_id: str
    file_url: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    total_experience_years: float = 0.0
    employment_gaps: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
