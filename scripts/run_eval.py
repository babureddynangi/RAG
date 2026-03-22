import json, os, sys, time, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.models import Query
from app.core.taxonomy import load_taxonomy
from app.core.retriever_baseline import retrieve_baseline
from app.core.retriever_state import retrieve_state_rag
from scripts.build_chunks import load_chunks_with_embeddings, embed_text

BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "benchmark_queries.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "eval_results.csv")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "summary.json")

def hit_at_k(results, expected_ids, k):
    top_ids = [r.chunk.chunk_id for r in results[:k]]
    return int(any(eid in top_ids for eid in expected_ids))

def stage_confusion(results, expected_stage, k=1):
    if not expected_stage: return 0
    top = results[:k]
    return int(any(r.chunk.primary_stage != expected_stage for r in top))

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    chunks = load_chunks_with_embeddings()
    taxonomy = load_taxonomy()
    with open(BENCHMARK_PATH) as f:
        queries = json.load(f)

    rows, b_h1, b_h3, s_h1, s_h3, s_scr, latencies = [], [], [], [], [], [], []

    for q in queries:
        query = Query(query_id=q["query_id"], text=q["text"], stage=q.get("stage"), top_k=5)
        expected_ids = q.get("expected_chunk_ids", [])
        expected_stage = q.get("stage")
        t0 = time.time()
        qemb = embed_text(query.text)
        baseline = retrieve_baseline(query, chunks, qemb)
        state_rag = retrieve_state_rag(query, chunks, qemb, taxonomy)
        latency = int((time.time() - t0) * 1000)
        bh1 = hit_at_k(baseline, expected_ids, 1)
        bh3 = hit_at_k(baseline, expected_ids, 3)
        sh1 = hit_at_k(state_rag, expected_ids, 1)
        sh3 = hit_at_k(state_rag, expected_ids, 3)
        scr = stage_confusion(state_rag, expected_stage, 1)
        b_h1.append(bh1); b_h3.append(bh3); s_h1.append(sh1); s_h3.append(sh3)
        s_scr.append(scr); latencies.append(latency)
        rows.append({"query_id": q["query_id"], "text": q["text"], "stage": expected_stage,
                     "baseline_h1": bh1, "baseline_h3": bh3, "state_rag_h1": sh1,
                     "state_rag_h3": sh3, "stage_confusion": scr, "latency_ms": latency,
                     "baseline_top1": baseline[0].chunk.chunk_id if baseline else "",
                     "state_rag_top1": state_rag[0].chunk.chunk_id if state_rag else ""})
        print(f"{q['query_id']} | B_H1={bh1} SR_H1={sh1} SCR={scr} {latency}ms")

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)

    n = len(rows)
    summary = {"n_queries": n, "baseline_top1_acc": sum(b_h1)/n, "baseline_top3_acc": sum(b_h3)/n,
               "state_rag_top1_acc": sum(s_h1)/n, "state_rag_top3_acc": sum(s_h3)/n,
               "stage_confusion_rate": sum(s_scr)/n, "avg_latency_ms": sum(latencies)/n}
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

if __name__ == "__main__":
    main()
