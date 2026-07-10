from __future__ import annotations

from typing import Protocol

from src.domain.auth import GoogleIdentity


class GoogleIdentityProvider(Protocol):
    def build_authorization_url(self, state: str, nonce: str) -> str:
        ...

    def exchange_code_for_identity(self, code: str, expected_nonce: str) -> GoogleIdentity:
        ...
