import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.models import Query
from core.taxonomy import load_taxonomy
from core.retriever_baseline import retrieve_baseline
from core.retriever_state import retrieve_state_rag

CHUNKS = None
TAXONOMY = None

def _init():
    global CHUNKS, TAXONOMY
    if CHUNKS is None:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
        from build_chunks import load_chunks_with_embeddings
        CHUNKS = load_chunks_with_embeddings()
    if TAXONOMY is None:
        TAXONOMY = load_taxonomy()

def hit_at_k(results, expected_ids, k):
    top_ids = [r.chunk.chunk_id for r in results[:k]]
    return int(any(eid in top_ids for eid in expected_ids))

def handler(event, context):
    """POST /evaluate - runs baseline vs state-rag on a batch of queries."""
    _init()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
    from build_chunks import embed_text

    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
    queries = body.get("queries", [])

    results = []
    for q in queries:
        query = Query(
            query_id=q.get("query_id", "q"),
            text=q["text"],
            stage=q.get("stage"),
            top_k=q.get("top_k", 5),
        )
        expected_ids = q.get("expected_chunk_ids", [])
        t0 = time.time()
        qemb = embed_text(query.text)
        baseline = retrieve_baseline(query, CHUNKS, qemb)
        state_rag = retrieve_state_rag(query, CHUNKS, qemb, TAXONOMY)
        latency = int((time.time() - t0) * 1000)

        results.append({
            "query_id": query.query_id,
            "text": query.text,
            "stage": query.stage,
            "baseline_top3": [r.chunk.chunk_id for r in baseline[:3]],
            "state_rag_top3": [r.chunk.chunk_id for r in state_rag[:3]],
            "baseline_h1": hit_at_k(baseline, expected_ids, 1),
            "baseline_h3": hit_at_k(baseline, expected_ids, 3),
            "state_rag_h1": hit_at_k(state_rag, expected_ids, 1),
            "state_rag_h3": hit_at_k(state_rag, expected_ids, 3),
            "latency_ms": latency,
        })

    n = len(results)
    summary = {}
    if n:
        summary = {
            "n_queries": n,
            "baseline_top1_acc": sum(r["baseline_h1"] for r in results) / n,
            "baseline_top3_acc": sum(r["baseline_h3"] for r in results) / n,
            "state_rag_top1_acc": sum(r["state_rag_h1"] for r in results) / n,
            "state_rag_top3_acc": sum(r["state_rag_h3"] for r in results) / n,
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results, "summary": summary}),
    }
