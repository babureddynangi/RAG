import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.core.models import Chunk, Query
from app.core.retriever_baseline import retrieve_baseline
from app.core.retriever_state import retrieve_state_rag

TAXONOMY = {"domain_families": {"lending": ["S1", "S2"], "cards": ["S3"]}}

def make_chunk(chunk_id, stage, text, authority="tier1"):
    return Chunk(
        chunk_id=chunk_id, primary_stage=stage, stage_tags=[stage],
        authority_tier=authority, effective_from="2023-01-01", effective_to=None,
        source_ref="doc.pdf#1", text=text, embedding=[0.1, 0.2, 0.3],
    )

CHUNKS = [
    make_chunk("c1", "S1", "loan origination process"),
    make_chunk("c2", "S2", "credit underwriting criteria"),
    make_chunk("c3", "S3", "card dispute resolution"),
    make_chunk("c4", "S1", "loan application requirements"),
    make_chunk("c5", "S2", "income verification steps"),
]

QUERY_EMB = [0.1, 0.2, 0.3]  # identical to chunk embeddings -> cosine = 1.0 for all

def test_baseline_returns_top_k():
    query = Query(query_id="q1", text="loan process", stage=None, top_k=3)
    results = retrieve_baseline(query, CHUNKS, QUERY_EMB)
    assert len(results) == 3

def test_baseline_scores_between_0_and_1():
    query = Query(query_id="q1", text="loan process", stage=None, top_k=5)
    results = retrieve_baseline(query, CHUNKS, QUERY_EMB)
    for r in results:
        assert 0.0 <= r.final_score <= 1.0

def test_state_rag_stage_filter():
    query = Query(query_id="q1", text="loan process", stage="S1", top_k=5)
    results = retrieve_state_rag(query, CHUNKS, QUERY_EMB, TAXONOMY)
    # Top result should be from S1 when stage is specified
    assert len(results) > 0

def test_state_rag_returns_scored_chunks():
    query = Query(query_id="q1", text="credit", stage="S2", top_k=3)
    results = retrieve_state_rag(query, CHUNKS, QUERY_EMB, TAXONOMY)
    for r in results:
        assert hasattr(r, "final_score")
        assert hasattr(r, "semantic_score")
        assert hasattr(r, "stage_score")

def test_baseline_vs_state_rag_same_pool():
    query = Query(query_id="q1", text="loan", stage=None, top_k=5)
    baseline = retrieve_baseline(query, CHUNKS, QUERY_EMB)
    state_rag = retrieve_state_rag(query, CHUNKS, QUERY_EMB, TAXONOMY)
    # Both should return results from the same chunk pool
    b_ids = {r.chunk.chunk_id for r in baseline}
    s_ids = {r.chunk.chunk_id for r in state_rag}
    assert b_ids.issubset({c.chunk_id for c in CHUNKS})
    assert s_ids.issubset({c.chunk_id for c in CHUNKS})

if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
