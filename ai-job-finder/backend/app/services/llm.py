"""Thin wrapper around the DeepSeek API (OpenAI-compatible).

Optional dependency at runtime: when no credentials are configured (or the API call
fails), callers fall back to deterministic templates — the app must work keyless.
"""
from __future__ import annotations

import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


def llm_available() -> bool:
    return bool(get_settings().deepseek_api_key)


def generate_text(prompt: str, *, system: str | None = None, max_tokens: int = 2048) -> str | None:
    """Single completion; returns None on any failure so callers can fall back."""
    settings = get_settings()
    if not settings.deepseek_api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=max_tokens,
            messages=messages,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None
    except Exception as exc:  # noqa: BLE001 — any LLM failure falls back to templates
        logger.warning("LLM generation failed: %s", exc)
        return None
