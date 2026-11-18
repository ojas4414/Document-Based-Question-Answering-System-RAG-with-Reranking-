import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from backend.query import faiss_search, rerank_results
from backend.store import load_chunks

KS = (1, 3, 5)


def load_questions(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            rows.append(json.loads(line))
    return rows


def norm(text):
    return " ".join(text.split())


def first_hit(results, span, cut):
    for rank, r in enumerate(results[:cut], 1):
        if span in norm(r["chunk"]):
            return rank
    return None


def score(ranks, cut):
    n = len(ranks)
    out = {f"recall@{k}": sum(1 for r in ranks if r and r <= k) / n for k in KS}
    out[f"MRR@{cut}"] = sum(1 / r for r in ranks if r and r <= cut) / n
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--questions", default="eval/questions.jsonl")
    p.add_argument("--pool", type=int, default=20)
    p.add_argument("--cut", type=int, default=5)
    p.add_argument("--out", default="results/retrieval_eval.md")
    args = p.parse_args()

    qs = load_questions(args.questions)
    chunks = [norm(c) for c in load_chunks()]
    missing = [q["question"] for q in qs if not any(norm(q["answer_span"]) in c for c in chunks)]
    if missing:
        sys.exit(f"{len(missing)} answer spans not found in any chunk: {missing}")

    faiss_ranks, rerank_ranks, pool_ranks, rows = [], [], [], []
    for q in qs:
        span = norm(q["answer_span"])
        pool = faiss_search(q["question"], top_k=args.pool)
        reranked = rerank_results(q["question"], pool)
        fr = first_hit(pool, span, args.cut)
        rr = first_hit(reranked, span, args.cut)
        pr = first_hit(pool, span, args.pool)
        faiss_ranks.append(fr)
        rerank_ranks.append(rr)
        pool_ranks.append(pr)
        rows.append((q["question"], pr, fr, rr))

    a = score(faiss_ranks, args.cut)
    b = score(rerank_ranks, args.cut)
    pool_recall = sum(1 for r in pool_ranks if r) / len(qs)
    cols = list(a)

    lines = [
        "| System | " + " | ".join(cols) + " |",
        "|---" * (len(cols) + 1) + "|",
        "| (a) FAISS only | " + " | ".join(f"{a[c]:.3f}" for c in cols) + " |",
        "| (b) FAISS + reranker | " + " | ".join(f"{b[c]:.3f}" for c in cols) + " |",
        "",
        f"Gold span anywhere in the FAISS pool of {args.pool} (ceiling for any reranker): {pool_recall:.3f}",
        f"Questions where the reranker changed the top-{args.cut} rank of the gold chunk: "
        f"{sum(1 for _, _, f, r in rows if f != r)} of {len(qs)}",
    ]
    table = "\n".join(lines)
    print(table)

    per_q = ["| # | Question | Rank in pool | Rank FAISS | Rank reranked |", "|---|---|---|---|---|"]
    for i, (text, pr, fr, rr) in enumerate(rows, 1):
        per_q.append(f"| {i} | {text} | {pr or '-'} | {fr or '-'} | {rr or '-'} |")

    cmd = Path(os.path.relpath(sys.executable)).as_posix() + " " + " ".join(sys.argv)
    docs = sorted({q["doc"] for q in qs})
    report = [
        "# Retrieval evaluation",
        "",
        f"- Date: {date.today().isoformat()}",
        f"- Eval set: {len(qs)} questions from `{args.questions}` (documents: {', '.join(docs)})",
        f"- Chunks in index: {len(chunks)}",
        f"- Protocol: FAISS returns a pool of {args.pool}; (a) keeps FAISS order, (b) reranks the pool; both are cut to the top {args.cut}.",
        f"- A chunk counts as relevant if it contains the question's answer span (whitespace-normalised, case-sensitive). "
        f"MRR@{args.cut} scores 0 when the gold chunk is outside the top {args.cut}.",
        f"- Command: `{cmd}`",
        "",
        "## Results",
        "",
        table,
        "",
        "## Per question (rank of first relevant chunk, '-' = not found)",
        "",
        "\n".join(per_q),
        "",
    ]
    Path(args.out).parent.mkdir(exist_ok=True)
    Path(args.out).write_text("\n".join(report), encoding="utf-8")
    print(f"\nsaved {args.out}")


if __name__ == "__main__":
    main()
