import os

DATA_FOLDER = "data"


def load_documents(folder):
    documents = {}
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            path = os.path.join(folder, filename)
            with open(path, "r", encoding="utf-8") as f:
                documents[filename] = f.read()
    return documents


def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


if __name__ == "__main__":
    documents = load_documents(DATA_FOLDER)

    all_chunks = []
    for filename, text in documents.items():
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append({
                "source": filename,
                "chunk_id": f"{filename}::chunk_{i}",
                "text": chunk,
            })

    print(f"Documents loaded: {len(documents)}")
    print(f"Total chunks created: {len(all_chunks)}")

    extra = len(all_chunks) - len(documents)
    if extra == 0:
        print("Every document fit into a single chunk (they're short and focused).")
    else:
        print(f"{extra} extra chunk(s) came from splitting longer documents.")

    print("\n--- Example chunk ---")
    print("Source:  ", all_chunks[0]["source"])
    print("Chunk id:", all_chunks[0]["chunk_id"])
    print("Text:    ", all_chunks[0]["text"][:200], "...")