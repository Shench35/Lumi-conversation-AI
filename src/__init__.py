from fastapi import FastAPI
from src.main import route

app = FastAPI(
    title="RAG API",
    description="A simple Retrieval-Augmented Generation (RAG) API using FastAPI, ChromaDB, and Ollama.",
    version="1.0.0"
)

app.include_router(route)                                                                                                                   