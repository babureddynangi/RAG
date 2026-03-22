import json, os, sys, time, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.models import Query
from app.core.taxonomy import load_taxonomy
from app.core.retriever_baseline import retrieve_baseline
from app.core.retriever_metadata import retrieve_metadata_filter
from app.core.retriever_hybrid import retrieve_hybrid
from app.core.retriever_reranker import retrieve_reranker
from app.core.retriever_state import retrieve_state_rag
from app.core.retriever_ablation import (retrieve_ablation_stage_only,
    retrieve_ablation_stage_temporal, retrieve_ablation_stage_authority)
from scripts.build_chunks import load_chunks_with_embeddings, embed_text

BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "benchmark_queries.json")
OUTPUT_PATH    = os.path.join(os.path.dirname(__file__), "..", "outputs", "eval_results.csv")
SUMMARY_PATH   = os.path.join(os.path.dirname(__file__), "..", "outputs", "summary.json")

SYSTEMS = ["baseline","metadata","hybrid","reranker",
           "ablation_stage","ablation_stage_temporal","ablation_stage_authority",
           "state_rag"]

def hit_at_k(results, expected_ids, k):
    top_ids = [r.chunk.chunk_id for r in results[:k]]
    return int(any(eid in top_ids for eid in expected_ids))

def scr(results, stage, k=1):
    if not stage: return 0
    return int(any(r.chunk.primary_stage != stage for r in results[:k]))

def run_all(query, chunks, qemb, taxonomy):
    return {
        "baseline":                  retrieve_baseline(query, chunks, qemb),
        "metadata":                  retrieve_metadata_filter(query, chunks, qemb),
        "hybrid":                    retrieve_hybrid(query, chunks, qemb),
        "reranker":                  retrieve_reranker(query, chunks, qemb),
        "ablation_stage":            retrieve_ablation_stage_only(query, chunks, qemb, taxonomy),
        "ablation_stage_temporal":   retrieve_ablation_stage_temporal(query, chunks, qemb, taxonomy),
        "ablation_stage_authority":  retrieve_ablation_stage_authority(query, chunks, qemb, taxonomy),
        "state_rag":                 retrieve_state_rag(query, chunks, qemb, taxonomy),
    }

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    chunks = load_chunks_with_embeddings()
    taxonomy = load_taxonomy()
    with open(BENCHMARK_PATH) as f:
        queries = json.load(f)
    rows = []
    acc = {s: {"h1": [], "h3": [], "scr": [], "lat": []} for s in SYSTEMS}
    for q in queries:
        query = Query(query_id=q["query_id"], text=q["text"], stage=q.get("stage"), top_k=5)
        expected_ids = q.get("expected_chunk_ids", [])
        t0 = time.time()
        qemb = embed_text(query.text)
        results = run_all(query, chunks, qemb, taxonomy)
        latency = int((time.time() - t0) * 1000)
        row = {"query_id": q["query_id"], "text": q["text"],
               "stage": q.get("stage",""), "query_type": q.get("query_type",""),
               "latency_ms": latency}
        parts = [q["query_id"]]
        for s in SYSTEMS:
            res = results[s]
            h1 = hit_at_k(res, expected_ids, 1)
            h3 = hit_at_k(res, expected_ids, 3)
            sc = scr(res, q.get("stage"), 1)
            top1 = res[0].chunk.chunk_id if res else ""
            row[f"{s}_h1"]=h1; row[f"{s}_h3"]=h3; row[f"{s}_scr"]=sc; row[f"{s}_top1"]=top1
            acc[s]["h1"].append(h1); acc[s]["h3"].append(h3)
            acc[s]["scr"].append(sc); acc[s]["lat"].append(latency)
            parts.append(f"{s[:8]}=H1:{h1}")
        rows.append(row)
        print(" | ".join(parts))
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    n = len(rows)
    summary = {"n_queries": n, "corpus_size": len(chunks), "systems": {}}
    for s in SYSTEMS:
        a = acc[s]
        summary["systems"][s] = {
            "top1_accuracy":        round(sum(a["h1"])/n, 4),
            "top3_accuracy":        round(sum(a["h3"])/n, 4),
            "stage_confusion_rate": round(sum(a["scr"])/n, 4),
            "avg_latency_ms":       round(sum(a["lat"])/n, 1),
        }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n=== SUMMARY ({n} queries, {len(chunks)} chunks) ===")
    print(f"{'System':<28} {'Top-1':>7} {'Top-3':>7} {'SCR':>7} {'Lat':>7}")
    print("-" * 58)
    for s in SYSTEMS:
        d = summary["systems"][s]
        print(f"{s:<28} {d['top1_accuracy']:>7.4f} {d['top3_accuracy']:>7.4f} {d['stage_confusion_rate']:>7.4f} {d['avg_latency_ms']:>7.1f}")

if __name__ == "__main__":
    main()
