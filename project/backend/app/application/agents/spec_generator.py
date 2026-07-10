"""Agente Gerador de Especificações (specs/phase-04/008): dogfooding do Spec-as-Code (ADR-0001)."""
from __future__ import annotations

from app.domain.entities import Artifact, Conversation, ExecutiveUnderstanding

_SPEC_TEMPLATE = """\
# Spec (gerada) — {title}

## Objetivo
{summary}

## Problema
{diagnosis}

## Contexto
Serviço: {service_type}. Briefing original: {briefing}

## Regras de negócio
- Revisão humana obrigatória antes de uso com o cliente.

## Critérios de aceite
{criteria}

## Não objetivos
- Substituir julgamento humano da pré-vendas.

## Aviso
{human_review_notice}
"""

_ADR_TEMPLATE = """\
# ADR (gerada) — {title}

## Contexto
{diagnosis}

## Problema
Lacunas identificadas: {gaps}

## Decisão
A definir por especialista humano a partir deste levantamento.

## Consequências
{risks}
"""


def generate_artifacts(
    *, conversation: Conversation, understanding: ExecutiveUnderstanding, kinds: list[str]
) -> list[Artifact]:
    artifacts: list[Artifact] = []
    title = conversation.title or conversation.service_type or "Oportunidade"

    if "spec" in kinds:
        content = _SPEC_TEMPLATE.format(
            title=title,
            summary=understanding.summary,
            diagnosis=understanding.diagnosis,
            service_type=conversation.service_type,
            briefing=conversation.briefing,
            criteria="\n".join(f"- {step}" for step in understanding.next_steps) or "- A definir",
            human_review_notice=understanding.human_review_notice,
        )
        artifacts.append(
            Artifact(
                conversation_id=conversation.id, tenant_id=conversation.tenant_id,
                kind="spec", title=f"Spec — {title}", content=content,
            )
        )

    if "adr" in kinds:
        content = _ADR_TEMPLATE.format(
            title=title,
            diagnosis=understanding.diagnosis,
            gaps=", ".join(understanding.missing_information) or "nenhuma identificada",
            risks="\n".join(f"- {r}" for r in understanding.risks) or "- Nenhum risco registrado",
        )
        artifacts.append(
            Artifact(
                conversation_id=conversation.id, tenant_id=conversation.tenant_id,
                kind="adr", title=f"ADR — {title}", content=content,
            )
        )

    return artifacts
