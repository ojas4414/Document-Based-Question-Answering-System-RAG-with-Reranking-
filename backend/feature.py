import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.embedding import embedding_text
from backend.logger import setup
logger=setup()

def feature_eng(query,chunk):
    q_vec=embedding_text([query])
    c_vec=embedding_text([chunk])

    scores = cosine_similarity(q_vec,c_vec)[0][0]
    length=len(chunk.split())
    overlaps = len(set(query.split()) & set(chunk.split()))


    return np.array([scores,length,overlaps])