"""Calibration harness — run a query through bad-research, judge it, compare to
baselines, emit a CalibrationReport. OFFLINE (SPEC §14): never a per-run gate.

Deferred grounding-calibration items (Plan 06 hardening — to MEASURE in the live
calibration run, NOT change here):
  - `is_factual_claim` coverage: fraction of report sentences the claim-extractor
    actually classifies as factual (vs missed) — surfaces under-extraction.
  - NLI hypothesis construction: whether the entailment hypothesis is the claim
    sentence vs a templated paraphrase — affects SUPPORTED/CONTRADICTED accuracy.
  - fuzzy-anchor verifiability: how often `extract_spans` finds a quote anchor by
    fuzzy match vs exact, and the false-anchor rate that implies.
  - NLI label-order: confirm the model's (entailment/neutral/contradiction) index
    order maps correctly to VerifyVerdict (a silent swap inverts every verdict).
These feed the `factual` + `citation` judge axes; the live run should log them as
calibration diagnostics so the separate grounding-hardening pass has targets.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from bad_research.calibrate.baselines import Baseline, BaselineUnavailable
from bad_research.calibrate.cost import CostMeter
from bad_research.calibrate.judge import Judge, JudgeVerdict


@dataclass
class BadRunOutput:
    """What the bad-research runner returns for one query."""

    report: str
    corpus: list[dict[str, object]]
    cost: CostMeter


# A runner is any callable query -> BadRunOutput. The CLI supplies the real one
# (drives the pipeline); tests supply a fake. Keeps the harness host-agnostic.
BadRunner = Callable[[str], BadRunOutput]


@dataclass
class SystemResult:
    name: str
    report: str
    verdict: JudgeVerdict
    cost_usd: float = 0.0


@dataclass
class CalibrationReport:
    query: str
    bad: SystemResult
    baselines: list[SystemResult] = field(default_factory=list)

    def delta_vs(self, baseline_name: str) -> float:
        """bad-research pass-rate minus the named baseline's (positive = we win)."""
        for b in self.baselines:
            if b.name == baseline_name:
                return round(self.bad.verdict.pass_rate - b.verdict.pass_rate, 9)
        raise KeyError(baseline_name)

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query,
            "bad": {
                "verdict": self.bad.verdict.to_dict(),
                "cost": self.bad.cost_usd,
            },
            "baselines": [
                {"name": b.name, "verdict": b.verdict.to_dict(), "cost": b.cost_usd}
                for b in self.baselines
            ],
            "deltas": {b.name: self.delta_vs(b.name) for b in self.baselines},
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        v = self.bad.verdict
        lines = [
            "# Calibration Report",
            "",
            f"**Query:** {self.query}",
            "",
            "## bad-research",
            f"- pass-rate: **{v.pass_rate:.3f}** — {'PASS' if v.passed else 'FAIL'}",
            f"- cost: **${self.bad.cost_usd:.4f}**",
            "- axes (categorical rails):",
        ]
        for axis, rail in v.rails.as_str_dict().items():
            lines.append(f"  - {axis}: {rail}")
        lines.append(f"- rationale: {v.rationale}")
        if self.baselines:
            lines += [
                "",
                "## Baselines",
                "",
                "| system | pass-rate | pass | cost | delta (bad-base) |",
                "|---|---|---|---|---|",
            ]
            for b in self.baselines:
                lines.append(
                    f"| {b.name} | {b.verdict.pass_rate:.3f} | "
                    f"{'PASS' if b.verdict.passed else 'FAIL'} | ${b.cost_usd:.4f} | "
                    f"{self.delta_vs(b.name):+.3f} |"
                )
        else:
            lines += ["", "_No external baselines available (key-gated; offline run)._"]
        return "\n".join(lines) + "\n"


def run_calibration(
    query: str,
    *,
    runner: BadRunner,
    baselines: list[Baseline],
    judge: Judge,
) -> CalibrationReport:
    """Run + judge bad-research and every available baseline on one query."""
    out = runner(query)
    bad_verdict = judge.judge(query, out.report, out.corpus)
    bad = SystemResult(
        name="bad-research",
        report=out.report,
        verdict=bad_verdict,
        cost_usd=out.cost.total_usd(),
    )

    baseline_results: list[SystemResult] = []
    for b in baselines:
        try:
            if not b.available():
                continue
            br = b.run(query)
        except (BaselineUnavailable, NotImplementedError):
            continue
        bv = judge.judge(query, br.report, br.corpus)
        baseline_results.append(SystemResult(name=br.name, report=br.report, verdict=bv))

    return CalibrationReport(query=query, bad=bad, baselines=baseline_results)


__all__ = [
    "BadRunOutput",
    "BadRunner",
    "CalibrationReport",
    "SystemResult",
    "run_calibration",
]
