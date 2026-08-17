import json
import os
from sentence_transformers import SentenceTransformer
import chromadb

CHUNK_SIZE = 60
CHUNK_OVERLAP = 10

def load_files():
    with open("data/repo_files.json", "r", encoding="utf-8") as f:
        return json.load(f)

def chunk_file(file_entry):
    lines = file_entry["content"].splitlines()

    if len(lines) == 0:
        return []

    chunks = []
    if len(lines) <= CHUNK_SIZE:
        chunks.append({
            "repo": file_entry["repo"],
            "path": file_entry["path"],
            "start_line": 1,
            "end_line": len(lines),
            "text": file_entry["content"]
        })
        return chunks

    
def main():
    print("Loading files...")
    files = load_files()

    print("Chunking...")
    all_chunks = []
    for file_entry in files:
        all_chunks.extend(chunk_file(file_entry))
    print(f"  → {len(all_chunks)} chunks from {len(files)} files")

    print("Loading embedding model (this downloads ~80MB the first time)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Embedding chunks...")
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Storing in ChromaDB...")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection("codexquery")

    ids = [f"{c['repo']}_{c['path']}_{c['start_line']}" for c in all_chunks]
    metadatas = [
        {"repo": c["repo"], "path": c["path"], "start_line": c["start_line"], "end_line": c["end_line"]}
        for c in all_chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas
    )

    print(f"\nDone. {len(all_chunks)} chunks stored in ChromaDB (chroma_db/ folder).")

if __name__ == "__main__":
    main()