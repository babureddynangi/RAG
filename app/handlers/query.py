import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.models import Query
from core.taxonomy import load_taxonomy
from core.retriever_baseline import retrieve_baseline
from core.retriever_state import retrieve_state_rag
from core.generator import generate_answer
from scripts.build_chunks import load_chunks_with_embeddings

CHUNKS = None
TAXONOMY = None

def _init():
    global CHUNKS, TAXONOMY
    if CHUNKS is None:
        CHUNKS = load_chunks_with_embeddings()
    if TAXONOMY is None:
        TAXONOMY = load_taxonomy()

def handler(event, context):
    _init()
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
    query = Query(query_id="q1", text=body["query"], stage=body.get("stage"), top_k=body.get("top_k", 3))
    from scripts.build_chunks import embed_text
    t0 = time.time()
    qemb = embed_text(query.text)
    baseline = retrieve_baseline(query, CHUNKS, qemb)
    state_rag = retrieve_state_rag(query, CHUNKS, qemb, TAXONOMY)
    latency = int((time.time() - t0) * 1000)
    top_sr = state_rag[0] if state_rag else None
    return {
        "statusCode": 200,
        "body": json.dumps({
            "baseline": [{"chunk_id": r.chunk.chunk_id, "text": r.chunk.text[:200], "score": r.final_score, "source_ref": r.chunk.source_ref} for r in baseline],
            "state_rag": [{"chunk_id": r.chunk.chunk_id, "text": r.chunk.text[:200], "score": r.final_score, "source_ref": r.chunk.source_ref, "stage": r.chunk.primary_stage} for r in state_rag],
            "answer": generate_answer(query.text, state_rag),
            "score_breakdown": {"semantic": round(top_sr.semantic_score, 4), "stage": round(top_sr.stage_score, 4), "temporal": round(top_sr.temporal_score, 4), "authority": round(top_sr.authority_score, 4), "final": round(top_sr.final_score, 4)} if top_sr else {},
            "latency_ms": latency
        })
    }
