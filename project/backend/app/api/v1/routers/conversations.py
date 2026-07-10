"""Superfície de API — Conversas (specs/phase-01/003, specs/phase-07/002)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant_and_user, get_db, get_llm
from app.api.v1.schemas.conversation import (
    ConversationCreateRequest,
    ConversationDTO,
    MessageDTO,
    SendMessageRequest,
    SendMessageResponse,
)
from app.application.orchestrator import process_turn
from app.domain.entities import Conversation, DiscoveryState, Message, MessageRole
from app.domain.ports.llm_provider import LLMProvider
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SqlAlchemyConversationRepository,
    SqlAlchemyDiscoveryStateRepository,
    SqlAlchemyPortfolioRepository,
    SqlAlchemyPromptRepository,
    SqlAlchemyQuestionBankRepository,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _to_dto(conversation: Conversation) -> ConversationDTO:
    return ConversationDTO(
        id=conversation.id, service_type=conversation.service_type, briefing=conversation.briefing,
        title=conversation.title, created_at=conversation.created_at,
        messages=[MessageDTO(id=m.id, role=m.role.value, content=m.content, created_at=m.created_at) for m in conversation.messages],
    )


@router.post("", response_model=ConversationDTO, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreateRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> ConversationDTO:
    """Formulário fixo de serviço é obrigatório para iniciar o motor (specs/phase-01/005)."""
    tenant_id, user_id = tenant_user
    conversation = Conversation(
        tenant_id=tenant_id, user_id=user_id, service_type=payload.service_type,
        briefing=payload.briefing, title=payload.title or payload.service_type,
    )
    repo = SqlAlchemyConversationRepository(db)
    repo.add(conversation)

    state_repo = SqlAlchemyDiscoveryStateRepository(db)
    state_repo.save(DiscoveryState(conversation_id=conversation.id, tenant_id=tenant_id))

    return _to_dto(conversation)


@router.get("", response_model=list[ConversationDTO])
def list_conversations(
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> list[ConversationDTO]:
    tenant_id, _ = tenant_user
    repo = SqlAlchemyConversationRepository(db)
    return [_to_dto(c) for c in repo.list_for_tenant(tenant_id)]


@router.get("/{conversation_id}", response_model=ConversationDTO)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> ConversationDTO:
    tenant_id, _ = tenant_user
    repo = SqlAlchemyConversationRepository(db)
    conversation = repo.get(tenant_id, conversation_id)
    if conversation is None:
        # Recurso de outro tenant nunca vaza existência (specs/phase-07/004).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    return _to_dto(conversation)


@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
    llm: LLMProvider = Depends(get_llm),
) -> SendMessageResponse:
    tenant_id, _ = tenant_user
    conv_repo = SqlAlchemyConversationRepository(db)
    conversation = conv_repo.get(tenant_id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    state_repo = SqlAlchemyDiscoveryStateRepository(db)
    state = state_repo.get_by_conversation(tenant_id, conversation_id)
    if state is None:
        state = DiscoveryState(conversation_id=conversation_id, tenant_id=tenant_id)

    portfolio = SqlAlchemyPortfolioRepository(db).list_for_tenant(tenant_id)
    reference_questions = SqlAlchemyQuestionBankRepository(db).list_by_domain(state.primary_category or conversation.service_type)
    prompt = SqlAlchemyPromptRepository(db).get_active(tenant_id)

    user_msg = Message(role=MessageRole.USER, content=payload.content)
    conversation.messages.append(user_msg)

    assistant_text = await process_turn(
        llm=llm, conversation=conversation, state=state, prompt=prompt,
        portfolio=portfolio, reference_questions=reference_questions, user_message=payload.content,
    )
    assistant_msg = Message(role=MessageRole.ASSISTANT, content=assistant_text)
    conversation.messages.append(assistant_msg)

    conv_repo.save(conversation)
    state_repo.save(state)

    return SendMessageResponse(
        assistant_message=MessageDTO(
            id=assistant_msg.id, role=assistant_msg.role.value, content=assistant_msg.content,
            created_at=assistant_msg.created_at,
        ),
        coverage_by_category=state.coverage_by_category,
        overall_coverage=state.overall_coverage(),
    )
