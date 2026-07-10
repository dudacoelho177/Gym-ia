"""Orquestrador (specs/phase-04/001): coordena os 7 agentes condicionalmente, por turno, idempotente."""
from __future__ import annotations

import logging

from app.domain.entities import Conversation, DiscoveryState, PortfolioItem, Prompt, ReferenceQuestion
from app.domain.ports.llm_provider import LLMProvider
from app.application import discovery
from app.application import prompt_engine
from app.application.agents import classifier, interpreter, question_generator, validator

logger = logging.getLogger("gym_ai.orchestrator")


async def process_turn(
    *,
    llm: LLMProvider,
    conversation: Conversation,
    state: DiscoveryState,
    prompt: Prompt | None,
    portfolio: list[PortfolioItem],
    reference_questions: list[ReferenceQuestion],
    user_message: str,
) -> str:
    # 1) Interpretador — extrai fatos, nunca inventa. A resposta pertence à categoria perguntada
    # no turno anterior (`pending_category`); no 1º turno ainda não há pergunta pendente.
    facts = await interpreter.interpret(
        llm, briefing=conversation.briefing, message=user_message, answered_category=state.pending_category
    )
    for fact in facts:
        discovery.register_fact(state, fact)

    # 2) Classificador — só roda se ainda não classificado (idempotente).
    if state.primary_category is None:
        classification = await classifier.classify(
            llm, service_type=conversation.service_type, briefing=conversation.briefing
        )
        state.primary_category = classification.get("primary_category")
        state.secondary_categories = classification.get("secondary_categories", [])
        state.classification_confidence = classification.get("confidence", 0.0)

    # 3) Especialista do Serviço — DESLIGADO do turno por ora: seu plano de temas não é consumido
    # pela seleção adaptativa (puramente Python, item 4) e cada chamada real ao provider soma
    # ~5-15s de latência sem alterar o resultado. Ver débito em technical-context-lite.md §4.

    # 4) Seleção adaptativa (specs/phase-05/002) — decide a categoria a perguntar agora.
    category = discovery.select_next_category(state)
    if category is None:
        logger.info("discovery_complete", extra={"conversation_id": conversation.id, "tenant_id": conversation.tenant_id})
        return (
            "Cobertura completa das categorias de discovery. Você já pode gerar o Relatório de "
            "Entendimento Executivo — lembre-se de revisar tudo com um profissional de pré-vendas."
        )

    # 5) Gerador de Perguntas — uma pergunta por vez, com `reason`, sob o prompt em camadas
    # (Pré-Prompt -> Editável -> Briefing -> Contexto -> Histórico, ADR-0005/specs/phase-03).
    layered_payload = prompt_engine.compose_prompt_payload(
        editable_prompt=prompt, conversation=conversation, discovery_state=state, new_message=user_message
    )
    layered_system_prompt = prompt_engine.build_system_prompt(layered_payload)

    question_bank_texts = [q.text for q in reference_questions]
    attempts = 0
    approved = False
    question_data: dict = {}
    while attempts < validator.MAX_REGENERATION_ATTEMPTS and not approved:
        question_data = await question_generator.generate_question(
            llm, category=category, layered_system_prompt=layered_system_prompt
        )
        # 6) Validador — 2ª linha do guard-rail de portfólio + qualidade da pergunta.
        result = await validator.validate_question(
            llm,
            question=question_data.get("question", ""),
            reason=question_data.get("reason"),
            asked_themes=state.asked_themes,
            portfolio=portfolio,
            question_bank_texts=question_bank_texts,
        )
        approved = result.get("approved", False)
        attempts += 1

    if not approved:
        logger.info("question_rejected_after_retries", extra={"conversation_id": conversation.id})
        return "Não foi possível formular a próxima pergunta com segurança — sinalizando para revisão humana."

    question_text = question_data["question"]
    state.asked_themes.append(question_text)
    state.pending_category = category
    return _compose_reply(question_data, question_text)


def _compose_reply(question_data: dict, question_text: str) -> str:
    """Diálogo (se houver) + pergunta principal + três sugestões de pergunta (sempre, ADR-0005)."""
    parts = []
    dialogue_response = question_data.get("dialogue_response")
    if dialogue_response:
        parts.append(dialogue_response)
    parts.append(question_text)

    suggestions = [s for s in question_data.get("suggested_questions") or [] if s][:3]
    if suggestions:
        parts.append("Outras perguntas que você também pode explorar:\n" + "\n".join(f"- {s}" for s in suggestions))

    return "\n\n".join(parts)
