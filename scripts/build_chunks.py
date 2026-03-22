import json, os, pickle
from typing import List
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.json")
CHUNKS_EXTRA_PATH = os.path.join(DATA_DIR, "chunks_extra.json")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings.pkl")

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
    raw = _load_all_chunks()
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

def _load_all_chunks():
    with open(CHUNKS_PATH) as f:
        raw = json.load(f)
    if os.path.exists(CHUNKS_EXTRA_PATH):
        with open(CHUNKS_EXTRA_PATH) as f:
            raw += json.load(f)
    return raw

def main():
    raw = _load_all_chunks()
    print(f"Loaded {len(raw)} chunks total")
    model = get_model()
    # load existing embeddings to avoid re-embedding unchanged chunks
    embeddings = {}
    if os.path.exists(EMBEDDINGS_PATH):
        with open(EMBEDDINGS_PATH, "rb") as f:
            embeddings = pickle.load(f)
    for r in raw:
        if r["chunk_id"] not in embeddings:
            print(f"  Embedding {r['chunk_id']}")
            embeddings[r["chunk_id"]] = model.encode(r["text"]).tolist()
        else:
            print(f"  Cached  {r['chunk_id']}")
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"Saved {len(embeddings)} embeddings to {EMBEDDINGS_PATH}")

if __name__ == "__main__":
    main()
