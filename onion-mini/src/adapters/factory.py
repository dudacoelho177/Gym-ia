from __future__ import annotations

import os

from src.domain.ports import LLMProvider

from .llm import (
    DeterministicLLMAdapter,
    FallbackLLMAdapter,
    OpenAILLMAdapter,
    OpenRouterLLMAdapter,
)


def create_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "openrouter").strip().lower()
    fallback_name = os.getenv("LLM_FALLBACK_PROVIDER", "openai").strip().lower()
    timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))

    if provider_name in {"deterministic", "local", "none"}:
        return DeterministicLLMAdapter()

    primary = _build_provider(provider_name, timeout_seconds)
    fallback = _build_provider(fallback_name, timeout_seconds)

    if _is_remote_provider(primary) and _is_remote_provider(fallback):
        return FallbackLLMAdapter(primary=primary, fallback=fallback)
    if _is_remote_provider(primary):
        return FallbackLLMAdapter(primary=primary, fallback=DeterministicLLMAdapter())
    if _is_remote_provider(fallback):
        return fallback
    return primary


def _build_provider(provider_name: str, timeout_seconds: float) -> LLMProvider:
    if provider_name == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            return DeterministicLLMAdapter()
        return OpenRouterLLMAdapter(
            api_key=api_key,
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            timeout_seconds=timeout_seconds,
        )
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return DeterministicLLMAdapter()
        return OpenAILLMAdapter(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            timeout_seconds=timeout_seconds,
        )
    return DeterministicLLMAdapter()


def _is_remote_provider(provider: LLMProvider) -> bool:
    return not isinstance(provider, DeterministicLLMAdapter)
