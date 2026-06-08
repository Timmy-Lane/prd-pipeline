"""Chunk-level FTS5/BM25 lane. Reuses hyperresearch's query preprocessing and
the body weight; chunk_fts has a single content column so we only weight body."""
from __future__ import annotations

import sqlite3
from typing import Any

from bad_research.retrieval.constants import BM25_BODY_WEIGHT
from bad_research.search.fts import preprocess_query  # forked hyperresearch helper

_CHUNK_FTS_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
    chunk_id UNINDEXED,
    body,
    note_id UNINDEXED,
    tokenize='porter unicode61'
);
"""


def create_chunk_fts(conn: sqlite3.Connection) -> None:
    conn.executescript(_CHUNK_FTS_DDL)
    conn.commit()


def index_chunk_fts(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    """Upsert chunk bodies. FTS5 has no PK, so delete-by-chunk_id then insert."""
    for r in rows:
        conn.execute("DELETE FROM chunk_fts WHERE chunk_id = ?", (r["chunk_id"],))
    conn.executemany(
        "INSERT INTO chunk_fts (chunk_id, body, note_id) VALUES (:chunk_id, :body, :note_id)",
        rows,
    )
    conn.commit()


def search_chunk_fts(conn: sqlite3.Connection, query: str, *, limit: int) -> list[tuple[str, float]]:
    """Return [(chunk_id, abs_bm25)] best-first. abs() because SQLite bm25
    returns negatives (smaller = better); hyperresearch takes abs()."""
    fts_query = preprocess_query(query)
    sql = """
        SELECT chunk_id, bm25(chunk_fts, 0.0, ?, 0.0) AS score
        FROM chunk_fts
        WHERE chunk_fts MATCH ?
        ORDER BY score
        LIMIT ?
    """
    try:
        rows = conn.execute(sql, (BM25_BODY_WEIGHT, fts_query, limit)).fetchall()
    except sqlite3.OperationalError:
        return []
    return [(r["chunk_id"], abs(r["score"])) for r in rows]
