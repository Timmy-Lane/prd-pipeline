"""Offline calibration harness (SPEC §14). Never a per-run gate.

`bad calibrate <query>` runs a query through bad-research, meters its 5-component
cost, and scores the report on the 5-axis LLM-judge rubric — comparing against
key-gated baselines (hyperresearch / Perplexity / Grok) when their keys are set.
The offline path (StubJudge + a stub runner) runs with zero keys and zero network.
"""

from __future__ import annotations

from bad_research.calibrate.baselines import (
    Baseline,
    BaselineResult,
    BaselineUnavailable,
    available_baselines,
)
from bad_research.calibrate.cost import CostMeter
from bad_research.calibrate.harness import (
    BadRunner,
    BadRunOutput,
    CalibrationReport,
    SystemResult,
    run_calibration,
)
from bad_research.calibrate.judge import (
    AxisRails,
    Judge,
    JudgeRail,
    JudgeVerdict,
    LLMJudge,
    StubJudge,
)

__all__ = [
    "AxisRails",
    "BadRunOutput",
    "BadRunner",
    "Baseline",
    "BaselineResult",
    "BaselineUnavailable",
    "CalibrationReport",
    "CostMeter",
    "Judge",
    "JudgeRail",
    "JudgeVerdict",
    "LLMJudge",
    "StubJudge",
    "SystemResult",
    "available_baselines",
    "run_calibration",
]
