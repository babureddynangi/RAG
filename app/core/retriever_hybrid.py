"""
Baseline 3: Hybrid lexical + vector retrieval (BM25-style term overlap + cosine).
Approximates BM25 with TF-IDF-like term overlap score, then linearly combines with semantic.
"""
import re, math
from typing import List
from .models import Chunk, Query, ScoredChunk
from .retriever_baseline import cosine_similarity


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def _term_overlap_score(query_tokens: List[str], chunk_text: str) -> float:
    """Normalised term overlap: |query_terms ∩ chunk_terms| / |query_terms|"""
    chunk_tokens = set(_tokenize(chunk_text))
    if not query_tokens:
        return 0.0
    hits = sum(1 for t in query_tokens if t in chunk_tokens)
    return hits / len(query_tokens)


def retrieve_hybrid(query: Query, chunks: List[Chunk], query_embedding: List[float],
                    alpha: float = 0.6) -> List[ScoredChunk]:
    """alpha controls semantic weight; (1-alpha) is lexical weight."""
    query_tokens = _tokenize(query.text)
    results = []
    for chunk in chunks:
        if chunk.embedding is None:
            continue
        sem = cosine_similarity(query_embedding, chunk.embedding)
        lex = _term_overlap_score(query_tokens, chunk.text)
        final = alpha * sem + (1 - alpha) * lex
        results.append(ScoredChunk(chunk=chunk, semantic_score=sem, final_score=final))
    results.sort(key=lambda x: x.final_score, reverse=True)
    return results[:query.top_k]
