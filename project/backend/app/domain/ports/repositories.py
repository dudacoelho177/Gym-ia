"""Ports de repositório (ADR-0002) — adapters concretos (SQLAlchemy) implementam estas interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import (
    Conversation,
    DiscoveryState,
    Prompt,
    PortfolioItem,
    ReferenceQuestion,
)


class ConversationRepository(ABC):
    @abstractmethod
    def add(self, conversation: Conversation) -> None: ...

    @abstractmethod
    def get(self, tenant_id: str, conversation_id: str) -> Conversation | None: ...

    @abstractmethod
    def list_for_tenant(self, tenant_id: str) -> list[Conversation]: ...

    @abstractmethod
    def save(self, conversation: Conversation) -> None: ...


class DiscoveryStateRepository(ABC):
    @abstractmethod
    def get_by_conversation(self, tenant_id: str, conversation_id: str) -> DiscoveryState | None: ...

    @abstractmethod
    def save(self, state: DiscoveryState) -> None: ...


class PortfolioRepository(ABC):
    @abstractmethod
    def list_for_tenant(self, tenant_id: str) -> list[PortfolioItem]: ...

    @abstractmethod
    def add(self, item: PortfolioItem) -> None: ...

    @abstractmethod
    def find_mentions(self, tenant_id: str, text: str) -> list[str]:
        """Retorna nomes/aliases do catálogo mencionados em `text` (guard-rail, ADR-0010)."""
        ...


class QuestionBankRepository(ABC):
    @abstractmethod
    def list_by_domain(self, domain: str) -> list[ReferenceQuestion]: ...

    @abstractmethod
    def add(self, question: ReferenceQuestion) -> None: ...


class PromptRepository(ABC):
    @abstractmethod
    def get_active(self, tenant_id: str) -> Prompt | None: ...

    @abstractmethod
    def save(self, prompt: Prompt) -> None: ...
