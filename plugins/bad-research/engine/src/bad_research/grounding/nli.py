"""Tier-B NLI entailment check -- cross-encoder/nli-deberta-v3-base (frozen).
Local, $0, CPU-fine. dossier 08 §2.2 option 1."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol

# INTERFACES.md frozen constant (the bare HF repo name resolves to
# cross-encoder/nli-deberta-v3-base when loaded).
NLI_MODEL_NAME = "nli-deberta-v3-base"

ENTAILMENT_PASS = 0.70  # dossier §2.2: entailment >= 0.70 -> PASS
CONTRADICTION_FLAG = 0.50  # dossier §2.2: contradiction >= 0.50 -> FLAG hard


class NLILabel(StrEnum):
    ENTAILMENT = "entailment"
    NEUTRAL = "neutral"
    CONTRADICTION = "contradiction"


def classify_nli(scores: dict[str, float]) -> NLILabel:
    """Map a {entailment, neutral, contradiction} softmax to a decision.

    Contradiction is checked before entailment so a quote that says the OPPOSITE
    is never silently passed (dossier §2.2)."""
    if scores.get("contradiction", 0.0) >= CONTRADICTION_FLAG:
        return NLILabel.CONTRADICTION
    if scores.get("entailment", 0.0) >= ENTAILMENT_PASS:
        return NLILabel.ENTAILMENT
    return NLILabel.NEUTRAL


class NLIModel(Protocol):
    """premise = quoted_support, hypothesis = report sentence -> softmax dict."""

    def predict(self, premise: str, hypothesis: str) -> dict[str, float]: ...


class CrossEncoderNLI:
    """Lazy wrapper over the real model. Imported only when actually used so the
    grounding package has no hard torch/transformers dependency at import time."""

    def __init__(self, model_name: str = NLI_MODEL_NAME) -> None:
        self.model_name = model_name
        self._model: Any = None  # the external CrossEncoder is untyped (lazy heavy dep)

    def _ensure(self) -> None:
        if self._model is None:
            from sentence_transformers import CrossEncoder  # type: ignore  # heavy; lazy

            # The cross-encoder/ prefix is the canonical HF path.
            repo = self.model_name
            if "/" not in repo:
                repo = f"cross-encoder/{repo}"
            self._model = CrossEncoder(repo)

    def _label_index(self, name: str) -> int:
        """Resolve a label NAME (entailment/contradiction/neutral) to its logit
        index by reading the model's own config.id2label map ({index: name}).

        This is the anti-silent-inversion fix: we never assume the checkpoint
        orders its logits [contradiction, entailment, neutral]. If a checkpoint
        orders them differently, indexing by position would flip every verdict
        (a contradiction would read as entailment). Indexing by NAME makes the
        physical logit order irrelevant."""
        id2label = self._model.config.id2label  # {0: "CONTRADICTION", ...}
        for idx, label in id2label.items():
            if str(label).lower() == name:
                return int(idx)
        raise ValueError(
            f"label {name!r} not in model id2label={id2label!r}; "
            "the checkpoint does not look like a 3-way NLI model"
        )

    def predict(self, premise: str, hypothesis: str) -> dict[str, float]:
        self._ensure()
        import numpy as np

        logits = self._model.predict([(premise, hypothesis)])[0]
        exp = np.exp(logits - np.max(logits))
        probs = exp / exp.sum()
        # Index the logits by LABEL NAME, not by hardcoded position, so the
        # name-keyed dict the pipeline consumes is correct regardless of how the
        # checkpoint internally orders contradiction/entailment/neutral.
        return {
            "entailment": float(probs[self._label_index("entailment")]),
            "contradiction": float(probs[self._label_index("contradiction")]),
            "neutral": float(probs[self._label_index("neutral")]),
        }
