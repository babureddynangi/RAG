# state-rag-mvp

Research MVP proving stage-aware retrieval outperforms vanilla retrieval on regulated consumer-credit workflow queries.

## Local Run

```bash
pip install -r requirements.txt
python scripts/build_chunks.py      # generate embeddings
python scripts/run_eval.py          # run benchmark
```

## Deploy to AWS

```bash
pip install -r requirements.txt -t lambda_pkg/
cp -r app lambda_pkg/
cd lambda_pkg && zip -r ../lambda.zip . && cd ..
cd infra && terraform init && terraform apply
```

## API Usage

```bash
curl -X POST <api_url>/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are adverse action notice requirements?", "stage": "S3", "top_k": 3}'
```

## Scoring Formula

```
final_score = 0.45*semantic + 0.30*stage + 0.15*temporal + 0.10*authority
```
