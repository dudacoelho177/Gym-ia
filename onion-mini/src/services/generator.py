from __future__ import annotations

from src.adapters.factory import create_llm_provider
from src.domain import DiscoveryRoteiro, Opportunity, Portfolio
from src.domain.ports import LLMProvider
from src.services.classifier import classify_opportunity
from src.services.question_planner import plan_questions
from src.services.validator import enrich_with_validation


def generate_discovery_roteiro(
    opportunity: Opportunity,
    portfolio: Portfolio,
    llm_provider: LLMProvider | None = None,
) -> DiscoveryRoteiro:
    classification, confidence = classify_opportunity(opportunity, portfolio)
    priority_questions, complementary_questions = plan_questions(
        opportunity,
        classification,
    )
    roteiro = DiscoveryRoteiro(
        classification=classification,
        confidence=confidence,
        priority_questions=priority_questions,
        complementary_questions=complementary_questions,
    )
    enriched = enrich_with_validation(roteiro, opportunity, portfolio)
    provider = llm_provider or create_llm_provider()
    return provider.refine(enriched)
