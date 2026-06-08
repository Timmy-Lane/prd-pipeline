"""Frozen retrieval contracts (INTERFACES.md §retrieval/base.py).

`Chunk` and `Reranker` live here (the stable contracts). The concrete
`RetrievalEngine` lives in `engine.py` and is re-exported from the package
`__init__` so `from bad_research.retrieval import RetrievalEngine` resolves to
the implementation, not a stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Chunk:
    chunk_id: str            # sha1(url + "#" + heading)
    note_id: str
    text: str
    char_start: int
    char_end: int
    score: float
    source_id: str


@runtime_checkable
class Reranker(Protocol):
    def rerank(self, query: str, docs: list[str]) -> list[tuple[int, float]]:
        """Return [(doc_index, score)] sorted by score descending."""
        ...
