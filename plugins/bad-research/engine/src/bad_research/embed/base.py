"""Base Protocol + keyless factory for the EmbedProvider seam.

The neural recall lane is OPTIONAL ([local] extra). Default impl:
BgeLocalEmbedProvider (bge-small-en-v1.5, dim 384) — built in KR-5
(embed/bge_local.py). KR-1 leaves the Protocol + an import-guarded factory.
Cohere (the old API embedder) is removed — pure keyless.
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable


@runtime_checkable
class EmbedProvider(Protocol):
    name: str
    dim: int

    def embed(
        self,
        texts: list[str],
        *,
        input_type: Literal["document", "query"],
    ) -> list[list[float]]: ...


def get_embed_provider(name: str = "bge-local", **kwargs) -> EmbedProvider:
    """Load an embed provider by name. Default = the local BGE bi-encoder ([local]).

    Keyless: no API embedder. The dense lane is opt-in — installed via
    `pip install bad-research[local]` and built in KR-5 (embed/bge_local.py).
    """
    if name == "bge-local":
        try:
            from bad_research.embed.bge_local import (  # type: ignore[import-not-found]
                BgeLocalEmbedProvider,
            )
        except ImportError as exc:
            raise ImportError(
                'bge-local requires the local neural stack: '
                'pip install "bad-research[local]" (built in KR-5)'
            ) from exc
        return BgeLocalEmbedProvider(**kwargs)

    raise ValueError(f"Unknown embed provider: {name!r}. Available: bge-local")
