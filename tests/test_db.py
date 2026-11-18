import sqlite3

import pytest

from backend import db


@pytest.fixture
def conn(tmp_path):
    c = db.connect(str(tmp_path / "test.db"))
    c.executemany("INSERT INTO documents VALUES (?, ?, ?, ?, ?)", [
        (1, "a.pdf", "aa", 10, "2026-11-01T00:00"),
        (2, "b.pdf", "bb", 5, "2026-11-01T00:00"),
    ])
    c.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)", [
        (10, 1, 0, "alpha", 0),
        (11, 1, 1, "beta", 1),
        (20, 2, 0, "gamma", 2),
    ])
    c.executemany("INSERT INTO queries VALUES (?, ?, ?)", [
        (1, "what is alpha", "2026-11-01T10:00"),
        (2, "what is gamma", "2026-11-03T08:00"),
    ])
    c.executemany(
        "INSERT INTO feedback (query_id, chunk_id, rank_shown, label, created_at) VALUES (?, ?, ?, ?, ?)", [
            (1, 10, 1, 1, "2026-11-01T10:00"),
            (1, 11, 2, 0, "2026-11-01T10:01"),
            (1, 10, 1, 0, "2026-11-02T09:00"),
            (2, 20, 1, 1, "2026-11-03T08:00"),
            (2, 10, 3, 0, "2026-11-03T08:01"),
        ])
    yield c
    c.close()


def test_join_returns_source_for_every_vote(conn):
    rows = conn.execute(db.FEEDBACK_WITH_SOURCE).fetchall()
    assert len(rows) == 5
    assert rows[0] == ("what is alpha", "a.pdf", 0, 1, 1, "2026-11-01T10:00")
    assert rows[-1] == ("what is gamma", "a.pdf", 0, 3, 0, "2026-11-03T08:01")


def test_group_by_rate_per_document(conn):
    rows = conn.execute(db.DOCUMENT_FEEDBACK_STATS, {"min_votes": 1}).fetchall()
    assert rows == [("b.pdf", 1, 1, 1.0), ("a.pdf", 4, 1, 0.25)]


def test_group_by_having_filters_small_documents(conn):
    rows = conn.execute(db.DOCUMENT_FEEDBACK_STATS, {"min_votes": 2}).fetchall()
    assert rows == [("a.pdf", 4, 1, 0.25)]


def test_window_keeps_latest_vote_per_query_chunk(conn):
    rows = conn.execute(db.LATEST_LABELS).fetchall()
    assert rows == [
        ("what is alpha", "alpha", 0),
        ("what is alpha", "beta", 0),
        ("what is gamma", "alpha", 0),
        ("what is gamma", "gamma", 1),
    ]


def test_window_breaks_timestamp_ties_by_insert_order(conn):
    conn.execute(
        "INSERT INTO feedback (query_id, chunk_id, rank_shown, label, created_at) VALUES (2, 20, 1, 0, '2026-11-03T08:00')")
    rows = dict(((q, c), l) for q, c, l in conn.execute(db.LATEST_LABELS))
    assert rows[("what is gamma", "gamma")] == 0


def test_chunk_history_newest_first(conn):
    rows = conn.execute(db.CHUNK_FEEDBACK_HISTORY, {"chunk_id": 10}).fetchall()
    assert rows == [(3, 0, "2026-11-03T08:01"), (1, 0, "2026-11-02T09:00"), (1, 1, "2026-11-01T10:00")]


def test_chunk_history_uses_index_for_filter_and_order(conn):
    plan = " ".join(r[3] for r in conn.execute("EXPLAIN QUERY PLAN " + db.CHUNK_FEEDBACK_HISTORY, {"chunk_id": 10}))
    assert "USING INDEX idx_feedback_chunk_time (chunk_id=?)" in plan
    assert "TEMP B-TREE" not in plan


@pytest.mark.parametrize("sql", [
    "INSERT INTO feedback (query_id, chunk_id, rank_shown, label, created_at) VALUES (1, 10, 1, 2, 't')",
    "INSERT INTO feedback (query_id, chunk_id, rank_shown, label, created_at) VALUES (1, 999, 1, 1, 't')",
    "INSERT INTO feedback (query_id, chunk_id, rank_shown, label, created_at) VALUES (1, 10, 0, 1, 't')",
    "INSERT INTO chunks (document_id, position, text) VALUES (1, 0, 'duplicate position')",
    "INSERT INTO documents (filename, sha256, pages, ingested_at) VALUES ('a.pdf', 'x', 1, 't')",
])
def test_constraints_reject_bad_rows(conn, sql):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)


def test_deleting_document_cascades_to_chunks_and_feedback(conn):
    conn.execute("DELETE FROM documents WHERE id = 1")
    assert conn.execute("SELECT COUNT(*) FROM chunks").fetchone() == (1,)
    assert conn.execute("SELECT COUNT(*) FROM feedback").fetchone() == (1,)
