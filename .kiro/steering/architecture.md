# Architecture Steering

## Stack
- Runtime: Python 3.11
- API: AWS API Gateway HTTP API + Lambda
- Storage: DynamoDB (chunks + metadata), S3 (taxonomy, benchmark, raw)
- Embeddings: offline local generation (sentence-transformers), vectors stored in DynamoDB
- Logs: CloudWatch
- IaC: Terraform

## Scoring Formula
final_score = 0.45*semantic + 0.30*stage + 0.15*temporal + 0.10*authority

## Stage Score
- 1.0 exact match, 0.7 in stage_tags, 0.3 same domain, 0.0 otherwise

## Temporal Score
- 1.0 active today, 0.2 superseded

## Authority Score
- tier1=1.0, tier2=0.8, tier3=0.6, tier4=0.4
