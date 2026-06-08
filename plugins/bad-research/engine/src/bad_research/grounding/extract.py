"""DSS span extraction (Glean): turn a verbatim quoted_support into char offsets
inside the note body. Deterministic, $0 -- no LLM. dossier 08 §1.1."""

from __future__ import annotations

# rapidfuzz is the fuzzy-locate fallback for lightly-normalized quotes.
from rapidfuzz import fuzz

FUZZY_RATIO_FLOOR = 95.0  # dossier §1.1: partial-ratio >= 95 to accept a fuzzy locate


def extract_spans(
    claim: str,
    quoted_support: str,
    note_body: str,
) -> tuple[int, int] | None:
    """Return (char_start, char_end) of quoted_support inside note_body.

    1. Exact find (char_end exclusive; body[start:end] == quote).
    2. Fuzzy fallback: slide a window of len(quote) (+/- 20%) over the body,
       accept the best window with rapidfuzz partial-ratio >= 95.
    3. None when neither locates it -- the caller drops the claim (a quote that
       isn't in the body is a hallucinated quote; dossier §1.1).
    """
    quote = quoted_support.strip()
    if not quote:
        return None

    idx = note_body.find(quote)
    if idx != -1:
        return (idx, idx + len(quote))

    return _fuzzy_locate(quote, note_body)


def _fuzzy_locate(quote: str, body: str) -> tuple[int, int] | None:
    qlen = len(quote)
    if qlen == 0 or qlen > len(body):
        # Quote longer than the whole body: try whole-body ratio once.
        if qlen > len(body) and fuzz.partial_ratio(quote, body) >= FUZZY_RATIO_FLOOR:
            return (0, len(body))
        return None

    best_score = 0.0
    best_span: tuple[int, int] | None = None
    # Window between 80% and 120% of the quote length, stepped to keep it cheap.
    win_min = max(1, int(qlen * 0.8))
    win_max = min(len(body), int(qlen * 1.2) + 1)
    step = max(1, qlen // 8)
    for start in range(0, len(body) - win_min + 1, step):
        for win in (qlen, win_min, win_max):
            end = min(start + win, len(body))
            score = fuzz.partial_ratio(quote, body[start:end])
            if score > best_score:
                best_score = score
                best_span = (start, end)
        if best_score >= 100.0:
            break

    if best_span is not None and best_score >= FUZZY_RATIO_FLOOR:
        return best_span
    return None


def body_to_lines(body: str) -> list[tuple[int, int]]:
    """Return a list of (char_start, char_end) for each line (0-indexed, exclusive end).

    Handles LF and CRLF line endings (bare-CR / old-Mac `\r` is NOT split on). A
    trailing newline does NOT produce a spurious empty final entry. The slice
    body[char_start:char_end] reproduces the line content WITHOUT its line terminator.
    """
    if not body:
        return []
    result: list[tuple[int, int]] = []
    pos = 0
    n = len(body)
    while pos < n:
        # find the next newline (LF), handling CRLF as one unit
        nl = body.find("\n", pos)
        if nl == -1:
            # last line with no trailing newline
            result.append((pos, n))
            break
        # CRLF: the content ends before the CR
        content_end = nl - 1 if nl > pos and body[nl - 1] == "\r" else nl
        result.append((pos, content_end))
        pos = nl + 1
    # If the body ends with a newline the loop adds an empty-range trailing
    # entry — drop it.
    if result and result[-1][0] == result[-1][1]:
        result.pop()
    return result


def char_span_to_line_range(
    body_lines: list[tuple[int, int]],
    char_start: int,
    char_end: int,
) -> tuple[int, int]:
    """Given precomputed body_lines from body_to_lines(), return 1-based
    (line_start, line_end) covering the char span [char_start, char_end).

    O(n) scan; n is number of lines in the note (typically < 500).
    Clamps to [1, len(body_lines)] on out-of-range input.
    """
    if not body_lines:
        return (1, 1)
    n = len(body_lines)
    line_start: int | None = None
    line_end: int | None = None
    for i, (cs, ce) in enumerate(body_lines):
        # A line overlaps the span if its range intersects [char_start, char_end).
        # Use inclusive overlap: the span touches this line if cs < char_end and ce > char_start.
        # Treat char_end == char_start (empty span) as touching the line that contains char_start.
        span_end = char_end if char_end > char_start else char_start + 1
        if (cs < span_end and ce > char_start) or (cs <= char_start < ce):
            line_no = i + 1  # 1-based
            if line_start is None:
                line_start = line_no
            line_end = line_no
    if line_start is None:
        # span is before or after all lines — clamp
        if char_start >= body_lines[-1][1]:
            return (n, n)
        return (1, 1)
    return (line_start, line_end)  # type: ignore[return-value]
