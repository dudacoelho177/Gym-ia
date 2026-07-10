from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import (
    Conversation,
    DiscoveryCategory,
    DiscoveryState,
    Fact,
    Message,
    MessageRole,
    Prompt,
    PromptVersion,
    PortfolioItem,
    ReferenceQuestion,
)
from app.domain.ports.repositories import (
    ConversationRepository,
    DiscoveryStateRepository,
    PortfolioRepository,
    PromptRepository,
    QuestionBankRepository,
)
from app.infrastructure.db.models import (
    ConversationModel,
    DiscoveryStateModel,
    MessageModel,
    PortfolioItemModel,
    PromptModel,
    PromptVersionModel,
    ReferenceQuestionModel,
)


class SqlAlchemyConversationRepository(ConversationRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, conversation: Conversation) -> None:
        model = ConversationModel(
            id=conversation.id,
            tenant_id=conversation.tenant_id,
            user_id=conversation.user_id,
            service_type=conversation.service_type,
            briefing=conversation.briefing,
            title=conversation.title,
        )
        self.db.add(model)
        self.db.commit()

    def get(self, tenant_id: str, conversation_id: str) -> Conversation | None:
        model = self.db.get(ConversationModel, conversation_id)
        if model is None or model.tenant_id != tenant_id or model.is_deleted:
            return None
        return _to_domain_conversation(model)

    def list_for_tenant(self, tenant_id: str) -> list[Conversation]:
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.tenant_id == tenant_id, ConversationModel.is_deleted.is_(False))
            .order_by(ConversationModel.created_at.desc())
        )
        return [_to_domain_conversation(m) for m in self.db.scalars(stmt)]

    def save(self, conversation: Conversation) -> None:
        model = self.db.get(ConversationModel, conversation.id)
        if model is None:
            raise ValueError(f"Conversation {conversation.id} não encontrada")
        model.title = conversation.title
        model.service_type = conversation.service_type
        model.briefing = conversation.briefing
        model.is_deleted = conversation.is_deleted
        existing_ids = {m.id for m in model.messages}
        for msg in conversation.messages:
            if msg.id not in existing_ids:
                model.messages.append(MessageModel(id=msg.id, role=msg.role.value, content=msg.content))
        self.db.commit()


def _to_domain_conversation(model: ConversationModel) -> Conversation:
    return Conversation(
        id=model.id,
        tenant_id=model.tenant_id,
        user_id=model.user_id,
        service_type=model.service_type,
        briefing=model.briefing,
        title=model.title,
        is_deleted=model.is_deleted,
        created_at=model.created_at,
        messages=[
            Message(id=m.id, role=MessageRole(m.role), content=m.content, created_at=m.created_at)
            for m in model.messages
        ],
    )


