# Architecture

This document explains how the Dog Wiki Assistant is built internally: how the
knowledge base becomes searchable, what happens when a question is asked, and
how the Docker containers, ports, and the OpenAI API fit together.

There are two distinct phases: **indexing** (done once, offline, whenever the
knowledge base changes) and **querying** (done every time a user asks a
question).

## 1. Indexing pipeline (offline)

Turns the raw `.txt` documents into a searchable vector database.

```mermaid
flowchart LR
    A["data/*.txt<br/>knowledge base<br/>(~95 documents)"] --> B["chunk_docs.py<br/>split into overlapping<br/>word-based chunks"]
    B --> C["build_index.py"]
    C -- "POST /v1/embeddings<br/>(batches of 100)" --> D[("OpenAI API<br/>text-embedding-3-small")]
    D -- "1536-dim vectors" --> C
    C --> E["chunk_embeddings.json<br/>(chunks + vectors, saved to disk)"]
    E --> F["load_to_chroma.py"]
    F --> G[("ChromaDB<br/>backend/chroma_db/")]
```

Run once with `python build_index.py` followed by `python load_to_chroma.py`
(from inside `backend/`), and again any time the documents in `data/` change.
This is the only step that calls OpenAI's **embeddings** endpoint.

## 2. Query flow (runtime)

What happens, in order, when a user types a question into the page.

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend container<br/>nginx, port 80→8080
    participant B as Backend container<br/>FastAPI, port 8000
    participant C as ChromaDB<br/>backend/chroma_db/
    participant O as OpenAI API

    U->>F: GET http://localhost:8080/
    F-->>U: index.html (served from image)

    Note over U,B: User types a question and clicks "Ask"

    U->>B: POST http://localhost:8000/ask<br/>{ "question": "..." }
    B->>O: POST /v1/embeddings<br/>(embed the question)
    O-->>B: query vector (1536 numbers)
    B->>C: collection.query(vector, top_k=3)
    C-->>B: top-3 chunks + source filenames
    B->>O: POST /v1/chat/completions<br/>(context + question, model: gpt-5-mini)
    O-->>B: generated answer
    B-->>U: { "answer": "...", "sources": [...] } JSON
```

Two things worth noting:

- **The browser calls the backend directly**, not through the frontend
  container. The frontend's only job is to serve the static page; the page's
  own JavaScript then talks straight to `http://localhost:8000`. This is
  exactly why **CORS** has to be configured on the backend — the browser sees
  the page (origin `:8080`) and the API (origin `:8000`) as two different
  origins.
- Every question makes **two** calls to OpenAI: one to embed the question
  (cheap), one to generate the answer (the main cost).

## 3. Docker containers, ports, and networking

How the two services are packaged and how traffic reaches them.

```mermaid
flowchart TB
    subgraph Host["Your machine (localhost)"]
        Browser["🌐 Browser"]
        Env[".env file<br/>OPENAI_API_KEY"]
        Vol["backend/chroma_db/<br/>mounted volume"]
    end

    subgraph DC["Docker Compose network"]
        FEC["frontend container<br/>nginx:alpine<br/>built from frontend/Dockerfile<br/>listens on port 80"]
        BEC["backend container<br/>python:3.12-slim + FastAPI<br/>built from backend/Dockerfile<br/>listens on port 8000"]
    end

    OpenAI[("api.openai.com<br/>external, HTTPS")]

    Browser -->|"localhost:8080 → container :80"| FEC
    Browser -->|"localhost:8000/ask → container :8000"| BEC
    Env -.->|"env_file, not baked into image"| BEC
    Vol -.->|"volume mount, persists between runs"| BEC
    BEC -->|"HTTPS, outbound only"| OpenAI
```

### Port mapping

| Service  | Host address            | Container port | Maps to |
|----------|--------------------------|-----------------|---------|
| frontend | `http://localhost:8080` | 80               | nginx serving `index.html` |
| backend  | `http://localhost:8000` | 8000             | FastAPI (`uvicorn`) |

`compose.yml`'s `ports: "8080:80"` and `"8000:8000"` mean **host:container** —
the first number is what you type in your browser; the second is what the
process inside the container actually listens on.

### Why the API key and the database aren't inside the image

Two deliberate design choices:

- **`.env` is never copied into the backend image** (`.dockerignore` blocks
  it). The key is injected at *run time* via `env_file` in `compose.yml`, so
  the image itself contains no secrets and could be shared safely.
- **`chroma_db/` is a mounted volume, not part of the image.** The image
  contains only code; the actual vector database lives on the host and is
  attached when the container starts. This also means the database survives
  container restarts and rebuilds.

### OpenAI endpoints used

| Endpoint                     | Called from        | When                              | Model                     |
|-------------------------------|---------------------|-------------------------------------|----------------------------|
| `POST /v1/embeddings`         | `build_index.py`, `search.py` | Indexing, and once per user question | `text-embedding-3-small`  |
| `POST /v1/chat/completions`   | `ask.py`            | Once per user question (generation) | `gpt-5-mini`               |

Both are standard OpenAI REST endpoints, called over HTTPS from inside the
backend container — outbound only; nothing external calls *into* the
container except through the mapped ports above.