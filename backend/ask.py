import os
from dotenv import load_dotenv
from openai import OpenAI

from search import search

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-5-mini"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about dogs. "
    "Answer using ONLY the information in the provided context. "
    "If the answer is not in the context, say you don't have that information "
    "rather than guessing. "
    "Answer directly and naturally, as if you simply know the information. "
    "Do NOT mention the context, the provided documents, or phrases like "
    "'based on the information given' — just give the answer."
)


def build_context(results):
    context = ""
    for distance, chunk in results:
        context += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"
    return context


def answer_question(query):
    # 1. Retrieve the most relevant chunks (your search.py)
    results = search(query)

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

    sources = [chunk["source"] for distance, chunk in results]
    return answer, sources


if __name__ == "__main__":

    query = "How do I stop my puppy from nipping?"
    answer, sources = answer_question(query)

    print(f"Question: {query}\n")
    print(f"Answer:\n{answer}\n")
    print("Sources used:")
    for s in sorted(set(sources)):
        print(f"  - {s}")