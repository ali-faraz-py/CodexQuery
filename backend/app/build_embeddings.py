import json
import numpy as np
from fastembed import TextEmbedding

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

def main():
    print("Loading files...")
    with open("data/repo_files.json", "r", encoding="utf-8") as f:
        files = json.load(f)

    print("Chunking...")
    all_chunks = []
    for file_entry in files:
        all_chunks.extend(chunk_file(file_entry))
    print(f"  → {len(all_chunks)} chunks")

    print("Loading embedding model...")
    embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print("Embedding chunks...")
    texts = [c["text"] for c in all_chunks]
    vectors = np.array([e for e in embed_model.embed(texts)])

    metadata = [
        {"repo": c["repo"], "path": c["path"], "start_line": c["start_line"],
         "end_line": c["end_line"], "text": c["text"]}
        for c in all_chunks
    ]

    np.save("data/embeddings.npy", vectors)
    with open("data/chunks_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)

    print(f"Saved {len(all_chunks)} vectors to data/embeddings.npy and data/chunks_metadata.json")

if __name__ == "__main__":
    main()