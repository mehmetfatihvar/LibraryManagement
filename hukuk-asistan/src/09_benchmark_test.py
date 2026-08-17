"""
09_benchmark_test.py
====================
Benchmark the retrieval quality and latency of the search engine against the
test queries in data/queries/test_queries.json.

Metrics reported per query and in aggregate:
  * latency (ms)
  * results returned
  * top-1 similarity score
  * keyword-hit rate: fraction of `expected_keywords` that appear in the
    returned snippets (a lightweight, label-free relevance proxy)

    Inputs : data/queries/test_queries.json
             the built FAISS index + metadata
    Output : data/processed/benchmark_report.json + printed table

Run:
    python src/09_benchmark_test.py
"""

from __future__ import annotations

import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

import config

# ---- Import the digit-prefixed search engine module --------------------- #
_spec = importlib.util.spec_from_file_location(
    "search_engine", Path(__file__).with_name("07_search_engine.py")
)
_search_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_search_module)  # type: ignore[union-attr]
SearchEngine = _search_module.SearchEngine


def _keyword_hit_rate(keywords: list[str], texts: list[str]) -> float:
    """Fraction of `keywords` that appear (case-insensitively) in any snippet."""
    if not keywords:
        return 0.0
    blob = " ".join(texts).lower()
    hits = sum(1 for kw in keywords if kw.lower() in blob)
    return hits / len(keywords)


def main() -> None:
    if not config.TEST_QUERIES_JSON.exists():
        sys.exit(f"Test queries not found at {config.TEST_QUERIES_JSON}.")

    with open(config.TEST_QUERIES_JSON, encoding="utf-8") as f:
        spec = json.load(f)
    queries = spec["queries"]

    print(f"Loading search engine (backend={config.EMBEDDING_BACKEND})…")
    engine = SearchEngine().load()

    per_query: list[dict] = []
    print("\n" + "=" * 78)
    print(f"{'ID':<4}{'Topic':<22}{'ms':>7}{'#res':>6}{'top1':>7}{'kw-hit':>8}")
    print("=" * 78)

    for item in queries:
        t0 = time.perf_counter()
        results = engine.search(item["query"])
        latency_ms = (time.perf_counter() - t0) * 1000

        snippets = [r.snippet for r in results]
        top1 = results[0].score if results else 0.0
        kw_rate = _keyword_hit_rate(item.get("expected_keywords", []), snippets)

        per_query.append(
            {
                "id": item["id"],
                "query": item["query"],
                "topic": item.get("topic", ""),
                "latency_ms": round(latency_ms, 1),
                "num_results": len(results),
                "top1_score": round(top1, 4),
                "keyword_hit_rate": round(kw_rate, 3),
            }
        )
        print(f"{item['id']:<4}{item.get('topic', '')[:21]:<22}"
              f"{latency_ms:>7.1f}{len(results):>6}{top1:>7.3f}{kw_rate:>8.2f}")

    # ---- Aggregate ------------------------------------------------------- #
    latencies = [q["latency_ms"] for q in per_query]
    top1s = [q["top1_score"] for q in per_query]
    kw_rates = [q["keyword_hit_rate"] for q in per_query]

    aggregate = {
        "num_queries": len(per_query),
        "latency_ms_mean": round(statistics.mean(latencies), 1),
        "latency_ms_p95": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 1),
        "top1_score_mean": round(statistics.mean(top1s), 4),
        "keyword_hit_rate_mean": round(statistics.mean(kw_rates), 3),
    }

    print("=" * 78)
    print("AGGREGATE")
    print(f"  queries               : {aggregate['num_queries']}")
    print(f"  latency mean / p95 ms : {aggregate['latency_ms_mean']} / {aggregate['latency_ms_p95']}")
    print(f"  top-1 score mean      : {aggregate['top1_score_mean']}")
    print(f"  keyword hit rate mean : {aggregate['keyword_hit_rate_mean']}")
    print("=" * 78)

    report = {"aggregate": aggregate, "per_query": per_query}
    with open(config.BENCHMARK_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved report → {config.BENCHMARK_REPORT}")


if __name__ == "__main__":
    main()
