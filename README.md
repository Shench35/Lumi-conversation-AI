
# RAG Project: Intelligent Web-Augmented Conversation System

An advanced Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and Google Gemini. This application transforms static web content into a dynamic knowledge base, allowing users to have context-aware conversations powered by real-time data retrieval.

## 🚀 Features

- **Dynamic Web Scraped Context:** Automatically fetches and processes content from targeted web sources.
- **AI-Powered Retrieval:** Utilizes HuggingFace embeddings (`all-MiniLM-L6-v2`) and ChromaDB for high-performance semantic search.
- **Multimodal LLM Integration:** Powered by Google Gemini (`gemini-2.0-flash`) for concise, human-like responses.
- **Secure Authentication:** Complete JWT-based auth system with role-based access control (Admin/User) and email verification.
- **Scalable Architecture:** Fully containerized with Docker, featuring asynchronous database operations (SQLModel/PostgreSQL) and Redis-backed token security.

## 🛠️ Technical Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
- **RAG Framework:** [LangChain](https://www.langchain.com/)
- **Large Language Model:** [Google Gemini 2.0 Flash](https://ai.google.dev/)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/)
- **Primary Database:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Cache/Security:** [Redis](https://redis.io/) (Token Blocklisting)
- **Deployment:** [Docker](https://www.docker.com/) & [Uvicorn](https://www.uvicorn.org/)

## 🏗️ How It Was Built

1.  **Modular Design:** The project is structured into distinct modules: `auth` for security, `rag_db` for data persistence, and `RAG_System` for the core intelligence logic.
2.  **The RAG Pipeline:** 
    - **Extraction:** Custom scrapers using `BeautifulSoup4` and `requests` pull clean text from web targets.
    - **Chunking:** `RecursiveCharacterTextSplitter` optimizes text segments for embedding.
    - **Vectorization:** Texts are converted into 384-dimensional vectors using Sentence-Transformers.
    - **Retrieval:** A semantic search identifies the most relevant context for any user query.
3.  **Asynchronous First:** Every endpoint and database interaction is built using `async/await` to ensure high concurrency and responsiveness.
4.  **Containerization:** A multi-stage Docker strategy ensures that system dependencies and AI models are pre-cached for rapid deployment.

## 🌟 Benefits

- **Accuracy:** Reduces LLM hallucinations by providing factual, retrieved context.
- **Privacy & Security:** Implements rigorous token blocklisting and account verification.
- **Efficiency:** Pre-downloads heavy embedding models during build time to ensure the API is ready the moment the container starts.
- **Extensibility:** The modular `RAGPipeLine` class allows for easy swapping of LLMs (e.g., Ollama, OpenAI) or scrapers.

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Docker (optional)
- Redis Server
- Google AI API Key (for Gemini)

### Installation
1.  **Clone the repo:**
    ```bash
    git clone https://github.com/yourusername/RAG_Project.git
    cd RAG_Project
    ```
2.  **Set up environment variables (.env):**
    ```env
    DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
    GOOGLE_API_KEY=your_gemini_key
    REDIS_HOST=localhost
    JWT_SECRET=your_secret
    ```
3.  **Run with Docker:**
    ```bash
    docker build -t rag-app .
    docker run -p 8000:8000 --env-file .env rag-app
    ```

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
=======
