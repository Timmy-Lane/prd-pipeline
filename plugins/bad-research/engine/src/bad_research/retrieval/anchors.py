"""Provenance + grounding table DDL (INTERFACES.md §Vault schema additions).

`sources` populated by Plan 05/07; `claim_anchors` populated by Plan 06.
Created here so the retrieval engine can be wired against a complete schema."""
from __future__ import annotations

import sqlite3

PROVENANCE_DDL = """
CREATE TABLE IF NOT EXISTS sources (
    source_id      TEXT PRIMARY KEY,   -- 16-char sha256
    url            TEXT,
    domain         TEXT,
    domain_tier    REAL,
    fetch_provider TEXT,
    tier           INTEGER,
    fetched_at     TEXT,
    document_date  TEXT,
    event_date     TEXT
);
CREATE INDEX IF NOT EXISTS idx_sources_domain ON sources(domain);

CREATE TABLE IF NOT EXISTS claim_anchors (
    anchor_id      TEXT PRIMARY KEY,   -- = quote_sha (8-char)
    note_id        TEXT,
    char_start     INTEGER,
    char_end       INTEGER,
    claim          TEXT,
    quoted_support TEXT,
    verified       INTEGER,
    verify_score   REAL,
    line_start     INTEGER,
    line_end       INTEGER
);
CREATE INDEX IF NOT EXISTS idx_claim_anchors_note ON claim_anchors(note_id);
"""


def create_provenance_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(PROVENANCE_DDL)
    conn.commit()
