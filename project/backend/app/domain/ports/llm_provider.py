"""Porta LLMProvider (ADR-0004) — a aplicação depende desta interface, nunca do SDK do provedor."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResult:
    content: dict[str, Any]
    raw_text: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema_name: str,
    ) -> LLMResult:
        """Gera saída estruturada e validável (ADR-0008). Implementações fazem parse/retry."""
        raise NotImplementedError
