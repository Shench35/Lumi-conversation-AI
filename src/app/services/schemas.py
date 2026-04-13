import uuid
from typing import Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):
    q: str
    session_id: Optional[uuid.UUID] = None
