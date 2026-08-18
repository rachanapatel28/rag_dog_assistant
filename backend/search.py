import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "dog_wiki"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 3

# Open the Chroma collection once, when the module is imported
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def search(query, top_k=TOP_K):
    # 1. Embed the query the same way we embedded the chunks
    response = client.embeddings.create(model=EMBED_MODEL, input=[query])
    query_vec = response.data[0].embedding

    # 2. Let Chroma find the closest chunks (returned nearest-first)
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)

    # 3. Reshape Chroma's response into (distance, chunk) pairs
    scored = []
    for chunk_id, text, meta, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunk = {"source": meta["source"], "chunk_id": chunk_id, "text": text}
        scored.append((distance, chunk))
    
    return scored
    

if __name__ == "__main__":

    query = "how do I stop my puppy from nipping?"
    results = search(query)

    print(f"Query: {query}\n")
    print(f"Top {len(results)} closest chunks (lower distance = closer):\n")
    for distance, chunk in results:
        print(f"[{distance:.3f}] {chunk['source']}")
        print(f"        {chunk['text'][:160]}...")
        print()