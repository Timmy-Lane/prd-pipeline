"""Stage 5 — source-authority ranking (dossier 07 §5).

final = reranker_score x DOMAIN_TIER_multiplier, sorted desc. One multiply, free.
The deterministic encoding of Claude Research eval axis #4 ("primary sources over
lower-quality secondary"). DEMOTES, never drops (dropping is Stages 1-2).
NIA's deep-rank long-tail penalty is CUT (our per-run corpus is small; §5.1).
"""

from __future__ import annotations

from bad_research.quality.dedup import _tier_mult  # reuse the stamp-or-classify helper
from bad_research.web.base import WebResult


def authority_rank(results: list[WebResult]) -> list[WebResult]:
    """Sort by relevance_score x domain_tier_multiplier, descending."""
    for r in results:
        rel = float(r.metadata.get("relevance_score", 0.0))
        r.metadata["authority_score"] = rel * _tier_mult(r)
    return sorted(results, key=lambda r: r.metadata["authority_score"], reverse=True)
