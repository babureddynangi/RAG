"""
Baseline 2: Vector RAG + metadata filter
Filters by stage tag match before cosine ranking. No composite scoring.
"""
import numpy as np
from typing import List
from .models import Chunk, Query, ScoredChunk
from .retriever_baseline import cosine_similarity


def retrieve_metadata_filter(query: Query, chunks: List[Chunk], query_embedding: List[float]) -> List[ScoredChunk]:
    if query.stage:
        filtered = [c for c in chunks if query.stage == c.primary_stage or query.stage in c.stage_tags]
        if not filtered:
            filtered = chunks
    else:
        filtered = chunks

    results = []
    for chunk in filtered:
        if chunk.embedding is None:
            continue
        sem = cosine_similarity(query_embedding, chunk.embedding)
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem, final_score=sem))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
