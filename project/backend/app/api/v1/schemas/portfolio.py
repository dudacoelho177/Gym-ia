from __future__ import annotations

from pydantic import BaseModel, Field


class PortfolioItemDTO(BaseModel):
    id: str
    category: str
    name: str
    description: str
    aliases: list[str]
    is_active: bool


class PortfolioItemCreateRequest(BaseModel):
    category: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = ""
    aliases: list[str] = []


class ReferenceQuestionDTO(BaseModel):
    id: str
    domain: str
    category: str
    text: str
    is_priority: bool


class ReferenceQuestionCreateRequest(BaseModel):
    domain: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    is_priority: bool = True
