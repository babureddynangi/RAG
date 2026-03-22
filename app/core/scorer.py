from datetime import date
from .models import Chunk
from .taxonomy import same_domain

WEIGHTS = {"semantic": 0.45, "stage": 0.30, "temporal": 0.15, "authority": 0.10}
AUTHORITY_MAP = {"tier1": 1.0, "tier2": 0.8, "tier3": 0.6, "tier4": 0.4}

def stage_score(query_stage: str, chunk: Chunk, taxonomy: dict) -> float:
    if not query_stage:
        return 0.5
    if query_stage == chunk.primary_stage:
        return 1.0
    if query_stage in chunk.stage_tags:
        return 0.7
    if same_domain(query_stage, chunk.primary_stage, taxonomy):
        return 0.3
    return 0.0

def temporal_score(chunk: Chunk) -> float:
    today = date.today().isoformat()
    if chunk.effective_to and chunk.effective_to < today:
        return 0.2
    return 1.0

def authority_score(chunk: Chunk) -> float:
    return AUTHORITY_MAP.get(chunk.authority_tier, 0.4)

def composite_score(semantic: float, stage: float, temporal: float, authority: float) -> float:
    return (WEIGHTS["semantic"] * semantic + WEIGHTS["stage"] * stage +
            WEIGHTS["temporal"] * temporal + WEIGHTS["authority"] * authority)
