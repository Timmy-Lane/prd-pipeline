"""Vertical routing (dossier 13 §8.2). Fire the right keyless API only on the
right intent — generic WebSearch stays the always-on baseline; Wikipedia is
always-on grounding (1 seed); verticals fan ONLY on the first <=2 seed queries
(politeness, §2.1)."""

from __future__ import annotations

import re

# KNOWN: the verbatim route table (dossier 13 §8.2). Names map to provider
# instances at fan-out time (the funnel owns the name->instance map, KR-6).
VERTICAL_ROUTES: dict[str, list[str]] = {
    "academic": ["openalex", "arxiv", "semantic_scholar", "crossref"],
    "medical": ["europe_pmc", "pubmed", "openalex"],
    "technical": ["arxiv", "openalex", "ddgs"],
    "general": [],
}

_ACADEMIC = re.compile(r"\b(paper|study|et al\.?|arxiv|doi|systematic review|preprint|citation)\b", re.I)
_MEDICAL = re.compile(r"\b(disease|drug|gene|clinical trial|patients?|mg/kg|in vivo|crispr|cancer|therapy)\b", re.I)
_TECHNICAL = re.compile(r"\b(error|stack trace|api|library|framework|protocol|how to (implement|configure))\b", re.I)

_SEED_LIMIT = 2          # verticals fan on <=2 seed queries (§8.2)


def detect_intent(question: str) -> str:
    """DESIGNED regex fallback (§8.2); the host model normally tags intent in the
    expansion step. medical > academic > technical precedence (most specific wins —
    a medical signal beats the generic "systematic review"/"paper" academic cues)."""
    if _MEDICAL.search(question):
        return "medical"
    if _ACADEMIC.search(question):
        return "academic"
    if _TECHNICAL.search(question):
        return "technical"
    return "general"


def route_query(question: str, queries: list[str], intent: str) -> list[tuple[str, str]]:
    """Return (query, provider_name) tasks. WebSearch on every query (baseline) +
    Wikipedia on 1 seed (grounding) + intent-routed verticals on <=2 seeds."""
    tasks: list[tuple[str, str]] = [(q, "websearch") for q in queries]
    if queries:
        tasks.append((queries[0], "wikipedia"))            # always-on grounding (1 seed)
    for prov in VERTICAL_ROUTES.get(intent, []):
        for q in queries[:_SEED_LIMIT]:
            tasks.append((q, prov))                        # verticals on seed queries only
    return tasks
