from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env_name: str = "development"
    log_level: str = "INFO"
    log_format: str | None = None
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/notifications_hub"

    @property
    def resolved_log_format(self) -> str:
        if self.log_format is not None:
            return self.log_format
        return "json" if self.env_name == "prod" else "text"


@lru_cache
def get_settings() -> Settings:
    return Settings()
