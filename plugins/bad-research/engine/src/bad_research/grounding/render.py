"""Per-sentence single-index [N] citation render (Perplexity; SPEC §9).
No References section in prose -- sources live off-band (the anchor map)."""

from __future__ import annotations

import re

# [4] numeric indices, and [[note-id]] wiki-links -- both are citation tokens.
# A wikilink body may carry a line-anchor suffix (e.g. :L42-L58) and/or a display
# alias (|alias). The colon-line-spec is captured as PART of the note-id group
# (group 1 below), not treated as an alias separator, so the full
# `note-id:L42-L58` key survives verbatim (A-4).
_NUMERIC_CITE = re.compile(r"\[(\d+)\]")
_WIKILINK_CITE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")

# A line-anchor suffix `:L<start>-L<end>` at the very end of a citation token.
_LINE_ANCHOR_RE = re.compile(r":L(\d+)-L(\d+)$")


def render_citation(sentence: str, anchor_indices: list[int]) -> str:
    """Append ` [N]` per index, in order, after the sentence's terminal text.

    A sentence with no indices is returned unchanged (background/transition
    sentences carry no [N] -- dossier §1.3)."""
    base = sentence.rstrip()
    if not anchor_indices:
        return base
    tail = " ".join(f"[{i}]" for i in anchor_indices)
    return f"{base} {tail}"


def extract_citations(sentence: str) -> list[str]:
    """Return the citation tokens in/adjacent to a sentence.

    Returns numeric [N] indices (as strings) and [[note-id]] /
    [[note-id:L42-L58]] wiki-link targets. For wikilinks with a display alias
    (`[[id|alias]]`) the alias is stripped. For line-anchored tokens
    (`[[id:L42-L58]]`) the full `id:L42-L58` key is returned verbatim — the
    colon-line-spec is inside the note-id group, not treated as an alias — so
    use parse_line_anchor() to split it. Legacy bare `[[note-id]]` tokens are
    unchanged."""
    out: list[str] = []
    for m in re.finditer(r"\[(\d+)\]|\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", sentence):
        out.append(m.group(1) if m.group(1) is not None else m.group(2).strip())
    return out


def parse_line_anchor(token: str) -> tuple[str, int | None, int | None]:
    """Split a citation token into (note_id, line_start, line_end).

    For a line-anchored token like "source-note-12:L42-L58" returns
    ("source-note-12", 42, 58). For a bare note-id (or a numeric [N] index
    string) returns (token, None, None) — a no-op for legacy tokens."""
    m = _LINE_ANCHOR_RE.search(token)
    if m:
        note_id = token[: m.start()]
        return (note_id, int(m.group(1)), int(m.group(2)))
    return (token, None, None)


# B-8 readability: a citation TOKEN is either a numeric [N] index or a [[wikilink]].
# This is the same grammar extract_citations recognises, kept consistent so the
# coalescer and the extractor never disagree on what counts as a cite. The
# wikilink body may carry an optional colon-line-spec (:L42-L58) which is kept as
# part of the SAME token (not split as an alias) so distinct line ranges of one
# note stay distinct cites (A-4; round2-citation §5).
_CITE_TOKEN = re.compile(r"\[\d+\]|\[\[[^\]|]+(?::[^\]|]+)?(?:\|[^\]]*)?\]\]")
# A "cite tail" = one or more whitespace-separated citation tokens at the very
# end of a sentence's run (what render_citation appends: e.g. " [1] [2] [3]").
_CITE_TAIL = re.compile(
    r"(?:\s*(?:\[\d+\]|\[\[[^\]|]+(?::[^\]|]+)?(?:\|[^\]]*)?\]\]))+\s*$"
)
# Split prose into sentence units so each unit keeps ITS OWN trailing cite tail.
# The boundary is the whitespace that FOLLOWS a sentence's terminal punctuation
# and its optional cite tail, and PRECEDES the next sentence's first character.
# Using a finditer-driven splitter (below) rather than re.split keeps each unit =
# `<prose><optional cite tail>` instead of orphaning the tail onto the next unit.
_UNIT = re.compile(
    r".*?[.!?]"                                                       # minimal prose to a terminator
    r"(?=\s|$)"                                                        # terminator not mid-token (e.g. 12.4)
    r"(?:\s*(?:\[\d+\]|\[\[[^\]|]+(?::[^\]|]+)?(?:\|[^\]]*)?\]\]))*",  # + its own cite tail
    re.DOTALL,
)


