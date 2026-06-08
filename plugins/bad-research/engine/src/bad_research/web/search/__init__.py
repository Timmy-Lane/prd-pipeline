"""Keyless search layer (KR-2, dossier 13).

The keyless replacement for the deleted paid provider cascade: the host WebSearch
tool adapter (default), ddgs, self-host SearXNG, 7 scholarly verticals, RRF k=60
fusion, host-model rerank, intent routing, and the 0.70/<30% retrieve-until-good
loop. Zero API keys — only the Claude Code host model + local OSS + free APIs.
"""

from __future__ import annotations

from bad_research.web.search.base import (
    DdgsProvider,
    KeylessSearchConfig,
    SearxngProvider,
    WebSearchToolProvider,
)
from bad_research.web.search.loop import retrieve_until_good
from bad_research.web.search.rank import rrf_fuse, rrf_fuse_with_verticals
from bad_research.web.search.rerank import HostModelReranker
from bad_research.web.search.route import VERTICAL_ROUTES, detect_intent, route_query
from bad_research.web.search.verticals import (
    ArxivProvider,
    CrossrefProvider,
    EuropePMCProvider,
    OpenAlexProvider,
    PubMedProvider,
    SemanticScholarProvider,
    WikipediaProvider,
)

__all__ = [
    "VERTICAL_ROUTES",
    "ArxivProvider",
    "CrossrefProvider",
    "DdgsProvider",
    "EuropePMCProvider",
    "HostModelReranker",
    "KeylessSearchConfig",
    "OpenAlexProvider",
    "PubMedProvider",
    "SearxngProvider",
    "SemanticScholarProvider",
    "WebSearchToolProvider",
    "WikipediaProvider",
    "detect_intent",
    "retrieve_until_good",
    "route_query",
    "rrf_fuse",
    "rrf_fuse_with_verticals",
]
