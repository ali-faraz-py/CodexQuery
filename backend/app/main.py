from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import numpy as np
from fastembed import TextEmbedding
from groq import Groq, RateLimitError, AuthenticationError

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
embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("Loading precomputed embeddings...")
stored_vectors = np.load("data/embeddings.npy")
with open("data/chunks_metadata.json", "r", encoding="utf-8") as f:
    chunks_metadata = json.load(f)
print(f"Loaded {len(chunks_metadata)} chunks.")

def cosine_similarity_search(question_vector, top_k=4):
    question_vector = question_vector / np.linalg.norm(question_vector)
    norms = np.linalg.norm(stored_vectors, axis=1)
    normalized_stored = stored_vectors / norms[:, np.newaxis]
    similarities = normalized_stored @ question_vector
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [(chunks_metadata[i], 1 - similarities[i]) for i in top_indices]

DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY")

class QueryRequest(BaseModel):
    question: str
    api_key: str | None = None

@app.get("/")
def health_check():
    return {"status": "CodexQuery API is running"}

@app.post("/query")
def query(request: QueryRequest):
    question_vector = np.array(list(embed_model.embed([request.question]))[0])

    RELEVANCE_THRESHOLD = 1.6
    results = cosine_similarity_search(question_vector, top_k=4)
    relevant = [(meta, dist) for meta, dist in results if dist < RELEVANCE_THRESHOLD]

    if not relevant:
        return {
            "answer": "I couldn't find anything in Ali's repositories relevant to that question. Try asking about a specific project or technical detail.",
            "sources": []
        }

    context_parts = []
    sources = []
    for meta, dist in relevant:
        label = f"{meta['repo']}/{meta['path']} (lines {meta['start_line']}-{meta['end_line']})"
        context_parts.append(f"### {label}\n{meta['text']}")
        sources.append(label)

    context = "\n\n".join(context_parts)

    prompt = f"""You are CodexQuery, an assistant that answers questions about Ali's software projects.

Relevant information from Ali's repositories:
{context}

Question: {request.question}

Answer the question using the information above. If it doesn't contain enough detail to answer, say so honestly rather than guessing. Speak naturally, as if you simply know this information about Ali's projects — don't refer to "the context," "the documents," or how the information was provided to you."""

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
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "That API key doesn't look valid. Double-check it and try again."
            }
        )

    return {
        "answer": completion.choices[0].message.content,
        "sources": sources
    }