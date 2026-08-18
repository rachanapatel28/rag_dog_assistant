import json
import chromadb

# 1. Load the embeddings you already built
with open("chunk_embeddings.json") as f:
    chunks = json.load(f)   # assuming a list of dicts

# 2. Reshape into the four lists Chroma wants
ids        = [c["chunk_id"] for c in chunks]   # a unique id per chunk
embeddings = [c["embedding"] for c in chunks]       # the vectors you precomputed
documents  = [c["text"] for c in chunks]            # the chunk text itself
metadatas  = [{"source": c["source"]} for c in chunks]  # which doc it came from

# 3. Open a persistent Chroma database (just a folder on disk)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="dog_wiki")

# 4. Store everything
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas,
)

print("Vectors stored:", collection.count())