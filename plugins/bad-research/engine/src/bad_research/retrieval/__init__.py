"""Perplexity x NIA hybrid retrieval engine.

Public surface: `Chunk`, `Reranker` (contracts, base.py), `RetrievalEngine`
(concrete impl, engine.py), `chunk_note` (chunker.py)."""

from __future__ import annotations

from bad_research.retrieval.base import Chunk, Reranker
from bad_research.retrieval.chunker import chunk_note
from bad_research.retrieval.engine import RetrievalEngine

__all__ = ["Chunk", "Reranker", "RetrievalEngine", "chunk_note"]
