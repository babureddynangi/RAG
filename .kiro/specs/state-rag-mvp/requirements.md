# Requirements

## Functional
- R1: Load stage taxonomy from YAML
- R2: Store chunks in DynamoDB with full metadata schema
- R3: Baseline retriever: cosine similarity over embeddings
- R4: STATE-RAG retriever: stage pre-filter + composite rerank
- R5: Query API: POST /query returns baseline + state-rag results + answer
- R6: Eval API: POST /evaluate runs benchmark, writes CSV + JSON
- R7: GET /health returns 200
- R8: Benchmark: 40-60 queries with ground truth stage + doc ids
- R9: Metrics: top-1, top-3, Stage Confusion Rate, latency

## Non-Functional
- NF1: Lambda cold start < 3s
- NF2: Query response < 2s warm
- NF3: All infra via Terraform
- NF4: Local run without AWS (offline mode)
