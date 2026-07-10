from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.domain import DiscoveryRoteiro


class DeterministicLLMAdapter:
    """Fallback local: keeps the same seam a real LLM provider will use later."""

    def refine(self, roteiro: DiscoveryRoteiro) -> DiscoveryRoteiro:
        return roteiro


class LLMProviderError(RuntimeError):
    """Raised when a remote LLM provider cannot refine the roteiro."""


@dataclass(frozen=True)
class OpenAICompatibleLLMAdapter:
    name: str
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float = 20.0

    def refine(self, roteiro: DiscoveryRoteiro) -> DiscoveryRoteiro:
        if not self.api_key:
            raise LLMProviderError(f"{self.name} API key is not configured.")

        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Voce refina roteiros de discovery em portugues brasileiro. "
                        "Responda somente JSON valido com os mesmos campos recebidos."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(roteiro.to_dict(), ensure_ascii=False),
                },
            ],
        }
        response = self._post_chat_completions(payload)
        content = self._extract_content(response)
        updates = self._parse_json_content(content)
        return self._apply_updates(roteiro, updates)

    def _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/onion-mini",
                "X-Title": "Onion Mini",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMProviderError(f"{self.name} HTTP error {exc.code}: {detail}") from exc
        except (TimeoutError, URLError, json.JSONDecodeError) as exc:
            raise LLMProviderError(f"{self.name} request failed: {exc}") from exc

    def _extract_content(self, response: dict[str, Any]) -> str:
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"{self.name} returned an invalid response.") from exc

    def _parse_json_content(self, content: str) -> dict[str, Any]:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(f"{self.name} returned non-JSON content.") from exc
        if not isinstance(parsed, dict):
            raise LLMProviderError(f"{self.name} returned JSON that is not an object.")
        return parsed

    def _apply_updates(
        self,
        roteiro: DiscoveryRoteiro,
        updates: dict[str, Any],
    ) -> DiscoveryRoteiro:
        for field_name in [
            "classification",
            "confidence",
            "portfolio_matches",
            "missing_information",
            "assumptions",
            "risks",
        ]:
            if field_name in updates:
                setattr(roteiro, field_name, updates[field_name])
        return roteiro


class OpenRouterLLMAdapter(OpenAICompatibleLLMAdapter):
    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-4o-mini",
        timeout_seconds: float = 20.0,
    ) -> None:
        super().__init__(
            name="openrouter",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model=model,
            timeout_seconds=timeout_seconds,
        )


class OpenAILLMAdapter(OpenAICompatibleLLMAdapter):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout_seconds: float = 20.0,
    ) -> None:
        super().__init__(
            name="openai",
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            model=model,
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class FallbackLLMAdapter:
    primary: object
    fallback: object

    def refine(self, roteiro: DiscoveryRoteiro) -> DiscoveryRoteiro:
        try:
            return self.primary.refine(roteiro)
        except Exception:
            return self.fallback.refine(roteiro)
