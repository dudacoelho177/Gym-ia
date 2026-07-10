from __future__ import annotations

from src.domain import DiscoveryRoteiro, Opportunity, Portfolio


REQUIRED_FIELDS = {
    "description": "Descricao da oportunidade",
    "solution_type": "Tipo de solucao",
    "customer_segment": "Cliente ou segmento",
    "objective": "Objetivo da demanda",
    "initial_scope": "Escopo inicial",
}


def enrich_with_validation(
    roteiro: DiscoveryRoteiro,
    opportunity: Opportunity,
    portfolio: Portfolio,
) -> DiscoveryRoteiro:
    missing = [
        label
        for field_name, label in REQUIRED_FIELDS.items()
        if not getattr(opportunity, field_name).strip()
    ]
    roteiro.missing_information.extend(missing)

    matched_offers = portfolio.offers_for(roteiro.classification.split(" + ")[0])
    if matched_offers:
        roteiro.portfolio_matches.extend(
            f"{offer.name} ({offer.category})" for offer in matched_offers
        )
    else:
        roteiro.portfolio_matches.append(
            "Nenhuma oferta aderente encontrada no portfolio informado; validar com especialista."
        )
        roteiro.risks.append(
            "Risco de desalinhamento com o portfolio por ausencia de oferta correspondente."
        )

    if roteiro.confidence == "baixa":
        roteiro.risks.append(
            "Classificacao com baixa confianca; confirmar categoria antes de usar o roteiro com cliente."
        )

    roteiro.assumptions.append(
        "O roteiro e apoio a decisao e precisa de revisao de pre-vendas antes de uso externo."
    )
    roteiro.assumptions.append(
        "Perguntas foram geradas apenas a partir do briefing e do portfolio disponivel."
    )
    return roteiro
