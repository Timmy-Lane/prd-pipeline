"""Quality / no-bullshit filtering pipeline (SPEC §8, dossier 07).

Public API — the contract every other plan imports. Five-stage cheap-before-expensive
filter + the mandatory untrusted-content injection preamble.
"""

from __future__ import annotations

from bad_research.quality.content_filter import looks_like_paywall, postfetch_filter
from bad_research.quality.dedup import dedup
from bad_research.quality.injection import INJECTION_PREAMBLE, wrap_untrusted
from bad_research.quality.prefilter import (
    DOMAIN_TIER,
    Candidate,
    TierInfo,
    canonical_url,
    domain_tier,
    is_blocklisted,
    prefetch_filter,
    seo_farm_score,
)
from bad_research.quality.rank import authority_rank
from bad_research.quality.relevance import (
    RELEVANCE_DROP_THRESHOLD,
    RERETRIEVE_MAX_ROUNDS,
    RERETRIEVE_PASS_FRACTION,
    RelevanceResult,
    score_and_filter,
)
from bad_research.quality.sources import build_source_row, source_id, upsert_source

__all__ = [  # noqa: RUF022 — grouped by pipeline stage (the 5-stage contract), not alphabetical
    # Stage 1
    "seo_farm_score", "DOMAIN_TIER", "domain_tier", "TierInfo", "Candidate",
    "canonical_url", "is_blocklisted", "prefetch_filter",
    # Stage 2
    "postfetch_filter", "looks_like_paywall",
    # Stage 3
    "dedup",
    # Stage 4
    "score_and_filter", "RelevanceResult", "RELEVANCE_DROP_THRESHOLD",
    "RERETRIEVE_PASS_FRACTION", "RERETRIEVE_MAX_ROUNDS",
    # Stage 5
    "authority_rank",
    # Injection defense
    "INJECTION_PREAMBLE", "wrap_untrusted",
    # sources provenance
    "source_id", "build_source_row", "upsert_source",
]
