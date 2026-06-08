"""funnel/store.py — the production vault adapter.

`gather` (and Stage E `filter_and_store`) call a duck-typed seam with the exact
signature `store_note(*, title, body, url, provider) -> note_id`. The funnel
tests inject a FakeVault that satisfies it directly. In production the real
hyperresearch vault exposes lower-level primitives (`core.note.write_note` +
the `sources` row via `quality.sources.upsert_source`), so this adapter wraps
them to present the one `store_note` method the funnel contract requires.

This module is NOT touched by the funnel's isolation tests (those inject
FakeVault); it is the glue the width-sweep skill backend (Plan 08) uses when it
assembles the real FunnelDeps.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class VaultStore:
    """Adapt a hyperresearch vault to the funnel's `store_note` contract.

    Wraps `core.note.write_note` (markdown is truth) + `quality.sources`
    bookkeeping (the `sources` row). Returns the note_id (the note file stem).
    """

    def __init__(self, vault: Any, *, fetch_tier: int = 1, tags: list[str] | None = None):
        self._vault = vault
        self._fetch_tier = fetch_tier
        # Run-scoped tags (the funnel's vault_tag) applied to EVERY stored note so
        # `bad search --tag <vault_tag>` and the corpus survey can find the run's
        # corpus. Without this the funnel stored untagged notes that no
        # tag-filtered survey could see.
        self._tags = [t for t in (tags or []) if t]
        # Note ids stored this run, in store order. The standalone CLI funnel
        # reports THIS as "sources gathered" — the corpus on disk is the
        # load-bearing output, independent of the Stage-F rerank (whose
        # host-model reranker cannot score inside a CLI subprocess and would
        # otherwise make the run look empty).
        self.stored_note_ids: list[str] = []

    def store_note(self, *, title: str, body: str, url: str, provider: str) -> str:
        from bad_research.core.note import write_note

        note_path = write_note(
            self._vault.notes_dir,
            title=title or url,
            body=body,
            tags=list(self._tags),
            status="draft",
            source=url,
            extra_frontmatter={
                "source": url,
                "fetch_provider": provider,
                "fetched_at": datetime.now(UTC).isoformat(),
            },
        )
        note_id = note_path.stem
        self.stored_note_ids.append(note_id)

        # Best-effort: record the sources row so authority/recency survive. The
        # funnel never fails on a bookkeeping miss — markdown is the truth.
        conn = getattr(self._vault, "db", None)
        if conn is not None:
            try:
                row = build_source_row_from_url(url, provider, self._fetch_tier)
                if row is not None:
                    conn.execute(
                        "INSERT OR REPLACE INTO sources "
                        "(source_id, url, domain, domain_tier, fetch_provider, tier, "
                        " fetched_at, document_date, event_date) "
                        "VALUES (:source_id, :url, :domain, :domain_tier, "
                        ":fetch_provider, :tier, :fetched_at, :document_date, "
                        ":event_date)",
                        row,
                    )
                    conn.commit()
            except Exception:  # pragma: no cover - bookkeeping must never abort a run
                pass

        return note_id


def build_source_row_from_url(url: str, provider: str, fetch_tier: int) -> dict[str, Any] | None:
    """Build a `sources` row from just a URL (the funnel stores bodies, not full
    WebResults, by the time it reaches the vault). Returns None if the quality
    helpers are unavailable."""
    try:
        from bad_research.quality import domain_tier, source_id
    except Exception:  # pragma: no cover - quality extra not installed
        return None
    info = domain_tier(url)
    from urllib.parse import urlsplit

    return {
        "source_id": source_id(url),
        "url": url,
        "domain": urlsplit(url).netloc,
        "domain_tier": info.multiplier,
        "fetch_provider": provider,
        "tier": info.prefetch_priority,
        "fetched_at": datetime.now(UTC).isoformat(),
        "document_date": None,
        "event_date": None,
    }
