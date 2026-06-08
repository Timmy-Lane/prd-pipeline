"""The in-pipeline grader (Stage 12.5) — Claude's `define_outcome` 5-axis judge
turned into a gating loop. Wraps calibrate/judge.py::LLMJudge (the SAME single
strong-model call, NOT an ensemble) and extends its rubric to also emit a
patcher-shaped `findings` array, so the failing-axis defects join the critic +
gate findings the patcher already consumes. Keyless: one host-model call per
round; the loop counter lives in the bad-research-12.5-grader skill. dossier 16 §4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bad_research.calibrate.constants import JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE, JUDGE_TIER
from bad_research.calibrate.judge import JUDGE_SYSTEM, AxisRails, JudgeVerdict, _extract_json
from bad_research.grounding.gate import Finding
from bad_research.llm.base import LLMMessage, LLMProvider

# The one clause appended to the offline JUDGE_SYSTEM rubric to make the verdict
# patcher-compatible (dossier 16 §4.1). The findings array maps each NON-passing
# axis (rail = borderline | fail; E2 — categorical, no numbers) to the
# {failure_mode, severity, location, recommendation} shape the patcher, critics,
# and gate all share.
GRADER_FINDINGS_CLAUSE = (
    'Also output "findings": a JSON array of the SPECIFIC defects behind any axis '
    'whose rail is "borderline" or "fail", each {"axis","severity":"critical|major|'
    'minor","failure_mode":"missing|under-covered|miscited|misordered","location":'
    '"<H2 or sentence>","recommendation":"<surgical fix>"}. A critical finding is '
    "one that, left unfixed, makes an axis fail. Map completeness misses to the "
    "decomposition's required_section_headings + atomic items."
)

GRADER_SYSTEM = JUDGE_SYSTEM + "\n" + GRADER_FINDINGS_CLAUSE


@dataclass
class GraderVerdict:
    """A JudgeVerdict (5 axes + pass) plus the patcher-shaped findings."""

    verdict: JudgeVerdict
    findings: list[Finding]

    @property
    def passed(self) -> bool:
        return self.verdict.passed

    def to_dict(self) -> dict[str, Any]:
        d = self.verdict.to_dict()  # includes rails, pass_rate, passed, rationale
        d["findings"] = [
            {
                "failure_mode": f.failure_mode,
                "severity": f.severity,
                "location": f.location,
                "recommendation": f.recommendation,
            }
            for f in self.findings
        ]
        return d


def _parse_findings(raw: dict[str, Any]) -> list[Finding]:
    """Translate the judge's `findings` array into patcher-shaped Finding rows.
    Tolerant: a non-list or a malformed row degrades to fewer/zero findings, never
    an exception (the axes still gate even if findings are unusable)."""
    rows = raw.get("findings")
    if not isinstance(rows, list):
        return []
    out: list[Finding] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        severity = str(r.get("severity", "major"))
        if severity not in ("critical", "major", "minor"):
            severity = "major"
        out.append(
            Finding(
                failure_mode=str(r.get("failure_mode", "under-covered")),
                severity=severity,
                location=str(r.get("location", "")),
                recommendation=str(r.get("recommendation", "")),
            )
        )
    return out


@dataclass
class Grader:
    """In-pipeline grader over an LLMProvider. ONE host-model call per round."""

    provider: LLMProvider
    tier: str = JUDGE_TIER

    def grade(self, query: str, report: str, corpus: list[dict[str, Any]]) -> GraderVerdict:
        corpus_block = "\n".join(
            f"[{c.get('note_id', i)}] {c.get('url', '')}\n{c.get('text', '')[:1200]}"
            for i, c in enumerate(corpus)
        )
        user = (
            f"QUERY:\n{query}\n\n"
            f"CORPUS (the evidence the report had access to):\n{corpus_block}\n\n"
            f"REPORT TO JUDGE:\n{report}\n\n"
            "Score now, then list the defect findings. JSON only."
        )
        resp = self.provider.complete(
            [
                LLMMessage(role="system", content=GRADER_SYSTEM),
                LLMMessage(role="user", content=user),
            ],
            tier=self.tier,  # type: ignore[arg-type]
            max_tokens=JUDGE_MAX_TOKENS,
            temperature=JUDGE_TEMPERATURE,
        )
        raw = _extract_json(resp.text)
        rails = AxisRails.from_raw(raw)
        verdict = JudgeVerdict.from_rails(rails, rationale=str(raw.get("rationale", "")))
        return GraderVerdict(verdict=verdict, findings=_parse_findings(raw))


__all__ = ["GRADER_FINDINGS_CLAUSE", "GRADER_SYSTEM", "Grader", "GraderVerdict"]
