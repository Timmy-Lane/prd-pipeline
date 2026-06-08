"""Grounding-recall harness — measure the KEYLESS deterministic guards' catch-rate
against deterministic mutations of known-grounded claims, with an honest disclosure
of the band the keyless path does NOT decide.

WHY (honest version). The keyless grounding path accepts a cited sentence as
SUPPORTED via the near-verbatim ENTAILMENT shortcut ONLY when it is lexically
near-verbatim AND agrees on numbers, negation, and direction with the cited span
(grounding/gate.py: `claim_quote_overlap >= CLAIM_QUOTE_OVERLAP_SKIP` and NOT
`numeric_or_negation_mismatch`). This harness takes grounded (claim, quote) pairs,
applies deterministic MUTATIONS that should break support, and measures — purely
keyless, no FakeLLM scripting a verdict — how each mutation class fares against the
deterministic guards.

Two outcomes are tracked SEPARATELY, because they are NOT the same strength of
guarantee:
  * AFFIRMATIVE CATCH — `numeric_or_negation_mismatch` (number / date / negation /
    antonym-directional, plus an unsupported APPENDED number) positively FIRES. The
    keyless layer itself identifies the contradiction; no host call is needed. This
    is the real keyless catch-rate.
  * ESCALATE-ONLY — no deterministic signal fires, but lexical overlap falls below
    the near-verbatim bar, so the pair is merely DENIED the shortcut and handed to
    the host-model judge (keyless-no-host: flagged `needs_host_judgment`). The
    keyless layer does NOT decide these — it defers. Counting a deferral as a "catch"
    would overstate the keyless guarantee, so escalate-only is reported apart from
    affirmative catch and is NOT credited to the keyless catch-rate.

HONESTY (a prior reviewer's note). A FakeLLM that scripts the Tier-C verdict makes
the "catch" circular, so this harness NEVER calls an LLM. The AFFIRMATIVE layer
catches NUMBER, NEGATION, ANTONYM/DIRECTIONAL flips, and UNSUPPORTED-APPEND (the
appended fact carries a number the span lacks → numeric mismatch fires). It does NOT
affirmatively catch a pure PARAPHRASE-CONTRADICTION that keeps numbers/negation/
direction intact: that pair fires NO deterministic signal and is only ESCALATED to
the host judge — exactly the band the keyless path cannot decide on its own, so its
keyless AFFIRMATIVE catch-rate is 0 BY DESIGN. The report labels every mutation's
affirmative catch-rate, separates the escalate-only column, AND discloses the
uncaught paraphrase band explicitly; it is a regression floor + an honest published
metric, NOT a "we catch everything" claim.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from .gate import (
    CLAIM_QUOTE_OVERLAP_SKIP,
    claim_quote_overlap,
    numeric_or_negation_mismatch,
)


class Mutation(StrEnum):
    """The deterministic mutation classes applied to a grounded claim."""

    NUMBER_FLIP = "number_flip"
    NEGATION_FLIP = "negation_flip"
    ANTONYM_FLIP = "antonym_flip"
    UNSUPPORTED_APPEND = "unsupported_append"
    # The disclosed-uncaught band: a semantic contradiction phrased as a paraphrase,
    # keeping numbers/negation/direction intact and overlap below the near-verbatim
    # bar. NO deterministic signal fires — the keyless layer only ESCALATES it to the
    # host judge, so its keyless AFFIRMATIVE catch-rate is 0 BY DESIGN.
    PARAPHRASE_CONTRADICTION = "paraphrase_contradiction"


# Mutation classes the KEYLESS deterministic layer AFFIRMATIVELY catches (a guard
# positively fires). The paraphrase-contradiction band is deliberately excluded — it
# is the disclosed gap (escalate-only, no affirmative signal).
DETERMINISTIC_CATCHABLE: frozenset[Mutation] = frozenset({
    Mutation.NUMBER_FLIP,
    Mutation.NEGATION_FLIP,
    Mutation.ANTONYM_FLIP,
    Mutation.UNSUPPORTED_APPEND,
})


@dataclass(frozen=True)
class GroundedClaim:
    """One known-grounded fixture: a claim that the quote genuinely supports."""

    claim: str
    quote: str


@dataclass
class MutationCase:
    """A single mutated claim derived from a grounded fixture."""

    mutation: Mutation
    original_claim: str
    mutated_claim: str
    quote: str
    applied: bool  # False when the mutation didn't apply to this fixture (skipped)


# ── deterministic mutators ────────────────────────────────────────────────────
_NUM_RE = re.compile(r"\d[\d,]*\.?\d*")
# Antonym swaps reused from the gate's lexicon shape (a subset that reads naturally
# in prose); the gate's `directional_antonym_mismatch` recognises both poles.
_ANTONYM_SWAP = {
    "grew": "declined", "rose": "fell", "increased": "decreased",
    "higher": "lower", "more": "less", "gained": "lost",
    "ratified": "rejected", "approved": "denied", "improved": "worsened",
    "expanded": "contracted",
}


def _mutate_number(claim: str) -> str | None:
    """Flip the FIRST number in the claim to a different value (append '9' to its
    leading digit-run, guaranteeing a value the quote lacks). None if no number."""
    m = _NUM_RE.search(claim)
    if not m:
        return None
    original = m.group(0)
    # Change the integer part deterministically: prepend '9' so it is a new number.
    mutated = "9" + original if not original.startswith("9") else "1" + original
    return claim[: m.start()] + mutated + claim[m.end():]


def _mutate_negation(claim: str) -> str | None:
    """Insert a negation after the first auxiliary/verb-ish anchor so polarity flips.
    Conservative: inserts ' did not' / ' does not' / ' not' deterministically. None
    if no safe insertion point is found."""
    # Flip the first occurrence of a copula / common verb to its negated form.
    patterns = [
        (re.compile(r"\b(is)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(was)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(are)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(were)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(has)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(have)\b", re.IGNORECASE), r"\1 not"),
        (re.compile(r"\b(can)\b", re.IGNORECASE), r"\1not"),
    ]
    for pat, repl in patterns:
        if pat.search(claim):
            return pat.sub(repl, claim, count=1)
    # Fall back: prefix with a hard negation so polarity differs from the quote.
    return "It is not the case that " + claim[0].lower() + claim[1:]


def _mutate_antonym(claim: str) -> str | None:
    """Swap the first directional/antonym term for its opposite. None if the claim
    contains no swappable term."""
    tokens = re.findall(r"[A-Za-z]+|\W+", claim)
    for i, tok in enumerate(tokens):
        low = tok.lower()
        if low in _ANTONYM_SWAP:
            swapped = _ANTONYM_SWAP[low]
            # Preserve leading capitalisation.
            if tok[:1].isupper():
                swapped = swapped.capitalize()
            tokens[i] = swapped
            return "".join(tokens)
    return None


def _mutate_unsupported_append(claim: str) -> str:
    """Append an unsupported clause (a fabricated quantified fact the quote can't
    cover). Lowers the claim→quote overlap below the near-verbatim bar."""
    return (
        claim.rstrip(". ")
        + ", and this single factor alone accounted for 87.3% of the total observed effect worldwide."
    )


def _mutate_paraphrase_contradiction(claim: str) -> str:
    """A semantic contradiction phrased WITHOUT a number/negation/antonym flip and
    rephrased so lexical overlap with the quote drops — the disclosed band the
    keyless deterministic layer cannot decide (it escalates to the host judge).

    Deterministic: reword the claim's assertion into an opposing synonym-level
    statement that shares few content tokens with the quote, using no negation
    particle and no antonym lexicon word."""
    return (
        "Independent reassessment instead attributes the outcome to wholly distinct "
        "underlying mechanisms than those summarised above."
    )


_MUTATORS = {
    Mutation.NUMBER_FLIP: _mutate_number,
    Mutation.NEGATION_FLIP: _mutate_negation,
    Mutation.ANTONYM_FLIP: _mutate_antonym,
    Mutation.UNSUPPORTED_APPEND: _mutate_unsupported_append,
    Mutation.PARAPHRASE_CONTRADICTION: _mutate_paraphrase_contradiction,
}


def build_cases(claims: list[GroundedClaim]) -> list[MutationCase]:
    """Apply every mutation class to every grounded fixture. A mutation that does
    not apply to a given fixture (e.g. number-flip on a number-free claim) is
    recorded with applied=False and excluded from that class's catch-rate."""
    cases: list[MutationCase] = []
    for gc in claims:
        for mutation, mutator in _MUTATORS.items():
            mutated = mutator(gc.claim)
            if mutated is None or mutated == gc.claim:
                cases.append(MutationCase(mutation, gc.claim, gc.claim, gc.quote, applied=False))
            else:
                cases.append(MutationCase(mutation, gc.claim, mutated, gc.quote, applied=True))
    return cases


