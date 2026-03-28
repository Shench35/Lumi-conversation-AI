from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.app.main import main_route
from src.auth.routes import auth_router
from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI(
    title="RAG API",
    description="A simple Retrieval-Augmented Generation (RAG) API using FastAPI, ChromaDB, and Ollama.",
    version="1.0.0"
)



@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "http://127.0.0.1:5500"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",  # ← this is the one hitting your backend
    ],  # VS Code Live Server default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_route) 
app.include_router(auth_router) 