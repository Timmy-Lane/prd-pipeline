"""Keyless ranking — RRF k=60 fusion + consensus/DOI/richness tie-breaks.

Pure algebra, no I/O. KNOWN math (dossier 13 §3.2 verbatim, §8.3 refinements);
RRF_K imported from retrieval/constants.py (the single source of truth, =60).
"""

from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit

from bad_research.retrieval.constants import RRF_K
from bad_research.web.base import WebResult

_TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "fbclid", "gclid"}


def canon(url: str) -> str:
    """Firecrawl-style URL canon (dossier 13 §3.1): drop scheme-case, fragment,
    www, default port, trailing slash, tracking params. Looser than full content
    hashing but enough for pre-fetch dedup."""
    s = urlsplit(url.strip())
    netloc = s.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    if netloc.endswith(":80") or netloc.endswith(":443"):
        netloc = netloc.rsplit(":", 1)[0]
    path = s.path.rstrip("/") or "/"
    kept = [kv for kv in s.query.split("&") if kv and kv.split("=", 1)[0] not in _TRACKING]
    query = "&".join(sorted(kept))
    return urlunsplit(("", netloc, path, query, ""))


def _richer(a: WebResult | None, b: WebResult) -> WebResult:
    """Field-merge (dossier 13 §1.3): keep the longer content/title, union sources,
    prefer https. Returns the merged representative."""
    if a is None:
        rep = WebResult(url=b.url, title=b.title, content=b.content,
                        metadata=dict(b.metadata), links=list(b.links))
        rep.metadata["sources"] = {b.metadata.get("source")} - {None}
        return rep
    # keep the longer content/title
    if len(b.content or "") > len(a.content or ""):
        a.content = b.content
    if len(b.title or "") > len(a.title or ""):
        a.title = b.title
    if b.url.startswith("https://") and not a.url.startswith("https://"):
        a.url = b.url
    # union the source set; carry over any structured metadata b has that a lacks
    src = a.metadata.setdefault("sources", set())
    if b.metadata.get("source"):
        src.add(b.metadata["source"])
    for fld in ("doi", "year", "authors", "citations", "oa_pdf", "native_score"):
        if a.metadata.get(fld) in (None, "", [], {}) and b.metadata.get(fld) not in (None, "", [], {}):
            a.metadata[fld] = b.metadata[fld]
    return a


def rrf_fuse(ranked_lists: list[list[WebResult]], *, k: int = RRF_K) -> list[WebResult]:
    """RRF over ranked lists, keyed on canonical URL. Consensus tie-break: at
    equal RRF, more sources wins (dossier 13 §3.2). Returns merged WebResults
    sorted descending."""
    scores: dict[str, float] = defaultdict(float)
    reps: dict[str, WebResult] = {}
    for lst in ranked_lists:
        for rank, r in enumerate(lst, start=1):
            key = canon(r.url)
            scores[key] += 1.0 / (k + rank)
            reps[key] = _richer(reps.get(key), r)
    ordered = sorted(
        reps,
        key=lambda key: (scores[key], len(reps[key].metadata.get("sources", ()))),
        reverse=True,
    )
    out = []
    for key in ordered:
        rep = reps[key]
        rep.metadata["sources"] = sorted(rep.metadata.get("sources", set()))
        rep.metadata["rrf_score"] = scores[key]
        out.append(rep)
    return out


def _identity(r: WebResult) -> str:
    """DOI-first identity (§8.3.1): collapse the same paper across arXiv/DOI/OA/PMC."""
    doi = (r.metadata or {}).get("doi")
    return f"doi:{doi.lower()}" if doi else canon(r.url)


def _richness(r: WebResult) -> int:
    m = r.metadata or {}
    return sum(bool(m.get(f)) for f in ("doi", "content", "citations", "oa_pdf")) + bool(r.content)


def rrf_fuse_with_verticals(ranked_lists: list[list[WebResult]], *, k: int = RRF_K) -> list[WebResult]:
    """§3.2 RRF + DOI-first dedup + metadata-richness tie-break (§8.3). No formula
    change — RRF stays rank-based; only the identity key and tie-break differ."""
    scores: dict[str, float] = defaultdict(float)
    reps: dict[str, WebResult] = {}
    for lst in ranked_lists:
        for rank, r in enumerate(lst, start=1):
            key = _identity(r)
            scores[key] += 1.0 / (k + rank)
            reps[key] = _richer(reps.get(key), r)
    ordered = sorted(
        reps,
        key=lambda key: (scores[key], len(reps[key].metadata.get("sources", ())), _richness(reps[key])),
        reverse=True,
    )
    out = []
    for key in ordered:
        rep = reps[key]
        rep.metadata["sources"] = sorted(rep.metadata.get("sources", set()))
        rep.metadata["rrf_score"] = scores[key]
        out.append(rep)
    return out
