"""Bridge: BadResearchConfig → BadRunner. The only seam that drives the live pipeline.

Unit tests use a stub runner (Task 11); this is the production path used by
`bad calibrate`. It is `live` (needs keys) — when the pipeline modules (Plans 02-08)
aren't wired or keys are absent, the underlying stages degrade gracefully (honest
empty corpus + no-evidence report), and a hard import failure raises so the CLI
can fall back to the offline stub.
"""

from __future__ import annotations

from typing import Any

from bad_research.calibrate.cost import CostMeter
from bad_research.calibrate.harness import BadRunner, BadRunOutput


def default_runner(config: Any) -> BadRunner:
    """Return a runner that drives the bad-research pipeline for one query.

    `config=None` -> default BadResearchConfig.
    """
    if config is None:
        try:
            from bad_research.config import BadResearchConfig

            config = BadResearchConfig()
        except Exception:  # pragma: no cover - config always loads in practice
            config = None

    def _run(query: str) -> BadRunOutput:
        meter = CostMeter()
        # The production drive: Plan 08's pipeline entrypoint. Imported lazily so
        # the calibration package is importable without the full pipeline (and so
        # unit tests never touch it). The CostMeter is populated at each stage
        # boundary inside run_query via .record(...) / .record_response(...).
        try:
            from bad_research.pipeline import run_query
        except Exception as exc:  # pragma: no cover - exercised only live
            raise RuntimeError(
                "bad-research pipeline not available; run `bad calibrate` with a wired "
                "pipeline + provider keys, or use the offline stub path."
            ) from exc

        result = run_query(query, config=config, cost_meter=meter)  # pragma: no cover
        return BadRunOutput(  # pragma: no cover
            report=result.report,
            corpus=result.corpus,
            cost=meter,
        )

    return _run


__all__ = ["default_runner"]
