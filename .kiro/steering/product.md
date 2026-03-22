# Product Steering: state-rag-mvp

## Goal
Prove that stage-aware retrieval returns better evidence than vanilla retrieval on regulated consumer-credit workflow queries.

## MVP Scope
- Tiny corpus: 30-80 policy/regulation/SOP chunks
- Two retrievers: baseline semantic + STATE-RAG stage-aware
- Evaluation: 40-60 benchmark queries
- Paper-demo friendly output

## Out of Scope
- Enterprise auth, real-time ingestion, fancy UI
- OpenSearch, SageMaker, multi-tenant features
