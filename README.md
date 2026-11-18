# 📄 Document Question Answering System (RAG)

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** system that answers user questions using custom documents.

Instead of relying solely on a language model’s internal knowledge, the system retrieves relevant document context and generates grounded answers. This improves factual accuracy and reduces hallucinations.

---

## 🚀 Why This Project Matters

Large Language Models often struggle with domain-specific knowledge.

This system solves that by:

* retrieving relevant document context
* reranking results for relevance
* generating grounded answers using retrieved knowledge

This architecture is widely used in enterprise search, knowledge assistants, and document intelligence systems.

---

## 🧠 System Architecture

1. **Document Ingestion & Chunking**
   Documents are split into overlapping chunks for semantic retrieval.

2. **Semantic Embedding**
   SentenceTransformers convert text chunks into vector representations.

3. **Vector Search (FAISS)**
   Similar chunks are retrieved using cosine similarity.

4. **Supervised Reranking**
   A trained reranking model improves retrieval relevance.

5. **LLM Answer Generation**
   Retrieved context is passed to an LLM to generate grounded responses.
   Generation calls the **OpenAI API first**, and automatically falls back to a
   **local Ollama model** if that call fails for any reason — missing or invalid
   key, rate limit, exhausted credits, or network error. Both paths build the
   identical prompt, so answers stay comparable, and every call logs which path
   produced it.

6. **FastAPI Backend**
   Clean REST endpoints expose ingestion, retrieval, and query functionality.

---

## ✨ Key Features

✔ Custom document ingestion
✔ FAISS-powered semantic search
✔ Trained reranker for improved relevance
✔ Grounded answers using retrieved context
✔ Resilient generation: OpenAI primary with automatic local-model fallback
✔ Modular pipeline design
✔ Logging & evaluation support

---

## 🔌 API Endpoints

### POST `/ingest`

Builds the vector index from uploaded documents.

### POST `/search`

Returns retrieved document chunks (useful for debugging retrieval).

### POST `/query`

Runs the full RAG pipeline and returns the final answer.

---

## 🛠 Tech Stack

* Python
* FastAPI
* FAISS
* SentenceTransformers
* Scikit-learn
* OpenAI API (primary generation)
* Ollama (local fallback generation)

---

## ⚙️ How to Run

### 1️⃣ Clone the repository

```
git clone https://github.com/ojas4414/Document-Based-Question-Answering-System-RAG-with-Reranking-
cd Document-Based-Question-Answering-System-RAG-with-Reranking-
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Configure generation

Generation tries OpenAI first and falls back to a local Ollama model, so you can
run this with an OpenAI key, without one, or with both.

**OpenAI path (primary)** — set your key as an environment variable:

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
```

```bash
# macOS / Linux
export OPENAI_API_KEY="sk-..."
```

