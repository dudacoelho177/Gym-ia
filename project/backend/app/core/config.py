from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./gym_ai.db"

    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/auto"

    dev_tenant_api_key: str = "dev-tenant-key"
    dev_tenant_slug: str = "clear-it-demo"

    cors_allowed_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
