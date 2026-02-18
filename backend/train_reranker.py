import pickle
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression

from backend.feature import feature_eng
from backend.train_data import build_training_set
from backend.store import load_chunks
from backend.feedback_store import load_feedback


MODEL_PATH = Path("models/reranker.pkl")


def train():
    chunks = load_chunks()

    queries = [
        "How does document ingestion work?",
        "What is FAISS used for?",
        "How are embeddings created?",
    ]

    synthetic_data = build_training_set(chunks, queries)
    feedback_data = load_feedback()

    dataset = synthetic_data + feedback_data

    X = []
    y = []

    for query, chunk, label in dataset:
        X.append(feature_eng(query, chunk))
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print("Reranker trained and saved")
    print("Total samples:", len(y))
    print("Feedback samples:", len(feedback_data))


if __name__ == "__main__":
    train()
