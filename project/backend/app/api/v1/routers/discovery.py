"""Saída do Discovery — Relatório Executivo & Artefatos (specs/phase-06)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant_and_user, get_db, get_llm
from app.api.v1.schemas.discovery import ArtifactDTO, ArtifactGenerationRequest, ExecutiveUnderstandingDTO
from app.application.agents.spec_generator import generate_artifacts
from app.application.agents.summary_agent import generate_executive_understanding
from app.domain.ports.llm_provider import LLMProvider
from app.infrastructure.db.models import ArtifactModel as ArtifactORM
from app.infrastructure.db.models import ExecutiveUnderstandingModel
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SqlAlchemyConversationRepository,
    SqlAlchemyDiscoveryStateRepository,
)

router = APIRouter(prefix="/conversations/{conversation_id}", tags=["discovery-output"])


@router.get("/state")
def get_discovery_state(
    conversation_id: str,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> dict:
    """Cobertura atual do DiscoveryState — usado pela UI ao reabrir uma conversa do histórico."""
    tenant_id, _ = tenant_user
    state = SqlAlchemyDiscoveryStateRepository(db).get_by_conversation(tenant_id, conversation_id)
    if state is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery ainda não iniciado")
    return {"coverage_by_category": state.coverage_by_category, "overall_coverage": state.overall_coverage()}


@router.post("/understanding", response_model=ExecutiveUnderstandingDTO)
async def generate_understanding(
    conversation_id: str,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
    llm: LLMProvider = Depends(get_llm),
) -> ExecutiveUnderstandingDTO:
    """Disponível a qualquer momento da conversa, não só no fim (specs/phase-01/003)."""
    tenant_id, _ = tenant_user
    conv_repo = SqlAlchemyConversationRepository(db)
    conversation = conv_repo.get(tenant_id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    state = SqlAlchemyDiscoveryStateRepository(db).get_by_conversation(tenant_id, conversation_id)
    if state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discovery ainda não iniciado")

    understanding = await generate_executive_understanding(
        llm, state=state, conversation_id=conversation_id, tenant_id=tenant_id
    )

    version = db.query(ExecutiveUnderstandingModel).filter_by(conversation_id=conversation_id).count() + 1
    understanding.version = version
    model = ExecutiveUnderstandingModel(
        id=understanding.id, conversation_id=conversation_id, tenant_id=tenant_id,
        summary=understanding.summary, diagnosis=understanding.diagnosis,
        missing_information=understanding.missing_information, risks=understanding.risks,
        assumptions=understanding.assumptions, next_steps=understanding.next_steps,
        complexity=understanding.complexity, human_review_notice=understanding.human_review_notice,
        version=version,
    )
    db.add(model)
    db.commit()

    return ExecutiveUnderstandingDTO(**understanding.__dict__)


@router.post("/artifacts", response_model=list[ArtifactDTO])
async def generate_conversation_artifacts(
    conversation_id: str,
    payload: ArtifactGenerationRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
    llm: LLMProvider = Depends(get_llm),
) -> list[ArtifactDTO]:
    """Geração assíncrona sob demanda; falha isolada não bloqueia o lote (specs/phase-06/002)."""
    tenant_id, _ = tenant_user
    conv_repo = SqlAlchemyConversationRepository(db)
    conversation = conv_repo.get(tenant_id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    state = SqlAlchemyDiscoveryStateRepository(db).get_by_conversation(tenant_id, conversation_id)
    if state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discovery ainda não iniciado")

    understanding = await generate_executive_understanding(
        llm, state=state, conversation_id=conversation_id, tenant_id=tenant_id
    )
    artifacts = generate_artifacts(conversation=conversation, understanding=understanding, kinds=payload.kinds)

    dtos = []
    for artifact in artifacts:
        model = ArtifactORM(
            id=artifact.id, conversation_id=conversation_id, tenant_id=tenant_id,
            kind=artifact.kind, title=artifact.title, content=artifact.content,
        )
        db.add(model)
        dtos.append(ArtifactDTO(id=artifact.id, kind=artifact.kind, title=artifact.title, content=artifact.content))
    db.commit()

    return dtos
