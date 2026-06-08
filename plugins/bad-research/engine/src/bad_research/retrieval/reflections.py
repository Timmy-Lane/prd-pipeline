"""Distilled-reflection memory — the append-only short-term memory the research
loop carries between width-sweep rounds (Tavily, E5 / steal-list #1).

The pattern: keep only the DISTILLED reflections between iterations, not the raw
sources. Each round/locus contributes one record holding ≤3 distilled claim
bullets (drawn from the fetcher's `claims-*.json`, NOT raw text), the open gaps,
and the `cited_note_ids` that point back to the vault. The re-retrieve decision
and the next-round query planning read THIS file + `open_gaps` — never the raw
corpus — so inter-round token growth is linear (n·m) instead of quadratic
(n·m·(m+1)/2): a ~-66% token win vs re-reading the corpus each round.

The raw note bodies stay on disk in the vault. They are re-injected ONLY at
synthesis, and only for the `cited_note_ids` a section will actually cite —
Tavily's "re-inject raw only at the end". That preserves the verbatim
`quoted_support` spans the `uncited-gate` / `recitation-gate` / `anchors.py`
grounding lane needs, while keeping the mid-pipeline context lean.

The artifact is plain Markdown so the host model can read it directly without a
parser; this helper is the deterministic ($0, keyless) read/append/compact lane
the Python side and tests use.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── frozen constants ─────────────────────────────────────────────────────────
# ≤3 distilled claim bullets per source/round — Tavily distilled-reflection
# (core/08:2617-2620). Distillation, not summarization: each bullet is a claim
# from claims-*.json, never raw prose.
REFLECTION_BULLET_CAP = 3

# ≤10K-token synthesis-context ceiling — Chroma context-rot
# (YC_ROOT_ACCESS.md:L14075). The distilled context fed to synthesis is capped
# here; raw spans are re-injected on top, targeted to the cited note_ids only.
SYNTHESIS_CONTEXT_TOKEN_CEILING = 10_000

# A cheap, deterministic token estimate (no tokenizer dep): ~4 chars/token, the
# standard English heuristic. Used only to decide when to compact — never billed.
_CHARS_PER_TOKEN = 4

_RECORD_RE = re.compile(
    r"^<!--\s*reflection\s+(\{.*?\})\s*-->$", re.MULTILINE
)


@dataclass
class Reflection:
    """One width-sweep round / locus reflection.

    `key_findings` are ≤3 distilled claim bullets (from claims-*.json), NOT raw
    note bodies. `cited_note_ids` point back to the vault for synthesis-time raw
    re-injection.
    """

    round: int
    sub_question: str
    key_findings: list[str] = field(default_factory=list)
    open_gaps: list[str] = field(default_factory=list)
    cited_note_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.round < 0:
            raise ValueError(f"round must be >= 0, got {self.round}")
        # enforce the ≤3 distilled-bullet cap at construction so an over-eager
        # distiller can never balloon the reflection back toward the raw corpus.
        if len(self.key_findings) > REFLECTION_BULLET_CAP:
            self.key_findings = self.key_findings[:REFLECTION_BULLET_CAP]

    # ── serialization ────────────────────────────────────────────────────────
    def to_block(self) -> str:
        """Render as a Markdown block carrying a machine-parseable HTML comment.

        The human-readable bullets are the body; the trailing comment is the
        exact-round-trip payload the helper re-parses. The model reads the body;
        the Python lane reads the comment."""
        payload = {
            "round": self.round,
            "sub_question": self.sub_question,
            "key_findings": self.key_findings,
            "open_gaps": self.open_gaps,
            "cited_note_ids": self.cited_note_ids,
        }
        lines = [f"### Round {self.round} — {self.sub_question}", ""]
        if self.key_findings:
            lines.append("**Key findings (distilled):**")
            lines += [f"- {b}" for b in self.key_findings]
            lines.append("")
        if self.open_gaps:
            lines.append("**Open gaps:**")
            lines += [f"- {g}" for g in self.open_gaps]
            lines.append("")
        if self.cited_note_ids:
            lines.append("**Cited notes (vault):** " + ", ".join(self.cited_note_ids))
            lines.append("")
        lines.append(f"<!-- reflection {json.dumps(payload, ensure_ascii=False)} -->")
        return "\n".join(lines)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Reflection:
        return cls(
            round=int(payload.get("round", 0)),
            sub_question=str(payload.get("sub_question", "")),
            key_findings=list(payload.get("key_findings", [])),
            open_gaps=list(payload.get("open_gaps", [])),
            cited_note_ids=list(payload.get("cited_note_ids", [])),
        )


class ReflectionLog:
    """Append-only reflections artifact at `research/temp/reflections.md`.

    `append` adds one record; `read` parses them back in file order; `open_gaps`
    / `cited_note_ids` aggregate across rounds for the planner / synthesizer;
    `compact` drops the OLDEST records until the file is under the ≤10K-token
    synthesis ceiling (keeping the most-recent reflections, which carry the live
    gaps)."""

    _HEADER = "# Reflections — distilled short-term memory\n\n"

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    # ── append ─────────────────────────────────────────────────────────────
    def append(self, rec: Reflection) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        block = rec.to_block()
        if not self.path.exists():
            self.path.write_text(self._HEADER + block + "\n", encoding="utf-8")
            return
        existing = self.path.read_text(encoding="utf-8")
        sep = "" if existing.endswith("\n") else "\n"
        self.path.write_text(existing + sep + "\n" + block + "\n", encoding="utf-8")

    # ── read ───────────────────────────────────────────────────────────────
    def read(self) -> list[Reflection]:
        if not self.path.exists():
            return []
        text = self.path.read_text(encoding="utf-8")
        out: list[Reflection] = []
        for m in _RECORD_RE.finditer(text):
            try:
                payload = json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
            out.append(Reflection.from_payload(payload))
        return out

    # ── aggregates the loop reads INSTEAD of the raw corpus ──────────────────
    def open_gaps(self) -> list[str]:
        """All open gaps across rounds, in order. The next-round query planner
        reads this — not the raw corpus — to decide what to search next."""
        gaps: list[str] = []
        for r in self.read():
            gaps.extend(r.open_gaps)
        return gaps

    def cited_note_ids(self) -> list[str]:
        """The de-duplicated, order-preserving union of every reflection's cited
        note_ids. Synthesis re-injects raw bodies ONLY for these ids."""
        seen: set[str] = set()
        out: list[str] = []
        for r in self.read():
            for nid in r.cited_note_ids:
                if nid not in seen:
                    seen.add(nid)
                    out.append(nid)
        return out

    # ── synthesis-context budget (Chroma ≤10K ceiling) ───────────────────────
    def estimated_tokens(self) -> int:
        """Cheap char/4 token estimate of the whole artifact ($0, no tokenizer)."""
        if not self.path.exists():
            return 0
        return len(self.path.read_text(encoding="utf-8")) // _CHARS_PER_TOKEN

    def within_synthesis_ceiling(self) -> bool:
        return self.estimated_tokens() <= SYNTHESIS_CONTEXT_TOKEN_CEILING

    def compact(self) -> list[Reflection]:
        """Drop the OLDEST reflections until the artifact is under the ≤10K-token
        synthesis ceiling, keeping the most-recent records (they carry the live
        gaps the planner still needs). Rewrites the file and returns the kept
        records. A no-op when already under the ceiling."""
        recs = self.read()
        if self.estimated_tokens() <= SYNTHESIS_CONTEXT_TOKEN_CEILING:
            return recs
        kept = list(recs)
        # peel from the front (oldest) until the rendered file fits
        while kept and self._render_tokens(kept) > SYNTHESIS_CONTEXT_TOKEN_CEILING:
            kept.pop(0)
        self._rewrite(kept)
        return kept

    # ── internals ────────────────────────────────────────────────────────────
    def _render(self, recs: list[Reflection]) -> str:
        body = "\n\n".join(r.to_block() for r in recs)
        return self._HEADER + body + ("\n" if recs else "")

    def _render_tokens(self, recs: list[Reflection]) -> int:
        return len(self._render(recs)) // _CHARS_PER_TOKEN

    def _rewrite(self, recs: list[Reflection]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self._render(recs), encoding="utf-8")


__all__ = [
    "REFLECTION_BULLET_CAP",
    "SYNTHESIS_CONTEXT_TOKEN_CEILING",
    "Reflection",
    "ReflectionLog",
]
