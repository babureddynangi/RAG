# Constraints

- AWS free-tier friendly only
- No OpenSearch
- No SageMaker
- Corpus max 80 chunks
- Benchmark max 60 queries
- All modules must be independently testable
- Terraform must be minimal: S3, DynamoDB, Lambda, API Gateway, IAM, CloudWatch
- Stage detection: prefer explicit injection, fallback rule-based only
