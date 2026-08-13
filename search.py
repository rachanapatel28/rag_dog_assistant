import os
import json
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INDEX_FILE = "chunk_embeddings.json"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 3


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def load_index(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def search(query, chunks, top_k=TOP_K):
    # 1. Embed the query the same way we embedded the chunks
    response = client.embeddings.create(model=EMBED_MODEL, input=[query])
    query_vec = response.data[0].embedding

    # 2. Score the query against every chunk
    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_vec, chunk["embedding"])
        scored.append((score, chunk))

    # 3. Sort by score, highest first, and keep the top few
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    chunks = load_index(INDEX_FILE)
    print(f"Loaded {len(chunks)} chunks from {INDEX_FILE}\n")

    query = "how do I stop my puppy from nipping?"
    results = search(query, chunks)

    print(f"Query: {query}\n")
    print(f"Top {len(results)} most relevant chunks:\n")
    for score, chunk in results:
        print(f"[{score:.3f}] {chunk['source']}")
        print(f"        {chunk['text'][:160]}...")
        print()