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

6. **FastAPI Backend**
   Clean REST endpoints expose ingestion, retrieval, and query functionality.

---

## ✨ Key Features

✔ Custom document ingestion
✔ FAISS-powered semantic search
✔ Trained reranker for improved relevance
✔ Grounded answers using retrieved context
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
* OpenAI API

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

### 3️⃣ Start the API server

```
uvicorn main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

### 4️⃣ Open API documentation

```
http://127.0.0.1:8000/docs
```

### 5️⃣ Ingest documents

Use the `/ingest` endpoint to build the vector index.

### 6️⃣ Ask questions

Send a request to `/query` to receive grounded answers.

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
