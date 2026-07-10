"""Agente Classificador (specs/phase-04/003): domínio/serviço ancorado no portfólio."""
from __future__ import annotations

from app.domain.ports.llm_provider import LLMProvider


async def classify(llm: LLMProvider, *, service_type: str, briefing: str) -> dict:
    result = await llm.generate_structured(
        system_prompt=(
            "Classifique a oportunidade ancorado no portfólio e serviço selecionado.\n"
            "Responda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
            "exatamente neste formato:\n"
            '{"primary_category": "string", "secondary_categories": ["string"], '
            '"confidence": 0.0, "justification": "string"}'
        ),
        user_payload={"service_type": service_type, "briefing": briefing},
        response_schema_name="classifier",
    )
    return result.content
