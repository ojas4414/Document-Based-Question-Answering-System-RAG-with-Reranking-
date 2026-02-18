import faiss
from backend.embedding import embedding_text
from backend.store import load_chunks
from sklearn.metrics.pairwise import cosine_similarity
from backend.logger import  setup
import pickle
from backend.feature import feature_eng
from backend.logger import setup
logger = setup()

with open("models/reranker.pkl","rb") as f:
    reranker=pickle.load(f)

def rerank_results(query,results):
    reranked=[]

    for r in results:
        feats =feature_eng(query,r["chunk"]).reshape(1,-1)
        score= reranker.predict_proba(feats)[0][1]
        reranked.append((score,r))
    reranked.sort(reverse=True , key=lambda x: x[0])
    return [r for _,r in reranked]

logger=setup()
Index_Path="index/faiss.index"

def query_search(query:str,top_k: int =5):
    logger.info(f"Running retrievel for query:{query}")
    try :
        index=faiss.read_index(Index_Path)
    except Exception as e:
        logger.info("Faiss has failed to store index",exc_info=True)
        raise


    emb_q_vec=embedding_text([query]).astype("float32")
    logger.info(f"Query embedded")

    scores,indices=index.search(emb_q_vec,top_k)
    logger.info(f"Faiss search complete: {top_k}")
    logger.info(f"{len(indices)} candidate chunks")
    
    if not indices.any():
        logger.info("Faiss has returned no results")

    chunks=load_chunks()
    results=[]

    for score,indx in zip(scores[0],indices[0]):
        results.append({
            "chunk":chunks[indx],
            "score":float(score)
        }
        )
    logger.info(f"")
    results=rerank_results(query,results)
    return results
def fine_tune_results(query_emb,chunks,chunk_emb,top_k=5 ):
    logger.info(f"Reranking {len(chunks)} chunks") 

    scores=cosine_similarity(query_emb,chunk_emb)[0]
    ranked= sorted(
        zip(chunks,scores),
        reverse=True
    )
    return ranked[:top_k]

