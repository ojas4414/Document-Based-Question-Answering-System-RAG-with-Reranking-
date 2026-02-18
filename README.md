# Document-Based-Question-Answering-System-RAG-with-Reranking-
## Overview
This project implements a Retrieval-Augmented Generation (RAG) system that answers user questions using custom documents.

## Architecture
1. Document ingestion and chunking
2. Semantic embedding using SentenceTransformers
3. Vector search using FAISS
4. Supervised reranking (trained model)
5. LLM-based answer generation
6. FastAPI backend with clean endpoints

## Key Features
- Custom document ingestion
- FAISS-based semantic retrieval
- Trained reranker for improved relevance
- LLM grounding using retrieved context
- Logging and evaluation

## API Endpoints
- POST /ingest – Build vector index
- POST /search – Debug retrieval
- POST /query – Full RAG pipeline

## Tech Stack
Python, FastAPI, FAISS, SentenceTransformers, scikit-learn, OpenAI API
