"""Entidades e agregados de domínio (specs/phase-07/001). Sem dependência de FastAPI/SQLAlchemy/LLM SDK."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def new_id() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DiscoveryCategory(str, Enum):
    """As 10 categorias fixas de discovery (business-context-lite.md §6)."""

    CONTEXTO_NEGOCIO = "contexto_negocio"
    AMBIENTE_ATUAL = "ambiente_atual"
    ESCOPO_TECNICO = "escopo_tecnico"
    OPERACAO_SUSTENTACAO = "operacao_sustentacao"
    SEGURANCA_CONFORMIDADE = "seguranca_conformidade"
    VOLUMETRIA_CAPACIDADE = "volumetria_capacidade"
    CRITICIDADE = "criticidade"
    GOVERNANCA = "governanca"
    PREMISSAS_EXCLUSOES = "premissas_exclusoes"
    RISCOS_VALIDACOES = "riscos_validacoes"


@dataclass
class Tenant:
    id: str = field(default_factory=new_id)
    name: str = ""
    slug: str = ""
    created_at: datetime = field(default_factory=now)


@dataclass
class User:
    id: str = field(default_factory=new_id)
    tenant_id: str = ""
    email: str = ""
    role: str = "user"  # "user" | "admin"
    created_at: datetime = field(default_factory=now)


@dataclass
class Message:
    id: str = field(default_factory=new_id)
    role: MessageRole = MessageRole.USER
    content: str = ""
    created_at: datetime = field(default_factory=now)


@dataclass
class Conversation:
    id: str = field(default_factory=new_id)
    tenant_id: str = ""
    user_id: str = ""
    service_type: str = ""
    briefing: str = ""
    title: str = ""
    messages: list[Message] = field(default_factory=list)
    is_deleted: bool = False
    created_at: datetime = field(default_factory=now)


@dataclass
class Fact:
    key: str
    value: str
    category: DiscoveryCategory
    source: str  # "explicit" | "inferred"
    confidence: float = 1.0


@dataclass
class DiscoveryState:
    id: str = field(default_factory=new_id)
    conversation_id: str = ""
    tenant_id: str = ""
    facts: list[Fact] = field(default_factory=list)
    asked_themes: list[str] = field(default_factory=list)
    coverage_by_category: dict[str, float] = field(
        default_factory=lambda: {c.value: 0.0 for c in DiscoveryCategory}
    )
    primary_category: str | None = None
    secondary_categories: list[str] = field(default_factory=list)
    classification_confidence: float = 0.0
    pending_category: str | None = None
    updated_at: datetime = field(default_factory=now)

    def overall_coverage(self) -> float:
        values = list(self.coverage_by_category.values())
        return round(sum(values) / len(values), 2) if values else 0.0


@dataclass
class PortfolioItem:
    id: str = field(default_factory=new_id)
    tenant_id: str | None = None  # None = catálogo global
    category: str = ""
    name: str = ""
    description: str = ""
    aliases: list[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class ReferenceQuestion:
    id: str = field(default_factory=new_id)
    domain: str = ""
    category: DiscoveryCategory = DiscoveryCategory.CONTEXTO_NEGOCIO
    text: str = ""
    is_priority: bool = True


@dataclass
class PromptVersion:
    id: str = field(default_factory=new_id)
    prompt_id: str = ""
    content: str = ""
    version_number: int = 1
    created_at: datetime = field(default_factory=now)


@dataclass
class Prompt:
    id: str = field(default_factory=new_id)
    tenant_id: str = ""
    name: str = ""
    is_active: bool = True
    active_version_id: str | None = None
    versions: list[PromptVersion] = field(default_factory=list)


@dataclass
class ExecutiveUnderstanding:
    id: str = field(default_factory=new_id)
    conversation_id: str = ""
    tenant_id: str = ""
    summary: str = ""
    diagnosis: str = ""
    missing_information: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    complexity: str = "media"
    human_review_notice: str = (
        "Saída gerada por IA — apoio à decisão. Requer revisão de um profissional de pré-vendas antes do uso com clientes."
    )
    version: int = 1
    created_at: datetime = field(default_factory=now)


@dataclass
class Artifact:
    id: str = field(default_factory=new_id)
    conversation_id: str = ""
    tenant_id: str = ""
    kind: str = ""  # "spec" | "adr" | "prd" | "user_story"
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=now)
