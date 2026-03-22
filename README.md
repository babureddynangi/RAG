# RAG Evaluation Research: Page-Index vs Chunked vs State-RAG

This repository contains two end-to-end research experiments comparing retrieval strategies for regulated financial documents. The goal is to determine whether structured, context-aware retrieval meaningfully outperforms naive chunked retrieval in compliance and regulatory QA tasks — and to build a production-ready MVP that proves the hypothesis.

---

## The Problem

Standard RAG systems split documents into fixed-size chunks and retrieve by cosine similarity alone. In regulated domains (consumer credit, compliance, collections), this creates two failure modes:

1. **Citation drift** — the right answer is retrieved but attributed to the wrong page or section
2. **Stage blindness** — a query about fraud investigation retrieves underwriting content because the embeddings are semantically close but contextually wrong

Both failures are costly in regulated environments where auditability and traceability matter.

---

## What We Built

### Experiment 1: `page-index-eval/`

A head-to-head evaluation of **page-index retrieval vs chunked retrieval** on 3 synthetic fintech policy documents and 20 questions across three task types.

- **Page-index** treats each full page as a single retrieval unit, preserving document structure
- **Chunked** splits pages into overlapping text segments (~200 tokens each)
- Both systems use the same embedding model and LLM for a fair comparison
- Questions span fact lookup, page-grounded evidence, and cross-page reasoning

**Stack:** Amazon Titan Embeddings · Amazon Nova Lite (Bedrock) · FAISS · Python

### Experiment 2: `state-rag-mvp/`

A production MVP proving that **stage-aware composite scoring** outperforms vanilla cosine retrieval on 40 regulatory compliance queries across 8 consumer credit lifecycle stages.

- **Baseline** retrieves by cosine similarity only
- **State-RAG** applies a composite scoring formula that weights semantic similarity, regulatory stage alignment, document authority tier, and temporal validity
- Queries are mapped to lifecycle stages (S1–S8): Origination → Underwriting → Adverse Action → Dispute Resolution → Fraud/BSA → Collections → Charge-Off → Servicing
- Includes a Lambda-deployable API handler and full Terraform infrastructure

**Stack:** sentence-transformers · FAISS · AWS Lambda · API Gateway · DynamoDB · S3 · Terraform

---

## Key Results

### Experiment 1 — Page-Index vs Chunked (20 questions, 3 documents)

| System     | Answer Correct | Citation Correct | Avg Latency |
|:-----------|---------------:|-----------------:|------------:|
| chunked    |          0.725 |            0.625 |       573ms |
| page_index |          0.850 |            0.550 |       638ms |

- Page-index gained **+12.5 points** on answer accuracy, driven by fact-lookup (1.0 vs 0.857) and cross-page reasoning (0.8 vs 0.7)
- Chunked held a **+7.5 point citation edge** — smaller chunks map more precisely to individual pages
- Page-index adds ~65ms latency on average; largest gap on cross-page queries (+159ms)

### Experiment 2 — State-RAG vs Baseline (40 queries, 8 lifecycle stages)

| System    | Top-1 Accuracy | Top-3 Accuracy | Stage Confusion | Avg Latency |
|:----------|--------------:|---------------:|----------------:|------------:|
| Baseline  |         0.950 |          0.975 |             N/A |       357ms |
| State-RAG |         0.975 |          1.000 |           0.000 |       357ms |

- State-RAG achieved **100% Top-3 accuracy** with zero stage confusion across all 8 stages
- Stage pre-filter recovered 2 queries that baseline missed (Q032 Fraud/BSA, Q035 CARD Act)
- No latency overhead — composite scoring adds negligible compute vs embedding lookup

### Scoring Formula

```
final_score = 0.45 × semantic + 0.30 × stage + 0.15 × temporal + 0.10 × authority
```

---

## Repository Structure

