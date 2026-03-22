import json, os, pickle
from typing import List
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "chunks.json")
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "embeddings.pkl")

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_text(text: str) -> List[float]:
    return get_model().encode(text).tolist()

def load_chunks_with_embeddings():
    from app.core.models import Chunk
    with open(CHUNKS_PATH) as f:
        raw = json.load(f)
    if os.path.exists(EMBEDDINGS_PATH):
        with open(EMBEDDINGS_PATH, "rb") as f:
            embeddings = pickle.load(f)
    else:
        embeddings = {}
    chunks = []
    for r in raw:
        c = Chunk(**{k: v for k, v in r.items()})
        c.embedding = embeddings.get(r["chunk_id"])
        chunks.append(c)
    return chunks

def main():
    print(f"Loading chunks from {CHUNKS_PATH}")
    with open(CHUNKS_PATH) as f:
        raw = json.load(f)
    model = get_model()
    embeddings = {}
    for r in raw:
        print(f"  Embedding {r['chunk_id']}")
        embeddings[r["chunk_id"]] = model.encode(r["text"]).tolist()
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"Saved {len(embeddings)} embeddings to {EMBEDDINGS_PATH}")

if __name__ == "__main__":
    main()
