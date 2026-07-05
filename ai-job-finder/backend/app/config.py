"""Application configuration loaded from environment variables (.env supported)."""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Job Finder"
    version: str = "0.1.0"
    debug: bool = False

    # sqlite by default; set DATABASE_URL=postgresql+psycopg://... in production
    database_url: str = Field(default="sqlite:///./jobfinder.db", alias="DATABASE_URL")

    # CORS — Vite dev server by default
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")

    # LLM (optional — template fallback used when unset)
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    llm_model: str = Field(default="claude-opus-4-8", alias="LLM_MODEL")

    # Key-gated connectors (all optional)
    adzuna_app_id: str | None = Field(default=None, alias="ADZUNA_APP_ID")
    adzuna_app_key: str | None = Field(default=None, alias="ADZUNA_APP_KEY")
    adzuna_country: str = Field(default="in", alias="ADZUNA_COUNTRY")  # in, us, gb, ...
    jooble_api_key: str | None = Field(default=None, alias="JOOBLE_API_KEY")
    rapidapi_key: str | None = Field(default=None, alias="RAPIDAPI_KEY")

    # Company career pages polled via public board APIs (comma-separated board slugs)
    greenhouse_boards: str = Field(default="stripe,cloudflare,databricks", alias="GREENHOUSE_BOARDS")
    lever_boards: str = Field(default="", alias="LEVER_BOARDS")

    # Connector behaviour
    connector_timeout_seconds: float = 12.0
    default_limit_per_source: int = 30

    # Email digest (optional)
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    # On Vercel the filesystem is read-only except /tmp — keep the demo SQLite there
    # unless a real DATABASE_URL (e.g. hosted Postgres) is configured.
    if os.environ.get("VERCEL") and "DATABASE_URL" not in os.environ:
        settings.database_url = "sqlite:////tmp/jobfinder.db"
    return settings


def data_path(filename: str) -> str:
    """Absolute path to a bundled data file in app/data/."""
    return os.path.join(os.path.dirname(__file__), "data", filename)
