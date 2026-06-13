"""Environment-only configuration for the shared core.

Deliberately dependency-light (plain os.getenv, no settings library) so any app can
import core without pulling extra packages. API keys come from the environment only —
never from code, config tables, or the UI.
"""
from __future__ import annotations

import os


class Settings:
    # provider selection: "anthropic" | "openai_compatible"
    llm_mode: str = os.getenv("LLM_MODE", "anthropic")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ace_model_default: str = os.getenv("MODEL_DEFAULT", "claude-sonnet-4-5")
    ace_model_hard: str = os.getenv("MODEL_HARD", "claude-opus-4-1")
    local_llm_base_url: str = os.getenv("LLM_BASE_URL", "")


settings = Settings()
