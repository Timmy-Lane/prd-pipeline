"""CostMeter — 5-component cost metering (Perplexity, dossier 09 §A4.2 / 05§7).

OFFLINE only: used by the calibration harness to report where money went and to
score the `efficiency` axis. NOT a per-run gate (SPEC §10 Excluded list).
Components: input, output, reasoning, citation, search_queries.

Plan 08's pipeline POPULATES this at each stage boundary via `.record(...)` /
`.record_response(...)`; the harness reads `.total_usd()`. Honours the frozen
INTERFACES.md CostMeter surface verbatim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from bad_research.calibrate.constants import (
    COST_COMPONENTS,
    SEARCH_QUERY_PRICE_USD,
    TIER_PRICE_USD_PER_MTOK,
)


@dataclass
class _StageCost:
    tier: str
    input: int = 0
    output: int = 0
    reasoning: int = 0
    citation: int = 0
    search_queries: int = 0

    def usd(self) -> float:
        price = TIER_PRICE_USD_PER_MTOK.get(self.tier, {"input": 0.0, "output": 0.0})
        token_usd = (
            self.input * price["input"]
            # reasoning + citation tokens bill at the tier's OUTPUT rate.
            + (self.output + self.reasoning + self.citation) * price["output"]
        ) / 1_000_000
        return token_usd + self.search_queries * SEARCH_QUERY_PRICE_USD


@dataclass
class CostMeter:
    """Accumulate per-stage 5-component usage; convert to USD; emit cost-report.json."""

    _stages: dict[str, _StageCost] = field(default_factory=dict)

    def record(
        self,
        *,
        stage: str,
        tier: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        reasoning_tokens: int = 0,
        citation_tokens: int = 0,
        search_queries: int = 0,
    ) -> None:
        sc = self._stages.get(stage)
        if sc is None:
            sc = _StageCost(tier=tier)
            self._stages[stage] = sc
        sc.tier = tier  # last writer wins on tier label
        sc.input += input_tokens
        sc.output += output_tokens
        sc.reasoning += reasoning_tokens
        sc.citation += citation_tokens
        sc.search_queries += search_queries

    def record_response(
        self, *, stage: str, tier: str, usage: dict, search_queries: int = 0
    ) -> None:
        """Convenience: ingest an LLMResponse.usage dict directly."""
        self.record(
            stage=stage,
            tier=tier,
            input_tokens=int(usage.get("input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            reasoning_tokens=int(usage.get("reasoning_tokens", 0) or 0),
            citation_tokens=int(usage.get("citation_tokens", 0) or 0),
            search_queries=search_queries,
        )

    def _stage_usd(self) -> dict[str, float]:
        """Per-stage cost rounded to 8 places — the exact values the report emits."""
        return {name: round(sc.usd(), 8) for name, sc in self._stages.items()}

    def total_usd(self) -> float:
        # Sum the SAME per-stage rounded values the report emits, so
        # `total_usd == sum(by_stage[*].usd)` holds bit-for-bit (no float drift).
        return sum(self._stage_usd().values())

    def by_component(self) -> dict[str, int]:
        out = {c: 0 for c in COST_COMPONENTS}
        for sc in self._stages.values():
            for c in COST_COMPONENTS:
                out[c] += getattr(sc, c)
        return out

    def to_dict(self) -> dict:
        stage_usd = self._stage_usd()
        return {
            "components": list(COST_COMPONENTS),
            "total_usd": sum(stage_usd.values()),
            "by_component": self.by_component(),
            "by_stage": {
                name: {
                    "tier": sc.tier,
                    **{c: getattr(sc, c) for c in COST_COMPONENTS},
                    "usd": stage_usd[name],
                }
                for name, sc in self._stages.items()
            },
        }

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


__all__ = ["CostMeter"]
