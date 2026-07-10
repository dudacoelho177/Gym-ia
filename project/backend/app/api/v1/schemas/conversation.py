"""DTOs de API (specs/phase-07/002) — distintos das entidades de domínio."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    service_type: str = Field(..., min_length=1)
    briefing: str = ""
    title: str = ""


class MessageDTO(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ConversationDTO(BaseModel):
    id: str
    service_type: str
    briefing: str
    title: str
    created_at: datetime
    messages: list[MessageDTO] = []


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class SendMessageResponse(BaseModel):
    assistant_message: MessageDTO
    coverage_by_category: dict[str, float]
    overall_coverage: float
