import pickle
from pathlib import Path

FEEDBACK_PATH = Path("data/feedback.pkl")

def save_feedback(query: str, chunk: str, feedback_: str):
    FEEDBACK_PATH.parent.mkdir(exist_ok=True)

    if FEEDBACK_PATH.exists():
        with open(FEEDBACK_PATH, "rb") as f:
            data = pickle.load(f)
    else:
        data = []

    data.append((query, chunk, feedback_))

    with open(FEEDBACK_PATH, "wb") as f:
        pickle.dump(data, f)


def load_feedback():
    if not FEEDBACK_PATH.exists():
        return []
    with open(FEEDBACK_PATH, "rb") as f:
        return pickle.load(f)
