CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL,
    pages INTEGER NOT NULL CHECK (pages > 0),
    ingested_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    text TEXT NOT NULL,
    faiss_id INTEGER UNIQUE,
    UNIQUE (document_id, position)
);

CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    rank_shown INTEGER NOT NULL CHECK (rank_shown >= 1),
    label INTEGER NOT NULL CHECK (label IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_chunk_time ON feedback (chunk_id, created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_query ON feedback (query_id);
