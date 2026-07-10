from __future__ import annotations

from typing import Protocol

from src.domain.auth import AuthSession, UserId


class SessionManager(Protocol):
    def create_session(self, user_id: UserId) -> AuthSession:
        ...

    def verify_session(self, token: str) -> AuthSession | None:
        ...

    def revoke_session(self, token: str) -> None:
        ...
