import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.core.models import Chunk
from app.core.scorer import stage_score, temporal_score, authority_score, composite_score

def make_chunk(**kwargs):
    defaults = dict(
        chunk_id="c1", primary_stage="S1", stage_tags=["S1"],
        authority_tier="tier1", effective_from="2023-01-01", effective_to=None,
        source_ref="doc.pdf#1", text="sample text", embedding=None,
    )
    defaults.update(kwargs)
    return Chunk(**defaults)

TAXONOMY = {"domain_families": {"lending": ["S1", "S2"], "cards": ["S3"]}}

def test_stage_score_exact_match():
    chunk = make_chunk(primary_stage="S2", stage_tags=["S2"])
    assert stage_score("S2", chunk, TAXONOMY) == 1.0

def test_stage_score_tag_match():
    chunk = make_chunk(primary_stage="S1", stage_tags=["S1", "S2"])
    assert stage_score("S2", chunk, TAXONOMY) == 0.7

def test_stage_score_same_domain():
    chunk = make_chunk(primary_stage="S1", stage_tags=["S1"])
    # S1 and S2 share domain "lending"
    assert stage_score("S2", chunk, TAXONOMY) == 0.3

def test_stage_score_no_match():
    chunk = make_chunk(primary_stage="S1", stage_tags=["S1"])
    # S3 is "cards" domain, S1 is "lending"
    assert stage_score("S3", chunk, TAXONOMY) == 0.0

def test_stage_score_no_query_stage():
    chunk = make_chunk()
    assert stage_score(None, chunk, TAXONOMY) == 0.5

def test_temporal_score_active():
    chunk = make_chunk(effective_to=None)
    assert temporal_score(chunk) == 1.0

def test_temporal_score_expired():
    chunk = make_chunk(effective_to="2020-01-01")
    assert temporal_score(chunk) == 0.2

def test_authority_score_tier1():
    chunk = make_chunk(authority_tier="tier1")
    assert authority_score(chunk) == 1.0

def test_authority_score_tier3():
    chunk = make_chunk(authority_tier="tier3")
    assert authority_score(chunk) == 0.6

def test_composite_score_range():
    score = composite_score(0.8, 1.0, 1.0, 1.0)
    assert 0.0 <= score <= 1.0

def test_composite_score_weights():
    # All components = 1.0 should give 1.0
    assert composite_score(1.0, 1.0, 1.0, 1.0) == 1.0
    # All components = 0.0 should give 0.0
    assert composite_score(0.0, 0.0, 0.0, 0.0) == 0.0

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
