from fastapi import APIRouter, Depends
import chromadb
import ollama
import asyncio
import os

from src.app.services.schemas import QueryRequest

from sqlmodel.ext.asyncio.session import AsyncSession
from src.rag_db.main import get_session
from src.rag_db.models import User, QueryLog, UserQuery
from src.auth.dependencies import AccessTokenBearer
from src.auth.dependencies import RoleChecker
from sqlmodel import select
from fastapi.exceptions import HTTPException
from fastapi import status
from src.auth.services import UserService
from src.app.RAG_System.pipeline import RAGPipeLine
import uuid


main_route = APIRouter(prefix="/app", tags=["App"])
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")
ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
client = ollama.Client(host=ollama_host)
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
service = UserService()
rag_pipeline = RAGPipeLine()




@main_route.get("/", dependencies=[Depends(role_checker)])
async def root(session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    user = token_details.get("user")
    user_email = user.get("email")

    result = await session.exec(select(User).where(User.email == user_email))
    db_user = result.first()

    return {
        "email": user_email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "username": db_user.username,
        "role": db_user.role,
    }



@main_route.post("/query")
async def query(
    request: QueryRequest,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker)
):
    user_email = token_details.get("user", {}).get("email")
    user = await service.get_user_by_email(user_email, session)

    if not user or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Check your email for the verification code."
        )

    q = request.q.strip()
    if not q:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    # Use provided session_id or create a new one
    session_id = request.session_id if request.session_id else uuid.uuid4()

    try:
       docs = await rag_pipeline.web_doc_inventory()
       print("Done with docs")

       splits = await rag_pipeline.chunking(docs)
       print("Done with spliting")

       retriever = await rag_pipeline.embedding_docs_and_retrival(splits)
       print("Done with retriever")

       prompt, llm = await rag_pipeline.prompt_template()
       print("Done with prompt and llm")

       answer = await rag_pipeline.rag_chain(docs, retriever, prompt, llm, q)
       print(answer)
       
       # Store in UserQuery table
       user_query = UserQuery(
           uid=user.uid,
           session_id=session_id,
           query=q,
           response=answer
       )
       session.add(user_query)
       await session.commit()
       
       return {
           "answer": answer,
           "session_id": session_id,
           "qid": user_query.qid
       }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence system error: {str(e)}"
        )