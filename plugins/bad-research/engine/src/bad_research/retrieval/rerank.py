"""Rerankers behind the Reranker Protocol — KEYLESS.

Default: ClaudeCodeReranker — the host model (no API key) scores each candidate
0..1 with the SINGLE frozen LLM-rerank prompt (dossier 15 §5.3 / 13 §4.1). There
is exactly ONE rerank prompt in the codebase: KR-2 froze it as
``web/search/rerank.py::LLM_RERANK_PROMPT_SYSTEM`` (with the injection preamble
baked in) and froze a hardened ``_parse_scores`` that degrades malformed host
output to original order. This module REUSES both verbatim (imported, not
re-authored) so the search reranker (HostModelReranker) and the vault reranker
(ClaudeCodeReranker) speak the identical contract — search vs. vault candidates,
same prompt, same parser.

One batched call, pointwise JSON output, temperature=0, ~800-char truncation,
graceful 0.0 on any parse/call failure (the three-tier blend then leans on the
`initial` score so no candidate is silently dropped).

Offline ([local] extra): BGEReranker — local cross-encoder. The DEFAULT is the
LIGHT ms-marco-MiniLM (``reranker="local"``/``"light"``, dossier 15 §5.2). The
ZeroEntropy **zerank-2** opt-in (``reranker="zerank2"``, +8.7pp NDCG@10 over
MiniLM, STEAL_LIST #6b) is supported but NOT the default — it is a 4B CC-BY-NC
model whose ``predict()`` returns raw logits (needs ``sigmoid(score/5)``), so it
is a documented opt-in, not a silent default swap (E14). torch is imported
lazily, only when a scorer is constructed.

Floor: the identity reranker (``reranker="none"``) — input order preserved (the
--no-rerank speed/zero-token fallback, §5.1).

NO Cohere. NO mandatory local model.
"""
from __future__ import annotations

import logging
import math
from collections.abc import Callable
from typing import Any

from bad_research.llm.base import LLMMessage
from bad_research.retrieval.base import Reranker

# ── The ONE frozen rerank prompt + parser (single source of truth) ───────────
# KR-2 created and froze these in web/search/rerank.py (dossier 13 §4.1, shared
# with dossier 15 §5.3). We import — never duplicate — so a future edit to the
# rubric/parser changes BOTH call sites at once.
from bad_research.web.search.rerank import (
    LLM_RERANK_PROMPT_SYSTEM as LLM_RERANK_SYSTEM,
)
from bad_research.web.search.rerank import (
    LLM_RERANK_TRUNC_CHARS,
    _parse_scores,
    _truncate,
)

__all__ = [
    "LLM_RERANK_SYSTEM",
    "LOCAL_RERANKER_LIGHT",
    "ZERANK2_MODEL",
    "BGEReranker",
    "ClaudeCodeReranker",
    "IdentityReranker",
    "Scorer",
    "get_reranker",
]

# A local cross-encoder scorer: maps [(query, doc)] -> [relevance_score].
Scorer = Callable[[list[tuple[str, str]]], list[float]]

# ── [local] reranker models ───────────────────────────────────────────────────
# The DEFAULT (unchanged): the LIGHT 22M-param ms-marco MiniLM cross-encoder
# (dossier 15 §5.2). Drop-in via the plain-sigmoid loader.
LOCAL_RERANKER_LIGHT = "ms-marco-MiniLM-L-6-v2"

# E14 / STEAL_LIST #6b — the ZeroEntropy zerank-2 cross-encoder (+8.7pp NDCG@10
# over MiniLM, core/13:271-321). Documented OPT-IN, *not* the default. Verified
# 2026-05-27 via the HF API: `zeroentropy/zerank-2-reranker` exists, gated=false,
# `config_sentence_transformers.json` model_type=CrossEncoder (so CrossEncoder
# CAN load it). Two reasons it is NOT made the default:
#   1. License is **CC-BY-NC-4.0 (non-commercial)** — the README states a
#      commercial license must be obtained separately. A non-commercial model is
#      not a safe silent default for the [local] extra.
#   2. It is a 4B-param Qwen3 reranker whose `predict()` returns RAW "Yes" logits,
#      NOT a [0,1] probability (README breaking change, May 2026). The [0,1] map
#      is a TEMPERATURE-SCALED sigmoid `sigmoid(score/5)` (_zerank2_sigmoid),
#      *not* the plain sigmoid MiniLM's loader applies — so it needs its own
#      normalization or scores are mis-scaled (a broken default).
# Opt in via `reranker="zerank2"` (CLI/config); the loader below wires the correct
# sigmoid so the opt-in path is not broken. Keyless: a local download, no API key.
ZERANK2_MODEL = "zeroentropy/zerank-2-reranker"


