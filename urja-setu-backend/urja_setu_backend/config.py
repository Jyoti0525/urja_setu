"""Application configuration, loaded from environment / .env."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "URJA-SETU"
    version: str = "0.1.0"
    mode: str = "demo"  # demo | live

    # CORS — frontend dev origin (frontend runs on :4000)
    cors_origins: list[str] = ["http://localhost:4000"]

    # Free LLM (Groq primary, Gemini fallback, Ollama local fallback)
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Data stores
    database_url: str = "postgresql://urja:urja@localhost:5432/urja"
    redis_url: str = "redis://localhost:6379/0"

    # Feeds
    gdelt_enabled: bool = False
    aisstream_api_key: str | None = None


settings = Settings()
