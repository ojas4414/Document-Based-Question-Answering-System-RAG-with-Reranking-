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
