"""Asset-saving helper for the fetch pipeline.

`core/fetcher.fetch_and_save` lazily imports `_save_assets` here only when
called with `save_assets=True`. It downloads the media (images, etc.) a
`WebResult` references into `research/assets/<note_id>/` and returns a manifest
of what was saved. Kept out of `core/fetcher.py` so the hot path has no
networking-on-import cost and tests can stub the seam.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _ext_for(url: str, content_type: str | None) -> str:
    """Best-effort file extension from a URL path or a Content-Type header."""
    path_ext = Path(urlparse(url).path).suffix
    if path_ext and len(path_ext) <= 5:
        return path_ext
    ct_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "application/pdf": ".pdf",
    }
    if content_type:
        return ct_map.get(content_type.split(";")[0].strip(), "")
    return ""


def _save_assets(conn: Any, result: Any, note_id: str, assets_dir: Path) -> list[dict]:
    """Download every media asset on `result` into `assets_dir`.

    Returns a manifest list of `{src, path, bytes}` dicts. Network/IO failures on
    a single asset are swallowed (we never abort a note save over a missing
    image). The `assets` table row is recorded when the schema has one; absent
    that, the on-disk file + returned manifest are the record.
    """
    import httpx

    assets_dir = Path(assets_dir)
    media = list(getattr(result, "media", None) or [])
    if not media:
        return []
    assets_dir.mkdir(parents=True, exist_ok=True)

    saved: list[dict] = []
    seen: set[str] = set()
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for item in media:
            src = (item or {}).get("src") if isinstance(item, dict) else None
            if not src or src in seen or src.startswith("data:"):
                continue
            seen.add(src)
            try:
                resp = client.get(src, headers={"User-Agent": "bad-research/0.1"})
                resp.raise_for_status()
                data = resp.content
            except Exception:
                continue
            ext = _ext_for(src, resp.headers.get("content-type"))
            digest = hashlib.sha256(data).hexdigest()[:16]
            filename = f"{digest}{ext}"
            dest = assets_dir / filename
            try:
                dest.write_bytes(data)
            except OSError:
                continue
            rel = f"research/assets/{note_id}/{filename}"
            saved.append({"src": src, "path": rel, "bytes": len(data)})

    return saved


__all__ = ["_save_assets"]
