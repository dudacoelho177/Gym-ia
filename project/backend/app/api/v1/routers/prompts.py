"""Prompt Editável — CRUD + versionamento imutável (specs/phase-03/002, ADR-0012)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant_and_user, get_db
from app.api.v1.schemas.prompt import PromptDTO, PromptUpsertRequest, PromptVersionDTO
from app.domain.entities import Prompt, PromptVersion
from app.infrastructure.repositories.sqlalchemy_repositories import SqlAlchemyPromptRepository

router = APIRouter(prefix="/prompts", tags=["prompts"])


def _to_dto(prompt: Prompt) -> PromptDTO:
    return PromptDTO(
        id=prompt.id, name=prompt.name, is_active=prompt.is_active,
        active_version_id=prompt.active_version_id,
        versions=[
            PromptVersionDTO(id=v.id, version_number=v.version_number, content=v.content, created_at=v.created_at)
            for v in prompt.versions
        ],
    )


@router.get("/active", response_model=PromptDTO | None)
def get_active_prompt(
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> PromptDTO | None:
    tenant_id, _ = tenant_user
    repo = SqlAlchemyPromptRepository(db)
    prompt = repo.get_active(tenant_id)
    return _to_dto(prompt) if prompt else None


@router.put("/active", response_model=PromptDTO)
def upsert_active_prompt(
    payload: PromptUpsertRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> PromptDTO:
    """Cada edição cria uma NOVA PromptVersion imutável (nunca update in-place, ADR-0012)."""
    tenant_id, _ = tenant_user
    repo = SqlAlchemyPromptRepository(db)
    prompt = repo.get_active(tenant_id)
    if prompt is None:
        prompt = Prompt(tenant_id=tenant_id, name=payload.name, is_active=True)

    next_version_number = len(prompt.versions) + 1
    new_version = PromptVersion(prompt_id=prompt.id, content=payload.content, version_number=next_version_number)
    prompt.versions.append(new_version)
    prompt.active_version_id = new_version.id
    prompt.name = payload.name
    repo.save(prompt)
    return _to_dto(prompt)


@router.post("/active/versions/{version_id}/activate", response_model=PromptDTO)
def activate_prompt_version(
    version_id: str,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> PromptDTO:
    """Ativa uma versão já existente (rollback) — não cria versão nova, só move o ponteiro (ADR-0012)."""
    tenant_id, _ = tenant_user
    repo = SqlAlchemyPromptRepository(db)
    prompt = repo.get_active(tenant_id)
    if prompt is None or not any(v.id == version_id for v in prompt.versions):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão não encontrada")

    prompt.active_version_id = version_id
    repo.save(prompt)
    return _to_dto(prompt)
