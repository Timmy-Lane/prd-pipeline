"""Pure fusion algebra (dossier 04 §3.2). No I/O — fully unit-testable."""
from __future__ import annotations

from bad_research.retrieval.constants import (
    DEEP_RANK_PENALTY,
    DEFAULT_SOURCE_TYPE_WEIGHT,
    RETRIEVAL_WEIGHT,
    RETRIEVAL_WEIGHT_DEFAULT,
    RRF_K,
    SOURCE_TYPE_WEIGHT,
)


def minmax_normalize(scores: list[float]) -> list[float]:
    """Map scores into [0,1]. Constant input → all 1.0 (lane stays informative)."""
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [1.0 for _ in scores]
    span = hi - lo
    return [(s - lo) / span for s in scores]


def _normalize_map(score_map: dict[str, float]) -> dict[str, float]:
    keys = list(score_map)
    norm = minmax_normalize([score_map[k] for k in keys])
    return dict(zip(keys, norm, strict=True))


def hybrid_fuse(vec_scores: dict[str, float], bm25_scores: dict[str, float],
                *, alpha: float) -> dict[str, float]:
    """alpha*norm(vector) + (1-alpha)*norm(bm25), aligned by candidate id.
    A candidate missing from a lane contributes 0 from that lane."""
    nv = _normalize_map(vec_scores)
    nb = _normalize_map(bm25_scores)
    ids = set(nv) | set(nb)
    return {cid: alpha * nv.get(cid, 0.0) + (1 - alpha) * nb.get(cid, 0.0) for cid in ids}


def retrieval_weight(pre_rerank_rank: int) -> float:
    """Three-tier weight keyed on 1-based pre-rerank rank (NIA §5.2)."""
    if pre_rerank_rank <= 3:
        return RETRIEVAL_WEIGHT[3]    # 0.75
    if pre_rerank_rank <= 10:
        return RETRIEVAL_WEIGHT[10]   # 0.60
    return RETRIEVAL_WEIGHT_DEFAULT   # 0.40


def three_tier_fuse(initial_score: float, reranker_score: float, pre_rerank_rank: int) -> float:
    """final = max(0, w*initial + (1-w)*reranker - penalty)."""
    w = retrieval_weight(pre_rerank_rank)
    base = w * initial_score + (1 - w) * reranker_score
    if pre_rerank_rank > 10:
        base -= DEEP_RANK_PENALTY * (pre_rerank_rank - 10)
    return max(0.0, base)


def apply_source_type_weight(score: float, content_type: str | None) -> float:
    return score * SOURCE_TYPE_WEIGHT.get(content_type or "", DEFAULT_SOURCE_TYPE_WEIGHT)


def rrf_merge(*ranked_lists: list[str], k: float = RRF_K) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion. Sums 1/(rank0 + k) over lists (0-based, LanceDB §8.8).
    Returns [(id, score)] sorted descending."""
    acc: dict[str, float] = {}
    for lst in ranked_lists:
        for rank0, cid in enumerate(lst):
            acc[cid] = acc.get(cid, 0.0) + 1.0 / (rank0 + k)
    return sorted(acc.items(), key=lambda kv: kv[1], reverse=True)
