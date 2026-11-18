# Document Question Answering (RAG with reranking)

Answers questions about your own PDFs: it splits them into chunks, finds the chunks closest to the question with FAISS, reorders them with a small trained reranker, and asks an LLM to answer from those chunks only.
It is a FastAPI service; generation uses OpenAI when `OPENAI_API_KEY` works and falls back to a local Ollama model otherwise.

## Run it

Put one or more PDFs in `data/documents/`, then:

```
pip install -r requirements.txt
uvicorn backend.main:app
curl -X POST http://127.0.0.1:8000/ingest
```

Then ask a question:

```
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{"query":"..."}'
```

Requires Python 3.10. Without an OpenAI key, install [Ollama](https://ollama.com), `ollama pull llama3.2:3b`
and set `OLLAMA_MODEL=llama3.2:3b` (the default, `llama3`, must otherwise be pulled).

## Results

Retrieval on 25 AI-generated questions about one 162-page PDF (details and limitations in [Evaluation](#evaluation)):

| System | recall@1 | recall@3 | recall@5 | MRR@5 |
|---|---|---|---|---|
| FAISS only | 0.400 | 0.680 | 0.720 | 0.537 |
| FAISS + reranker | 0.360 | 0.640 | 0.680 | 0.483 |

The shipped reranker does not help: it was trained on 6 randomly labelled examples.

## How it works

```
PDF -> pypdf text -> 400-word chunks (80-word overlap) -> all-MiniLM-L6-v2 embeddings -> FAISS IndexFlatIP
question -> embed -> FAISS top 10 -> reranker -> top 5 chunks -> LLM (OpenAI, else Ollama) -> answer
```

| Path | What it does |
|---|---|
| `backend/main.py` | API: `/health`, `/ingest`, `/search` (retrieval only), `/query` (retrieval + answer), `/feedback` |
| `backend/query.py` | FAISS search and reranking |
| `backend/feature.py`, `backend/train_reranker.py` | Reranker features (cosine, chunk length, word overlap) and logistic-regression training |
| `backend/LLM.py` | Prompt and generation, OpenAI first then Ollama |
| `frontend/app.py` | Optional Streamlit UI: `streamlit run frontend/app.py` |
| `eval.py`, `eval/questions.jsonl` | Retrieval evaluation |

`/feedback` takes `{"query", "chunk", "label": 0 or 1}`; `python -m backend.train_reranker` retrains the reranker on
the hard-coded examples plus that feedback. Interactive API docs are at `http://127.0.0.1:8000/docs`.

Generation settings (environment variables):

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | unset | If absent or failing, generation goes to Ollama |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `OLLAMA_MODEL` | `llama3` | Local fallback model |

The server log names the path used for each answer, e.g. `GENERATION PATH = OLLAMA FALLBACK (model=llama3.2:3b)`.
If neither path works, `/query` returns an error naming both causes.

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
