"""canonicalize_url — Firecrawl-style URL normalization for dedup (dossier 10
§3.1, FC §28.5). Collapses cosmetic variants so `a.com/p` and `a.com/p/`,
`www.a.com/p`, and `a.com/p#x` all dedup to one candidate.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

_DEFAULT_PORTS = {"http": "80", "https": "443"}
_INDEX_RE = re.compile(r"/index\.(html?|php|aspx?|jsp|cgi)$", re.IGNORECASE)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())

    scheme = parts.scheme.lower() or "https"

    host = parts.hostname or ""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]

    # Drop default port; keep non-default ports.
    netloc = host
    if parts.port is not None and str(parts.port) != _DEFAULT_PORTS.get(scheme):
        netloc = f"{host}:{parts.port}"

    path = parts.path
    # strip index.* files
    path = _INDEX_RE.sub("", path)
    # strip a single trailing slash (but keep root "/")
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # drop fragment; preserve query (it is semantically meaningful)
    return urlunsplit((scheme, netloc, path, parts.query, ""))
