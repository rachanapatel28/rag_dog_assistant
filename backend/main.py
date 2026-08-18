from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ask import answer_question

app = FastAPI(title = "Dog Assistant API", description="An API for answering questions about dogs using a retrieval-augmented generation approach.")

# Allow the separately-served frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str
    
@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: Question):
    answer, sources = answer_question(payload.question)
    unique_sorces = sorted(set(sources))
    return {"answer": answer, "sources": unique_sorces}