def _cite_set(unit: str) -> frozenset[str]:
    """The SOURCE SET a sentence-unit cites (order-independent — {1,2} == {2,1})."""
    return frozenset(extract_citations(unit))


def _strip_cite_tail(unit: str) -> str:
    """The sentence prose with its trailing cite tail removed (provenance moves to
    the group cite; the prose itself is preserved byte-for-byte otherwise)."""
    return _CITE_TAIL.sub("", unit).rstrip()


def coalesce_citations(text: str) -> str:
    """Collapse the repeated per-sentence cite tail across a RUN of CONSECUTIVE
    sentences that share the SAME source set into ONE group cite at the end of
    the run (B-8 readability — hyperresearch's one clean win was paragraph-level
    cites reading better than dense `[n][n][n]` repeated every sentence).

    Provenance is FULLY preserved:
      * every sentence's prose survives verbatim;
      * the union of cited sources is identical before and after (no source is
        dropped or invented — assert via extract_citations);
      * a sentence citing a DISTINCT source keeps its own cite and BREAKS the run
        (we only ever coalesce consecutive same-set sentences, never merge
        distinct source sets);
      * uncited sentences pass through unchanged and also break a run.

    Set-equality, not sequence-equality: {1,2} and {2,1} coalesce. Works for both
    numeric [N] and [[wikilink]] tokens.

    CONTRACT: call this ONLY as the final visual pass, AFTER the per-sentence
    `no_uncited_claim_gate` and the recitation gate have passed — it groups cites
    across sentences, so a per-sentence uncited check run afterwards would
    false-positive on the now-grouped sentences. (Step 16.8 enforces this ordering;
    a code caller must honour it too.)"""
    # Split into sentence units, each carrying its own (optional) trailing cites.
    # _UNIT consumes `<prose up to a terminator><that sentence's cite tail>`; any
    # trailing remainder with no terminator (e.g. a dangling fragment) is kept.
    units: list[str] = [m.group(0).strip() for m in _UNIT.finditer(text) if m.group(0).strip()]
    consumed = sum(len(m.group(0)) for m in _UNIT.finditer(text))
    remainder = text[consumed:].strip()
    if remainder:
        units.append(remainder)
    if len(units) <= 1:
        return text

    out_parts: list[str] = []
    i = 0
    n = len(units)
    while i < n:
        cset = _cite_set(units[i])
        # An uncited unit (empty set) is never coalesced — emit as-is, move on.
        if not cset:
            out_parts.append(units[i].strip())
            i += 1
            continue

        # Gather the maximal run of CONSECUTIVE units citing the identical set.
        j = i
        while j < n and _cite_set(units[j]) == cset:
            j += 1
        run = units[i:j]

        if len(run) == 1:
            # A lone cited sentence — leave its cite exactly where it was.
            out_parts.append(run[0].strip())
        else:
            # Coalesce: emit each sentence's PROSE (cite tail stripped), then ONE
            # group cite — built from the run's last unit so token spelling/order
            # is preserved verbatim (no re-rendering of indices).
            tail_match = _CITE_TAIL.search(run[-1])
            group_cite = tail_match.group(0).strip() if tail_match else ""
            prose = " ".join(_strip_cite_tail(u) for u in run)
            out_parts.append(f"{prose} {group_cite}".rstrip())
        i = j

    return " ".join(out_parts)
