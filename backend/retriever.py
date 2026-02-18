import faiss
import numpy as np
from pathlib import Path
from backend.logger import setup
logger=setup()

INDEX_PATH=Path("index/faiss.index")

def indexing(embeddings:np.ndarray):
    logger.info("Starting indexing")
    dim=embeddings.shape[1]
    index=faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index
logger.info("Indexing completed")

def save_info(index):
    INDEX_PATH.parent.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
 
