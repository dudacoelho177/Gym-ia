"""Adapter real via OpenRouter (ADR-0004) — SDK OpenAI apontando `base_url` para o OpenRouter."""
from __future__ import annotations

import json
from typing import Any

import httpx

from app.domain.ports.llm_provider import LLMProvider, LLMResult

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _strip_markdown_fences(text: str) -> str:
    """Alguns modelos devolvem ```json {...} ``` mesmo com response_format=json_object — remove
    a cerca de código antes do parse (reparo controlado, ADR-0008)."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else stripped[3:]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


class OpenRouterLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY ausente — configure .env")
        self._api_key = api_key
        self._model = model

    MAX_RETRIES = 2

    async def generate_structured(
        self, *, system_prompt: str, user_payload: dict[str, Any], response_schema_name: str
    ) -> LLMResult:
        last_error: Exception | None = None
        for _ in range(self.MAX_RETRIES + 1):
            try:
                return await self._call_once(system_prompt, user_payload, response_schema_name)
            except _RetryableProviderError as exc:
                last_error = exc
                continue
        raise ValueError(
            f"OpenRouter não devolveu JSON válido para schema '{response_schema_name}' "
            f"após {self.MAX_RETRIES + 1} tentativas (modelo '{self._model}')"
        ) from last_error

    async def _call_once(
        self, system_prompt: str, user_payload: dict[str, Any], response_schema_name: str
    ) -> LLMResult:
        async with httpx.AsyncClient(base_url=OPENROUTER_BASE_URL, timeout=60.0) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "response_format": {"type": "json_object"},
                    # Modelos de raciocínio (ex.: gpt-oss) podem consumir todo o orçamento de
                    # tokens só "pensando" e devolver content=None se o limite for baixo demais.
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

        raw_text = data["choices"][0]["message"]["content"]
        if not raw_text:
            raise _RetryableProviderError(f"OpenRouter devolveu content vazio/None para '{response_schema_name}'")

        try:
            content = json.loads(_strip_markdown_fences(raw_text))
        except json.JSONDecodeError as exc:
            raise _RetryableProviderError(
                f"OpenRouter retornou JSON inválido para schema '{response_schema_name}': {raw_text[:200]!r}"
            ) from exc

        usage = data.get("usage", {})
        return LLMResult(
            content=content,
            raw_text=raw_text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            model=data.get("model", self._model),
        )


class _RetryableProviderError(Exception):
    """Content vazio/None ou JSON inválido — normalmente um modelo de raciocínio que estourou o
    orçamento de tokens só "pensando". Vale tentar de novo antes de desistir (ADR-0008)."""
