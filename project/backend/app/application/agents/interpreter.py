"""Agente Interpretador (specs/phase-04/002): extrai fatos estruturados, nunca inventa."""
from __future__ import annotations

from app.domain.entities import DiscoveryCategory, Fact
from app.domain.ports.llm_provider import LLMProvider


async def interpret(
    llm: LLMProvider, *, briefing: str, message: str, answered_category: str | None = None
) -> list[Fact]:
    """`answered_category` é a categoria da última pergunta feita — a resposta pertence a ela
    (specs/phase-05/001: toda informação descoberta altera o estado da categoria correta)."""
    result = await llm.generate_structured(
        system_prompt=(
            "Extraia fatos explícitos do texto do usuário; o que faltar vira lacuna, nunca invente.\n"
            "Responda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
            "exatamente neste formato:\n"
            '{"facts": [{"key": "string", "value": "string", "source": "explicit"|"inferred", '
            '"confidence": 0.0}], "gaps": ["string"]}\n'
            "Se nenhum fato novo foi informado, responda com \"facts\": []."
        ),
        user_payload={"briefing": briefing, "message": message},
        response_schema_name="interpreter",
    )
    category = DiscoveryCategory(answered_category) if answered_category else DiscoveryCategory.CONTEXTO_NEGOCIO
    facts = []
    for raw in result.content.get("facts", []):
        facts.append(
            Fact(
                key=raw.get("key", "fact"),
                value=raw.get("value", ""),
                category=category,
                source=raw.get("source", "inferred"),
                confidence=raw.get("confidence", 0.5),
            )
        )
    return facts
