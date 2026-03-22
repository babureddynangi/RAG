import numpy as np
from typing import List
from .models import Chunk, Query, ScoredChunk
from .retriever_baseline import cosine_similarity
from .scorer import stage_score, temporal_score, authority_score, composite_score

def retrieve_state_rag(query: Query, chunks: List[Chunk], query_embedding: List[float], taxonomy: dict) -> List[ScoredChunk]:
    # Stage pre-filter: keep exact + tag matches + same domain
    if query.stage:
        filtered = [c for c in chunks if query.stage == c.primary_stage or query.stage in c.stage_tags]
        if not filtered:
            filtered = chunks  # fallback to full corpus
    else:
        filtered = chunks

    results = []
    for chunk in filtered:
        if chunk.embedding is None:
            continue
        sem = cosine_similarity(query_embedding, chunk.embedding)
        ss = stage_score(query.stage, chunk, taxonomy)
        ts = temporal_score(chunk)
        auth = authority_score(chunk)
        final = composite_score(sem, ss, ts, auth)
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem, stage_score=ss,
                                   temporal_score=ts, authority_score=auth, final_score=final))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
