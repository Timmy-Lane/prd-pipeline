"""LLMProvider seam — Anthropic-first behind a thin Protocol (SPEC §3, dossier 06 A6)."""

from __future__ import annotations

from bad_research.llm.base import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ModelTier,
    get_llm_provider,
)

__all__ = [
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "ModelTier",
    "get_llm_provider",
]