def _zerank2_sigmoid(logit: float) -> float:
    """Map a zerank-2 raw "Yes" logit to a [0,1] score: sigmoid(logit / 5).

    zerank-2 (post May-2026) returns the raw "Yes"-token logit from `predict()`,
    not a probability. The README's documented conversion is a temperature-scaled
    sigmoid with T=5 (e.g. logit 5.4062 -> 0.746, logit -4.5 -> 0.289). The plain
    sigmoid MiniLM uses would mis-scale these, so zerank-2 gets its own."""
    return 1.0 / (1.0 + math.exp(-logit / 5.0))


def _build_user_message(query: str, docs: list[str]) -> str:
    """Assemble the user message: the query + 0-based numbered, truncated chunks.
    0-based numbering matches the shared KR-2 prompt + parser exactly."""
    passages = "\n".join(
        f"[{i}] {_truncate(d, LLM_RERANK_TRUNC_CHARS)}" for i, d in enumerate(docs)
    )
    return f"QUERY: {query}\nPASSAGES:\n{passages}"


class ClaudeCodeReranker:
    """The DEFAULT keyless reranker — the host model scores candidates 0..1 with
    the ONE frozen prompt + parser (shared with web/search HostModelReranker).

    ``llm`` is any LLMProvider (bad_research.llm.base). The skill path supplies
    the host model; the headless/calibration path supplies AnthropicProvider. No
    key is read here — the provider owns that. The frozen prompt already carries
    the injection preamble, so no extra preamble plumbing is needed."""

    name = "claude-code"
    # Process-global: a broken host LLM degrades rerank silently to BM25 order, so
    # we surface it ONCE (per process) rather than repeatedly or never. [§5.3]
    _host_failure_warned = False

    def __init__(self, *, llm: Any = None, tier: str = "work"):
        # llm may be None at construction: the host provider is resolved LAZILY on
        # the first rerank() call (the skill path supplies the host model only when
        # an actual rerank happens — no key is read at build time, keyless-correct).
        self._llm = llm
        self._tier = tier

    def _provider(self) -> Any:
        """Resolve the host LLM provider lazily (cached). Only touched when a real
        rerank is performed — never at construction, so the keyless build path
        (get_reranker → _build_reranker) never reads ANTHROPIC_API_KEY."""
        if self._llm is None:
            from bad_research.llm.base import get_llm_provider

            self._llm = get_llm_provider("anthropic")
        return self._llm

    def rerank(self, query: str, docs: list[str]) -> list[tuple[int, float]]:
        if not docs:
            return []
        messages = [
            LLMMessage(role="system", content=LLM_RERANK_SYSTEM),
            LLMMessage(role="user", content=_build_user_message(query, docs)),
        ]
        try:
            resp = self._provider().complete(messages, tier=self._tier, temperature=0,
                                             max_tokens=2048)
            # The shared KR-2 parser returns a list[float] (0-based, all-0.0 on a
            # fully-unparseable reply, per-item 0.0 on a missing/malformed item).
            scores = _parse_scores(resp.text, n=len(docs))
        except Exception as e:  # a failed host call must not crash retrieval (§5.3)
            # Degrade to BM25/initial order (no candidate dropped) — but a broken host
            # LLM silently lowering rerank quality should be observable, so warn ONCE.
            if not ClaudeCodeReranker._host_failure_warned:
                ClaudeCodeReranker._host_failure_warned = True
                logging.getLogger("bad_research.rerank").warning(
                    "host-model rerank failed (%s); degrading to BM25/initial order "
                    "until the host LLM is reachable.", e,
                )
            scores = [0.0] * len(docs)
        # Clamp to [0,1] (defensive; the parser already keeps the model's raw float).
        scored = [(i, max(0.0, min(1.0, float(s)))) for i, s in enumerate(scores)]
        scored.sort(key=lambda x: (-x[1], x[0]))  # desc by score, stable by index
        return scored


