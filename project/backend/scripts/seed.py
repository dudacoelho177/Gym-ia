"""Seed do catálogo de Portfólio + Question Bank (specs/phase-02) — dados de exemplo, fictícios."""
from app.domain.entities import DiscoveryCategory, PortfolioItem, ReferenceQuestion
from app.infrastructure.db.session import SessionLocal, init_db
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SqlAlchemyPortfolioRepository,
    SqlAlchemyQuestionBankRepository,
)

PORTFOLIO_SEED = [
    ("Observabilidade", "Monitoramento e Observabilidade 360", ["APM", "monitoramento"]),
    ("Cybersegurança", "SOC Gerenciado", ["SOC", "security operations center"]),
    ("Backup", "Backup e Disaster Recovery", ["DR", "recuperação de desastres"]),
    ("Cloud", "Migração e Gestão Multicloud", ["cloud", "migração cloud"]),
    ("Infraestrutura", "Sustentação de Infraestrutura (COPS)", ["COPS", "sustentação"]),
    ("Redes", "Gestão de Redes e Conectividade", ["redes", "conectividade"]),
]

QUESTION_BANK_SEED = [
    ("infraestrutura", DiscoveryCategory.AMBIENTE_ATUAL, "Como está estruturado o ambiente hoje?"),
    ("infraestrutura", DiscoveryCategory.CRITICIDADE, "Qual o SLA exigido pela operação?"),
    ("cybersegurança", DiscoveryCategory.SEGURANCA_CONFORMIDADE, "Existe alguma certificação de compliance vigente?"),
    ("backup", DiscoveryCategory.RISCOS_VALIDACOES, "Qual o RPO/RTO esperado para o ambiente?"),
]


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        portfolio_repo = SqlAlchemyPortfolioRepository(db)
        if not portfolio_repo.list_for_tenant("__global__"):
            for category, name, aliases in PORTFOLIO_SEED:
                portfolio_repo.add(PortfolioItem(tenant_id=None, category=category, name=name, aliases=aliases))

        question_repo = SqlAlchemyQuestionBankRepository(db)
        for domain, category, text in QUESTION_BANK_SEED:
            if not question_repo.list_by_domain(domain):
                question_repo.add(ReferenceQuestion(domain=domain, category=category, text=text))
        print("Seed concluído: portfólio + question bank.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
