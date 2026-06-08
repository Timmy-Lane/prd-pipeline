"""Base types and factory for the LLMProvider seam.

Contract is frozen in ultimate-research/INTERFACES.md. The default impl is
AnthropicProvider (llm/anthropic.py); LiteLLMProvider is an optional future escape
hatch (dossier 06 A6). The factory keeps SDK imports lazy so optional deps stay optional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

# triage -> Haiku, work -> Sonnet, heavy -> Opus (resolved via config.model_tiers).
ModelTier = Literal["triage", "work", "heavy"]


@dataclass
class LLMMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict]


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[dict] = field(default_factory=list)  # [] if none
    usage: dict = field(default_factory=dict)  # {input_tokens, output_tokens, cache_read, cache_write}
    model: str = ""


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        tier: ModelTier,
        tools: list[dict] | None = None,
        cache: bool = False,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse: ...


def get_llm_provider(name: str = "anthropic", **kwargs) -> LLMProvider:
    """Load an LLM provider by name. Defaults to Anthropic (the GA backend)."""
    if name == "anthropic":
        from bad_research.llm.anthropic import AnthropicProvider

        return AnthropicProvider(**kwargs)

    raise ValueError(f"Unknown LLM provider: {name!r}. Available: anthropic")