class IdentityReranker:
    """The --no-rerank floor (dossier 15 §5.1): input order preserved, descending
    pseudo-scores, stable by index. Keyless, deterministic, $0."""

    name = "identity"

    def rerank(self, query: str, docs: list[str]) -> list[tuple[int, float]]:
        n = len(docs)
        return [(i, float(n - i)) for i in range(n)]


def _default_bge_scorer(model: str) -> Scorer:
    """Build a local cross-encoder scorer ([local] extra). Lazy import so the
    module imports cleanly with no torch installed. Prefer FlagEmbedding; fall
    back to sentence-transformers CrossEncoder.

    Normalization to [0,1] is MODEL-AWARE: the zerank-2 opt-in returns raw "Yes"
    logits and needs the temperature-scaled `sigmoid(score/5)` (_zerank2_sigmoid);
    every other cross-encoder (MiniLM default) uses the plain sigmoid. Using the
    wrong sigmoid mis-scales scores — that mismatch is exactly why zerank-2 is an
    explicit opt-in, not the silent default (E14 / STEAL_LIST #6b)."""
    repo = model if model.startswith(("BAAI/", "cross-encoder/", "zeroentropy/")) \
        else f"cross-encoder/{model}"
    norm = _zerank2_sigmoid if model == ZERANK2_MODEL else \
        (lambda s: 1.0 / (1.0 + math.exp(-float(s))))
    try:
        from FlagEmbedding import FlagReranker  # type: ignore

        fr = FlagReranker(repo, use_fp16=True)
        return lambda pairs: fr.compute_score(pairs, normalize=True)
    except ImportError:
        from sentence_transformers import CrossEncoder  # type: ignore

        ce = CrossEncoder(repo)
        return lambda pairs: [norm(float(s)) for s in ce.predict(pairs)]


class BGEReranker:
    """Local cross-encoder ([local]). Default model is the LIGHT ms-marco MiniLM
    (LOCAL_RERANKER_LIGHT, dossier 15 §5.2 — not the 560 MB m3) for the keyless
    ``reranker="local"``/``"light"``. Pass ``model=ZERANK2_MODEL`` for the
    documented zerank-2 opt-in (E14 / STEAL_LIST #6b)."""

    def __init__(self, *, model: str = LOCAL_RERANKER_LIGHT,
                 scorer: Scorer | None = None):
        self.model = model
        self._scorer = scorer if scorer is not None else _default_bge_scorer(model)

    def rerank(self, query: str, docs: list[str]) -> list[tuple[int, float]]:
        if not docs:
            return []
        scores = self._scorer([(query, d) for d in docs])
        scored = list(enumerate(float(s) for s in scores))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored


def get_reranker(config: Any, *, llm: Any = None,
                 bge_scorer: Scorer | None = None) -> Reranker:
    """Keyless reranker factory (INTERFACES_KEYLESS §5.3):
      "host"    → ClaudeCodeReranker (default; host model, no key)
      "local"   → BGEReranker(LOCAL_RERANKER_LIGHT = ms-marco-MiniLM) ([local])
      "light"   → alias of "local" — the documented lightweight fallback name
      "zerank2" → BGEReranker(ZERANK2_MODEL) — the E14 zerank-2 opt-in ([local];
                  +8.7pp NDCG@10, CC-BY-NC, model-aware sigmoid wired in the loader)
      "none"    → IdentityReranker (the --no-rerank floor)
    ``config.reranker`` selects; falls back to "host". The ``llm`` kwarg injects a
    host provider for tests/headless; if absent on the "host" path the provider is
    resolved LAZILY on first rerank() (no key is read at factory time for any
    branch — the keyless build path never touches ANTHROPIC_API_KEY)."""
    choice = getattr(config, "reranker", "host")
    if choice == "none":
        return IdentityReranker()
    if choice in ("local", "light"):
        return BGEReranker(model=LOCAL_RERANKER_LIGHT, scorer=bge_scorer)
    if choice == "zerank2":
        return BGEReranker(model=ZERANK2_MODEL, scorer=bge_scorer)
    # "host" (default): ClaudeCodeReranker resolves the host LLM lazily (llm may be None).
    return ClaudeCodeReranker(llm=llm)
