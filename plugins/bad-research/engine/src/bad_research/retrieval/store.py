"""Embedded LanceDB chunk store (teardowns/LANCEDB.md).

Vector lane of the hybrid engine. Deterministic IVF_HNSW_PQ index when the
table is large enough; flat (brute-force) search below the threshold and as a
prefilter fallback under low selectivity. Cosine metric.

[VERIFIED 2026-05-26] against lancedb==0.30.2 (newer than the plan's >=0.13;
all plan APIs confirmed working verbatim — no [CORRECTION] needed):
  - lancedb.connect(str) ; db.create_table(name, schema=) ; tbl.count_rows()
  - tbl.merge_insert("chunk_id").when_matched_update_all()
        .when_not_matched_insert_all().execute(arrow_table)  → idempotent on PK
  - tbl.search(vec).distance_type("cosine").limit(k).to_list() → rows with
    "_distance" (ascending) + the stored columns ("chunk_id", ...).
  - tbl.create_index(metric=, num_partitions=, num_sub_vectors=,
        vector_column_name=, index_type="IVF_HNSW_PQ", m=, ef_construction=,
        replace=True)  — kwargs match the installed signature.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # type-only — never imported at runtime in the keyless default
    import pyarrow as pa

from bad_research.retrieval.constants import (
    LANCE_HNSW_EF_CONSTRUCTION,
    LANCE_HNSW_M,
    LANCE_INDEX_MIN_ROWS,
    LANCE_NUM_PARTITIONS_TARGET,
    LANCE_PQ_NUM_SUB_VECTORS,
)

TABLE = "chunks"


class LanceChunkStore:
    def __init__(self, lance_dir: Path, *, dim: int):
        import lancedb  # type: ignore[import-untyped]  # ([local] extra)

        self.dir = Path(lance_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.db = lancedb.connect(str(self.dir))
        self._table = self._open_or_create()

    def _schema(self) -> pa.Schema:
        import pyarrow as pa  # ([local] extra)

        return pa.schema([
            pa.field("chunk_id", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), self.dim)),
            pa.field("note_id", pa.string()),
            pa.field("char_start", pa.int64()),
            pa.field("char_end", pa.int64()),
            pa.field("model", pa.string()),
            pa.field("dim", pa.int64()),
        ])

    def _open_or_create(self) -> Any:
        # list_tables() (table_names() is deprecated in lancedb 0.30.x).
        existing = self.db.list_tables() if hasattr(self.db, "list_tables") else self.db.table_names()
        if TABLE in existing:
            return self.db.open_table(TABLE)
        return self.db.create_table(TABLE, schema=self._schema())

    def upsert(self, rows: list[dict[str, Any]]) -> None:
        """Idempotent on chunk_id (merge_insert delete-then-insert on match)."""
        import pyarrow as pa  # ([local] extra)

        if not rows:
            return
        tbl = pa.Table.from_pylist(rows, schema=self._schema())
        (self._table.merge_insert("chunk_id")
            .when_matched_update_all()
            .when_not_matched_insert_all()
            .execute(tbl))

    def count(self) -> int:
        return int(self._table.count_rows())

    def _pq_sub_vectors(self) -> int:
        """PQ num_sub_vectors MUST divide the vector dimension (lance-index
        hard constraint). The frozen LANCE_PQ_NUM_SUB_VECTORS=16 divides the
        production Cohere dim (1024) cleanly; for any other dim we fall back to
        the largest divisor of `dim` that is <= 16 (so e.g. dim=8 → 8, dim=768 →
        16, dim=384 → 16). [CORRECTION 2026-05-26: lancedb 0.30.2 raises
        'num_sub_vectors must divide vector dimension' otherwise — the plan's
        flat constant 16 crashes the index build on non-multiple-of-16 dims.]"""
        if self.dim % LANCE_PQ_NUM_SUB_VECTORS == 0:
            return LANCE_PQ_NUM_SUB_VECTORS
        for k in range(min(LANCE_PQ_NUM_SUB_VECTORS, self.dim), 0, -1):
            if self.dim % k == 0:
                return k
        return 1

    def maybe_build_index(self) -> bool:
        """Build a deterministic IVF_HNSW_PQ index iff rows >= threshold.
        Returns True if an index was (or already is) present."""
        n = self.count()
        if n < LANCE_INDEX_MIN_ROWS:
            return False
        num_partitions = max(1, min(4096, n // LANCE_NUM_PARTITIONS_TARGET or 1))
        # Deterministic build: fixed params, no random sampling knobs left to default.
        self._table.create_index(
            metric="cosine",
            vector_column_name="vector",
            index_type="IVF_HNSW_PQ",
            num_partitions=num_partitions,
            num_sub_vectors=self._pq_sub_vectors(),
            m=LANCE_HNSW_M,
            ef_construction=LANCE_HNSW_EF_CONSTRUCTION,
            replace=True,
        )
        return True

    def search_vector(self, query_vector: list[float], *, top_k: int,
                      where: str | None = None) -> list[tuple[str, float]]:
        """Return [(chunk_id, cosine_distance)] ascending by distance.

        With < LANCE_INDEX_MIN_ROWS rows (or no index) LanceDB performs a flat
        scan automatically — exact and deterministic. A restrictive prefilter
        (`where`) is applied pre-search (prefilter=True) so low-selectivity
        filters fall back to flat scan (LANCEDB §5)."""
        q = self._table.search(query_vector).distance_type("cosine").limit(top_k)
        if where:
            q = q.where(where, prefilter=True)
        rows = q.to_list()
        return [(r["chunk_id"], float(r["_distance"])) for r in rows]

    @staticmethod
    def distance_to_score(distance: float) -> float:
        """Cosine distance → similarity in [0,1]: 1 - d, clamped."""
        return max(0.0, min(1.0, 1.0 - distance))