class SqlAlchemyDiscoveryStateRepository(DiscoveryStateRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_conversation(self, tenant_id: str, conversation_id: str) -> DiscoveryState | None:
        stmt = select(DiscoveryStateModel).where(
            DiscoveryStateModel.conversation_id == conversation_id,
            DiscoveryStateModel.tenant_id == tenant_id,
        )
        model = self.db.scalars(stmt).first()
        if model is None:
            return None
        return DiscoveryState(
            id=model.id,
            conversation_id=model.conversation_id,
            tenant_id=model.tenant_id,
            facts=[Fact(**f) for f in model.facts],
            asked_themes=list(model.asked_themes),
            coverage_by_category=dict(model.coverage_by_category),
            primary_category=model.primary_category,
            secondary_categories=list(model.secondary_categories),
            classification_confidence=model.classification_confidence,
            pending_category=model.pending_category,
            updated_at=model.updated_at,
        )

    def save(self, state: DiscoveryState) -> None:
        model = self.db.get(DiscoveryStateModel, state.id)
        facts_payload = [
            {
                "key": f.key,
                "value": f.value,
                "category": f.category.value if isinstance(f.category, DiscoveryCategory) else f.category,
                "source": f.source,
                "confidence": f.confidence,
            }
            for f in state.facts
        ]
        if model is None:
            model = DiscoveryStateModel(
                id=state.id,
                conversation_id=state.conversation_id,
                tenant_id=state.tenant_id,
                facts=facts_payload,
                asked_themes=state.asked_themes,
                coverage_by_category=state.coverage_by_category,
                primary_category=state.primary_category,
                secondary_categories=state.secondary_categories,
                classification_confidence=state.classification_confidence,
                pending_category=state.pending_category,
            )
            self.db.add(model)
        else:
            model.facts = facts_payload
            model.asked_themes = state.asked_themes
            model.coverage_by_category = state.coverage_by_category
            model.primary_category = state.primary_category
            model.secondary_categories = state.secondary_categories
            model.classification_confidence = state.classification_confidence
            model.pending_category = state.pending_category
        self.db.commit()


class SqlAlchemyPortfolioRepository(PortfolioRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_for_tenant(self, tenant_id: str) -> list[PortfolioItem]:
        stmt = select(PortfolioItemModel).where(
            (PortfolioItemModel.tenant_id == tenant_id) | (PortfolioItemModel.tenant_id.is_(None)),
            PortfolioItemModel.is_active.is_(True),
        )
        return [
            PortfolioItem(
                id=m.id, tenant_id=m.tenant_id, category=m.category, name=m.name,
                description=m.description, aliases=list(m.aliases), is_active=m.is_active,
            )
            for m in self.db.scalars(stmt)
        ]

    def add(self, item: PortfolioItem) -> None:
        model = PortfolioItemModel(
            id=item.id, tenant_id=item.tenant_id, category=item.category, name=item.name,
            description=item.description, aliases=item.aliases, is_active=item.is_active,
        )
        self.db.add(model)
        self.db.commit()

    def find_mentions(self, tenant_id: str, text: str) -> list[str]:
        text_lower = text.lower()
        found = []
        for item in self.list_for_tenant(tenant_id):
            names = [item.name, *item.aliases]
            if any(n.lower() in text_lower for n in names if n):
                found.append(item.name)
        return found


class SqlAlchemyQuestionBankRepository(QuestionBankRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_by_domain(self, domain: str) -> list[ReferenceQuestion]:
        stmt = select(ReferenceQuestionModel).where(ReferenceQuestionModel.domain == domain)
        return [
            ReferenceQuestion(
                id=m.id, domain=m.domain, category=DiscoveryCategory(m.category),
                text=m.text, is_priority=m.is_priority,
            )
            for m in self.db.scalars(stmt)
        ]

    def add(self, question: ReferenceQuestion) -> None:
        model = ReferenceQuestionModel(
            id=question.id, domain=question.domain, category=question.category.value,
            text=question.text, is_priority=question.is_priority,
        )
        self.db.add(model)
        self.db.commit()


class SqlAlchemyPromptRepository(PromptRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_active(self, tenant_id: str) -> Prompt | None:
        stmt = select(PromptModel).where(PromptModel.tenant_id == tenant_id, PromptModel.is_active.is_(True))
        model = self.db.scalars(stmt).first()
        if model is None:
            return None
        return Prompt(
            id=model.id, tenant_id=model.tenant_id, name=model.name, is_active=model.is_active,
            active_version_id=model.active_version_id,
            versions=[
                PromptVersion(id=v.id, prompt_id=v.prompt_id, content=v.content, version_number=v.version_number, created_at=v.created_at)
                for v in model.versions
            ],
        )

    def save(self, prompt: Prompt) -> None:
        model = self.db.get(PromptModel, prompt.id)
        if model is None:
            model = PromptModel(
                id=prompt.id, tenant_id=prompt.tenant_id, name=prompt.name,
                is_active=prompt.is_active, active_version_id=prompt.active_version_id,
            )
            self.db.add(model)
        existing_ids = {v.id for v in model.versions} if model.versions else set()
        for version in prompt.versions:
            if version.id not in existing_ids:
                model.versions.append(
                    PromptVersionModel(
                        id=version.id, prompt_id=prompt.id, content=version.content,
                        version_number=version.version_number,
                    )
                )
        model.active_version_id = prompt.active_version_id
        model.is_active = prompt.is_active
        self.db.commit()
