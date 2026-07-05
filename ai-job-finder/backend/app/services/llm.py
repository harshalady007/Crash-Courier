"""Thin wrapper around the Anthropic SDK.

Optional dependency at runtime: when no credentials are configured (or the SDK call
fails), callers fall back to deterministic templates — the app must work keyless.
"""
from __future__ import annotations

import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


def llm_available() -> bool:
    return bool(get_settings().anthropic_api_key)


def generate_text(prompt: str, *, system: str | None = None, max_tokens: int = 2048) -> str | None:
    """Single completion; returns None on any failure so callers can fall back."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        kwargs: dict = {
            "model": settings.llm_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        if response.stop_reason == "refusal":
            logger.warning("LLM refused the request")
            return None
        parts = [block.text for block in response.content if block.type == "text"]
        return "\n".join(parts).strip() or None
    except Exception as exc:  # noqa: BLE001 — any LLM failure falls back to templates
        logger.warning("LLM generation failed: %s", exc)
        return None
