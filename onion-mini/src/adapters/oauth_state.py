from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone


class InMemoryOAuthStateStore:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self.ttl_seconds = ttl_seconds
        self._states: dict[str, tuple[str, datetime]] = {}

    def create_state(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        self._states[state] = (nonce, expires_at)
        return state, nonce

    def consume_state(self, state: str) -> str | None:
        item = self._states.pop(state, None)
        if item is None:
            return None

        nonce, expires_at = item
        if expires_at <= datetime.now(timezone.utc):
            return None
        return nonce
