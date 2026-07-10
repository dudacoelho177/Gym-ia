"""Agente Gerador de Perguntas (specs/phase-04/005): uma pergunta principal por vez, com `reason`,
mais diálogo real com o usuário e três sugestões de pergunta ao final (sempre)."""
from __future__ import annotations

from app.domain.ports.llm_provider import LLMProvider


async def generate_question(llm: LLMProvider, *, category: str, layered_system_prompt: str | None = None) -> dict:
    """`layered_system_prompt` é a composição do Prompt Engine (Pré-Prompt -> Editável -> Briefing
    -> Contexto -> Histórico, ADR-0005) — é o que efetivamente rege a pergunta gerada ao usuário."""
    base_instruction = layered_system_prompt or (
        "Dialogue com o usuário (responda ao que ele disse, se aplicável) e depois redija a "
        "próxima pergunta principal (uma só), ancorada no briefing/serviço, com motivo (reason), "
        "mais três sugestões de pergunta relacionadas."
    )
    schema_instruction = (
        "\n\nResponda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
        "exatamente neste formato: {"
        '"dialogue_response": "string ou null (resposta direta ao usuário, se ele perguntou/comentou algo; '
        'null se não houver nada a responder)", '
        '"question": "string (a pergunta principal)", '
        '"category": "string", '
        '"reason": "string", '
        '"suggested_questions": ["string", "string", "string"] (exatamente três sugestões de pergunta '
        "relacionadas, distintas da pergunta principal, para o usuário escolher)"
        "}"
    )
    result = await llm.generate_structured(
        system_prompt=base_instruction + schema_instruction,
        user_payload={"category": category},
        response_schema_name="next_question",
    )
    return result.content
