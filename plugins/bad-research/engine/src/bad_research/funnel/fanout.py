"""Stage A — fan-out. Many queries per step (Perplexity queries: List[str]),
fired across P providers in parallel (asyncio.gather), then flattened.

Breadth = M_QUERIES x P_PROVIDERS x K_PER_QUERY, gathered concurrently so
latency ≈ max single search, not the sum (dossier 10 §1.3, §5.1).

A dead provider degrades to the survivors (SPEC §13 provider failover) — one
provider's exception never aborts the fan-out.

Every provider call is routed through funnel._async.acall so the SYNCHRONOUS
real providers (Plan 03 blocking httpx) and the async test fakes both work.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Literal

from bad_research.funnel._async import acall


@dataclass
class SearchQuery:
    """Mirror of the Plan 03 SearchQuery (INTERFACES.md web/base.py). Redeclared
    here as the funnel's input contract; the real one is structurally identical.
    """

    query: str
    intent: Literal["keyword", "neural", "deep"] = "keyword"
    recency_days: int | None = None
    include_domains: list[str] | None = None
    exclude_domains: list[str] | None = None
    max_results: int = 10


# Deterministic lens suffixes — the programmatic fallback expansion when the
# skill doesn't supply its own lens plan (dossier 10 §1.2 lenses A/B/C).
_LENS_SUFFIXES = (
    "",                              # Lens A — core fact (verbatim query first)
    "latest developments",          # Lens A — state-of-the-art
    "original study foundational paper",   # Lens B — citation-chain depth
    "criticism limitations",        # Lens C — adversarial
    "alternative explanation",      # Lens C — dissent
    "primary data analysis",        # Lens B — upstream sources
)


def plan_queries(query: str, *, m_queries: int, k_per_query: int) -> list[SearchQuery]:
    """Expand one user query into ≤ m_queries SearchQuery seeds. Verbatim query
    is always the first seed. Cheap deterministic fallback for programmatic
    callers; the width-sweep skill (Plan 08) may pass a richer lens plan in."""
    seen: set[str] = set()
    out: list[SearchQuery] = []
    for suffix in _LENS_SUFFIXES:
        text = query if not suffix else f"{query} {suffix}"
        if text in seen:
            continue
        seen.add(text)
        out.append(SearchQuery(query=text, max_results=k_per_query))
        if len(out) >= m_queries:
            break
    return out[:m_queries]


async def fan_out(queries: list[Any], providers: list[Any]) -> list[Any]:
    """Fire every (query x provider) concurrently; flatten survivors.

    Returns the raw hit pool (with duplicates — Stage B dedups). Stamps the
    representative WebResults with serp_rank/serp_provider if the provider
    didn't already (fakes do; real providers set them in search_ex).
    """
    if not providers or not queries:
        return []

    async def _one(provider: Any, q: Any) -> list[Any]:
        try:
            results = await acall(provider.search_ex, q)
        except NotImplementedError:
            # A provider that cannot run in THIS context (e.g. the host
            # WebSearch tool adapter invoked from a CLI subprocess) raises
            # NotImplementedError. Skip it explicitly so it can never starve the
            # fan-out — the surviving keyless providers carry the run. This is the
            # named contract the standalone/CLI path relies on (SPEC §13 failover).
            return []
        except Exception:
            return []  # degrade: a dead provider drops out, never aborts the run
        for i, r in enumerate(results):
            if not getattr(r, "serp_provider", ""):
                r.serp_provider = provider.name
            if not getattr(r, "serp_rank", 0):
                r.serp_rank = i + 1
        return list(results)

    tasks = [_one(p, q) for q in queries for p in providers]
    batches = await asyncio.gather(*tasks)
    hits: list[Any] = []
    for b in batches:
        hits.extend(b)
    return hits
