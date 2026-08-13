"""
Standalone demo — NOT part of the RAG application.

Shows that OpenAI embeddings capture *meaning*: a query is compared to a few
candidate sentences, and the one closest in meaning scores highest, even when
it shares no words with the query.

Run directly with:  python embed_demo.py
Requires OPENAI_API_KEY in a .env file.
"""


import os
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


query = "my puppy keeps nipping my hands"

candidates = [
    "Puppy biting and mouthing are normal parts of play and exploration.",
    "Huskies have thick double coats and struggle in hot climates.",
    "Feed your dog a complete, balanced diet in measured portions.",
]

# Embed the query and all candidates in a single API call
texts = [query] + candidates
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,
)
vectors = [item.embedding for item in response.data]

query_vec = vectors[0]
candidate_vecs = vectors[1:]

print(f"Each embedding is a list of {len(query_vec)} numbers.\n")
print(f"Query: {query}\n")
print("Similarity to each candidate (higher = closer in meaning):\n")
for text, vec in zip(candidates, candidate_vecs):
    score = cosine_similarity(query_vec, vec)
    print(f"  {score:.3f}   {text}")
    