**Ollama path (fallback)** — install [Ollama](https://ollama.com), then pull a model:

```
ollama pull llama3.2:3b
```

Ollama loads the model into memory on first use, which can take 30-60s on a
CPU-only machine and may return a `500` while it does. Warm it up once before
your first `/query` so the fallback answers immediately:

```
curl http://localhost:11434/api/generate -d '{"model":"llama3.2:3b","prompt":"hi","stream":false}'
```

Optional overrides (defaults shown):

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | *unset* | If absent, generation goes straight to the fallback |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model used for generation |
| `OLLAMA_MODEL` | `llama3` | Local model used for the fallback |

If neither path is available, `/query` raises a clear error naming both causes.

### 4️⃣ Add your documents

Drop one or more PDFs into `data/documents/`. The loader indexes every `*.pdf`
in that folder.

### 5️⃣ Start the API server

Run from the **repository root** — the backend uses package-qualified imports:

```
uvicorn backend.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

### 6️⃣ Open API documentation

```
http://127.0.0.1:8000/docs
```

### 7️⃣ Ingest documents

`POST /ingest` reads every PDF in `data/documents/`, chunks it, embeds the
chunks, and writes the FAISS index:

```
curl -X POST http://127.0.0.1:8000/ingest
```

### 8️⃣ Ask questions

```
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the report say about water consumption?"}'
```

The server log records which generation path answered each call:

```
INFO | RAG-app | GENERATION PATH = OPENAI (model=gpt-4o-mini)
```

or, when OpenAI is unavailable:

```
WARNING | RAG-app | OpenAI generation failed (...) - falling back to Ollama
INFO    | RAG-app | GENERATION PATH = OLLAMA FALLBACK (model=llama3.2:3b)
```

---

## Evaluation

Retrieval was measured on 25 questions about one document, the Infosys ESG Report 2025-26
(162 pages, 186 chunks). Full per-question output: [results/retrieval_eval.md](results/retrieval_eval.md).

FAISS returns a pool of 20 chunks. (a) keeps the FAISS order; (b) reorders the pool with the
trained reranker. Both are cut to the top 5. A result counts as correct if the chunk contains the
question's gold answer span.

| System | recall@1 | recall@3 | recall@5 | MRR@5 |
|---|---|---|---|---|
| (a) FAISS only | 0.400 | 0.680 | 0.720 | 0.537 |
| (b) FAISS + reranker | 0.360 | 0.640 | 0.680 | 0.483 |

- The gold chunk was somewhere in the pool of 20 for 21 of 25 questions (0.840), so that is the
  ceiling for any reranker on this set.
- **The reranker adds nothing; it makes retrieval slightly worse.** It changed the gold chunk's
  rank on 4 questions, and moved it down every time (once out of the top 5).
- Why: `models/reranker.pkl` was trained on 6 examples (3 hard-coded queries, each with one
  "positive" and one "negative" chunk chosen by `random.choice`), so its labels carry no signal.
  The learned weights are 0.170 on cosine similarity, -0.0000072 on chunk length and -0.00077 on
  query-word overlap. The order is mostly cosine again, but the small negative overlap weight can
  push a chunk that shares more words with the query below one that shares fewer.
- 13 of the 25 questions are deliberately worded differently from the passage. FAISS found 9 of
  those 13 in the top 5, and 9 of the other 12.

Reproduce (after adding the PDF to `data/documents/`):

```
python scripts/dump_chunks.py
python eval.py --questions eval/questions.jsonl --pool 20 --cut 5 --out results/retrieval_eval.md
```

Limitations:

- Small set: 25 questions, so one question moves recall by 0.04. The 0.04 gap between (a) and (b)
  is a single question at each cut-off and is not evidence of anything beyond "no improvement".
- Single document; results may not transfer to other PDFs.
- The questions and gold spans in [eval/questions.jsonl](eval/questions.jsonl) were
  **AI-generated** (Claude) and spot-checked by the author. Passages were picked on a fixed
  schedule (every 7th chunk from chunk 4) and the set was committed before any retrieval was run.
- One gold span per question; a different chunk that also answers the question counts as a miss.
- The reranker was evaluated as shipped and was not retrained or tuned.

---

## Data model

A SQLite schema for documents, chunks, queries and relevance feedback, in
[backend/schema.sql](backend/schema.sql), with queries in [backend/db.py](backend/db.py).
It is not wired into the API yet: the app still stores chunks and feedback in pickle files
(`index/chunks.pkl`, `data/feedback.pkl`), and this schema is the intended replacement.

```
documents 1──* chunks 1──* feedback *──1 queries
```

| Table | Key columns | Why |
|---|---|---|
| `documents` | `id` PK, `filename` UNIQUE, `sha256` | One row per PDF; the hash tells a changed file from an unchanged one on re-ingest |
| `chunks` | `id` PK, `document_id` FK, UNIQUE `(document_id, position)`, `faiss_id` UNIQUE | A chunk's identity is its place in its document. `faiss_id` is kept separate because FAISS row numbers are reassigned whenever the index is rebuilt |
| `queries` | `id` PK, `text`, `created_at` | One row per question asked |
| `feedback` | `query_id` FK, `chunk_id` FK, `rank_shown`, `label` CHECK 0/1 | A user's relevant / not-relevant vote on a chunk shown at a given rank; the CHECK keeps labels usable by `train_reranker.py` |

Foreign keys use `ON DELETE CASCADE`, so deleting a document removes its chunks and their feedback.
SQLite enforces foreign keys only when `PRAGMA foreign_keys = ON` is set, which `db.connect()` does.

Indexes: SQLite does not index foreign-key columns automatically, so `feedback` gets
`idx_feedback_chunk_time (chunk_id, created_at)` and `idx_feedback_query (query_id)`.

Queries in `backend/db.py`:

- `FEEDBACK_WITH_SOURCE` (join): every vote with its query text, document and chunk position.
- `DOCUMENT_FEEDBACK_STATS` (GROUP BY): votes and relevant-rate per document, `HAVING` a minimum vote count.
- `LATEST_LABELS` (window function): `ROW_NUMBER() OVER (PARTITION BY query_id, chunk_id ORDER BY created_at DESC)` keeps only the newest vote per (query, chunk), so a user who changes their mind does not leave two contradictory training labels.
- `CHUNK_FEEDBACK_HISTORY` (uses an index): all votes on one chunk, newest first. The composite index covers both the filter and the sort; SQLite's plan is `SEARCH feedback USING INDEX idx_feedback_chunk_time (chunk_id=?)`, with no temp B-tree for the `ORDER BY`.

Tests ([tests/test_db.py](tests/test_db.py)) build a temporary database, check each query's exact
output, the constraints, the cascade, and the query plan:

```
pip install -r requirements-dev.txt
python -m pytest tests/test_db.py
```

---

## 📌 Example Use Cases

* Research document search
* Academic or legal knowledge bases
* Company internal knowledge assistants
* Technical documentation QA

---

## 🔮 Future Improvements

* Web interface for querying
* Hybrid search (keyword + vector)
* Streaming responses
* Feedback-based continuous learning

---

## 👨‍💻 Author

Built to explore retrieval-augmented generation, semantic search, and grounded AI systems.
