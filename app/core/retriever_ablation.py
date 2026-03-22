"""
Ablation retrievers for isolating the contribution of each State-RAG component.

  ablation_stage_only      : semantic + stage signal only (no temporal, no authority)
  ablation_stage_temporal  : semantic + stage + temporal (no authority)
  ablation_stage_authority : semantic + stage + authority (no temporal)

All three use the same stage pre-filter as State-RAG so the only variable
is which scoring components are active.
"""
from typing import List
from .models import Chunk, Query, ScoredChunk
from .retriever_baseline import cosine_similarity
from .scorer import stage_score, temporal_score, authority_score


def _stage_filter(query: Query, chunks: List[Chunk]) -> List[Chunk]:
    if query.stage:
        filtered = [c for c in chunks if query.stage == c.primary_stage or query.stage in c.stage_tags]
        return filtered if filtered else chunks
    return chunks


def retrieve_ablation_stage_only(query: Query, chunks: List[Chunk],
                                  query_embedding: List[float], taxonomy: dict) -> List[ScoredChunk]:
    """Stage pre-filter + 0.70 semantic + 0.30 stage. No temporal or authority."""
    filtered = _stage_filter(query, chunks)
    results = []
    for chunk in filtered:
        if chunk.embedding is None:
            continue
        sem = cosine_similarity(query_embedding, chunk.embedding)
        ss  = stage_score(query.stage, chunk, taxonomy)
        final = 0.70 * sem + 0.30 * ss
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem,
                                   stage_score=ss, final_score=final))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]


def retrieve_ablation_stage_temporal(query: Query, chunks: List[Chunk],
                                      query_embedding: List[float], taxonomy: dict) -> List[ScoredChunk]:
    """Stage pre-filter + 0.55 semantic + 0.30 stage + 0.15 temporal. No authority."""
    filtered = _stage_filter(query, chunks)
    results = []
    for chunk in filtered:
        if chunk.embedding is None:
            continue
        sem  = cosine_similarity(query_embedding, chunk.embedding)
        ss   = stage_score(query.stage, chunk, taxonomy)
        ts   = temporal_score(chunk)
        final = 0.55 * sem + 0.30 * ss + 0.15 * ts
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem,
                                   stage_score=ss, temporal_score=ts, final_score=final))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]


def retrieve_ablation_stage_authority(query: Query, chunks: List[Chunk],
                                       query_embedding: List[float], taxonomy: dict) -> List[ScoredChunk]:
    """Stage pre-filter + 0.55 semantic + 0.30 stage + 0.15 authority. No temporal."""
    filtered = _stage_filter(query, chunks)
    results = []
    for chunk in filtered:
        if chunk.embedding is None:
            continue
        sem  = cosine_similarity(query_embedding, chunk.embedding)
        ss   = stage_score(query.stage, chunk, taxonomy)
        auth = authority_score(chunk)
        final = 0.55 * sem + 0.30 * ss + 0.15 * auth
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem,
                                   stage_score=ss, authority_score=auth, final_score=final))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
