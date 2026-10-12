"""Shared configuration for OpenAI-compatible language model servers."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_default_model(override: Optional[str] = None) -> str:
    """Return an explicit model override, .env model, or legacy default."""
    return override or os.getenv("DEFAULT_MODEL") or "gpt-4o-mini"


def openai_client_kwargs(api_key: Optional[str] = None) -> dict:
    """Build OpenAI SDK arguments, including local vLLM configuration."""
    base_url = os.getenv("OPENAI_BASE_URL")
    configured_key = api_key or os.getenv("OPENAI_API_KEY")

    kwargs = {}
    if base_url:
        kwargs["base_url"] = base_url
        kwargs["api_key"] = configured_key or "EMPTY"
    elif configured_key:
        kwargs["api_key"] = configured_key
    return kwargs


def has_llm_config() -> bool:
    """Whether either an OpenAI key or an OpenAI-compatible endpoint is set."""
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_BASE_URL"))


def create_openai_client(api_key: Optional[str] = None):
    """Create an OpenAI SDK client for OpenAI or a compatible local server."""
    from openai import OpenAI

    return OpenAI(**openai_client_kwargs(api_key))
