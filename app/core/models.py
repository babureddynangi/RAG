from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

@dataclass
class Chunk:
    chunk_id: str
    text: str
    primary_stage: str
    stage_tags: List[str]
    authority_tier: str
    effective_from: str
    effective_to: Optional[str]
    source_ref: str
    embedding: Optional[List[float]] = field(default=None, repr=False)

@dataclass
class Query:
    query_id: str
    text: str
    stage: Optional[str] = None
    top_k: int = 3

@dataclass
class ScoredChunk:
    chunk: Chunk
    semantic_score: float = 0.0
    stage_score: float = 0.0
    temporal_score: float = 0.0
    authority_score: float = 0.0
    final_score: float = 0.0

@dataclass
class QueryResult:
    query: Query
    baseline: List[ScoredChunk]
    state_rag: List[ScoredChunk]
    answer: str
    latency_ms: int
