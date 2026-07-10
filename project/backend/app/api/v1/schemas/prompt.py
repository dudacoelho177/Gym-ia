from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PromptVersionDTO(BaseModel):
    id: str
    version_number: int
    content: str
    created_at: datetime


class PromptDTO(BaseModel):
    id: str
    name: str
    is_active: bool
    active_version_id: str | None
    versions: list[PromptVersionDTO]


class PromptUpsertRequest(BaseModel):
    name: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
