from __future__ import annotations

import unittest
from unittest.mock import patch

from src.adapters import OpenAILLMAdapter, create_llm_provider, load_opportunity, load_portfolio
from src.domain import Opportunity
from src.services import generate_discovery_roteiro


class BrokenLLMProvider:
    def refine(self, roteiro):
        raise RuntimeError("primary provider failed")


class MarkerLLMProvider:
    def refine(self, roteiro):
        roteiro.assumptions.append("Fallback LLM aplicado.")
        return roteiro


class FallbackLLMProvider:
    def __init__(self) -> None:
        self.primary = BrokenLLMProvider()
        self.fallback = MarkerLLMProvider()

    def refine(self, roteiro):
        try:
            return self.primary.refine(roteiro)
        except RuntimeError:
            return self.fallback.refine(roteiro)


class DiscoveryRoteiroTests(unittest.TestCase):
    def setUp(self) -> None:
        self.portfolio = load_portfolio("data/portfolio/reference_portfolio.json")

    def test_generates_backup_roteiro_with_portfolio_match(self) -> None:
        opportunity = load_opportunity("data/examples/backup_opportunity.json")

        roteiro = generate_discovery_roteiro(opportunity, self.portfolio)

        self.assertEqual(roteiro.classification, "backup")
        self.assertEqual(roteiro.confidence, "alta")
        self.assertTrue(any("Backup e Recuperacao" in item for item in roteiro.portfolio_matches))
        self.assertGreaterEqual(len(roteiro.priority_questions), 8)

    def test_flags_missing_information(self) -> None:
        opportunity = Opportunity(description="Preciso de apoio para seguranca.")

        roteiro = generate_discovery_roteiro(opportunity, self.portfolio)

        self.assertIn("Tipo de solucao", roteiro.missing_information)
        self.assertIn("Cliente ou segmento", roteiro.missing_information)
        self.assertIn("Objetivo da demanda", roteiro.missing_information)
        self.assertIn("Escopo inicial", roteiro.missing_information)

    def test_includes_required_question_categories(self) -> None:
        opportunity = load_opportunity("data/examples/cloud_opportunity.json")

        roteiro = generate_discovery_roteiro(opportunity, self.portfolio)
        categories = {question.category for question in roteiro.priority_questions}

        self.assertIn("Contexto de negocio", categories)
        self.assertIn("Ambiente atual", categories)
        self.assertIn("Escopo tecnico", categories)
        self.assertIn("Riscos e validacoes", categories)

    def test_unknown_category_requires_specialist_validation(self) -> None:
        opportunity = Opportunity(
            description="Cliente quer solucao de telefonia e atendimento por voz.",
            solution_type="telefonia",
            customer_segment="servicos",
            objective="melhorar atendimento",
            initial_scope="central telefonica",
        )

        roteiro = generate_discovery_roteiro(opportunity, self.portfolio)

        self.assertEqual(roteiro.classification, "validacao necessaria")
        self.assertIn(
            "Nenhuma oferta aderente encontrada no portfolio informado; validar com especialista.",
            roteiro.portfolio_matches,
        )
        self.assertTrue(any("portfolio" in risk for risk in roteiro.risks))

    def test_markdown_output_contains_core_sections(self) -> None:
        opportunity = load_opportunity("data/examples/soc_opportunity.json")

        roteiro = generate_discovery_roteiro(opportunity, self.portfolio)
        markdown = roteiro.to_markdown()

        self.assertEqual(roteiro.classification, "soc")
        self.assertIn("# Roteiro de Levantamento", markdown)
        self.assertIn("## Perguntas Prioritarias", markdown)
        self.assertIn("## Informacoes Faltantes", markdown)
        self.assertIn("## Riscos e Validacoes", markdown)

    def test_uses_fallback_llm_provider_when_primary_fails(self) -> None:
        opportunity = load_opportunity("data/examples/soc_opportunity.json")

        roteiro = generate_discovery_roteiro(
            opportunity,
            self.portfolio,
            llm_provider=FallbackLLMProvider(),
        )

        self.assertIn("Fallback LLM aplicado.", roteiro.assumptions)

    def test_factory_uses_openai_fallback_when_openrouter_key_is_missing(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "LLM_PROVIDER": "openrouter",
                "LLM_FALLBACK_PROVIDER": "openai",
                "OPENAI_API_KEY": "test-key",
            },
            clear=True,
        ):
            provider = create_llm_provider()

        self.assertIsInstance(provider, OpenAILLMAdapter)


if __name__ == "__main__":
    unittest.main()
