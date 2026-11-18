from pydantic import BaseModel
from typing import List ,Optional, Literal

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer:Optional[str] =None
    sources : List[str]
    
class FeedbackRequest(BaseModel):
    query:str
    chunk:str
    label:Literal[0,1]

