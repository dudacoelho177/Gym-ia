"""Superfície de API — Portfólio & Question Bank (specs/phase-02, specs/phase-07/002)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant_and_user, get_db
from app.api.v1.schemas.portfolio import (
    PortfolioItemCreateRequest,
    PortfolioItemDTO,
    ReferenceQuestionCreateRequest,
    ReferenceQuestionDTO,
)
from app.domain.entities import PortfolioItem, ReferenceQuestion, DiscoveryCategory
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SqlAlchemyPortfolioRepository,
    SqlAlchemyQuestionBankRepository,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/items", response_model=list[PortfolioItemDTO])
def list_portfolio_items(
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> list[PortfolioItemDTO]:
    tenant_id, _ = tenant_user
    repo = SqlAlchemyPortfolioRepository(db)
    return [_to_dto(item) for item in repo.list_for_tenant(tenant_id)]


@router.post("/items", response_model=PortfolioItemDTO, status_code=201)
def create_portfolio_item(
    payload: PortfolioItemCreateRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> PortfolioItemDTO:
    tenant_id, _ = tenant_user
    repo = SqlAlchemyPortfolioRepository(db)
    item = PortfolioItem(tenant_id=tenant_id, **payload.model_dump())
    repo.add(item)
    return _to_dto(item)


def _to_dto(item: PortfolioItem) -> PortfolioItemDTO:
    return PortfolioItemDTO(
        id=item.id, category=item.category, name=item.name,
        description=item.description, aliases=item.aliases, is_active=item.is_active,
    )


@router.get("/question-bank/{domain}", response_model=list[ReferenceQuestionDTO])
def list_question_bank(
    domain: str,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> list[ReferenceQuestionDTO]:
    repo = SqlAlchemyQuestionBankRepository(db)
    return [
        ReferenceQuestionDTO(id=q.id, domain=q.domain, category=q.category.value, text=q.text, is_priority=q.is_priority)
        for q in repo.list_by_domain(domain)
    ]


@router.post("/question-bank", response_model=ReferenceQuestionDTO, status_code=201)
def create_question(
    payload: ReferenceQuestionCreateRequest,
    db: Session = Depends(get_db),
    tenant_user: tuple[str, str] = Depends(get_current_tenant_and_user),
) -> ReferenceQuestionDTO:
    repo = SqlAlchemyQuestionBankRepository(db)
    question = ReferenceQuestion(
        domain=payload.domain,
        category=DiscoveryCategory(payload.category),
        text=payload.text,
        is_priority=payload.is_priority,
    )
    repo.add(question)
    return ReferenceQuestionDTO(
        id=question.id, domain=question.domain, category=question.category.value,
        text=question.text, is_priority=question.is_priority,
    )
