"""BgeLocalEmbedProvider — local bge-small bi-encoder ([local] extra).

Keyless: sentence-transformers runs on CPU, no network at inference once the
~130 MB model is downloaded. dim 384. Asymmetric: the query prefix
"Represent this sentence for searching relevant passages: " is applied for
input_type="query" (dossier 15 §4.1, §4.3); documents get no prefix.
torch/sentence-transformers are imported lazily so this module only loads when
the provider is actually constructed.
"""
from __future__ import annotations

from typing import Literal

_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class BgeLocalEmbedProvider:
    name: str = "bge-small-en-v1.5"
    dim: int = 384

    def __init__(self, *, model: str = "BAAI/bge-small-en-v1.5",
                 device: str | None = None):
        from sentence_transformers import (  # type: ignore[import-not-found]  # lazy ([local])
            SentenceTransformer,
        )

        self.name = model.split("/")[-1]
        self._model = SentenceTransformer(model, device=device)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str], *,
              input_type: Literal["document", "query"]) -> list[list[float]]:
        if not texts:
            return []
        payload = [(_QUERY_PREFIX + t) for t in texts] if input_type == "query" else list(texts)
        vecs = self._model.encode(payload, normalize_embeddings=True,
                                  convert_to_numpy=True)
        return [v.tolist() for v in vecs]
