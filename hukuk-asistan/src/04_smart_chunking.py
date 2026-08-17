"""
04_smart_chunking.py
====================
Split each cleaned decision into meaningful, overlapping chunks.

    Input : data/processed/decisions_clean.csv
    Output: data/processed/chunks.parquet

Strategy — "smart" chunking:
  1. Structure detection: Yargıtay decisions are loosely organised into
     sections such as DAVA (claim), CEVAP (answer), GEREKÇE (reasoning),
     KARAR / HÜKÜM / SONUÇ (verdict). We split the text on these section
     markers first, so a chunk never blends the claim with the verdict.
  2. Within each section, if the text is longer than CHUNK_SIZE we split it
     further on sentence boundaries with CHUNK_OVERLAP characters of overlap,
     preserving context across chunk borders.
  3. Chunks shorter than MIN_CHUNK_CHARS are discarded.

Each output row carries the parent decision's metadata plus a `chunk_id`,
`section` label and `chunk_index`, so search results can point back to the
exact decision.

Run:
    python src/04_smart_chunking.py
"""

from __future__ import annotations

import re
import sys

import pandas as pd
from tqdm import tqdm

import config


# Section markers frequently found in Turkish court decisions. The regex keeps
# the marker with the section that follows it (split *before* each marker).
#
# Matching is intentionally CASE-SENSITIVE (uppercase only): in these decisions
# real section headers are written in upper case (e.g. "GEREKÇE:"), whereas the
# same words in running text are lower case ("...karar verilmiştir"). Requiring
# upper case avoids spuriously splitting mid-sentence on common words.
_SECTION_MARKERS = [
    "DAVA",
    "CEVAP",
    "İLK DERECE MAHKEMESİ",
    "İSTİNAF",
    "TEMYİZ",
    "GEREKÇE",
    "DELİLLER",
    "DEĞERLENDİRME",
    "SONUÇ",
    "HÜKÜM",
    "KARAR",
]

_SECTION_RE = re.compile(
    r"(?=(?:" + "|".join(re.escape(m) for m in _SECTION_MARKERS) + r")\s*[:\-]?\s)"
)

# Sentence splitter tuned for Turkish: split after . ! ? … followed by a space.
_SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+")


def detect_sections(text: str) -> list[tuple[str, str]]:
    """
    Split `text` into (section_label, section_text) pairs.

    If no known markers are present, the whole decision is returned as a
    single "GENEL" (general) section.
    """
    parts = [p.strip() for p in _SECTION_RE.split(text) if p and p.strip()]
    if len(parts) <= 1:
        return [("GENEL", text.strip())]

    sections: list[tuple[str, str]] = []
    for part in parts:
        # Label = the leading marker word, if the part starts with one.
        label = "GENEL"
        upper = part[:40].upper()
        for marker in _SECTION_MARKERS:
            if upper.startswith(marker):
                label = marker
                break
        sections.append((label, part))
    return sections


def _split_with_overlap(text: str, size: int, overlap: int) -> list[str]:
    """
    Split `text` into <= `size`-char pieces on sentence boundaries, carrying
    `overlap` characters of context from the previous piece into the next.
    """
    if len(text) <= size:
        return [text]

    sentences = _SENTENCE_RE.split(text)
    chunks: list[str] = []
    current = ""

    for sent in sentences:
        if not sent:
            continue
        if len(current) + len(sent) + 1 <= size:
            current = f"{current} {sent}".strip()
        else:
            if current:
                chunks.append(current)
            # Start the next chunk with the tail of the previous one (overlap).
            tail = current[-overlap:] if overlap and current else ""
            current = f"{tail} {sent}".strip()
            # A single sentence longer than `size` is hard-split.
            while len(current) > size:
                chunks.append(current[:size])
                current = current[size - overlap:]
    if current:
        chunks.append(current)
    return chunks


def chunk_decision(text: str) -> list[tuple[str, int, str]]:
    """Return a list of (section_label, index_within_decision, chunk_text)."""
    results: list[tuple[str, int, str]] = []
    idx = 0
    for label, section_text in detect_sections(text):
        for piece in _split_with_overlap(
            section_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP
        ):
            piece = piece.strip()
            if len(piece) >= config.MIN_CHUNK_CHARS:
                results.append((label, idx, piece))
                idx += 1
    return results


def main() -> None:
    if not config.CLEAN_CSV.exists():
        sys.exit(
            f"Cleaned CSV not found at {config.CLEAN_CSV}.\n"
            "Run 03_preprocess.py first."
        )

    config.ensure_dirs()
    df = pd.read_csv(config.CLEAN_CSV)
    df["text"] = df["text"].fillna("").astype(str)

    rows: list[dict] = []
    for _, r in tqdm(df.iterrows(), total=len(df), desc="Chunking", unit="doc"):
        decision_id = r.get("id", "")
        for label, idx, piece in chunk_decision(r["text"]):
            rows.append(
                {
                    "chunk_id": f"{decision_id}__{idx}",
                    "decision_id": decision_id,
                    "section": label,
                    "chunk_index": idx,
                    "text": piece,
                    "source": r.get("source", ""),
                    "esasNo": r.get("esasNo", ""),
                    "kararNo": r.get("kararNo", ""),
                    "kararTarihi": r.get("kararTarihi", ""),
                }
            )

    chunks = pd.DataFrame(rows)
    chunks.to_parquet(config.CHUNKS_PARQUET, index=False)

    # ---- Report ---------------------------------------------------------- #
    per_doc = chunks.groupby("decision_id").size()
    print("\n===== Chunking report =====")
    print(f"Decisions in   : {len(df):,}")
    print(f"Chunks out     : {len(chunks):,}")
    print(f"Chunks / doc   : mean {per_doc.mean():.2f}, "
          f"median {per_doc.median():.0f}, max {per_doc.max()}")
    print(f"Chunk length   : mean {chunks['text'].str.len().mean():.0f} chars")
    print("\nSection distribution:")
    for sec, cnt in chunks["section"].value_counts().head(12).items():
        print(f"  {sec:<24}: {cnt:,}")
    print(f"\n💾 Saved chunks → {config.CHUNKS_PARQUET}")


if __name__ == "__main__":
    main()
