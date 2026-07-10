"""Agente Especialista do Serviço (specs/phase-04/004): monta plano de temas, nunca pergunta literal aqui."""
from __future__ import annotations

from app.domain.entities import ReferenceQuestion
from app.domain.ports.llm_provider import LLMProvider


async def build_discovery_plan(
    llm: LLMProvider, *, asked_themes: list[str], reference_questions: list[ReferenceQuestion]
) -> list[str]:
    result = await llm.generate_structured(
        system_prompt=(
            "Monte o plano de temas a cobrir usando o Question Bank como referência (nunca literal). "
            "As categorias válidas são: contexto_negocio, ambiente_atual, escopo_tecnico, "
            "operacao_sustentacao, seguranca_conformidade, volumetria_capacidade, criticidade, "
            "governanca, premissas_exclusoes, riscos_validacoes.\n"
            "Responda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
            'exatamente neste formato: {"themes_to_cover": ["string"]}'
        ),
        user_payload={
            "asked_themes": asked_themes,
            "reference_question_count": len(reference_questions),
        },
        response_schema_name="discovery_plan",
    )
    return result.content.get("themes_to_cover", [])
