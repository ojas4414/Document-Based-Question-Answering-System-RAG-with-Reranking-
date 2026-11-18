from  fastapi import FastAPI
from backend.schemas import QueryRequest,QueryResponse
from backend.chunker import chunk_text
from backend.loader import load_document
from backend.retriever import indexing,save_info
from backend.embedding import embedding_text
from backend.store import save_chunk
from backend.query import query_search
from backend.logger import setup
from backend.feedback_store import save_feedback
from backend.schemas import FeedbackRequest
from backend.LLM import generate_answer
############################################################

app =FastAPI(title="Document RAG API")
logger=setup()

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/query",response_model=QueryResponse)
def Query_docs(request:QueryRequest):
    q=request.query
    results=query_search(q,top_k=10)

    context_chunks=[r["chunk"] for r in results[:5]]

    answer=generate_answer(context_chunks,q)


 

    return QueryResponse(
        answer=answer,
        sources=context_chunks
    )

@app.post("/ingest")
def ingest_doc():

    logger.info("Ingestion started")
    doc =load_document("data/documents")
    logger.info(f"Loaded {len(doc)} documents")

    all_chunks=[]
    for _,text in doc:
        all_chunks.extend(chunk_text(text))
    logger.info(f"Created {len(all_chunks)} chunks") 

    embeddings=embedding_text(all_chunks)
    logger.info(f"Generated embeddings of shape {embeddings.shape}")

    index=indexing(embeddings)
    save_info(index)

    save_chunk(all_chunks)
    logger.info("Ingestion completed successfully")


    return{
            "documents_loaded":len(doc),
            "total_chunks":len(all_chunks),
            "embedding_dim":embeddings.shape[1],
            "example_chunk":all_chunks[0][:300]if all_chunks else " "
        }
@app.post("/search")
def search(Query:QueryRequest):

    q=Query.query
    results=query_search(q,top_k=5)

    return({
        "Results":results
    }
    )
   
@app.post("/feedback")
def feedback(feedback: FeedbackRequest):
    save_feedback(
        feedback.query,
        feedback.chunk,
        feedback.feedback_
    )
    logger.info("User feedback recorded")
    return {"status":"ok"}



