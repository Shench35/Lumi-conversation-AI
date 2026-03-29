from fastapi import APIRouter, Depends
import chromadb
import ollama
import asyncio

from src.app.get_keyword import keyword_getter
from src.app.emb_scraper import clean_text, scrape_wikipedia
from src.app.text_to_embed import to_embeding
from src.app.schemas import QueryRequest

from sqlmodel.ext.asyncio.session import AsyncSession
from src.rag_db.main import get_session
from src.rag_db.models import User
from src.auth.dependencies import AccessTokenBearer
from src.auth.dependencies import RoleChecker
from sqlmodel import select
from fastapi.exceptions import HTTPException
from fastapi import status
from src.auth.services import UserService


main_route = APIRouter()
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")
# client = ollama.Client(host="http://host.docker.internal:11434")
client = ollama.Client(host="http://127.0.0.1:11434")
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
service = UserService()





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

    try:
        keyword = keyword_getter(q)

        existing = collection.get(ids=[keyword])
        if not existing["documents"]:
            result = scrape_wikipedia(keyword)
            if not result or not result.get("text"):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find relevant information for your query.")
            clean_text_result = clean_text(result["text"])
            to_embeding(clean_text_result, keyword)

        results = collection.query(query_texts=[q], n_results=1)
        context = results["documents"][0][0] if results["documents"] else ""

        # answer = client.generate(
        #     model="tinyllama",
        #     prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"
        # )
        

        answer = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.generate(
            model="tinyllama",
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"
        )
    )

        return {
            "answer": answer["response"],
            "keyword": keyword
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence system error: {str(e)}"
        )