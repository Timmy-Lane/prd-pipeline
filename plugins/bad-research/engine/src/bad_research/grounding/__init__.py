"""Grounding / no-hallucination layer (Plan 06).

Forward: DSS span extraction + claim_anchors. Backward: CitationVerifier
(byte-identity -> local NLI -> triage-LLM judge) + the deterministic Stage-16
no-uncited-claim gate.
"""

from .anchors import AnchorStore, ClaimAnchor, build_from_claims, quote_sha
from .extract import extract_spans
from .gate import Finding, gate_blocks_ship, is_factual_claim, no_uncited_claim_gate
from .nli import NLI_MODEL_NAME, CrossEncoderNLI, NLILabel, classify_nli
from .render import coalesce_citations, extract_citations, render_citation
from .verifier import (
    CitationFinding,
    CitationPresentNLI,
    CitationVerifier,
    VerifyResult,
    VerifyVerdict,
    default_nli,
    nli_available,
    tier_a_byte_identity,
    tier_c_judge,
)

__all__ = [
    "NLI_MODEL_NAME",
    "AnchorStore",
    "CitationFinding",
    "CitationPresentNLI",
    "CitationVerifier",
    "ClaimAnchor",
    "CrossEncoderNLI",
    "Finding",
    "NLILabel",
    "VerifyResult",
    "VerifyVerdict",
    "build_from_claims",
    "classify_nli",
    "coalesce_citations",
    "default_nli",
    "extract_citations",
    "extract_spans",
    "gate_blocks_ship",
    "is_factual_claim",
    "nli_available",
    "no_uncited_claim_gate",
    "quote_sha",
    "render_citation",
    "tier_a_byte_identity",
    "tier_c_judge",
]
