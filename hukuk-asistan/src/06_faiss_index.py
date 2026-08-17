"""
06_faiss_index.py
=================
Build a FAISS vector index from the saved embeddings.

    Input : data/processed/embeddings.npy
    Output: data/processed/faiss.index

Because embeddings are L2-normalised in step 05, an inner-product index
(IndexFlatIP) yields cosine similarity directly. For large corpora we wrap it
in an IVF index for faster approximate search; for small corpora we keep the
exact flat index.

Run:
    python src/06_faiss_index.py
"""

from __future__ import annotations

import sys

import numpy as np

import config

# Above this many vectors we switch from exact (flat) to approximate (IVF)
# search to keep query latency low.
_IVF_THRESHOLD = 200_000


def build_index(vectors: np.ndarray):
    import faiss

    n, dim = vectors.shape
    vectors = np.ascontiguousarray(vectors.astype(np.float32))

    if n < _IVF_THRESHOLD:
        print(f"Building exact IndexFlatIP ({n:,} vectors, dim={dim})…")
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        return index

    # Approximate IVF index for large corpora.
    nlist = min(4096, max(64, int(np.sqrt(n))))
    print(f"Building IndexIVFFlat (nlist={nlist}, {n:,} vectors, dim={dim})…")
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
    index.train(vectors)
    index.add(vectors)
    index.nprobe = min(32, nlist)
    return index


def main() -> None:
    if not config.EMBEDDINGS_NPY.exists():
        sys.exit(
            f"Embeddings not found at {config.EMBEDDINGS_NPY}.\n"
            "Run 05_embedding.py first."
        )

    try:
        import faiss
    except ImportError:
        sys.exit("faiss is not installed. Run: pip install faiss-cpu")

    config.ensure_dirs()
    vectors = np.load(config.EMBEDDINGS_NPY)
    index = build_index(vectors)

    faiss.write_index(index, str(config.FAISS_INDEX))

    print("\n===== FAISS index report =====")
    print(f"Vectors indexed : {index.ntotal:,}")
    print(f"Dimensionality  : {vectors.shape[1]}")
    print(f"Metric          : inner product (cosine on normalised vectors)")
    print(f"\n💾 Saved index → {config.FAISS_INDEX}")


if __name__ == "__main__":
    main()
