"""
07_search_engine.py
===================
The retrieval core of the RAG system. Loads the FAISS index + chunk metadata
and answers natural-language queries with the most relevant Yargıtay
decisions.

Exposes a reusable `SearchEngine` class (imported by 08_api_server.py and
09_benchmark_test.py) and a small CLI for ad-hoc testing.

    Inputs : data/processed/faiss.index
             data/processed/chunks_meta.parquet

Run (interactive):
    python src/07_search_engine.py "kira sözleşmesinin feshi"
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import config


@dataclass
class ChunkHit:
    chunk_id: str
    decision_id: str
    section: str
    score: float
    text: str
    source: str
    esasNo: str
    kararNo: str
    kararTarihi: str


@dataclass
class DecisionResult:
    decision_id: str
    score: float
    source: str
    esasNo: str
    kararNo: str
    kararTarihi: str
    snippet: str
    matched_sections: list[str] = field(default_factory=list)


class SearchEngine:
    """Load the index once, then serve many queries."""

    def __init__(self) -> None:
        self._index = None
        self._meta: pd.DataFrame | None = None
        self._encoder = None  # lazy: a callable[list[str]] -> np.ndarray
        self._loaded = False

    # ------------------------------------------------------------------ #
    # Loading
    # ------------------------------------------------------------------ #
    def load(self) -> "SearchEngine":
        if self._loaded:
            return self

        import faiss

        if not config.FAISS_INDEX.exists():
            raise FileNotFoundError(
                f"FAISS index missing at {config.FAISS_INDEX}. "
                "Run 06_faiss_index.py first."
            )
        if not config.CHUNKS_META_PARQUET.exists():
            raise FileNotFoundError(
                f"Chunk metadata missing at {config.CHUNKS_META_PARQUET}. "
                "Run 05_embedding.py first."
            )

        self._index = faiss.read_index(str(config.FAISS_INDEX))
        self._meta = pd.read_parquet(config.CHUNKS_META_PARQUET).reset_index(drop=True)
        if self._index.ntotal != len(self._meta):
            raise RuntimeError(
                f"Index/metadata mismatch: {self._index.ntotal} vectors "
                f"vs {len(self._meta)} metadata rows."
            )
        self._encoder = self._build_encoder()
        self._loaded = True
        return self

    def _build_encoder(self):
        if config.EMBEDDING_BACKEND == "openai":
            from openai import OpenAI

            client = OpenAI()

            def encode(texts: list[str]) -> np.ndarray:
                resp = client.embeddings.create(
                    model=config.OPENAI_EMBEDDING_MODEL, input=texts
                )
                arr = np.asarray([d.embedding for d in resp.data], dtype=np.float32)
                return _normalize(arr)

            return encode

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(config.ST_MODEL_NAME)

        def encode(texts: list[str]) -> np.ndarray:
            arr = model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=config.NORMALIZE_EMBEDDINGS,
            )
            return arr.astype(np.float32)

        return encode

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    def search_chunks(self, query: str, candidates: int | None = None) -> list[ChunkHit]:
        """Return the top-scoring individual chunks for a query."""
        if not self._loaded:
            self.load()
        candidates = candidates or config.SEARCH_CANDIDATES

        qvec = self._encoder([query]).astype(np.float32)
        scores, idxs = self._index.search(qvec, candidates)

        hits: list[ChunkHit] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            if score < config.SIMILARITY_THRESHOLD:
                continue
            row = self._meta.iloc[int(idx)]
            hits.append(
                ChunkHit(
                    chunk_id=str(row.get("chunk_id", "")),
                    decision_id=str(row.get("decision_id", "")),
                    section=str(row.get("section", "")),
                    score=float(score),
                    text=str(row.get("text", "")),
                    source=str(row.get("source", "")),
                    esasNo=str(row.get("esasNo", "")),
                    kararNo=str(row.get("kararNo", "")),
                    kararTarihi=str(row.get("kararTarihi", "")),
                )
            )
        return hits

    def search(self, query: str, top_k: int | None = None) -> list[DecisionResult]:
        """
        Return the top-`k` *decisions* for a query.

        Chunk hits are grouped by their parent decision so the caller gets
        distinct decisions rather than several chunks of the same one. A
        decision's score is the best (max) score among its chunks.
        """
        top_k = top_k or config.TOP_K
        hits = self.search_chunks(query)

        grouped: dict[str, DecisionResult] = {}
        for h in hits:
            existing = grouped.get(h.decision_id)
            if existing is None:
                grouped[h.decision_id] = DecisionResult(
                    decision_id=h.decision_id,
                    score=h.score,
                    source=h.source,
                    esasNo=h.esasNo,
                    kararNo=h.kararNo,
                    kararTarihi=h.kararTarihi,
                    snippet=h.text[:400],
                    matched_sections=[h.section],
                )
            else:
                if h.score > existing.score:
                    existing.score = h.score
                    existing.snippet = h.text[:400]
                if h.section not in existing.matched_sections:
                    existing.matched_sections.append(h.section)

        results = sorted(grouped.values(), key=lambda r: r.score, reverse=True)
        return results[:top_k]


def _normalize(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.clip(norms, 1e-8, None)


def _cli() -> None:
    if len(sys.argv) < 2:
        print('Usage: python src/07_search_engine.py "your legal query"')
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    engine = SearchEngine().load()
    results = engine.search(query)

    print(f"\nQuery: {query}\n" + "=" * 60)
    if not results:
        print("No results above the similarity threshold.")
        return
    for i, r in enumerate(results, 1):
        print(f"\n#{i}  score={r.score:.3f}  [{r.source}] "
              f"Esas {r.esasNo} / Karar {r.kararNo}  ({r.kararTarihi})")
        print(f"    sections: {', '.join(r.matched_sections)}")
        print(f"    {r.snippet}…")


if __name__ == "__main__":
    _cli()