```
├── page-index-eval/              # Experiment 1
│   ├── src/
│   │   ├── ingest.py             # PDF → page JSONL
│   │   ├── page_index_rag.py     # page-level FAISS index + retrieval
│   │   ├── chunked_rag.py        # chunk-level FAISS index + retrieval
│   │   ├── evaluate.py           # run both systems on all questions
│   │   ├── summarize_results.py  # score aggregation + markdown export
│   │   └── create_pdfs.py        # synthetic fintech PDF generation
│   ├── docs/
│   │   ├── questions.csv         # 20 evaluation questions
│   │   └── gold_labels.csv       # gold answers + page citations
│   └── outputs/
│       ├── results.csv           # scored results by system and task
│       ├── results_raw.csv       # raw LLM outputs
│       ├── whitepaper_results.md # narrative summary
│       └── failure_cases.md      # per-question failure analysis
│
└── state-rag-mvp/                # Experiment 2 + production MVP
    ├── app/
    │   ├── core/
    │   │   ├── models.py          # Chunk, Query, ScoredChunk dataclasses
    │   │   ├── scorer.py          # composite scoring formula
    │   │   ├── retriever_baseline.py  # cosine similarity retriever
    │   │   ├── retriever_state.py     # stage pre-filter + composite rerank
    │   │   ├── generator.py       # templated answer generation
    │   │   └── taxonomy.py        # YAML stage/domain loader
    │   ├── data/
    │   │   ├── chunks.json        # 30 regulatory chunks with metadata
    │   │   ├── stages.yaml        # 8-stage lifecycle taxonomy
    │   │   └── benchmark_queries.json  # 40 queries with expected chunk IDs
    │   ├── handlers/
    │   │   ├── query.py           # Lambda handler: POST /query
    │   │   └── evaluate.py        # Lambda handler: POST /evaluate
    │   └── tests/
    │       ├── test_scorer.py     # 11 unit tests for scoring logic
    │       └── test_retriever.py  # 5 unit tests for retrieval
    ├── scripts/
    │   ├── build_chunks.py        # embed chunks → embeddings.pkl
    │   ├── run_eval.py            # full benchmark runner
    │   └── load_dynamodb.py       # load chunks + embeddings to DynamoDB
    ├── infra/                     # Terraform: Lambda, API GW, DynamoDB, S3, IAM
    └── outputs/
        ├── eval_results.csv       # per-query retrieval results
        ├── summary.json           # aggregate accuracy metrics
        ├── whitepaper_results.md  # combined narrative for both experiments
        └── combined_results.csv   # flat CSV of all metrics, both experiments
```

---

## Running Locally

```bash
# Experiment 1
pip install boto3 pandas pypdf faiss-cpu sentence-transformers reportlab
python page-index-eval/src/create_pdfs.py
python page-index-eval/src/ingest.py
python page-index-eval/src/page_index_rag.py
python page-index-eval/src/chunked_rag.py
python page-index-eval/src/evaluate.py
python page-index-eval/src/summarize_results.py

# Experiment 2
pip install -r state-rag-mvp/requirements.txt
python state-rag-mvp/scripts/build_chunks.py
python state-rag-mvp/scripts/run_eval.py
```

## Deploy to AWS (Experiment 2)

```bash
pip install -r requirements.txt -t lambda_pkg/
cp -r app lambda_pkg/
cd lambda_pkg && zip -r ../lambda.zip .
cd ../infra && terraform init && terraform apply
```

## API Usage

```bash
# Single query
curl -X POST <api_url>/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are adverse action notice requirements?", "stage": "S3", "top_k": 3}'

# Batch evaluation
curl -X POST <api_url>/evaluate \
  -H "Content-Type: application/json" \
  -d '{"queries": [{"query_id": "q1", "text": "What is the SAR filing threshold?", "stage": "S5"}]}'
```

---

## AWS Configuration

- Region: `us-east-1`
- S3 bucket: `sodl-mvp-bucket`
- Embedding model: `amazon.titan-embed-text-v1`
- Generation model: `amazon.nova-lite-v1:0`
- DynamoDB table: `state-rag-chunks`

---

## Conclusion

Structured retrieval consistently outperforms naive cosine similarity in regulated document QA. State-RAG reached 97.5% Top-1 and 100% Top-3 accuracy with zero stage confusion. Page-index retrieval improved answer accuracy by 12.5 points over chunked retrieval. These results support adopting stage-aware, page-boundary-preserving retrieval for compliance and regulatory document systems where auditability is non-negotiable.
