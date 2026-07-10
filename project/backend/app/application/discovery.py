"""Discovery Conversacional (specs/phase-05): DiscoveryState, seleção adaptativa, dedup."""
from __future__ import annotations

from difflib import SequenceMatcher

from app.domain.entities import DiscoveryCategory, DiscoveryState, Fact

# Criticidade fixa por categoria (score de prioridade, specs/phase-05/002).
_CATEGORY_CRITICALITY: dict[str, float] = {
    "contexto_negocio": 1.0,
    "escopo_tecnico": 0.95,
    "ambiente_atual": 0.9,
    "criticidade": 0.85,
    "seguranca_conformidade": 0.85,
    "riscos_validacoes": 0.8,
    "volumetria_capacidade": 0.7,
    "operacao_sustentacao": 0.7,
    "governanca": 0.6,
    "premissas_exclusoes": 0.6,
}

DEDUP_SIMILARITY_THRESHOLD = 0.82


FACT_COVERAGE_INCREMENT = 1.0
"""MVP: uma resposta grounded já cobre a categoria (breadth-first). Aprofundamento adaptativo
(2+ perguntas por categoria sob sinal forte, specs/phase-05/002) fica para depois — incrementos
parciais fariam o Gerador de Perguntas repetir a pergunta literal na 2ª rodada e o Validador
rejeitá-la para sempre (bug encontrado via Dogfood Mini). Ver débito em
technical-context-lite.md §4."""


def register_fact(state: DiscoveryState, fact: Fact) -> None:
    state.facts.append(fact)
    category = fact.category.value if isinstance(fact.category, DiscoveryCategory) else fact.category
    current = state.coverage_by_category.get(category, 0.0)
    state.coverage_by_category[category] = min(1.0, round(current + FACT_COVERAGE_INCREMENT, 2))


def select_next_category(state: DiscoveryState) -> str | None:
    """Score = criticidade x (1 - cobertura). Determinístico em empates (ordem alfabética).

    Categorias nunca perguntadas (cobertura 0) sempre têm prioridade sobre categorias já
    parcialmente cobertas — garante cobertura em largura antes de aprofundar. Sem essa regra,
    uma categoria de alta criticidade parcialmente coberta poderia ser re-selecionada antes de
    categorias ainda não tocadas, gerando a MESMA pergunta de novo (rejeitada como duplicata
    pelo Validador) — bug encontrado via Dogfood Mini ao rodar o fluxo de verdade.
    """
    never_asked = [
        (category, _CATEGORY_CRITICALITY.get(category, 0.5))
        for category, coverage in state.coverage_by_category.items()
        if coverage == 0.0
    ]
    if never_asked:
        never_asked.sort(key=lambda item: (-item[1], item[0]))
        return never_asked[0][0]

    candidates = [
        (category, _CATEGORY_CRITICALITY.get(category, 0.5) * (1 - coverage))
        for category, coverage in state.coverage_by_category.items()
        if coverage < 1.0
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[1], item[0]))
    return candidates[0][0]


def is_duplicate_question(candidate_question: str, asked_themes: list[str]) -> bool:
    """Heurística de similaridade textual (sem embeddings — ver débito em technical-context-lite.md)."""
    for asked in asked_themes:
        ratio = SequenceMatcher(None, candidate_question.lower(), asked.lower()).ratio()
        if ratio >= DEDUP_SIMILARITY_THRESHOLD:
            return True
    return False
