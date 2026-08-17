"""
config.py
=========
Central configuration for the Turkish Legal Decisions RAG system
("Hukuk Asistanı").

All paths, model settings, chunking parameters, search parameters and API
settings live here so every pipeline step (01..09) reads from a single
source of truth.

Environment variables (loaded from a `.env` file in the project root) can
override the most important knobs without editing code.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional; the pipeline still works without it
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
# BASE_DIR = .../hukuk-asistan  (parent of this src/ folder)
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Load environment variables from <BASE_DIR>/.env if present.
load_dotenv(BASE_DIR / ".env")

DATA_DIR: Path = BASE_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
QUERIES_DIR: Path = DATA_DIR / "queries"

# Pipeline artifacts (files produced by each step)
RAW_CSV: Path = RAW_DIR / "decisions_100k.csv"
CLEAN_CSV: Path = PROCESSED_DIR / "decisions_clean.csv"
CHUNKS_PARQUET: Path = PROCESSED_DIR / "chunks.parquet"
EMBEDDINGS_NPY: Path = PROCESSED_DIR / "embeddings.npy"
CHUNKS_META_PARQUET: Path = PROCESSED_DIR / "chunks_meta.parquet"
FAISS_INDEX: Path = PROCESSED_DIR / "faiss.index"
TEST_QUERIES_JSON: Path = QUERIES_DIR / "test_queries.json"
BENCHMARK_REPORT: Path = PROCESSED_DIR / "benchmark_report.json"


# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
DATASET_NAME: str = os.getenv(
    "DATASET_NAME", "erdem-erdem/Turkish-Law-Documents-700k-clustered"
)
# Download a sample instead of the full 702K decisions (1.75 GB) for speed.
SAMPLE_SIZE: int = int(os.getenv("SAMPLE_SIZE", "100000"))
DATASET_SPLIT: str = os.getenv("DATASET_SPLIT", "train")
HF_TOKEN: str | None = os.getenv("HF_TOKEN") or None

# Expected columns in the source dataset. If the upstream schema differs, the
# loader in 01_setup_dataset.py maps whatever it finds onto these names.
EXPECTED_COLUMNS: list[str] = [
    "text",
    "source",
    "id",
    "esasNo",
    "kararNo",
    "kararTarihi",
    "cluster_ids",
]


# --------------------------------------------------------------------------- #
# Embedding model
# --------------------------------------------------------------------------- #
# Two backends are supported:
#   * "sentence-transformers" (default, local, free)
#   * "openai"                (requires OPENAI_API_KEY)
EMBEDDING_BACKEND: str = os.getenv("EMBEDDING_BACKEND", "sentence-transformers")

# Multilingual model with strong Turkish support and a 384-dim output.
# A good Turkish-specific alternative:
#   "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
ST_MODEL_NAME: str = os.getenv(
    "ST_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
OPENAI_EMBEDDING_MODEL: str = os.getenv(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

# Dimensionality of the vectors produced by the active backend. This is
# resolved lazily at runtime (05_embedding.py) but we keep sensible defaults
# so 06/07 can build/load the index without loading the model.
EMBEDDING_DIM: int = int(
    os.getenv(
        "EMBEDDING_DIM",
        "384" if EMBEDDING_BACKEND == "sentence-transformers" else "1536",
    )
)

# Batch size used when encoding chunks.
EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "256"))
# Normalize embeddings so inner-product == cosine similarity.
NORMALIZE_EMBEDDINGS: bool = os.getenv("NORMALIZE_EMBEDDINGS", "1") == "1"


# --------------------------------------------------------------------------- #
# Chunking
# --------------------------------------------------------------------------- #
# Chunk size / overlap are measured in characters (robust and tokenizer-free).
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
# Discard chunks shorter than this after cleaning.
MIN_CHUNK_CHARS: int = int(os.getenv("MIN_CHUNK_CHARS", "120"))
# Minimum length of a raw decision to keep during preprocessing.
MIN_TEXT_CHARS: int = int(os.getenv("MIN_TEXT_CHARS", "100"))


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
TOP_K: int = int(os.getenv("TOP_K", "5"))
# Candidates retrieved from FAISS before de-duplication / grouping by decision.
SEARCH_CANDIDATES: int = int(os.getenv("SEARCH_CANDIDATES", "50"))
# Cosine-similarity floor; results below this are dropped.
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def ensure_dirs() -> None:
    """Create every data directory the pipeline needs (idempotent)."""
    for d in (DATA_DIR, RAW_DIR, PROCESSED_DIR, QUERIES_DIR):
        d.mkdir(parents=True, exist_ok=True)


def summary() -> str:
    """Return a human-readable snapshot of the active configuration."""
    lines = [
        "===== Hukuk Asistanı — Configuration =====",
        f"BASE_DIR             : {BASE_DIR}",
        f"DATASET_NAME         : {DATASET_NAME}",
        f"SAMPLE_SIZE          : {SAMPLE_SIZE:,}",
        f"EMBEDDING_BACKEND    : {EMBEDDING_BACKEND}",
        f"EMBEDDING_MODEL      : "
        f"{ST_MODEL_NAME if EMBEDDING_BACKEND == 'sentence-transformers' else OPENAI_EMBEDDING_MODEL}",
        f"EMBEDDING_DIM        : {EMBEDDING_DIM}",
        f"CHUNK_SIZE/OVERLAP   : {CHUNK_SIZE} / {CHUNK_OVERLAP}",
        f"TOP_K                : {TOP_K}",
        f"SIMILARITY_THRESHOLD : {SIMILARITY_THRESHOLD}",
        f"API                  : {API_HOST}:{API_PORT}",
        "==========================================",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    ensure_dirs()
    print(summary())
    print("\nData directories ready:")
    for d in (RAW_DIR, PROCESSED_DIR, QUERIES_DIR):
        print(f"  ✓ {d}")
