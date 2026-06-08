"""ActCache — replay action scripts without re-paying the agent loop.

Key = SHA-256 over {instruction, url, sorted variable NAMES}. Variable VALUES are NEVER
hashed and never stored — secrets must not leak into the cache (dossier 03 §1.5).
The cached payload is a JSON-serialisable action script the BrowseProvider can replay.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def replay_key_for(instruction: str, url: str, *, variables: dict | None = None) -> str:
    """Stable replay key. Uses variable NAMES only (sorted), never values."""
    var_names = sorted((variables or {}).keys())
    payload = json.dumps(
        {"instruction": instruction, "url": url, "variableKeys": var_names},
        sort_keys=True, ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ActCache:
    """File-backed action-script cache. One JSON file per key under `root`."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def put(self, key: str, script: dict) -> None:
        self._path(key).write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
