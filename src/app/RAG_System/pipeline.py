import os
import httpx
from dotenv import load_dotenv
import warnings
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from typing import List, Any

# Suppress warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

load_dotenv()

class RAGPipeLine():
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = "./db/chroma"

    async def web_doc_inventory(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
            response = await client.get("https://shench35.github.io/Generative-AI-Conversation/")
            
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n\n", strip=True)
        return [Document(page_content=text, metadata={"source": "https://shench35.github.io/Generative-AI-Conversation/"})]

    async def chunking(self, docs: List):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(docs)

    async def embedding_docs_and_retrival(self, splits: Any):
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )
        
        try:
            existing_count = len(vectorstore.get()['ids'])
        except Exception:
            existing_count = 0
        
        if existing_count == 0:
            print("Vector store is empty. Indexing documents...")
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding_model,
                persist_directory=self.persist_directory
            )
        
        return vectorstore.as_retriever()

    async def prompt_template(self):
        prompt = ChatPromptTemplate.from_template("""You are an exciting to call with and well collected and always ready to hear people our agent for Conversation with Human. 
                                                  Use the following pieces of retrieved context to response as humanly as possible. 
                                                  If you don't hae the response, just say that you don't know. 
                                                  Use a well structured and easy to understand grammers and keep the answer concise.

                                                  Question: {question} 

                                                  Context: {context} 

                                                  Answer:"""
                                                  )
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        return prompt, llm
    
    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    async def rag_chain(self, docs: List, retriever:Any, prompt: Any, llm: Any, query:str):
        rag_chain = (
            {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
            )
        return await rag_chain.ainvoke(query)
