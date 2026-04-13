import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import Column, func, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel
from src.auth.utils import verify_password


class User(SQLModel, table=True):

    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(String(50), nullable=False, server_default="user"))
    is_verified: bool = False
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    

    def __repr__(self):
        return f"<User {self.username}>"
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)


class QueryLog(SQLModel, table=True):
    
    __tablename__ = "query_logs"
    
    id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    query: str = Field(sa_column=Column(Text, nullable=False))
    response: str = Field(sa_column=Column(Text, nullable=True))
    timestamp: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    
    def __repr__(self):
        return f"<QueryLog user_id={self.user_id} timestamp={self.timestamp}>"


class UserQuery(SQLModel, table=True):
    __tablename__ = "User_query"

    qid: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    )
    uid: Optional[uuid.UUID] = Field(sa_column=Column(UUID, ForeignKey("users.uid"), nullable=True), default=None)
    session_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4))
    query: str = Field(sa_column=Column(Text, nullable=False))
    response: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))

    def __repr__(self):
        return f"<UserQuery qid={self.qid} session_id={self.session_id}>"
