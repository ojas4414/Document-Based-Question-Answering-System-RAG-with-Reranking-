from pydantic import BaseModel
from typing import List ,Optional

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer:Optional[str] =None
    sources : List[str]
    
class FeedbackRequest(BaseModel):
    query:str
    chunk:str
    feedback_:str

