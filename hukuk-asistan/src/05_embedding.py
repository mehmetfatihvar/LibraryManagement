"""
05_embedding.py
===============
Encode every chunk into a dense vector.

    Input : data/processed/chunks.parquet
    Output: data/processed/embeddings.npy      (float32, shape [N, dim])
            data/processed/chunks_meta.parquet (metadata aligned row-for-row)

Two backends (see config.EMBEDDING_BACKEND):
  * "sentence-transformers" — local, free, default.
  * "openai"                — requires OPENAI_API_KEY.

The two files are written in the same row order so `embeddings[i]` always
corresponds to `chunks_meta.iloc[i]`.

Run:
    python src/05_embedding.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from tqdm import tqdm

import config


# --------------------------------------------------------------------------- #
# Encoders
# --------------------------------------------------------------------------- #
def _encode_sentence_transformers(texts: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    print(f"Loading model: {config.ST_MODEL_NAME}")
    model = SentenceTransformer(config.ST_MODEL_NAME)
    vectors = model.encode(
        texts,
        batch_size=config.EMBEDDING_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=config.NORMALIZE_EMBEDDINGS,
    )
    return vectors.astype(np.float32)


def _encode_openai(texts: list[str]) -> np.ndarray:
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY from the environment
    model = config.OPENAI_EMBEDDING_MODEL
    print(f"Using OpenAI model: {model}")

    vectors: list[list[float]] = []
    batch = config.EMBEDDING_BATCH_SIZE
    for start in tqdm(range(0, len(texts), batch), desc="Embedding", unit="batch"):
        chunk = texts[start:start + batch]
        resp = client.embeddings.create(model=model, input=chunk)
        vectors.extend([d.embedding for d in resp.data])

    arr = np.asarray(vectors, dtype=np.float32)
    if config.NORMALIZE_EMBEDDINGS:
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / np.clip(norms, 1e-8, None)
    return arr


def encode(texts: list[str]) -> np.ndarray:
    """Dispatch to the configured embedding backend."""
    if config.EMBEDDING_BACKEND == "openai":
        return _encode_openai(texts)
    return _encode_sentence_transformers(texts)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    if not config.CHUNKS_PARQUET.exists():
        sys.exit(
            f"Chunks not found at {config.CHUNKS_PARQUET}.\n"
            "Run 04_smart_chunking.py first."
        )

    config.ensure_dirs()
    chunks = pd.read_parquet(config.CHUNKS_PARQUET)
    texts = chunks["text"].fillna("").astype(str).tolist()
    print(f"Encoding {len(texts):,} chunks with backend "
          f"'{config.EMBEDDING_BACKEND}'…")

    vectors = encode(texts)
    if vectors.shape[0] != len(chunks):
        sys.exit(
            f"Row mismatch: {vectors.shape[0]} vectors vs {len(chunks)} chunks."
        )

    np.save(config.EMBEDDINGS_NPY, vectors)
    # Persist the metadata in the exact same order as the vectors.
    chunks.to_parquet(config.CHUNKS_META_PARQUET, index=False)

    print("\n===== Embedding report =====")
    print(f"Vectors        : {vectors.shape[0]:,}")
    print(f"Dimensionality : {vectors.shape[1]}")
    print(f"dtype          : {vectors.dtype}")
    print(f"Normalized     : {config.NORMALIZE_EMBEDDINGS}")
    print(f"\n💾 Saved embeddings → {config.EMBEDDINGS_NPY}")
    print(f"💾 Saved metadata   → {config.CHUNKS_META_PARQUET}")
    print("\nNote: if EMBEDDING_DIM in config differs from "
          f"{vectors.shape[1]}, set EMBEDDING_DIM={vectors.shape[1]} "
          "before building the FAISS index.")


if __name__ == "__main__":
    main()