def affirmatively_caught(claim: str, quote: str) -> bool:
    """True iff the KEYLESS deterministic layer AFFIRMATIVELY catches the mutated
    claim — i.e. `numeric_or_negation_mismatch` (number/date/negation/antonym-
    directional, or an unsupported appended number) POSITIVELY fires. This is the
    real keyless catch: the layer identifies the contradiction itself, no host call.

    NO LLM is consulted — purely `numeric_or_negation_mismatch` from grounding/gate.py."""
    return numeric_or_negation_mismatch(claim, quote)


def escalated_only(claim: str, quote: str) -> bool:
    """True iff the pair is DENIED the near-verbatim shortcut but NOT affirmatively
    caught — no deterministic signal fired, yet lexical overlap fell below the
    near-verbatim bar, so the pair is merely escalated to the host judge (keyless-
    no-host: `needs_host_judgment`). The keyless layer does NOT decide these; it
    defers. Distinct from `affirmatively_caught` on purpose — a deferral is not a
    catch (counting it as one would overstate the keyless guarantee)."""
    if affirmatively_caught(claim, quote):
        return False
    return claim_quote_overlap(claim, quote) < CLAIM_QUOTE_OVERLAP_SKIP


@dataclass
class MutationReport:
    """Per-mutation outcome over the applied cases: affirmative catch vs escalate-only."""

    mutation: Mutation
    n_applied: int
    n_affirmed: int       # keyless layer affirmatively caught (a guard fired)
    n_escalated: int      # denied the shortcut but only deferred to the host judge
    deterministic_band: bool  # True = keyless layer is EXPECTED to affirmatively catch

    @property
    def affirmed_rate(self) -> float:
        """The keyless AFFIRMATIVE catch-rate (the honest headline metric)."""
        return (self.n_affirmed / self.n_applied) if self.n_applied else 0.0

    @property
    def escalated_rate(self) -> float:
        return (self.n_escalated / self.n_applied) if self.n_applied else 0.0


