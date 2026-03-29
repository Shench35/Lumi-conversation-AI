from pydantic import BaseModel

class QueryRequest(BaseModel):
    q: str
