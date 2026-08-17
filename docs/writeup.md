# Building a RAG assistant from scratch (as someone who'd never touched one)

A few weeks ago, "RAG" and "LLMs" were a wall of intimidating jargon to me. I have a data science background — my master's thesis was on evaluating time-series forecasting models — and I'm comfortable in Python, but the whole world of embeddings, vector databases, and retrieval-augmented generation felt like something other people knew how to do.

So I decided to build one. Not by following a copy-paste tutorial, but from the ground up, writing and understanding each piece myself, until the fog turned into something I could actually reason about. This is the story of that project: a small assistant I call the **Dog Wiki Assistant**, and everything I learned making it.

## What I built

The Dog Wiki Assistant answers questions about dogs — breeds, everyday care, health, training — using a knowledge base I put together, rather than whatever the language model happened to memorise. You type a question into a web page ("Is a husky a good dog for a hot climate?", "how do I stop my puppy nipping?") and it gives a clear, practical answer drawn only from its documents. Just as importantly, if you ask it something it doesn't have information about, it tells you so instead of making something up.

Under the hood it's a full retrieval-augmented generation pipeline with a FastAPI backend, a separate frontend, a Chroma vector database, and the whole thing packaged with Docker so it runs with a single command.

## Why a dog wiki?

I wanted a topic that was concrete, a little fun, and rich enough to ask real questions about. A dog knowledge base fit perfectly: there's genuine information a first-time owner or a curious person might want, and the questions have real answers you can check. I ended up writing around 90 short reference documents (breed profiles, care guides, health basics, training advice) plus a handful of longer in-depth guides.

That last detail turned out to matter more than I expected, which brings me to the first real lesson.

## Lesson 1: your system is only as good as your data

Early on, all my documents were short — a few sentences each. That meant my "chunking" step (splitting documents into searchable pieces) never actually did anything, because each document was already smaller than a chunk. It technically worked, but it wasn't testing the thing chunking exists for.

So I added several long-form guides, and suddenly chunking had real work to do: a 1,000-word guide gets split into a dozen overlapping pieces, and retrieval has to find the *right piece inside* a long document, not just the right file. That's the actual problem real RAG systems solve.

I also learned to be careful about *what* goes into the knowledge base. For the sections about local dog laws and shelters, I deliberately kept the information general and refused to invent specific addresses or phone numbers — because a knowledge base that confidently states made-up facts is worse than one that says "check the official source." Getting the data right is at least half of building a good RAG system.

## How it actually works

Once I understood the pieces, the pipeline stopped being mysterious. It's five steps:

1. **Chunking** — split every document into overlapping word-based chunks so each piece is a searchable, self-contained unit.
2. **Embedding** — turn each chunk into a vector of numbers that captures its *meaning*, using OpenAI's `text-embedding-3-small` model. The magic here is that similar meanings produce similar vectors, even when the words are different — "nipping" lands close to "biting and mouthing" despite sharing no letters.
3. **Storage** — load all those vectors into ChromaDB, a vector database built for fast similarity search.
4. **Retrieval** — when a question comes in, embed it the same way and ask Chroma for the closest chunks by meaning.
5. **Generation** — hand those chunks to the language model as context, with a firm instruction: answer *only* from this, and if the answer isn't here, say so.

The first time I saw a query about "nipping" correctly pull up a document about "biting" — matching on meaning, not keywords — the whole concept finally clicked. That's the entire trick of embeddings, and seeing it work on my own data was the moment it stopped being abstract.

## Lesson 2: build the plain version before reaching for a framework

There are frameworks that do most of this for you in a few lines. I deliberately didn't use them at first. I wrote the cosine-similarity function by hand, looped over the chunks myself, and saw exactly what was happening at each step. Only later did I move to ChromaDB — and because I'd already done it the manual way, I understood precisely what Chroma was doing for me under the hood, rather than treating it as a black box. I'd recommend that order to anyone learning: understand the mechanism first, adopt the convenience second.

## Turning it into a real app

A script in a terminal isn't a project you can show anyone, so I wrapped the pipeline in a **FastAPI** backend with an `/ask` endpoint, then built a simple frontend with a question box and an answer area.

I deliberately split the frontend and backend into two separately-served pieces that talk over HTTP — which meant running into **CORS**, the browser security rule that blocks a page on one origin from calling an API on another. Configuring it properly (rather than avoiding it) taught me how real web apps are structured, and why that error everyone hits actually exists.

Finally, I containerised everything with **Docker** and **Docker Compose**, so the entire app — backend and frontend together — starts with one command and runs identically on any machine. No more "activate the environment, open two terminals" dance; just `docker compose up`.

## Lesson 3: be suspicious of a perfect score

Because of my background, I wanted to actually *measure* whether the thing worked, not just eyeball it. So I built a test set of questions, each tagged with the document I'd expect the answer to come from, and wrote a small evaluation that checks how often retrieval surfaces the right source.

The first result was 100%. Every question, right source retrieved.

And instead of celebrating, I got suspicious — because a perfect score often means the test was too easy, not that the system is flawless. So I wrote a batch of deliberately harder questions: messy, real-user phrasing with typos, ambiguous queries, and questions naming two things at once. When retrieval *still* held up on those, the score meant something. That instinct — to distrust a flattering number and try to break your own system — was probably the most useful thing I brought from my old work into this new domain.


## What I actually took away

The biggest lesson wasn't technical. It was that the wall of intimidating jargon — LLMs, embeddings, vector search, Docker, CORS — was made of individual pieces, and each one turned out to be understandable once I stopped staring at the whole and just built the next small thing. Every concept felt like fog until I touched it, and then it wasn't.

I set out to learn RAG well enough to talk about it in an interview. I ended up with a containerised, documented, measured application that I understand line by line — and, more importantly, the confidence that the next unfamiliar thing is just another wall made of small, learnable pieces.

