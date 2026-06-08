"""Stage A→B dedup — URL-canonical + content-hash, $0, no model.

URL-canonical collapse uses canonicalize_url (Firecrawl-style). Content-hash
collapse uses sha256(content)[:16] (matches core/fetcher.py:137) to catch
mirror/syndicated pages with different URLs but identical bodies.

Output: list[Candidate] — the un-read candidate pool. Each Candidate carries
the SERP signals (provider_ranks) the rank stage (Stage C) fuses via RRF.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from bad_research.funnel.canonical import canonicalize_url
from bad_research.funnel.recency import stamp_age


@dataclass
class Candidate:
    """An un-read search hit. The funnel ranks these BEFORE fetching (Stage C)."""

    canonical_url: str
    result: Any                          # the representative WebResult (un-read SERP shape)
    provider_ranks: dict[str, int] = field(default_factory=dict)  # provider -> 1-based rank
    # Age in days since publication, computed at build from result.metadata['year']
    # and/or the content layer's published_date. None ⇒ undatable (gate passes it,
    # rank scores it neutral). Read by quality/prefilter.py::passes_recency_gate.
    published_days_ago: int | None = None

    @property
    def url(self) -> str:
        return self.canonical_url


def _content_hash(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()[:16]


def _stamp_candidate_age(cand: Candidate, today: date | datetime | None) -> None:
    """Compute age_days from the survivor's WebResult and stamp BOTH consumers.

    Writes `result.metadata['age_days']` (read by funnel/rank.py Freshness) and
    `cand.published_days_ago` (read by quality/prefilter.py recency gate). The
    age comes from metadata['year'] and/or an ISO published_date the content
    layer may have stashed in metadata['published_date'].
    """
    meta = getattr(cand.result, "metadata", None)
    if not isinstance(meta, dict):
        return
    published = meta.get("published_date") or meta.get("date")
    age = stamp_age(meta, today=today, published_date=published)
    cand.published_days_ago = age


def dedup(hits: list[Any], *, today: date | datetime | None = None) -> list[Candidate]:
    """Collapse raw fan-out hits into the candidate pool.

    Stage 1: URL-canonical dedup (cosmetic variants → one).
    Stage 2: content-hash dedup (mirrors/syndication → one).
    Provider ranks from every duplicate are merged onto the survivor.

    Each survivor is dated: age_days is computed from its WebResult's date
    signals and stamped onto BOTH result.metadata['age_days'] (rank.py) and
    Candidate.published_days_ago (recency gate). `today` is injected for
    determinism (defaults to UTC today only when omitted).
    """
    by_url: dict[str, Candidate] = {}
    for h in hits:
        cu = canonicalize_url(h.url)
        prov = getattr(h, "serp_provider", "") or "unknown"
        rank = getattr(h, "serp_rank", 0) or 0
        if cu in by_url:
            # keep first-seen representative; merge this provider's rank
            existing = by_url[cu]
            if prov not in existing.provider_ranks:
                existing.provider_ranks[prov] = rank
        else:
            by_url[cu] = Candidate(canonical_url=cu, result=h,
                                   provider_ranks={prov: rank} if rank else {prov: 0})

    # Stage 2 — content-hash collapse across distinct URLs.
    by_hash: dict[str, Candidate] = {}
    out: list[Candidate] = []
    for cand in by_url.values():
        body = getattr(cand.result, "content", "") or ""
        # Pages with no body yet (snippet-only) can't be content-deduped; keep them.
        if not body.strip():
            out.append(cand)
            continue
        ch = _content_hash(body)
        if ch in by_hash:
            # merge provider ranks onto the canonical survivor, drop the mirror
            survivor = by_hash[ch]
            for p, r in cand.provider_ranks.items():
                survivor.provider_ranks.setdefault(p, r)
        else:
            by_hash[ch] = cand
            out.append(cand)

    # Date every survivor (writes metadata['age_days'] + Candidate.published_days_ago).
    for cand in out:
        _stamp_candidate_age(cand, today)
    return out
