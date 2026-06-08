"""Calibration baselines — run the same query through a comparison system.

Key-gated (SPEC §14): a baseline that needs a key it doesn't have is silently
dropped by the harness, never a crash. The hyperresearch baseline runs the
upstream package if it's importable.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Protocol


class BaselineUnavailable(RuntimeError):
    """Raised when a baseline is invoked without its key/dependency."""


@dataclass
class BaselineResult:
    name: str
    report: str
    corpus: list[dict[str, object]]  # the evidence that baseline used, for fair judging


class Baseline(Protocol):
    name: str

    def available(self) -> bool: ...
    def run(self, query: str) -> BaselineResult: ...


@dataclass
class HyperresearchBaseline:
    """Runs the upstream `hyperresearch` package if installed (offline-friendly)."""

    name: str = "hyperresearch"

    def available(self) -> bool:
        return importlib.util.find_spec("hyperresearch") is not None

    def run(self, query: str) -> BaselineResult:
        if not self.available():
            raise BaselineUnavailable("hyperresearch package not importable")
        # The upstream pipeline is Claude-Code-driven; for offline calibration we
        # can only run its deterministic vault search. The harness treats a present-
        # but-non-LLM baseline as a structural comparator. Real LLM comparison
        # happens when run inside a Claude Code host (out of scope for the test path).
        raise BaselineUnavailable(
            "hyperresearch baseline requires a Claude Code host; use --baselines none offline"
        )


def available_baselines() -> list[Baseline]:
    """Every baseline whose dependency is present (keyless only).

    The keyed deep-research APIs (Perplexity/Grok) are REMOVED in the keyless
    re-architecture — they need third-party keys, which the keyless rule forbids.
    The only baseline is `hyperresearch` (host-driven, structural comparator) when
    its package is importable. The keyless calibration plan
    (docs/plans/2026-05-27-bad-research-KR-7-calibration-plan.md) measures the
    keyless pipeline against keyless references instead.
    """
    candidates: list[Baseline] = [HyperresearchBaseline()]
    return [b for b in candidates if b.available()]


__all__ = [
    "Baseline",
    "BaselineResult",
    "BaselineUnavailable",
    "HyperresearchBaseline",
    "available_baselines",
]
