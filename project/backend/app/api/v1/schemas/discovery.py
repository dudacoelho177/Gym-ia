from __future__ import annotations

from pydantic import BaseModel


class ExecutiveUnderstandingDTO(BaseModel):
    id: str
    summary: str
    diagnosis: str
    missing_information: list[str]
    risks: list[str]
    assumptions: list[str]
    next_steps: list[str]
    complexity: str
    human_review_notice: str
    version: int


class ArtifactDTO(BaseModel):
    id: str
    kind: str
    title: str
    content: str


class ArtifactGenerationRequest(BaseModel):
    kinds: list[str] = ["spec", "adr"]
