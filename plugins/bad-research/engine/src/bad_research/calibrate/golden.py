"""E1 — the golden-set eval corpus + per-component split + regression gate.

The keystone (Palantir 10%->90% by building evals from historical queries first,
PALANTIR.md:L341-353; CoCounsel's 999/1000 release gate, YC_ROOT_ACCESS.md:L13664):
a STORED corpus of representative research-query fixtures, each with an
Anthropic-style rubric, scored OFFLINE (no keys) through the categorical (E2)
judge, split per component (decompose / retrieval / synthesis), behind a
regression gate every later enhancement runs against.

A golden case is a JSON fixture (drop a file in `golden/` to extend it):

    {
      "id": "...",
      "query": "...",
      "report": "<the markdown report to judge>",
      "corpus": [{"note_id","url","text"}, ...],   # the evidence the report had
      "expected_behavior": ["...", "..."],          # Anthropic-style rubric
      "axes_floor": {"citation": "pass", ...},      # per-axis minimum rail
      "components": {                                # OPTIONAL per-component checks
        "decompose": {"decomp": {...}, "expected_route": "full"},
        "retrieval": {"expect_note_ids": ["n1","n3"]},
        "synthesis": {}                              # judged via the report+corpus
      }
    }

The seed set is built to PASS — it is the baseline the gate defends. Real runs
expand it; nothing here needs a live API call.

IMPORTANT — what this is and is NOT. This is a **regression smoke gate**: it answers
"did a change break a known-good baseline?", NOT "is the output good?". The default
keyless `RubricJudge` does deterministic presence/overlap checks (a citation regex per
line, word-overlap with the corpus, a banned-overclaim wordlist), not quality scoring
and not semantic entailment; the adversarial `requires_llm` fixtures are SKIPPED unless
you pass a real `--llm` judge. So a `pass_rate` of 1.0 here is the expected floor, not
evidence of quality and not a competitive benchmark — do not cite it as one.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bad_research.calibrate.constants import JUDGE_AXES, PASS_RATE_THRESHOLD, RAIL_CREDIT
from bad_research.calibrate.judge import AxisRails, Judge, JudgeRail, JudgeVerdict

# The shipped seed corpus lives next to this module.
GOLDEN_DIR = Path(__file__).parent / "golden"

# Components the eval splits on (the pipeline's deterministic seams).
COMPONENTS = ("decompose", "retrieval", "synthesis")

# Floor a per-corpus pass-rate must clear for the gate to pass (overridable).
GATE_FLOOR = PASS_RATE_THRESHOLD


# ── the case schema ────────────────────────────────────────────────────────────
@dataclass
class GoldenCase:
    id: str
    query: str
    report: str
    corpus: list[dict[str, Any]]
    expected_behavior: list[str]
    axes_floor: dict[str, str] = field(default_factory=dict)
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    # E1-2: a fixture that only the host-model LLMJudge can score (semantic
    # entailment / over-hedge detection). The keyless RubricJudge path SKIPS it.
    requires_llm: bool = False

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> GoldenCase:
        return cls(
            id=str(data["id"]),
            query=str(data["query"]),
            report=str(data.get("report", "")),
            corpus=list(data.get("corpus", [])),
            expected_behavior=list(data.get("expected_behavior", [])),
            axes_floor=dict(data.get("axes_floor", {})),
            components=dict(data.get("components", {})),
            requires_llm=bool(data.get("requires_llm", False)),
        )


def load_golden_corpus(directory: Path | str | None = None) -> list[GoldenCase]:
    """Load every `*.json` fixture in `directory` (default: the shipped GOLDEN_DIR),
    sorted by filename for determinism. A trailing drop-in file is picked up with
    no code change."""
    d = Path(directory) if directory is not None else GOLDEN_DIR
    cases: list[GoldenCase] = []
    for fp in sorted(d.glob("*.json")):
        try:
            cases.append(GoldenCase.from_json(json.loads(fp.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            # Fail closed with a clear message instead of a raw traceback — the
            # drop-in-a-file extensibility path should name the bad fixture.
            raise ValueError(f"golden fixture {fp.name} is malformed: {e}") from e
    return cases


# ── the deterministic, keyless categorical judge ───────────────────────────────
# A citation token in the report, numeric [N] or [[note-id]] wiki-link.
_CITE = re.compile(r"\[\[[^\]]+\]\]|\[\d+\]")
# Overclaim markers a grounded report avoids unless the corpus uses them too.
# Deliberately narrow: only unhedged absolutes that signal fabrication, not
# ordinary technical terms ("guarantee"/"always" appear legitimately in prose).
_OVERCLAIM = ("definitively", "cures all", "cure all", "miracle", "never fails", "100% effective")
_STOP = {
    "the", "a", "an", "is", "are", "of", "to", "and", "in", "on", "for", "it", "this",
    "that", "with", "as", "by", "at", "from", "no", "not", "does", "do", "can", "all",
}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP and len(w) > 2}


class RubricJudge:
    """A categorical (E2) judge that emits real `JudgeRail`s from OFFLINE signals —
    no LLM, no keys, deterministic. It is NOT a stub-that-always-passes: it
    discriminates a grounded, cited report from an uncited / overclaiming one, so
    the regression gate has teeth.

    Per-axis rails:
      - citation: pass iff every non-heading body line carries a cite; fail iff
        the body has zero cites; borderline otherwise.
      - factual: fail on an overclaim word the corpus does not itself use;
        pass iff the report's content words overlap the corpus (grounded);
        borderline on thin overlap.
      - completeness: pass iff the report has body content; borderline if thin.
      - source_quality: pass iff every corpus url looks authoritative-ish (has a
        host); borderline if a source lacks a url.
      - efficiency: pass unless the report is empty (fail) or pathologically long
        (borderline > 6000 chars with little corpus to back it).

    SCOPE (do not oversell): the `factual` axis is a grounding-OVERLAP proxy
    (content-word overlap with the corpus), NOT entailment. It catches uncited /
    ungrounded / overclaiming text, but it CANNOT catch a well-cited claim that
    *contradicts* its source (a report sharing the corpus's vocabulary passes).
    So this keyless gate guards judge + router + retrieval determinism and
    citation/grounding presence — not synthesis-correctness drift. Catching a
    cited contradiction needs the opt-in `LLMJudge` (host-model entailment) path.
    """

    def judge(self, query: str, report: str, corpus: list[dict[str, Any]]) -> JudgeVerdict:
        body = [
            ln.strip()
            for ln in report.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        corpus_text = " ".join(str(c.get("text", "")) for c in corpus)
        corpus_words = _words(corpus_text)

        rails: dict[str, JudgeRail] = {}

        # citation
        cited = [ln for ln in body if _CITE.search(ln)]
        if not body or not cited:
            rails["citation"] = JudgeRail.FAIL
        elif len(cited) == len(body):
            rails["citation"] = JudgeRail.PASS
        else:
            rails["citation"] = JudgeRail.BORDERLINE

        # factual — overclaim guard + grounding overlap
        report_lc = report.lower()
        overclaim = any(w in report_lc and w not in corpus_text.lower() for w in _OVERCLAIM)
        report_words = _words(report)
        overlap = len(report_words & corpus_words) / max(len(report_words), 1)
        if overclaim or not body:
            rails["factual"] = JudgeRail.FAIL
        elif overlap >= 0.20:
            rails["factual"] = JudgeRail.PASS
        else:
            rails["factual"] = JudgeRail.BORDERLINE

        # completeness
        rails["completeness"] = JudgeRail.PASS if len(body) >= 1 else JudgeRail.FAIL

        # source_quality
        urls = [str(c.get("url", "")) for c in corpus]
        if corpus and all("//" in u and u.split("//", 1)[1] for u in urls):
            rails["source_quality"] = JudgeRail.PASS
        elif corpus:
            rails["source_quality"] = JudgeRail.BORDERLINE
        else:
            rails["source_quality"] = JudgeRail.FAIL

        # efficiency
        if not body:
            rails["efficiency"] = JudgeRail.FAIL
        elif len(report) > 6000 and len(corpus) < 3:
            rails["efficiency"] = JudgeRail.BORDERLINE
        else:
            rails["efficiency"] = JudgeRail.PASS

        return JudgeVerdict.from_rails(
            AxisRails.from_raw({a: rails[a].value for a in JUDGE_AXES}),
            rationale="deterministic offline rubric",
        )


# ── per-component checks ($0, deterministic) ────────────────────────────────────
def _check_decompose(spec: dict[str, Any]) -> bool | None:
    """True/False iff a decompose fixture is present (classify_route matches);
    None when the case carries no decompose fixture (not applicable)."""
    if "decomp" not in spec or "expected_route" not in spec:
        return None
    from bad_research.skills.router import classify_route

    return classify_route(spec["decomp"]) == str(spec["expected_route"])


def _check_retrieval(spec: dict[str, Any], corpus: list[dict[str, Any]]) -> bool | None:
    """True iff every expected note_id is present in the (ranked) corpus. None when
    no retrieval fixture is present."""
    expect = spec.get("expect_note_ids")
    if not expect:
        return None
    have = {str(c.get("note_id", "")) for c in corpus}
    return all(str(nid) in have for nid in expect)


def _axes_floor_met(verdict: JudgeVerdict, floor: dict[str, str]) -> bool:
    """Every axis named in the case's `axes_floor` must meet/exceed its minimum
    rail (pass > borderline > fail by RAIL_CREDIT)."""
    got = verdict.rails.as_str_dict()
    for axis, min_rail in floor.items():
        if RAIL_CREDIT.get(got.get(axis, "fail"), 0.0) < RAIL_CREDIT.get(min_rail, 1.0):
            return False
    return True


# ── the corpus eval result + gate ───────────────────────────────────────────────
@dataclass
class CaseResult:
    id: str
    passed: bool
    verdict: JudgeVerdict
    components: dict[str, bool | None]


@dataclass
class CorpusEvalReport:
    cases: list[CaseResult]
    pass_rate: float
    components: dict[str, float]  # per-component pass-rate over applicable cases
    # audit 2026-06-01: count of requires_llm (adversarial) fixtures skipped on the
    # keyless RubricJudge path — surfaced so pass_rate can't read as "all passed" when
    # the hard cases were never scored. 0 on the --llm path (nothing skipped).
    skipped: int = 0

    @property
    def total(self) -> int:
        return len(self.cases)

    def gate_ok(self, *, floor: float = GATE_FLOOR, baseline: float | None = None) -> bool:
        """The regression gate: pass iff the corpus pass-rate clears the floor AND
        (if a stored baseline is given) does not regress below it."""
        clears_floor = self.pass_rate >= floor
        no_regression = baseline is None or self.pass_rate >= baseline
        return clears_floor and no_regression

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_type": "regression-smoke-gate",
            "disclaimer": (
                "Self-graded by the keyless deterministic RubricJudge (presence/overlap "
                "checks), NOT a quality benchmark or competitive measure. Adversarial "
                "(requires_llm) fixtures are skipped unless run with --llm. A pass_rate "
                "of 1.0 is the expected baseline floor, not evidence of quality."
            ),
            "pass_rate": self.pass_rate,
            "total": self.total,
            "skipped": self.skipped,
            "components": self.components,
            "cases": [
                {
                    "id": c.id,
                    "passed": c.passed,
                    "verdict": c.verdict.to_dict(),
                    "components": c.components,
                }
                for c in self.cases
            ],
        }


def evaluate_corpus(
    cases: list[GoldenCase], *, judge: Judge | None = None
) -> CorpusEvalReport:
    """Run every golden case through the categorical judge (default: the keyless
    deterministic RubricJudge) and the per-component split. A case PASSES iff the
    judge verdict passes, its `axes_floor` is met, and no present component check
    fails.

    Pass a real `LLMJudge` to score the corpus through the host model instead —
    the default needs zero keys (the keystone invariant)."""
    j = judge if judge is not None else RubricJudge()
    results: list[CaseResult] = []
    comp_tally: dict[str, list[bool]] = {c: [] for c in COMPONENTS}
    skipped = 0

    for case in cases:
        # E1-2: skip requires_llm fixtures on the keyless RubricJudge path — the
        # deterministic lexical judge cannot score semantic entailment, so these
        # adversarial fixtures are scored only on the opt-in --llm (LLMJudge) path.
        # Counted (not silently dropped) so the report shows the hard cases weren't run.
        if getattr(case, "requires_llm", False) and isinstance(j, RubricJudge):
            skipped += 1
            continue

        verdict = j.judge(case.query, case.report, case.corpus)

        comp_results: dict[str, bool | None] = {}
        dec = _check_decompose(case.components.get("decompose", {}))
        comp_results["decompose"] = dec
        ret = _check_retrieval(case.components.get("retrieval", {}), case.corpus)
        comp_results["retrieval"] = ret
        # synthesis is judged via the report+corpus verdict (+ its axes_floor).
        syn = verdict.passed and _axes_floor_met(verdict, case.axes_floor)
        comp_results["synthesis"] = syn

        for name, ok in comp_results.items():
            if ok is not None:
                comp_tally[name].append(ok)

        case_passed = (
            verdict.passed
            and _axes_floor_met(verdict, case.axes_floor)
            and all(v for v in comp_results.values() if v is not None)
        )
        results.append(
            CaseResult(id=case.id, passed=case_passed, verdict=verdict, components=comp_results)
        )

    pass_rate = round(sum(r.passed for r in results) / len(results), 9) if results else 0.0
    components = {
        name: round(sum(vals) / len(vals), 9) if vals else 1.0
        for name, vals in comp_tally.items()
    }
    return CorpusEvalReport(
        cases=results, pass_rate=pass_rate, components=components, skipped=skipped
    )


__all__ = [
    "COMPONENTS",
    "GATE_FLOOR",
    "GOLDEN_DIR",
    "CaseResult",
    "CorpusEvalReport",
    "GoldenCase",
    "RubricJudge",
    "evaluate_corpus",
    "load_golden_corpus",
]
