"""
08_api_server.py
================
FastAPI service that exposes the RAG search engine over HTTP.

Endpoints:
  GET  /            → service info
  GET  /health      → readiness probe (is the index loaded?)
  POST /search      → { "query": "...", "top_k": 5 } → ranked decisions
  GET  /search?q=…  → same, convenient for browsers

Run:
    uvicorn 08_api_server:app --host 0.0.0.0 --port 8000
  or simply:
    python src/08_api_server.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

import config

# ---- Import the sibling module whose filename starts with a digit -------- #
_spec = importlib.util.spec_from_file_location(
    "search_engine", Path(__file__).with_name("07_search_engine.py")
)
_search_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_search_module)  # type: ignore[union-attr]
SearchEngine = _search_module.SearchEngine


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Hukuki konu / soru")
    top_k: int = Field(default=config.TOP_K, ge=1, le=50)


class DecisionOut(BaseModel):
    decision_id: str
    score: float
    source: str
    esasNo: str
    kararNo: str
    kararTarihi: str
    matched_sections: list[str]
    snippet: str


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[DecisionOut]


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="Hukuk Asistanı — Turkish Legal RAG",
    description="Yargıtay kararları üzerinde anlamsal arama (semantic search).",
    version="1.0.0",
)

_engine = SearchEngine()


@app.on_event("startup")
def _startup() -> None:
    # Load the index eagerly so the first request isn't slow. If artifacts are
    # missing we keep the app up but /health will report not-ready.
    try:
        _engine.load()
    except Exception as exc:  # noqa: BLE001 - surfaced via /health
        app.state.load_error = str(exc)
    else:
        app.state.load_error = None


def _run_search(query: str, top_k: int) -> SearchResponse:
    if getattr(app.state, "load_error", None):
        raise HTTPException(status_code=503, detail=app.state.load_error)
    results = _engine.search(query, top_k=top_k)
    out = [
        DecisionOut(
            decision_id=r.decision_id,
            score=round(r.score, 4),
            source=r.source,
            esasNo=r.esasNo,
            kararNo=r.kararNo,
            kararTarihi=r.kararTarihi,
            matched_sections=r.matched_sections,
            snippet=r.snippet,
        )
        for r in results
    ]
    return SearchResponse(query=query, count=len(out), results=out)


@app.get("/")
def root() -> dict:
    return {
        "service": "Hukuk Asistanı — Turkish Legal RAG",
        "version": "1.0.0",
        "endpoints": ["/health", "POST /search", "GET /search?q=..."],
    }


@app.get("/health")
def health() -> dict:
    ready = getattr(app.state, "load_error", "not-initialised") is None
    return {"ready": ready, "error": getattr(app.state, "load_error", None)}


@app.post("/search", response_model=SearchResponse)
def search_post(req: SearchRequest) -> SearchResponse:
    return _run_search(req.query, req.top_k)


@app.get("/search", response_model=SearchResponse)
def search_get(
    q: str = Query(..., min_length=2, description="Hukuki konu / soru"),
    top_k: int = Query(default=config.TOP_K, ge=1, le=50),
) -> SearchResponse:
    return _run_search(q, top_k)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
