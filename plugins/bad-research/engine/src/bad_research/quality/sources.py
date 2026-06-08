"""Populate the `sources` provenance/dedup table (INTERFACES.md vault schema).

source_id = 16-char SHA-256 of the canonical URL. domain_tier REAL = the multiplier;
tier INT = the prefetch_priority (0..9). Dual-temporal {document_date, event_date}
read from WebResult.metadata when the extractor set them (Plan 06 grounding).
DDL is owned by Plan 01/02 schema migration; this module only writes rows.
"""

from __future__ import annotations

import hashlib
import sqlite3

from bad_research.quality.prefilter import canonical_url, domain_tier
from bad_research.web.base import WebResult


def source_id(url: str) -> str:
    """16-char SHA-256 hex of the canonical URL (INTERFACES.md `sources.source_id`)."""
    canon = canonical_url(url)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build_source_row(result: WebResult, *, fetch_provider: str, fetch_tier: int) -> dict[str, object]:
    """Build the `sources` row dict for a fetched WebResult.

    fetch_tier is the Tier 0-3 fetch ladder level (browse/base.fetch_tiered), distinct
    from the DOMAIN_TIER authority. We persist DOMAIN_TIER as domain_tier(REAL)+tier(INT).
    """
    info = domain_tier(result.url)
    return {
        "source_id": source_id(result.url),
        "url": result.url,
        "domain": result.domain,
        "domain_tier": info.multiplier,                 # REAL: 1.30 … 0.50
        "fetch_provider": fetch_provider,
        "tier": info.prefetch_priority,                 # INT: 0 … 9
        "fetched_at": result.fetched_at.isoformat(),
        "document_date": result.metadata.get("document_date"),
        "event_date": result.metadata.get("event_date"),
    }


def upsert_source(conn: sqlite3.Connection, result: WebResult, *,
                  fetch_provider: str, fetch_tier: int) -> None:
    """Idempotently write a sources row (INSERT OR REPLACE on source_id PK)."""
    row = build_source_row(result, fetch_provider=fetch_provider, fetch_tier=fetch_tier)
    conn.execute(
        "INSERT OR REPLACE INTO sources "
        "(source_id, url, domain, domain_tier, fetch_provider, tier, fetched_at, "
        " document_date, event_date) "
        "VALUES (:source_id, :url, :domain, :domain_tier, :fetch_provider, :tier, "
        ":fetched_at, :document_date, :event_date)",
        row,
    )
    conn.commit()
