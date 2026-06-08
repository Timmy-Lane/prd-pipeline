"""retrieve_until_good — the keyless quality gate (dossier 13 §3.4).

Perplexity's failsafe rebuilt keyless: rerank scores feed the 0.70 threshold; if
<30% of candidates clear it, reformulate and re-fan, up to max_rounds. The loop
is pure — expand/fan_out/rerank are injected callables (no I/O here)."""

from __future__ import annotations

from collections.abc import Callable

from bad_research.web.base import WebResult
from bad_research.web.search.base import KeylessSearchConfig

Expand = Callable[..., list[str]]                       # expand(question, findings=, gaps=) -> queries
FanOut = Callable[[list[str]], list[WebResult]]         # fan_out(queries) -> deduped pool
Rerank = Callable[[str, list[WebResult]], list[WebResult]]  # rerank(question, pool) -> pool w/ metadata["score"]


def _top(scored: list[WebResult], n: int) -> list[WebResult]:
    return sorted(scored, key=lambda r: r.metadata.get("score", 0.0), reverse=True)[:n]


def _infer_gaps(scored: list[WebResult]) -> list[str]:
    """DESIGNED: thin heuristic gap signal for re-expansion — the titles of the
    low-scoring half (the host-model expander turns these into reformulations)."""
    low = [r for r in scored if r.metadata.get("score", 0.0) < 0.5]
    return [r.title for r in low[:5] if r.title]


def retrieve_until_good(question: str, *, cfg: KeylessSearchConfig,
                        expand: Expand, fan_out: FanOut, rerank: Rerank) -> list[WebResult]:
    """≥ min_pass_fraction clear relevance_threshold → return; else reformulate +
    re-fan, ≤ max_rounds. Returns the best-effort passing set after the cap."""
    queries = expand(question)
    passing: list[WebResult] = []
    for _round in range(cfg.max_rounds):
        pool = fan_out(queries)
        scored = rerank(question, pool)
        passing = [r for r in scored if r.metadata.get("score", 0.0) >= cfg.relevance_threshold]
        if scored and len(passing) >= cfg.min_pass_fraction * len(scored):
            return passing                       # ≥30% cleared 0.70 → good enough
        if not scored:
            return passing                       # nothing came back; nothing to reformulate from
        # <30% passed → reformulate and go wider (Perplexity failsafe)
        queries = expand(question, findings=_top(scored, 5), gaps=_infer_gaps(scored))
    return passing                               # best-effort after max_rounds
