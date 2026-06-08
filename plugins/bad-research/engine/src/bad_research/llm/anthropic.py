"""AnthropicProvider — the default LLM backend.

Resolves model TIERS (triage/work/heavy) to concrete Claude IDs via config, applies
the --cheap demotion (heavy->work), and stamps Anthropic prompt-cache cache_control
breakpoints on the stable system+tools prefix when cache=True. This is the single
cheapest cost win in the product (dossier 09 A1.2): the 2nd..Nth spawn of a worker
type within a run pays ~10% of input-token cost on the cached prefix.

Anthropic allows <=4 cache_control breakpoints per request; we use 2 (last system
block + last tool). The CALLER is responsible for keeping the system+tools prefix
byte-identical across spawns so the cache actually hits; this provider only stamps
the markers.

Sampling params (temperature/top_p/top_k) are model-conditional: Opus-4.7-class
models (claude-opus-4-7*) unconditionally REJECT them with a 400 — those knobs
were removed on Opus 4.7 (not gated by extended thinking; it's by model). So we
only forward `temperature` when the RESOLVED model is not Opus-4.7-class. The
public complete() signature still accepts temperature=0.1; it just isn't sent to
Opus 4.7.
"""

from __future__ import annotations

import os
from typing import Any

from bad_research.config import BadResearchConfig
from bad_research.llm.base import LLMMessage, LLMResponse, ModelTier


class AnthropicProvider:
    """LLMProvider backed by the Anthropic Messages API."""

    name = "anthropic"

    def __init__(
        self,
        api_key: str | None = None,
        config: BadResearchConfig | None = None,
    ) -> None:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - hard dep, defensive
            raise ImportError(
                "anthropic provider requires: pip install anthropic"
            ) from exc

        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it or put it in "
                "~/.config/bad-research/config.toml."
            )

        self._config = config or BadResearchConfig()
        self._client = anthropic.Anthropic(api_key=key)

    def _resolve_model(self, tier: ModelTier) -> str:
        """tier -> concrete model ID, applying the --cheap heavy->work demotion."""
        tiers = self._config.model_tiers
        if tier == "heavy" and self._config.cheap:
            return tiers["work"]
        return tiers[tier]

    @staticmethod
    def _split_messages(
        messages: list[LLMMessage],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Split into Anthropic's top-level `system` blocks and the `messages[]` array.

        Anthropic does NOT accept role="system" inside messages[]; system text goes
        to the top-level `system` param as a list of text blocks.
        """
        system_blocks: list[dict[str, Any]] = []
        convo: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                text = m.content if isinstance(m.content, str) else ""
                system_blocks.append({"type": "text", "text": text})
            else:
                # tool role maps to a user turn carrying tool_result content
                role = "user" if m.role == "tool" else m.role
                convo.append({"role": role, "content": m.content})
        return system_blocks, convo

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        tier: ModelTier,
        tools: list[dict[str, Any]] | None = None,
        cache: bool = False,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        model = self._resolve_model(tier)
        system_blocks, convo = self._split_messages(messages)
        tools = list(tools) if tools else []

        # E7 — append-only prompt-cache discipline (DEEPLEARNINGAI.md A4, Genspark
        # >80% hit / 5-10x cost). The STABLE prefix is the system prompt block: it is
        # byte-identical across calls within a stage (the same rerank/judge/verify
        # system prompt is reused across batches, N-sample votes, and re-spawns),
        # while the VARIABLE content (query/passages/claims) lives in messages[]
        # AFTER it. Stamping cache_control on the last system block is always safe
        # (it never changes output, only enables cache hits) so it defaults ON via
        # config.prompt_cache — this is what makes the headless reranker / consistency
        # vote / calibrate judge actually HIT the cache (not a dead opt-in flag).
        # Degrades gracefully: no system block -> nothing stamped, no crash; SDKs/
        # models without prompt caching just ignore the key. Anthropic allows <=4
        # breakpoints; we use 1 (system) by default, +1 (last tool) when cache=True.
        if self._config.prompt_cache and system_blocks:
            system_blocks[-1] = {**system_blocks[-1], "cache_control": {"type": "ephemeral"}}
        if cache:
            # Explicit agent-loop opt-in: ALSO cache the last tool definition (the
            # stable tool registry). The cached prefix must be byte-identical across
            # spawns — that's the caller's job.
            if system_blocks and not self._config.prompt_cache:
                # honor the explicit opt-in even if the default discipline is disabled
                system_blocks[-1] = {**system_blocks[-1], "cache_control": {"type": "ephemeral"}}
            if tools:
                tools[-1] = {**tools[-1], "cache_control": {"type": "ephemeral"}}

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": convo,
        }
        if system_blocks:
            kwargs["system"] = system_blocks
        if tools:
            kwargs["tools"] = tools
        # Opus-4.7-class models reject sampling params (temperature/top_p/top_k)
        # with a 400; only forward temperature to non-Opus-4.7 models.
        if not model.startswith("claude-opus-4-7"):
            kwargs["temperature"] = temperature

        resp = self._client.messages.create(**kwargs)
        return self._to_llmresponse(resp)

    @staticmethod
    def _to_llmresponse(resp: Any) -> LLMResponse:
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(block.text)
            elif btype == "tool_use":
                tool_calls.append(
                    {"id": block.id, "name": block.name, "input": block.input}
                )

        usage_obj = resp.usage
        usage = {
            "input_tokens": getattr(usage_obj, "input_tokens", 0),
            "output_tokens": getattr(usage_obj, "output_tokens", 0),
            "cache_read": getattr(usage_obj, "cache_read_input_tokens", 0) or 0,
            "cache_write": getattr(usage_obj, "cache_creation_input_tokens", 0) or 0,
        }

        return LLMResponse(
            text="".join(text_parts),
            tool_calls=tool_calls,
            usage=usage,
            model=getattr(resp, "model", ""),
        )
