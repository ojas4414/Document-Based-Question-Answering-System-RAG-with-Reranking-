import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import ingest_doc
from backend.store import load_chunks

OUT = Path("index/chunks_dump.txt")


def main():
    print(ingest_doc())
    chunks = load_chunks()
    with open(OUT, "w", encoding="utf-8") as f:
        for i, c in enumerate(chunks):
            f.write(f"===== CHUNK {i} =====\n{c}\n\n")
    print(f"wrote {len(chunks)} chunks to {OUT}")


if __name__ == "__main__":
    main()
