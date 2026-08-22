# CodexQuery

An AI assistant that answers questions about my software portfolio, grounded in the actual code and documentation across 9 of my repositories, not generic knowledge about what those projects might contain.

**Live demo:** [codex-query.vercel.app](https://codex-query.vercel.app)

---

## What it does

CodexQuery is a Retrieval-Augmented Generation (RAG) chatbot. Instead of relying on an LLM's general training knowledge, it retrieves relevant chunks of my actual repositories, code, docstrings, and README content, and grounds every answer in that retrieved context. Ask it "what model does NeuralLens use?" and it answers from NeuralLens's real README, with a citation pointing to the exact file and line range.

This distinguishes it from most portfolio chatbots, which typically answer from a single resume or project-summary document. CodexQuery searches across an entire multi-project codebase and treats retrieval over code as a genuinely harder problem than retrieval over plain prose.

## Tech stack

**Backend:** FastAPI · Python · Groq (`openai/gpt-oss-120b`) · fastembed (`BAAI/bge-small-en-v1.5`) · numpy · deployed on Render

**Frontend:** Next.js (App Router) · Tailwind CSS · react-markdown · deployed on Vercel

## How it works

1. **Ingestion:**  A one-time local script pulls source files (`.py`, `.md`, `.txt`) from 9 of my repositories, filtering out dependency folders, build artifacts, and non-text files.
2. **Chunking:**  Files are split into overlapping ~60-line chunks (10-line overlap), so retrieval returns focused, coherent pieces rather than whole files or arbitrary cuts.
3. **Embedding:**  Each chunk is converted into a vector using `fastembed`, a lightweight ONNX-based embedding library.
4. **Storage:**  Vectors and their metadata (repo, file path, line range) are precomputed once and committed to the repo as a small numpy array, rather than stored in a live vector database.
5. **Retrieval:**  At query time, the question is embedded the same way, and compared against all stored vectors using cosine similarity (implemented directly in numpy) to find the top matches.
6. **Relevance filtering:**  Matches beyond a distance threshold are discarded, so genuinely off-topic questions get an honest "I don't know" instead of a forced answer.
7. **Generation:**  The retrieved chunks and the question are sent to Groq's `gpt-oss-120b`, instructed to answer only from the provided context and to say so plainly when the context isn't sufficient.

## Notable design decisions

**No vector database.** An early version used ChromaDB, but its dependency footprint (`kubernetes`, `grpcio`, `onnxruntime`, `opentelemetry`) was heavy enough to exceed Render's free-tier 512MB memory limit on its own, before any actual work ran. For a dataset of this size (under 100 chunks), a vector database's indexing machinery is unnecessary, a hand-written numpy cosine-similarity search does the same job with a fraction of the memory, and is mathematically equivalent for a dataset this size.

**Graceful rate-limit handling.** The backend uses a single shared Groq API key. If it's exhausted, the frontend shows a live countdown (read from Groq's actual `retry-after` response header) and offers an inline field to paste a personal Groq key, so anyone testing the demo can keep going without waiting.

**Grounded, honest refusals.** The system prompt explicitly instructs the model to decline rather than guess when retrieved context doesn't answer the question, verified by testing questions with no relevant match (e.g. general knowledge questions unrelated to my repos), which the bot correctly declines to answer.

## Known limitations

- The shared demo API key has Groq's free-tier rate limits; heavy simultaneous use may trigger the rate-limit flow described above.
- Render's free tier spins down after inactivity, so the first request after a period of no traffic may take up to a minute.
- The indexed data is a snapshot from when it was last buil, it reflects my repositories as they were at that time, not live updates.

## Repositories indexed

NeuralLens · Picassify · DiabetesDetector · AetherQuant · deepfake-detector · SentimentSense · PersonalFinanceTracker · python-weather-app · Python-CurrencyConverter

---

Built by [Ali Faraz](https://github.com/ali-faraz-py), part of a portfolio of ML/AI projects spanning classification, computer vision, and now retrieval-augmented generation.