from __future__ import annotations

from typing import Protocol

from src.domain import DiscoveryRoteiro


class LLMProvider(Protocol):
    def refine(self, roteiro: DiscoveryRoteiro) -> DiscoveryRoteiro:
        """Refine a generated discovery roteiro without changing the domain contract."""
        ...
