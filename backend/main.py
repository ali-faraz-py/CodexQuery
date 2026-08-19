from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq, RateLimitError

load_dotenv()

app = FastAPI(title="CodexQuery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_collection("codexquery")

DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY")

class QueryRequest(BaseModel):
    question: str
    api_key: str | None = None

@app.get("/")
def health_check():
    return {"status": "CodexQuery API is running"}

@app.post("/query")
def query(request: QueryRequest):
    question_embedding = embed_model.encode([request.question]).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=4
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    RELEVANCE_THRESHOLD = 1.6
    relevant = [(c, m) for c, m, d in zip(chunks, metadatas, distances) if d < RELEVANCE_THRESHOLD]

    if not relevant:
        return {
            "answer": "I couldn't find anything in Ali's repositories relevant to that question. Try asking about a specific project or technical detail.",
            "sources": []
        }

    context_parts = []
    sources = []
    for chunk, meta in relevant:
        label = f"{meta['repo']}/{meta['path']} (lines {meta['start_line']}-{meta['end_line']})"
        context_parts.append(f"### {label}\n{chunk}")
        sources.append(label)

    context = "\n\n".join(context_parts)

    prompt = f"""You are CodexQuery, an assistant that answers questions about Ali's software projects using only the provided code context.

Context from Ali's repositories:
{context}

Question: {request.question}

Answer the question using only the context above. If the context doesn't contain enough information to answer, say so honestly rather than guessing."""

    active_key = request.api_key if request.api_key else DEFAULT_GROQ_KEY
    client = Groq(api_key=active_key)

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
    except RateLimitError as e:
        retry_after = e.response.headers.get("retry-after")
        raise HTTPException(
            status_code=429,
            detail={
                "message": "The shared demo API key has hit its rate limit.",
                "retry_after_seconds": int(float(retry_after)) if retry_after else None,
                "used_custom_key": request.api_key is not None
            }
        )

    return {
        "answer": completion.choices[0].message.content,
        "sources": sources
    }