@dataclass
class RecallReport:
    """The full harness result + the honest uncaught-band disclosure."""

    per_mutation: list[MutationReport]
    n_grounded_unchanged_accepted: int  # grounded (unmutated) pairs the layer accepts
    n_grounded_total: int
    disclosure: str = field(default="")

    def deterministic_catch_rate(self) -> float:
        """AFFIRMATIVE catch-rate over the deterministic-catchable bands only (the
        regression floor applies to THIS, never to the disclosed paraphrase band)."""
        applied = sum(r.n_applied for r in self.per_mutation if r.deterministic_band)
        affirmed = sum(r.n_affirmed for r in self.per_mutation if r.deterministic_band)
        return (affirmed / applied) if applied else 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "per_mutation": [
                {
                    "mutation": str(r.mutation),
                    "n_applied": r.n_applied,
                    "n_affirmed_caught": r.n_affirmed,
                    "n_escalated_only": r.n_escalated,
                    "affirmed_catch_rate": round(r.affirmed_rate, 4),
                    "escalated_only_rate": round(r.escalated_rate, 4),
                    "deterministic_band": r.deterministic_band,
                }
                for r in self.per_mutation
            ],
            "deterministic_catch_rate": round(self.deterministic_catch_rate(), 4),
            "grounded_unchanged_accepted": self.n_grounded_unchanged_accepted,
            "grounded_total": self.n_grounded_total,
            "disclosure": self.disclosure,
        }


# The regression floor: the keyless deterministic guards must catch EVERY case in
# the deterministic-catchable bands (number/negation/antonym/unsupported-append).
# A drop below this floor means a guard regressed. The paraphrase-contradiction band
# is EXCLUDED from the floor — it is the disclosed gap, expected to be uncaught
# keyless.
REGRESSION_FLOOR = 1.0

_DISCLOSURE = (
    "DISCLOSED UNCAUGHT BAND: the keyless deterministic guards AFFIRMATIVELY catch "
    "number, negation, antonym/directional flips, and unsupported-append (the "
    "appended fact carries a number the span lacks → numeric mismatch fires). They do "
    "NOT affirmatively catch a pure paraphrase-contradiction that keeps numbers, "
    "negation, and direction intact: that pair fires NO deterministic signal and is "
    "only ESCALATED to the host-model judge (the keyless path flags it "
    "`needs_host_judgment`), so its keyless AFFIRMATIVE catch-rate is 0 BY DESIGN — a "
    "deferral, not a catch. No LLM is consulted by this harness, so the reported "
    "catch-rates are not circular (a prior reviewer's note: a FakeLLM scripting the "
    "verdict would be)."
)


