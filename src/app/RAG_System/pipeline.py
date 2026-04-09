
import os
from dotenv import load_dotenv
import warnings
import bs4
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Suppress LangSmith connection warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

load_dotenv('c:/Users/LENOVO/Codes/RAG_Project/.env')

# LangSmith Configuration
langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
langsmith_project = os.getenv('LANGSMITH_PROJECT')

if langsmith_api_key:
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_API_KEY'] = langsmith_api_key
    if langsmith_project:
        os.environ['LANGCHAIN_PROJECT'] = langsmith_project
    print("✓ LangSmith tracing configured")
    print("⚠ Note: If traces fail to send, verify your API key at https://smith.langchain.com/settings/api_keys")
else:
    print("⚠ WARNING: LANGSMITH_API_KEY not found in .env file")

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    os.environ['OPENAI_API_KEY'] = openai_api_key
else:
    print("⚠ WARNING: OPENAI_API_KEY not found in .env file")

# Verify LangSmith configuration
print("\n=== LangSmith Configuration Status ===")
print(f"LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_ENDPOINT: {os.environ.get('LANGCHAIN_ENDPOINT')}")
print(f"LANGCHAIN_API_KEY: {'✓ Set' if os.environ.get('LANGCHAIN_API_KEY') else '✗ Not set'}")
print(f"LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT', 'default')}")
print("\n✅ All LangChain operations will be automatically traced!")
print("=====================================\n")


import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from typing import List, Any

class RAGPipeLine():
    async def web_doc_inventory(self):
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

        response = requests.get(
            "https://shench35.github.io/Generative-AI-Conversation/",
            headers=headers
            )
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n\n", strip=True)

        # Wrap in a LangChain Document so the rest of your pipeline stays the same
        docs = [Document(page_content=text, metadata={"source": "https://shench35.github.io/Generative-AI-Conversation/"})]
        return docs

    async def chunking(self, docs: List):
        # CHUNKING THE DATA 
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        return splits

    async def embedding_docs_and_retrival(self, splits: Any):
        # EMBEDDING THE TEXTS
        embd = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=splits,embedding=embd)

        # RETRIVAL 
        retriever = vectorstore.as_retriever()

        return retriever

    async def prompt_template(self):
        # PROMPT TEMPLATES 
        prompt = ChatPromptTemplate.from_template("""You are an exciting to call with and well collected and always ready to hear people our agent for Conversation with Human. 
                                                  Use the following pieces of retrieved context to response as humanly as possible. 
                                                  If you don't hae the response, just say that you don't know. 
                                                  Use a well structured and easy to understand grammers and keep the answer concise.

                                                  Question: {question} 

                                                  Context: {context} 

                                                  Answer:"""
                                                  )
        #LANGUAGE MODEL
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        return prompt, llm
    
    async def format_docs(self, docs):
        # Post-processing
        pro_docs = "\n\n".join(doc.page_content for doc in docs)
        return pro_docs
    
    async def rag_chain(self, docs: List, retriever:Any, prompt: Any, llm: Any, query:str):
        post_procees = self.format_docs(docs)
        # Chain
        rag_chain = (
            {"context": retriever | post_procees, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
            )
        answer = rag_chain.invoke(query)
        return answer


