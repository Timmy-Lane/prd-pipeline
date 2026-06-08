"""Recency converter — turn a SERP hit's date signals into an age in days.

The funnel's two recency consumers want an *age* (days since publication), not a
*date*:
  - `funnel/rank.py` reads ``result.metadata['age_days']`` for the Freshness
    dimension (None ⇒ neutral score 1; a fresh page ⇒ 3).
  - `quality/prefilter.py::passes_recency_gate` reads
    ``Candidate.published_days_ago`` against ``RECENCY_MAX_AGE_DAYS``.

Both were INERT because nothing ever computed the age: the verticals stamp
``metadata['year']`` and the content layer can return an ISO ``published_date``,
but nobody converted either into ``age_days`` / ``published_days_ago``. This
module is that converter, and it is deterministic: the reference "today" is
injected, never read from the wall clock, so tests pin a fixed date.

Precision ladder (best first):
  1. an ISO ``published_date`` (exact day) — ``web/content/fetch_clean.py``
     ``extract_published_date`` returns this; the funnel passes it straight in.
  2. a ``metadata['year']`` (int or "2024" string) — anchored to Jan 1 of that
     year (conservative: a year-only source is treated as *no younger than* the
     start of its year, so it is never spuriously counted as fresher than it is).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any


def _today(today: date | datetime | None) -> date:
    if today is None:
        return datetime.now(UTC).date()
    if isinstance(today, datetime):
        return today.date()
    return today


def _year_from_meta(meta: dict[str, Any]) -> int | None:
    """Pull a 4-digit year out of metadata['year'] (int, '2024', or '2024-...')."""
    raw = meta.get("year")
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw if 1000 <= raw <= 9999 else None
    s = str(raw).strip()
    if len(s) >= 4 and s[:4].isdigit():
        y = int(s[:4])
        return y if 1000 <= y <= 9999 else None
    return None


def _date_from_iso(iso: str | None) -> date | None:
    """Parse an ISO-8601 date/datetime string (the extract_published_date shape)."""
    if not iso:
        return None
    s = str(iso).strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    # Bare YYYY-MM-DD already handled by fromisoformat; fall back to the leading
    # 10 chars (handles "2024-03-01T..." that some sources emit without tz).
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def compute_age_days(
    metadata: dict[str, Any] | None,
    *,
    today: date | datetime | None = None,
    published_date: str | None = None,
) -> int | None:
    """Days between publication and `today`. None when the hit can't be dated.

    `published_date` (an ISO string, e.g. from `extract_published_date`) wins
    when present; otherwise we fall back to `metadata['year']` (Jan 1 anchor).
    A future date clamps to 0 (never negative age). Deterministic: `today` is
    injected (defaults to UTC today only when omitted).
    """
    ref = _today(today)
    meta = metadata or {}

    pub = _date_from_iso(published_date)
    if pub is None:
        year = _year_from_meta(meta)
        if year is not None:
            pub = date(year, 1, 1)
    if pub is None:
        return None

    return max(0, (ref - pub).days)


def stamp_age(
    metadata: dict[str, Any],
    *,
    today: date | datetime | None = None,
    published_date: str | None = None,
) -> int | None:
    """Compute the age and write it into `metadata['age_days']` in place.

    Returns the age (or None). Idempotent: an already-stamped non-None
    `age_days` is preserved (so a precise upstream value isn't clobbered by a
    coarser year-only recompute). The funnel calls this at Candidate build so
    `rank.py`'s Freshness dimension and the recency gate both see a real age.
    """
    existing = metadata.get("age_days")
    if isinstance(existing, int):
        return existing
    age = compute_age_days(metadata, today=today, published_date=published_date)
    metadata["age_days"] = age
    return age
