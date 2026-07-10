from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Opportunity:
    description: str
    solution_type: str = ""
    customer_segment: str = ""
    objective: str = ""
    initial_scope: str = ""
    target_audience: str = "pre-vendas"

    def combined_text(self) -> str:
        return " ".join(
            part
            for part in [
                self.description,
                self.solution_type,
                self.customer_segment,
                self.objective,
                self.initial_scope,
                self.target_audience,
            ]
            if part
        ).lower()


@dataclass(frozen=True)
class PortfolioOffer:
    name: str
    category: str
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class Portfolio:
    offers: tuple[PortfolioOffer, ...] = ()

    @property
    def categories(self) -> set[str]:
        return {offer.category for offer in self.offers}

    def offers_for(self, category: str) -> tuple[PortfolioOffer, ...]:
        return tuple(offer for offer in self.offers if offer.category == category)


@dataclass(frozen=True)
class DiscoveryQuestion:
    category: str
    text: str
    priority: str
    audience: str = "pre-vendas"


@dataclass
class DiscoveryRoteiro:
    classification: str
    confidence: str
    portfolio_matches: list[str] = field(default_factory=list)
    priority_questions: list[DiscoveryQuestion] = field(default_factory=list)
    complementary_questions: list[DiscoveryQuestion] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "confidence": self.confidence,
            "portfolio_matches": self.portfolio_matches,
            "priority_questions": [question.__dict__ for question in self.priority_questions],
            "complementary_questions": [
                question.__dict__ for question in self.complementary_questions
            ],
            "missing_information": self.missing_information,
            "assumptions": self.assumptions,
            "risks": self.risks,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Roteiro de Levantamento",
            "",
            f"**Classificacao:** {self.classification}",
            f"**Confianca:** {self.confidence}",
            "",
            "## Aderencia ao Portfolio",
        ]
        lines.extend(f"- {item}" for item in self.portfolio_matches)
        lines.extend(["", "## Perguntas Prioritarias"])
        lines.extend(
            f"- **{question.category}:** {question.text}"
            for question in self.priority_questions
        )
        lines.extend(["", "## Perguntas Complementares"])
        lines.extend(
            f"- **{question.category}:** {question.text}"
            for question in self.complementary_questions
        )
        lines.extend(["", "## Informacoes Faltantes"])
        lines.extend(f"- {item}" for item in self.missing_information)
        lines.extend(["", "## Premissas"])
        lines.extend(f"- {item}" for item in self.assumptions)
        lines.extend(["", "## Riscos e Validacoes"])
        lines.extend(f"- {item}" for item in self.risks)
        return "\n".join(lines).strip() + "\n"
