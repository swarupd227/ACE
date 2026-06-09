"""Centralized configuration, loaded from environment (.env)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    ace_env: str = "demo"
    ace_auto_seed: bool = True
    ace_self_consistency_samples: int = 3

    # Database
    database_url: str = "postgresql+psycopg://ace:ace_dev_pw@db:5432/ace"

    # LLM — env holds the initial defaults + the secrets. The ACTIVE provider /
    # model / endpoint is admin-configurable at runtime via config_store (key
    # "llm"). API keys always stay here in the environment — never in the
    # database, never shown in the UI.
    llm_mode: str = "anthropic"  # anthropic | local  (initial default only)
    anthropic_api_key: str = ""
    openai_api_key: str = ""     # for any OpenAI-compatible endpoint (Azure OpenAI, OpenAI, vLLM, …)
    ace_model_default: str = "claude-sonnet-4-5"
    ace_model_hard: str = "claude-opus-4-1"
    local_llm_base_url: str = "http://host.docker.internal:11434/v1"
    local_llm_model: str = "llama3.1:8b"

    @property
    def llm_available(self) -> bool:
        if self.llm_mode == "anthropic":
            return bool(self.anthropic_api_key)
        return self.llm_mode == "local"


settings = Settings()
