from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import chromadb
from fastembed import TextEmbedding
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
embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection("codexquery")

if collection.count() == 0:
    print("ChromaDB is empty — building index from data/repo_files.json...")

    CHUNK_SIZE = 60
    CHUNK_OVERLAP = 10

    def chunk_file(file_entry):
        lines = file_entry["content"].splitlines()
        if len(lines) == 0:
            return []
        chunks = []
        if len(lines) <= CHUNK_SIZE:
            chunks.append({
                "repo": file_entry["repo"], "path": file_entry["path"],
                "start_line": 1, "end_line": len(lines), "text": file_entry["content"]
            })
            return chunks
        start = 0
        while start < len(lines):
            end = min(start + CHUNK_SIZE, len(lines))
            chunks.append({
                "repo": file_entry["repo"], "path": file_entry["path"],
                "start_line": start + 1, "end_line": end,
                "text": "\n".join(lines[start:end])
            })
            if end == len(lines):
                break
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    with open("data/repo_files.json", "r", encoding="utf-8") as f:
        files = json.load(f)

    all_chunks = []
    for file_entry in files:
        all_chunks.extend(chunk_file(file_entry))

    texts = [c["text"] for c in all_chunks]
    embeddings = [e.tolist() for e in embed_model.embed(texts)]
    ids = [f"{c['repo']}_{c['path']}_{c['start_line']}" for c in all_chunks]
    metadatas = [
        {"repo": c["repo"], "path": c["path"], "start_line": c["start_line"], "end_line": c["end_line"]}
        for c in all_chunks
    ]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Index built: {len(all_chunks)} chunks stored.")
else:
    print(f"ChromaDB already has {collection.count()} chunks — skipping rebuild.")

DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY")

class QueryRequest(BaseModel):
    question: str
    api_key: str | None = None

@app.get("/")
def health_check():
    return {"status": "CodexQuery API is running"}

@app.post("/query")
def query(request: QueryRequest):
    question_embedding = [e.tolist() for e in embed_model.embed([request.question])]

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