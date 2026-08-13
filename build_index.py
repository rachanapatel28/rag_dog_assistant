import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from chunk_docs import load_documents, chunk_text

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_FOLDER = "data"
OUTPUT_FILE = "chunk_embeddings.json"
EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100

# 1. Build the chunks (reusing the functions from chunk_docs.py)
documents = load_documents(DATA_FOLDER)
all_chunks = []
for filename, text in documents.items():
    for i, chunk in enumerate(chunk_text(text)):
        all_chunks.append({
            "source": filename,
            "chunk_id": f"{filename}::chunk_{i}",
            "text": chunk,
        })

print(f"Prepared {len(all_chunks)} chunks. Embedding in batches of {BATCH_SIZE}...")

# 2. Embed every chunk, a batch at a time
for start in range(0, len(all_chunks), BATCH_SIZE):
    batch = all_chunks[start:start + BATCH_SIZE]
    texts = [chunk["text"] for chunk in batch]
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    for chunk, item in zip(batch, response.data):
        chunk["embedding"] = item.embedding
    print(f"  Embedded chunks {start + 1} to {start + len(batch)}")

# 3. Save everything to a file so we never have to recompute
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f)

print(f"\nSaved {len(all_chunks)} chunks with embeddings to {OUTPUT_FILE}")
print(f"Each embedding has {len(all_chunks[0]['embedding'])} dimensions.")