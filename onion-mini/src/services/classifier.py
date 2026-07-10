from __future__ import annotations

from src.domain import Opportunity, Portfolio


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "infraestrutura": ("infraestrutura", "servidor", "servidores", "storage", "datacenter"),
    "cloud": ("cloud", "nuvem", "aws", "azure", "gcp", "iaas", "paas", "migracao"),
    "cyberseguranca": ("seguranca", "cyber", "firewall", "edr", "vulnerabilidade"),
    "backup": ("backup", "recuperacao", "restore", "rpo", "rto", "continuidade"),
    "observabilidade": ("observabilidade", "monitoramento", "logs", "metricas", "apm"),
    "redes": ("rede", "redes", "wan", "lan", "sd-wan", "switch", "roteador"),
    "cops": ("cops", "cloud ops", "operacao cloud", "sustentacao cloud"),
    "soc": ("soc", "siem", "incidente", "monitoramento de seguranca"),
    "sustentacao": ("sustentacao", "servicos gerenciados", "suporte", "operacao"),
}


def classify_opportunity(opportunity: Opportunity, portfolio: Portfolio) -> tuple[str, str]:
    text = opportunity.combined_text()
    scores: dict[str, int] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if opportunity.solution_type.strip().lower() == category:
            score += 3
        if score and category in portfolio.categories:
            score += 1
        if score:
            scores[category] = score

    if not scores:
        return "validacao necessaria", "baixa"

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_category, top_score = ordered[0]
    if top_score <= 1:
        return top_category, "baixa"
    if len(ordered) > 1 and ordered[1][1] == top_score:
        return f"{top_category} + validacao de categoria secundaria", "media"
    return top_category, "alta"
