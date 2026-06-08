"""Stage 4 — relevance thresholding + re-retrieve failsafe (dossier 07 §4).

ONE cross-encoder rerank (the swappable Reranker seam, Plan 02) -> 0.70 drop ->
if <30% of chunks pass, signal the search stage to re-retrieve (<=2 rounds).
Constants frozen in INTERFACES.md. The L1/L2/L3 Perplexity ladder is CUT (overkill);
we keep the thresholds, not the three-model machinery (dossier 07 §4.1).
"""

from __future__ import annotations

from dataclasses import dataclass

from bad_research.retrieval.base import Reranker
from bad_research.web.base import WebResult

RELEVANCE_DROP_THRESHOLD = 0.70   # PERPLEXITY_DEEP.md:1231 / INTERFACES.md
RERETRIEVE_PASS_FRACTION = 0.30   # PERPLEXITY_DEEP.md:1232 / INTERFACES.md
RECALL_FLOOR = 0.18               # GROK_HEAVY.md:1496 — coarse recall floor
CHUNK_CHARS = 1000                # TAVILY.md:1742 — scoring chunk size
RERETRIEVE_MAX_ROUNDS = 2         # dossier 07 §4.1


@dataclass
class RelevanceResult:
    kept: list[WebResult]
    pass_fraction: float
    should_reretrieve: bool


def score_and_filter(query: str, results: list[WebResult], reranker: Reranker,
                     *, rounds_remaining: int = RERETRIEVE_MAX_ROUNDS) -> RelevanceResult:
    """Rerank, drop < 0.70, and signal re-retrieve when < 30% pass.

    Stamps result.metadata['relevance_score']. Scores the first CHUNK_CHARS of each
    result's content (Tavily's 1000-char scoring chunk).
    """
    if not results:
        return RelevanceResult(kept=[], pass_fraction=0.0,
                               should_reretrieve=rounds_remaining > 0)

    docs = [(r.content or "")[:CHUNK_CHARS] for r in results]
    ranked = reranker.rerank(query, docs)  # [(idx, score)] desc

    kept: list[WebResult] = []
    passes = 0
    for idx, score in ranked:
        if score >= RELEVANCE_DROP_THRESHOLD:
            r = results[idx]
            r.metadata["relevance_score"] = score
            kept.append(r)
            passes += 1

    pass_fraction = passes / len(results)
    should_reretrieve = (pass_fraction < RERETRIEVE_PASS_FRACTION) and (rounds_remaining > 0)
    # kept already in rerank (desc) order
    return RelevanceResult(kept=kept, pass_fraction=pass_fraction,
                           should_reretrieve=should_reretrieve)
