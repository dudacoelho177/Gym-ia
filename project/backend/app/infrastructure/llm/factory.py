from app.core.config import get_settings
from app.domain.ports.llm_provider import LLMProvider
from app.infrastructure.llm.openrouter_provider import OpenRouterLLMProvider

_provider_instance: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    settings = get_settings()
    _provider_instance = OpenRouterLLMProvider(settings.openrouter_api_key, settings.openrouter_model)
    return _provider_instance
