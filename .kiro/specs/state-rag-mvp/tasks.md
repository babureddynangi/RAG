# Tasks

## Day 1
- [x] T1: Scaffold repo structure
- [ ] T2: Write stages.yaml taxonomy
- [ ] T3: Write chunks.json seed corpus (30+ chunks)
- [ ] T4: Write benchmark_queries.json (40+ queries)
- [ ] T5: Implement models.py (Chunk, Query, Result dataclasses)
- [ ] T6: Implement taxonomy.py (YAML loader)
- [ ] T7: Implement retriever_baseline.py (cosine similarity)
- [ ] T8: Implement retriever_state.py (stage filter + composite score)
- [ ] T9: Implement scorer.py (composite formula)
- [ ] T10: Implement generator.py (templated answer from top-3)
- [ ] T11: run_eval.py local eval script

## Day 2
- [ ] T12: handlers/query.py Lambda handler
- [ ] T13: handlers/evaluate.py Lambda handler
- [ ] T14: scripts/build_chunks.py (embed + upload to DynamoDB)
- [ ] T15: scripts/load_dynamodb.py
- [ ] T16: Terraform: S3, DynamoDB, Lambda, API Gateway, IAM, CloudWatch
- [ ] T17: Deploy + benchmark run
- [ ] T18: README
