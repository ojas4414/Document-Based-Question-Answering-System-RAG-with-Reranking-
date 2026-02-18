import pickle
from pathlib import Path


Chunk_path=Path("index/chunks.pkl")

def save_chunk(chunks):
    Chunk_path.parent.mkdir(exist_ok=True)
    with open(Chunk_path,'wb') as f:
        pickle.dump(chunks,f)
def load_chunks():
    with open(Chunk_path,'rb') as f:
        return pickle.load(f)
 