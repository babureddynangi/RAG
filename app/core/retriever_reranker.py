"""
Baseline 4: Reranker-only (no stage-aware gating).
Retrieves top-N by cosine, then reranks by authority + temporal validity only.
No stage scoring. Tests whether governance signals alone (without stage routing) help.
"""
from typing import List
from .models import Chunk, Query, ScoredChunk
from .retriever_baseline import cosine_similarity, retrieve_baseline
from .scorer import temporal_score, authority_score

CANDIDATE_POOL = 10  # retrieve wider pool before reranking


def retrieve_reranker(query: Query, chunks: List[Chunk], query_embedding: List[float]) -> List[ScoredChunk]:
    # Step 1: broad cosine retrieval
    broad_query = Query(query_id=query.query_id, text=query.text, stage=None, top_k=CANDIDATE_POOL)
    candidates = retrieve_baseline(broad_query, chunks, query_embedding)

    # Step 2: rerank by semantic + authority + temporal (no stage signal)
    results = []
    for sc in candidates:
        ts = temporal_score(sc.chunk)
        auth = authority_score(sc.chunk)
        # 0.60 semantic + 0.25 authority + 0.15 temporal — no stage component
        final = 0.60 * sc.semantic_score + 0.25 * auth + 0.15 * ts
        results.append(ScoredChunk(
            chunk=sc.chunk,
            semantic_score=sc.semantic_score,
            temporal_score=ts,
            authority_score=auth,
            final_score=final,
        ))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
