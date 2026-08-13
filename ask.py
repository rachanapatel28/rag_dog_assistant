import os
from dotenv import load_dotenv
from openai import OpenAI

from search import load_index, search

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-5-mini"
INDEX_FILE = "chunk_embeddings.json"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about dogs. "
    "Answer the question using ONLY the information in the provided context. "
    "If the answer is not in the context, say you don't have that information "
    "rather than guessing. Keep answers clear and practical."
)


def build_context(results):
    context = ""
    for score, chunk in results:
        context += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"
    return context


def answer_question(query, chunks):
    # 1. Retrieve the most relevant chunks (your search.py)
    results = search(query, chunks)

    # 2. Assemble them into a context block
    context = build_context(results)

    # 3. Ask the LLM to answer using that context
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\nQuestion: {query}"},
        ],
    )
    answer = response.choices[0].message.content

    sources = [chunk["source"] for score, chunk in results]
    return answer, sources


if __name__ == "__main__":
    chunks = load_index(INDEX_FILE)

    query = "what is the capital of France?"
    answer, sources = answer_question(query, chunks)

    print(f"Question: {query}\n")
    print(f"Answer:\n{answer}\n")
    print("Sources used:")
    for s in sorted(set(sources)):
        print(f"  - {s}")