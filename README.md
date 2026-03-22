# State-RAG vs Traditional RAG

Research MVP proving that stage-aware composite retrieval outperforms traditional cosine similarity RAG on regulated financial services documents.

---

## The Problem

Traditional RAG retrieves by semantic similarity alone. In regulated domains this causes two failure modes:

- **Stage blindness** — a fraud investigation query retrieves underwriting content because embeddings are semantically close but contextually wrong
- **Citation drift** — the right answer is retrieved but from the wrong regulatory stage or document section

Both failures are unacceptable in compliance contexts where every answer must be traceable to the correct policy, regulation, and lifecycle stage.

---

## The Approach

**Traditional RAG** ranks chunks by cosine similarity between query and chunk embeddings. No domain awareness.

**State-RAG** applies a composite scoring formula after a stage pre-filter:

```
final_score = 0.45 × semantic + 0.30 × stage + 0.15 × temporal + 0.10 × authority
```

- `semantic` — cosine similarity between query and chunk embeddings
- `stage` — alignment between query lifecycle stage and chunk's regulatory stage tags
- `temporal` — whether the chunk is within its effective date range
- `authority` — document authority tier (tier1 = regulation, tier2 = policy, tier3 = guidance)

Queries are mapped to one of 8 consumer credit lifecycle stages: Origination (S1) → Underwriting (S2) → Adverse Action (S3) → Dispute Resolution (S4) → Fraud & BSA (S5) → Collections (S6) → Charge-Off & Debt Sale (S7) → Servicing & Statements (S8).

---

## Results

Evaluated on 150 regulatory compliance queries across all 8 lifecycle stages and 7 query types (direct, paraphrase, hard negative, temporal, cross-stage, multi-chunk, ambiguous).

| System          | Top-1 Accuracy | Top-3 Accuracy | Stage Confusion | Avg Latency |
|:----------------|---------------:|---------------:|----------------:|------------:|
| Traditional RAG |         73.33% |         88.67% |          22.00% |        99ms |
| Hybrid          |         74.67% |         92.00% |          16.00% |        99ms |
| Reranker        |         71.33% |         87.33% |          21.33% |        99ms |
| Metadata Filter |         81.33% |         94.67% |           8.67% |        99ms |
| **State-RAG**   |     **81.33%** |     **97.33%** |       **0.00%** |    **99ms** |

State-RAG vs Traditional RAG: **+8 points Top-1, +8.7 points Top-3, -22 points stage confusion**. No latency overhead.

Full per-query results: [`outputs/combined_results.csv`](outputs/combined_results.csv)
Narrative summary: [`outputs/whitepaper_results.md`](outputs/whitepaper_results.md)

---

## Repository Structure

```
state-rag-mvp/
├── app/
│   ├── core/
│   │   ├── models.py              # Chunk, Query, ScoredChunk dataclasses
│   │   ├── scorer.py              # composite scoring formula
│   │   ├── retriever_baseline.py  # traditional cosine similarity retriever
│   │   ├── retriever_state.py     # stage pre-filter + composite rerank
│   │   ├── generator.py           # answer generation from top-k chunks
│   │   └── taxonomy.py            # lifecycle stage / domain family loader
│   ├── data/
│   │   ├── chunks.json            # 30 regulatory chunks with metadata
│   │   ├── stages.yaml            # 8-stage lifecycle taxonomy
│   │   └── benchmark_queries.json # 40 queries with expected chunk IDs
│   ├── handlers/
│   │   ├── query.py               # Lambda handler: POST /query
│   │   └── evaluate.py            # Lambda handler: POST /evaluate
│   └── tests/
│       ├── test_scorer.py         # 11 unit tests — scoring logic
│       └── test_retriever.py      # 5 unit tests — retrieval
├── scripts/
│   ├── build_chunks.py            # embed chunks → embeddings.pkl
│   ├── run_eval.py                # benchmark runner → outputs/
│   └── load_dynamodb.py           # load chunks + embeddings to DynamoDB
├── infra/                         # Terraform: Lambda, API Gateway, DynamoDB, S3, IAM
└── outputs/
    ├── eval_results.csv           # per-query retrieval results (40 rows)
    ├── summary.json               # aggregate accuracy metrics
    ├── combined_results.csv       # State-RAG vs Traditional RAG, all 40 queries
    └── whitepaper_results.md      # full narrative results
```

---

## Running Locally

```bash
pip install -r requirements.txt
python scripts/build_chunks.py   # generates app/data/embeddings.pkl
python scripts/run_eval.py       # writes outputs/eval_results.csv + summary.json
```

## Deploy to AWS

```bash
pip install -r requirements.txt -t lambda_pkg/
cp -r app lambda_pkg/
cd lambda_pkg && zip -r ../lambda.zip .
cd ../infra && terraform init && terraform apply
```

## API

```bash
# Query endpoint
curl -X POST <api_url>/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are adverse action notice requirements?", "stage": "S3", "top_k": 3}'

# Batch evaluate endpoint
curl -X POST <api_url>/evaluate \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"query_id": "q1", "text": "What is the SAR filing threshold?", "stage": "S5"}]}'
```

---

## AWS Config

| Setting          | Value                        |
|:-----------------|:-----------------------------|
| Region           | us-east-1                    |
| Embedding model  | amazon.titan-embed-text-v1   |
| Generation model | amazon.nova-lite-v1:0        |
| S3 bucket        | sodl-mvp-bucket              |
| DynamoDB table   | state-rag-chunks             |
