import json, os, numpy as np
from typing import List
from .models import Chunk, Query, ScoredChunk

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0

def retrieve_baseline(query: Query, chunks: List[Chunk], query_embedding: List[float]) -> List[ScoredChunk]:
    results = []
    for chunk in chunks:
        if chunk.embedding is None:
            continue
        sem = cosine_similarity(query_embedding, chunk.embedding)
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem, final_score=sem))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
