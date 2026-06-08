"""Resolve dangling `[N]` / `[[note-id]]` citation markers into a real
References appendix.

The shipped report carries bare citation markers — numeric `[N]` (Perplexity
single-index render, grounding/render.py) and `[[note-id]]` / `[[note-id:L42-L58]]`
wiki-links (the off-band anchor map). A reader opening the markdown sees only the
brackets; the source title/url lives in the vault note's frontmatter, not in the
report prose. This module closes that loop: it walks the report in reading order,
collects every distinct marker, looks each up in a `{note_id: SourceRef}` map
(built from the vault notes' frontmatter `title`/`source`), and emits an ordered,
de-duplicated References list. The numeric `[N]` form resolves POSITIONALLY against
the note map's insertion order ([1] = first note), mirroring the standalone gate
(cli/research._standalone_store_from_bodies).

Keyless + deterministic: pure string + frontmatter parsing, no LLM, no key.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from bad_research.grounding.render import extract_citations, parse_line_anchor

# Citation markers in reading order: numeric [N] OR [[note-id]] / [[note-id|alias]]
# / [[note-id:L42-L58]]. Mirrors grounding/render._CITE_TOKEN so the export layer
# and the verifier never disagree on what a cite is.
_MARKER_RE = re.compile(r"\[(\d+)\]|\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")

# A `## Sources` / `# References` heading — everything from here on is already an
# appendix, so we don't double-resolve markers inside an existing references block.
_REFS_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(sources|references)\b", re.IGNORECASE)


@dataclass(frozen=True)
class SourceRef:
    """One resolved source: the note id, its human title, and its url (if any)."""

    note_id: str
    title: str
    url: str | None = None

    def label(self) -> str:
        """The reference-line display text — title, with url appended when present
        and not already the title."""
        if self.url and self.url != self.title:
            return f"{self.title} — {self.url}"
        return self.title


@dataclass
class ResolvedReference:
    """One entry in the rendered References appendix."""

    n: int               # 1-based reference number as it appears in the appendix
    marker: str          # the resolved source key (note_id, or the numeric ordinal)
    ref: SourceRef | None  # None == dangling (no matching source); the gap is disclosed


def source_refs_from_notes(note_bodies: dict[str, str]) -> dict[str, SourceRef]:
    """Build a `{note_id: SourceRef}` map from raw note markdown bodies (with
    frontmatter). Title comes from the frontmatter `title:`, the url from `source:`
    (NoteMeta.source is the fetched url). A note with no frontmatter falls back to
    its id as the title. Insertion order is preserved (drives numeric [N] lookup)."""
    from bad_research.core.frontmatter import parse_frontmatter

    out: dict[str, SourceRef] = {}
    for note_id, raw in note_bodies.items():
        meta, _body = parse_frontmatter(raw or "")
        title = (meta.title or note_id).strip() or note_id
        url = (meta.source or "").strip() or None
        out[note_id] = SourceRef(note_id=note_id, title=title, url=url)
    return out


def source_refs_from_vault(notes_dir: Path) -> dict[str, SourceRef]:
    """Build the `{note_id: SourceRef}` map by reading every `*.md` in a vault's
    notes dir. The note id is the file stem (matches the verifier's note_bodies
    keying in cli/research._verify_report). Returns an empty map if the dir is
    absent."""
    bodies: dict[str, str] = {}
    if notes_dir.is_dir():
        for f in sorted(notes_dir.glob("*.md")):
            bodies[f.stem] = f.read_text(encoding="utf-8")
    return source_refs_from_notes(bodies)


def _strip_existing_refs(report_md: str) -> str:
    """Return the report prose up to (but excluding) any existing `## Sources` /
    `# References` heading — we resolve markers in the body only and emit our own
    appendix (mirrors grounding/gate.strip_sources_section)."""
    lines = report_md.splitlines()
    out: list[str] = []
    for line in lines:
        if _REFS_HEADING_RE.match(line):
            break
        out.append(line)
    return "\n".join(out)


def collect_markers(report_md: str) -> list[str]:
    """Every distinct citation marker in the report body, in first-appearance
    (reading) order. Numeric `[N]` markers are returned as their digit string;
    wiki-links as the `note-id` with any `:L42-L58` line-anchor suffix stripped
    (the suffix is reader-facing display, not a distinct source — A-4)."""
    body = _strip_existing_refs(report_md)
    seen: list[str] = []
    seen_set: set[str] = set()
    for raw_token in extract_citations(body):
        note_id, _ls, _le = parse_line_anchor(raw_token)
        key = note_id if note_id else raw_token
        if key and key not in seen_set:
            seen_set.add(key)
            seen.append(key)
    return seen


def resolve_references(
    report_md: str, sources: dict[str, SourceRef]
) -> list[ResolvedReference]:
    """Map every citation marker in the report to its source.

    Resolution, per marker (in reading order):
      * `[[note-id]]` → `sources[note-id]` directly.
      * numeric `[N]`  → the N-th source in `sources` insertion order (1-based;
        `[1]` = first note), matching the standalone gate's positional `[N]` rule.
      * unresolved     → ResolvedReference.ref is None (a dangling cite — honestly
        flagged in the appendix rather than silently dropped).

    Returns one ResolvedReference per DISTINCT marker, numbered 1..K in reading
    order — that number is what the appendix and the rewritten in-text marker use."""
    ordered_ids = list(sources.keys())
    resolved: list[ResolvedReference] = []
    for i, marker in enumerate(collect_markers(report_md), start=1):
        ref: SourceRef | None
        if marker.isdigit():
            idx = int(marker) - 1
            ref = sources[ordered_ids[idx]] if 0 <= idx < len(ordered_ids) else None
        else:
            ref = sources.get(marker)
        resolved.append(ResolvedReference(n=i, marker=marker, ref=ref))
    return resolved


def render_references_markdown(refs: list[ResolvedReference]) -> str:
    """Render the resolved references as a markdown `## References` appendix.

    Each line is `1. <title> — <url>` (a dangling marker becomes
    `N. [unresolved: <marker>]` so the gap is visible, never hidden). Returns an
    empty string when there are no markers."""
    if not refs:
        return ""
    lines = ["## References", ""]
    for r in refs:
        if r.ref is None:
            lines.append(f"{r.n}. [unresolved citation: `{r.marker}`]")
        else:
            lines.append(f"{r.n}. {r.ref.label()}")
    return "\n".join(lines) + "\n"
