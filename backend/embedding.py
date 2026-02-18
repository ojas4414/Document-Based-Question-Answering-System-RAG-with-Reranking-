from sentence_transformers import SentenceTransformer
import numpy as np

model= SentenceTransformer("all-MiniLM-L6-v2")
def normalization(vectors:np.ndarray):
    norm=np.linalg.norm(vectors,axis=1,keepdims=True)
    return vectors/norm

def embedding_text(text):
    embedding=model.encode(text,convert_to_numpy=True,show_progress_bar=True)
    embedding=embedding.astype("float32")
    embedding=normalization(embedding)
    return embedding
