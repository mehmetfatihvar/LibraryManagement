# Hukuk Asistanı — Turkish Legal Decisions RAG System

A retrieval system for Turkish court decisions (Yargıtay kararları). An
attorney describes a legal topic in natural language, and the system returns
the most relevant decisions using semantic (vector) search.

- **Dataset:** [`erdem-erdem/Turkish-Law-Documents-700k-clustered`](https://huggingface.co/datasets/erdem-erdem/Turkish-Law-Documents-700k-clustered) — 702,296 decisions (1997–2025). The pipeline samples 100K by default.
- **Stack:** Hugging Face `datasets` → smart chunking → `sentence-transformers` / OpenAI embeddings → FAISS vector index → FastAPI endpoint → benchmark.

---

## Architecture

```
Query ──► Embed query ──► FAISS search ──► group by decision ──► ranked Yargıtay decisions
                                  ▲
 decisions.csv ─► clean ─► smart chunks ─► embeddings ─► FAISS index
```

## Project layout

```
hukuk-asistan/
├─ data/
│  ├─ raw/          # downloaded dataset (decisions_100k.csv)
│  ├─ processed/    # clean text, chunks, embeddings, FAISS index
│  └─ queries/      # test_queries.json
├─ src/
│  ├─ config.py            # single source of truth for all settings
│  ├─ 01_setup_dataset.py  # download sample → data/raw/decisions_100k.csv
│  ├─ 02_explore_data.py   # EDA report
│  ├─ 03_preprocess.py     # clean + normalise + filter
│  ├─ 04_smart_chunking.py # section-aware chunking with overlap
│  ├─ 05_embedding.py      # encode chunks → embeddings.npy
│  ├─ 06_faiss_index.py    # build FAISS index
│  ├─ 07_search_engine.py  # SearchEngine class + CLI
│  ├─ 08_api_server.py     # FastAPI service
│  └─ 09_benchmark_test.py # latency + relevance benchmark
├─ requirements.txt
├─ run_pipeline.sh
└─ .env.example
```

## Setup

```bash
cd hukuk-asistan
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in OPENAI_API_KEY only if using the OpenAI backend
```

## Run the pipeline

Step by step:

```bash
python src/config.py            # verify config + create data dirs
python src/01_setup_dataset.py  # download 100K sample
python src/02_explore_data.py   # exploratory report
python src/03_preprocess.py     # clean text
python src/04_smart_chunking.py # chunk decisions
python src/05_embedding.py      # embed chunks
python src/06_faiss_index.py    # build FAISS index
python src/09_benchmark_test.py # benchmark
```

…or all at once: `bash run_pipeline.sh`

## Search from the CLI

```bash
python src/07_search_engine.py "kira sözleşmesinin haklı nedenle feshi"
```

## Run the API

```bash
cd src
uvicorn 08_api_server:app --host 0.0.0.0 --port 8000
```

Then:

```bash
curl "http://localhost:8000/search?q=işçinin%20kıdem%20tazminatı&top_k=5"

curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "trafik kazası destekten yoksun kalma tazminatı", "top_k": 5}'
```

Interactive docs at `http://localhost:8000/docs`.

## Configuration

All knobs live in `src/config.py` and can be overridden with environment
variables (or a `.env` file). Key settings:

| Variable | Default | Meaning |
|---|---|---|
| `SAMPLE_SIZE` | `100000` | How many decisions to download |
| `EMBEDDING_BACKEND` | `sentence-transformers` | `sentence-transformers` or `openai` |
| `ST_MODEL_NAME` | `paraphrase-multilingual-MiniLM-L12-v2` | Local embedding model |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1200` / `200` | Chunk sizing (chars) |
| `TOP_K` | `5` | Decisions returned per query |
| `SIMILARITY_THRESHOLD` | `0.30` | Minimum cosine similarity |

## Notes

- Embeddings are L2-normalised, so FAISS inner-product search yields cosine
  similarity directly.
- The smart chunker splits on Yargıtay section markers (`DAVA`, `GEREKÇE`,
  `SONUÇ`, `HÜKÜM`, …) before sentence-level splitting, so a chunk never
  blends the claim with the verdict.
- Generated data artifacts (CSV/parquet/npy/index) are git-ignored — rerun the
  pipeline to regenerate them.
