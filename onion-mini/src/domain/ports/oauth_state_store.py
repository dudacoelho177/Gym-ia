from __future__ import annotations

from typing import Protocol


class OAuthStateStore(Protocol):
    def create_state(self) -> tuple[str, str]:
        ...

    def consume_state(self, state: str) -> str | None:
        ...
