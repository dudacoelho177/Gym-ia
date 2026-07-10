"""Auth & Multitenancy (specs/phase-07/004) — MVP: API key estática por tenant via header `X-API-Key`.

Resolve o tenant ANTES de qualquer caso de uso; recurso de outro tenant nunca vaza (ver routers).
Simplificação assumida para o MVP (ver technical-context-lite.md §4 — débito conhecido):
substituir por JWT/OAuth real quando houver múltiplos tenants de verdade.
"""
from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.domain.entities import Tenant, User
from app.domain.ports.llm_provider import LLMProvider
from app.infrastructure.db.models import TenantModel, UserModel
from app.infrastructure.db.session import get_db
from app.infrastructure.llm.factory import get_llm_provider


def get_llm() -> LLMProvider:
    return get_llm_provider()


def _ensure_dev_tenant(db: Session, settings: Settings) -> TenantModel:
    tenant = db.query(TenantModel).filter_by(slug=settings.dev_tenant_slug).first()
    if tenant is None:
        tenant = TenantModel(id=Tenant().id, name="Clear IT (demo)", slug=settings.dev_tenant_slug)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant


def _ensure_dev_user(db: Session, tenant: TenantModel) -> UserModel:
    user = db.query(UserModel).filter_by(tenant_id=tenant.id).first()
    if user is None:
        user = UserModel(id=User().id, tenant_id=tenant.id, email="presales@clearit.demo", role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_tenant_and_user(
    x_api_key: str = Header(default=""),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> tuple[str, str]:
    if x_api_key != settings.dev_tenant_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida")
    tenant = _ensure_dev_tenant(db, settings)
    user = _ensure_dev_user(db, tenant)
    return tenant.id, user.id


__all__ = ["get_db", "get_llm", "get_current_tenant_and_user"]