def run_recall(claims: list[GroundedClaim]) -> RecallReport:
    """Run the harness over grounded fixtures and produce the honest per-mutation
    report (affirmative catch vs escalate-only). Purely deterministic + keyless (no LLM)."""
    cases = build_cases(claims)
    per: list[MutationReport] = []
    for mutation in Mutation:
        applied_cases = [c for c in cases if c.mutation == mutation and c.applied]
        n_affirmed = sum(
            1 for c in applied_cases if affirmatively_caught(c.mutated_claim, c.quote)
        )
        n_escalated = sum(
            1 for c in applied_cases if escalated_only(c.mutated_claim, c.quote)
        )
        per.append(MutationReport(
            mutation=mutation,
            n_applied=len(applied_cases),
            n_affirmed=n_affirmed,
            n_escalated=n_escalated,
            deterministic_band=mutation in DETERMINISTIC_CATCHABLE,
        ))

    # Sanity lane: the UNMUTATED grounded pairs should be ACCEPTED (the shortcut
    # taken) — i.e. the guard does not false-positive on genuinely-supported
    # near-verbatim claims (neither affirmatively caught nor escalated). Reported so a
    # regression that starts rejecting good claims is visible.
    n_accepted = sum(
        1 for gc in claims
        if not affirmatively_caught(gc.claim, gc.quote) and not escalated_only(gc.claim, gc.quote)
    )

    return RecallReport(
        per_mutation=per,
        n_grounded_unchanged_accepted=n_accepted,
        n_grounded_total=len(claims),
        disclosure=_DISCLOSURE,
    )


# ── built-in fixtures ─────────────────────────────────────────────────────────
# Known-grounded (claim, quote) pairs: each claim is near-verbatim of its quote and
# genuinely supported (numbers/negation/direction agree). The fixtures are crafted so
# every deterministic mutation applies (each has a number, a copula/verb for the
# negation flip, and a directional/antonym term for the antonym flip).
_BUILTIN_FIXTURES: list[GroundedClaim] = [
    GroundedClaim(
        claim="Global solar capacity grew 24 percent in 2023.",
        quote="Global solar capacity grew 24 percent in 2023, the report states.",
    ),
    GroundedClaim(
        claim="The vaccine is approved for 12 countries and improved outcomes.",
        quote="The vaccine is approved for 12 countries and improved patient outcomes.",
    ),
    GroundedClaim(
        claim="Inflation rose 3 percent and the index increased to 118 points.",
        quote="Inflation rose 3 percent and the index increased to 118 points last quarter.",
    ),
    GroundedClaim(
        claim="The treaty was ratified by 5 states and expanded trade.",
        quote="The treaty was ratified by 5 member states and expanded regional trade.",
    ),
]


def builtin_fixtures() -> list[GroundedClaim]:
    """The built-in grounded fixtures used when no --fixtures file is given."""
    return list(_BUILTIN_FIXTURES)


def load_fixtures(path: Path) -> list[GroundedClaim]:
    """Load grounded fixtures from a JSON file: a list of {claim, quote} dicts."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [GroundedClaim(claim=d["claim"], quote=d["quote"]) for d in data]


def format_report_text(report: RecallReport, *, floor: float = REGRESSION_FLOOR) -> str:
    """Human-readable per-mutation summary (affirmative catch + escalate-only) + the
    honest disclosure + the regression-floor verdict."""
    lines = [
        "Grounding-recall harness — KEYLESS deterministic catch-rate",
        "=" * 58,
        f"grounded fixtures: {report.n_grounded_total} "
        f"(unmutated accepted: {report.n_grounded_unchanged_accepted}/{report.n_grounded_total})",
        "",
        "per-mutation outcome (affirmative keyless catch | escalate-only deferral):",
    ]
    for r in report.per_mutation:
        tag = "" if r.deterministic_band else "  [DISCLOSED uncaught band]"
        lines.append(
            f"  {r.mutation:<26} affirmed {r.n_affirmed}/{r.n_applied} = {r.affirmed_rate:6.1%}"
            f"   escalated-only {r.n_escalated}/{r.n_applied}{tag}"
        )
    det = report.deterministic_catch_rate()
    lines += [
        "",
        f"deterministic-band AFFIRMATIVE catch-rate (regression-gated): {det:.1%}",
        f"regression floor: {floor:.1%}  ->  "
        + ("PASS" if det >= floor else "FAIL (a deterministic guard regressed)"),
        "",
        report.disclosure,
    ]
    return "\n".join(lines)


__all__ = [
    "DETERMINISTIC_CATCHABLE",
    "REGRESSION_FLOOR",
    "GroundedClaim",
    "Mutation",
    "MutationCase",
    "MutationReport",
    "RecallReport",
    "affirmatively_caught",
    "build_cases",
    "builtin_fixtures",
    "escalated_only",
    "format_report_text",
    "load_fixtures",
    "run_recall",
]
