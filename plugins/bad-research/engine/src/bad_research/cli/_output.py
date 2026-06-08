"""Console + JSON output for `bad doctor` / `bad calibrate`.

`models.output.success/error` return a Pydantic `Envelope` ({ok, data, error,
error_code, count, vault, timestamp}). `output()` renders it as a single JSON
line on stdout (so `typer.testing.CliRunner` captures a parseable payload).
Plain dicts pass through unchanged.
"""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console

console = Console()


def output(payload: Any, *, json_mode: bool) -> None:
    """Emit `payload` as one JSON line iff `json_mode`. Otherwise no-op (the
    caller prints its own rich console view)."""
    if not json_mode:
        return
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump(mode="json")
    print(json.dumps(payload, default=str))


__all__ = ["console", "output"]
