import os
from dotenv import load_dotenv
import warnings
from typing import List, Any

# Suppress warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
load_dotenv()

class RAGPipeLine():
    def __init__(self):
        self.persist_directory = "./db/chroma"
        self._embedding_model = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            # Switch to Google Embeddings to save RAM on Render
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from src.app.services.config import Config
            print("Initializing Google Generative AI Embeddings...")
            self._embedding_model = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=Config.GOOGLE_API_KEY
            )
        return self._embedding_model

    async def web_doc_inventory(self):
        import httpx
        from bs4 import BeautifulSoup
        from langchain_core.documents import Document
        # ... rest of the method logic
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            response = await client.get("https://shench35.github.io/Generative-AI-Conversation/")
            
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n\n", strip=True)
        return [Document(page_content=text, metadata={"source": "https://shench35.github.io/Generative-AI-Conversation/"})]

    async def chunking(self, docs: List):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(docs)

    async def embedding_docs_and_retrival(self, splits: Any):
        from langchain_community.vectorstores import Chroma
        print("Initializing Vector Store (In-Memory)...")
        # For simplicity and to avoid disk issues on Render, we'll index in-memory for now
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embedding_model
        )
        
        return vectorstore.as_retriever()

    async def prompt_template(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from src.app.services.config import Config

        prompt = ChatPromptTemplate.from_template("""You are an exciting to call with and well collected and always ready to hear people our agent for Conversation with Human. 
                                                  Use the following pieces of retrieved context to response as humanly as possible. 
                                                  If you don't hae the response, just say that you don't know. 
                                                  Use a well structured and easy to understand grammers and keep the answer concise.

                                                  Question: {question} 

                                                  Context: {context} 

                                                  Answer:"""
                                                  )
        print("Initializing LLM with Gemini 1.5 Flash...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0,
            google_api_key=Config.GOOGLE_API_KEY
        )
        return prompt, llm

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    async def rag_chain(self, docs: List, retriever:Any, prompt: Any, llm: Any, query:str):
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser

        print(f"Executing RAG Chain for query: {query}")
        # Ensure format_docs is used as a RunnableLambda for the pipeline
        from langchain_core.runnables import RunnableLambda

        context_chain = retriever | RunnableLambda(self.format_docs)

        rag_chain = (
            {"context": context_chain, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
            )
        return await rag_chain.ainvoke(query)
