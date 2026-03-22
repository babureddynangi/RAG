from typing import List
from .models import ScoredChunk

def generate_answer(query_text: str, results: List[ScoredChunk]) -> str:
    if not results:
        return "No relevant documents found for this query."
    lines = [f"Based on the retrieved regulatory evidence for: '{query_text}'\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.chunk.source_ref} (stage: {r.chunk.primary_stage}, score: {r.chunk.final_score:.3f})")
        lines.append(f"    {r.chunk.text[:300]}")
    return "\n".join(lines)
