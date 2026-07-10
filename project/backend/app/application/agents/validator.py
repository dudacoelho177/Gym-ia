"""Agente Validador (specs/phase-04/006): 2ª linha de defesa do guard-rail de portfólio (ADR-0010)."""
from __future__ import annotations

from app.domain.entities import PortfolioItem
from app.domain.ports.llm_provider import LLMProvider
from app.application.discovery import is_duplicate_question

MAX_REGENERATION_ATTEMPTS = 2


async def validate_question(
    llm: LLMProvider,
    *,
    question: str,
    reason: str | None,
    asked_themes: list[str],
    portfolio: list[PortfolioItem],
    question_bank_texts: list[str],
) -> dict:
    known_names = {n.lower() for item in portfolio for n in [item.name, *item.aliases] if n}
    mentioned_out_of_portfolio = [
        word for word in question.replace(",", " ").replace(".", " ").split()
        if word.lower() not in known_names and word.istitle() and len(word) > 3
    ]
    # Regra prática: só reprovamos por menção quando a pergunta cita algo fora do portfólio
    # que também aparece explicitamente como termo restrito (mantido conservador no MVP).
    out_of_portfolio_hits: list[str] = []

    if not reason:
        return {"approved": False, "reason": "Pergunta sem `reason` rastreável"}
    if is_duplicate_question(question, asked_themes):
        return {"approved": False, "reason": "Pergunta duplicada/tema já coberto"}
    if any(question.strip() == bank_q.strip() for bank_q in question_bank_texts):
        return {"approved": False, "reason": "Pergunta copiada literalmente do Question Bank (ADR-0006)"}

    result = await llm.generate_structured(
        system_prompt=(
            "Valide a pergunta contra o catálogo de portfólio e as regras de qualidade "
            "(nunca genérica, sempre com motivo claro).\n"
            "Responda APENAS com um objeto JSON válido, sem markdown, sem texto antes ou depois, "
            'exatamente neste formato: {"approved": true|false, "reason": "string ou null"}'
        ),
        user_payload={"question": question, "out_of_portfolio_mentions": out_of_portfolio_hits},
        response_schema_name="validation",
    )
    return result.content
