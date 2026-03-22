import json, os, sys, boto3, pickle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "chunks.json")
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "embeddings.pkl")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "state-rag-chunks")
REGION = os.environ.get("AWS_REGION", "us-east-1")

def main():
    with open(CHUNKS_PATH) as f:
        chunks = json.load(f)

    embeddings = {}
    if os.path.exists(EMBEDDINGS_PATH):
        with open(EMBEDDINGS_PATH, "rb") as f:
            embeddings = pickle.load(f)
        print(f"Loaded {len(embeddings)} embeddings from {EMBEDDINGS_PATH}")
    else:
        print("WARNING: embeddings.pkl not found. Run build_chunks.py first.")

    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    success, failed = 0, 0
    with table.batch_writer() as batch:
        for chunk in chunks:
            item = {
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "primary_stage": chunk["primary_stage"],
                "stage_tags": chunk["stage_tags"],
                "domain_family": chunk["domain_family"],
                "authority_tier": chunk["authority_tier"],
                "effective_from": chunk.get("effective_from", ""),
                "effective_to": chunk.get("effective_to", ""),
                "source_ref": chunk["source_ref"],
                "text": chunk["text"],
            }
            emb = embeddings.get(chunk["chunk_id"])
            if emb:
                # Store as JSON string (DynamoDB has no native float list type)
                item["embedding"] = json.dumps(emb)
            try:
                batch.put_item(Item=item)
                success += 1
                print(f"  Loaded {chunk['chunk_id']}")
            except Exception as e:
                failed += 1
                print(f"  FAILED {chunk['chunk_id']}: {e}")

    print(f"\nDone. {success} loaded, {failed} failed.")

if __name__ == "__main__":
    main()
