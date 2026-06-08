"""funnel/ — the six-stage scraper funnel (SPEC §6, dossier 10).

Public API:
    gather(query, *, mode) -> list[Chunk]   # the ONLY entry point callers use
    FunnelConfig                              # tiered constants

Invariant: callers receive reranked Chunk[] + [[note-id]] pointers,
never raw page bodies. Stages A-E run at $0 model cost.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bad_research.funnel.config import FunnelConfig

if TYPE_CHECKING:  # pragma: no cover
    from bad_research.funnel.orchestrator import gather

__all__ = ["FunnelConfig", "gather"]


def __getattr__(name: str) -> Any:
    """Lazily resolve `gather` so importing a single submodule (e.g. config)
    during TDD does not require the whole package to be assembled. PEP 562."""
    if name == "gather":
        from bad_research.funnel.orchestrator import gather

        return gather
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
