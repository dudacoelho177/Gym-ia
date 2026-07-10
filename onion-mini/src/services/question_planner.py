from __future__ import annotations

from src.domain import DiscoveryQuestion, Opportunity


PRIORITY_CATEGORIES = (
    "Contexto de negocio",
    "Ambiente atual",
    "Escopo tecnico",
    "Operacao e sustentacao",
    "Seguranca e conformidade",
    "Volumetria e capacidade",
    "Premissas e exclusoes",
    "Riscos e validacoes",
)

COMPLEMENTARY_CATEGORIES = (
    "Criticidade",
    "Governanca",
    "Compras e decisao",
)


BASE_PRIORITY_QUESTIONS = {
    "Contexto de negocio": "Qual problema o cliente deseja resolver e qual resultado espera alcancar?",
    "Ambiente atual": "Quais tecnologias, fornecedores, versoes, localidades e dependencias existem hoje?",
    "Escopo tecnico": "Quais componentes, integracoes e limites devem estar dentro do escopo inicial?",
    "Operacao e sustentacao": "Quem opera o ambiente hoje e quais horarios, SLAs, processos e ferramentas sao esperados?",
    "Seguranca e conformidade": "Existem requisitos regulatorios, politicas internas, segregacao de acesso ou restricoes de dados?",
    "Volumetria e capacidade": "Quais volumetrias de usuarios, ativos, servidores, chamados, eventos ou workloads devem ser consideradas?",
    "Premissas e exclusoes": "O que deve ficar explicitamente dentro e fora do escopo da proposta?",
    "Riscos e validacoes": "Quais pontos dependem de fabricante, inventario, acesso, janela de mudanca ou validacao tecnica?",
}

BASE_COMPLEMENTARY_QUESTIONS = {
    "Criticidade": "Quais servicos sao criticos e quais impactos ocorrem em caso de indisponibilidade?",
    "Governanca": "Quais ritos, relatorios, indicadores, comites ou processos de acompanhamento sao esperados?",
    "Compras e decisao": "Quem participa da decisao e ha prazo comercial, orcamento ou evento motivador?",
}

CATEGORY_SPECIFIC_QUESTIONS = {
    "infraestrutura": "Ha inventario de servidores, storage, virtualizacao e dependencias fisicas ou logicas?",
    "cloud": "Quais ambientes devem migrar ou operar em cloud e quais restricoes de arquitetura, custo ou seguranca existem?",
    "cyberseguranca": "Quais controles de seguranca existem hoje e quais riscos, incidentes ou requisitos motivam a demanda?",
    "backup": "Quais RPO, RTO, politicas de retencao, janelas de backup e requisitos de restore devem ser atendidos?",
    "observabilidade": "Quais aplicacoes, logs, metricas, eventos e dashboards precisam ser monitorados?",
    "redes": "Quais sites, links, equipamentos, topologias e requisitos de disponibilidade compoem a rede?",
    "cops": "Quais responsabilidades de operacao cloud ficam com cliente, fornecedor e parceiros?",
    "soc": "Quais fontes de log, casos de uso, playbooks e SLAs de resposta devem ser considerados?",
    "sustentacao": "Quais servicos, filas, SLAs, horarios e niveis de atendimento compoem a sustentacao?",
}


def plan_questions(opportunity: Opportunity, classification: str) -> tuple[
    list[DiscoveryQuestion], list[DiscoveryQuestion]
]:
    priority = [
        DiscoveryQuestion(category=category, text=text, priority="prioritaria")
        for category, text in BASE_PRIORITY_QUESTIONS.items()
    ]
    complementary = [
        DiscoveryQuestion(category=category, text=text, priority="complementar")
        for category, text in BASE_COMPLEMENTARY_QUESTIONS.items()
    ]

    category_key = classification.split(" + ")[0]
    specific_question = CATEGORY_SPECIFIC_QUESTIONS.get(category_key)
    if specific_question:
        priority.insert(
            3,
            DiscoveryQuestion(
                category=f"Especifico de {category_key}",
                text=specific_question,
                priority="prioritaria",
                audience=opportunity.target_audience,
            ),
        )

    return priority, complementary
