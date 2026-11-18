import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")

FEEDBACK_WITH_SOURCE = """
SELECT q.text AS query, d.filename, c.position, f.rank_shown, f.label, f.created_at
FROM feedback f
JOIN queries q ON q.id = f.query_id
JOIN chunks c ON c.id = f.chunk_id
JOIN documents d ON d.id = c.document_id
ORDER BY f.created_at
"""

DOCUMENT_FEEDBACK_STATS = """
SELECT d.filename,
       COUNT(*) AS votes,
       SUM(f.label) AS relevant,
       ROUND(AVG(f.label), 3) AS relevant_rate
FROM feedback f
JOIN chunks c ON c.id = f.chunk_id
JOIN documents d ON d.id = c.document_id
GROUP BY d.id
HAVING COUNT(*) >= :min_votes
ORDER BY relevant_rate DESC, d.filename
"""

LATEST_LABELS = """
SELECT query, chunk, label
FROM (
    SELECT q.text AS query, c.text AS chunk, f.label,
           ROW_NUMBER() OVER (
               PARTITION BY f.query_id, f.chunk_id
               ORDER BY f.created_at DESC, f.id DESC
           ) AS rn
    FROM feedback f
    JOIN queries q ON q.id = f.query_id
    JOIN chunks c ON c.id = f.chunk_id
)
WHERE rn = 1
ORDER BY query, chunk
"""

CHUNK_FEEDBACK_HISTORY = """
SELECT rank_shown, label, created_at
FROM feedback
WHERE chunk_id = :chunk_id
ORDER BY created_at DESC
"""


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    return conn
