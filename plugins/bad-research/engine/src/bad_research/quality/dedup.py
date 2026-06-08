"""Stage 3 — cross-source dedup on the retrieval path (dossier 07 §3).

Wraps core/similarity.py (forked verbatim from hyperresearch). Constants frozen
in INTERFACES.md: Jaccard 0.60 / shingle 3 / MinHash 128 / 16 bands / brute-vs-LSH
switch at 200 / min word count > 20.

Tie-break: when two WebResults are near-dupes, keep the higher DOMAIN_TIER copy
(the primary/docs version over the blog re-post; dossier 07 §3.1).
"""

from __future__ import annotations

from bad_research.core.similarity import (
    jaccard,
    lsh_candidates,
    minhash_signature,
    shingle,
)
from bad_research.quality.prefilter import DOMAIN_TIER, domain_tier
from bad_research.web.base import WebResult

DEDUP_JACCARD_THRESHOLD = 0.60  # INTERFACES.md / dedup.py:21 + NIA
LSH_THRESHOLD = 200             # dedup.py:17 — brute below, MinHash+LSH at/above
DEDUP_MIN_WORDS = 20            # dedup.py:43 — skip stubs


def _tier_mult(r: WebResult) -> float:
    # honor an explicitly-stamped tier (set upstream), else classify from URL
    name = r.metadata.get("domain_tier_name")
    if name in DOMAIN_TIER:
        return DOMAIN_TIER[name].multiplier
    return domain_tier(r.url).multiplier


def dedup(results: list[WebResult]) -> list[WebResult]:
    """Collapse near-duplicate WebResults at Jaccard >= 0.60. Keep higher-tier copy."""
    eligible: list[tuple[int, WebResult, set[str]]] = []
    for idx, r in enumerate(results):
        text = r.content or ""
        if len(text.split()) > DEDUP_MIN_WORDS:
            eligible.append((idx, r, shingle(text, n=3)))

    if len(eligible) < 2:
        return list(results)

    # build candidate pairs
    if len(eligible) >= LSH_THRESHOLD:
        sigs = {str(idx): minhash_signature(sh, num_perm=128) for idx, _, sh in eligible}
        raw_pairs = lsh_candidates(sigs, bands=16)
        idx_by_key = {str(idx): (idx, r, sh) for idx, r, sh in eligible}
        pairs = []
        for ka, kb in raw_pairs:
            _, _, sha = idx_by_key[ka]
            _, _, shb = idx_by_key[kb]
            if jaccard(sha, shb) >= DEDUP_JACCARD_THRESHOLD:
                pairs.append((int(ka), int(kb)))
    else:
        pairs = []
        for i in range(len(eligible)):
            for j in range(i + 1, len(eligible)):
                ia, ra, sha = eligible[i]
                ib, rb, shb = eligible[j]
                if jaccard(sha, shb) >= DEDUP_JACCARD_THRESHOLD:
                    pairs.append((ia, ib))

    # union-find collapse; within each cluster keep the highest-tier member
    drop: set[int] = set()
    for ia, ib in pairs:
        if ia in drop or ib in drop:
            continue
        ra, rb = results[ia], results[ib]
        # keep the higher tier multiplier; on a tie keep the earlier index
        if _tier_mult(rb) > _tier_mult(ra):
            drop.add(ia)
        else:
            drop.add(ib)

    return [r for idx, r in enumerate(results) if idx not in drop]
