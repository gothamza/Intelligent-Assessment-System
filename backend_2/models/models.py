# Standard library imports
import os
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Optional

# Third-party imports
from fastapi import (
    FastAPI, Depends, HTTPException, status, Query, APIRouter,
    Path, UploadFile, File, Form, Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from fastapi import logger
from passlib.context import CryptContext
from pydantic import BaseModel

# LangChain and LangGraph imports
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from langchain_ollama import OllamaLLM
from langchain_ollama import ChatOllama



from langchain.schema import AIMessage, HumanMessage, SystemMessage, Document
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredCSVLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

from langchain_groq import ChatGroq

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Project-specific imports
from auth.jwt import create_access_token
from auth.oauth2 import get_current_user
from models.database import get_db_connection
from models.config import settings
from models.groq_manager import groq_key_manager, llm_groq, call_groq_chat
from models.embed_gemini import GeminiEmbeddings
from models.hf_emb import *
from langchain_google_genai import ChatGoogleGenerativeAI
 
from langchain_openai import ChatOpenAI # Add this import
import chromadb



class ChatMessageRequest(BaseModel):
    chat_id: str
    role: str
    content: str

# Pydantic models for responses
class DocumentMetadata(BaseModel):
    doc_id: str
    user_id: int
    team_id: str
    doc_title: str
    file_type: str
    visibility: str
    upload_date: datetime
    collection_ids: Optional[List[int]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    reasoning: Optional[str] = None


class RAGMemoryRequest(BaseModel):
    doc_ids: Optional[List[str]] = None
    chat_id: str
    messages: Optional[List[dict]] = None  
    use_web_search: Optional[bool] = False 
    model_name: Optional[str] = None
    subject: Optional[str] = "Mathématiques"  # Matière sélectionnée
    grade: Optional[str] = "7ème année"  # Niveau d'études sélectionné
    course: Optional[str] = ""  # Cours/Thème spécifique sélectionné
    custom_instructions: Optional[str] = ""  # Instructions personnalisées de l'utilisateur
    language: Optional[str] = "Français"  # Langue de réponse sélectionnée (Français, English, العربية) 

class PromptTemplate(BaseModel):
    title: str
    content: str
    type: str  # 'system', 'simple', 'rag'
    tags: Optional[List[str]] = []
    
    visibility: str  # 'public', 'private', 'team'
    team_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    
# data base connection and initialization
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                team_id TEXT NOT NULL,
                doc_title TEXT NOT NULL,
                file_type TEXT NOT NULL,
                visibility TEXT NOT NULL,
                upload_date TIMESTAMP NOT NULL,
                file_path TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chats (
                chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                chat_title TEXT,
                chat_type TEXT NOT NULL DEFAULT 'llm',
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id SERIAL PRIMARY KEY,
                chat_id UUID REFERENCES chats(chat_id),
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                team_id TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT CHECK (type IN ('system', 'simple', 'rag')),
                tags TEXT[],
                visibility TEXT CHECK (visibility IN ('public', 'private', 'team')) DEFAULT 'public',
                team_id TEXT,
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS collections (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                parent_id INTEGER REFERENCES collections(id) ON DELETE CASCADE, -- For nesting collections
                created_by INTEGER REFERENCES users(id),
                visibility TEXT NOT NULL DEFAULT 'team', -- 'team', 'public', 'private'
                team_id TEXT, -- Can be NULL if public or private
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS collection_documents (
                collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
                doc_id TEXT REFERENCES documents(doc_id) ON DELETE CASCADE,
                PRIMARY KEY (collection_id, doc_id)
            );
            
            """)
            conn.commit()
            
            # Insert only if no users exist
            cur.execute("SELECT COUNT(*) FROM users;")
            user_count = cur.fetchone()["count"]
            if user_count == 0:
                cur.execute("""
            INSERT INTO users (login, password, team_id, role) VALUES ('user1@company.com', '$pbkdf2-sha512$25000$r/XeO8e4t/Zeq5USIoTQ2g$LZKv4W8yjlc6DIAmNPyEzzXwOyW190vg0zgN74AQwdskLr.vQZutwR89j89hFmzDWgfq1ijDpAnvLiWfShraOA', 'IT', 'admin');
            -- login: user1@company.com | password: Password1! | role: admin | team: IT
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user2@company.com', '$pbkdf2-sha512$25000$dC7FmPP.31vLee9da825lw$KTbYjznXaGz2NZ0dxyXNi8V1lpYOT0wWzS2vs1n3gkw8KQlxtlTc8iqJEGYYV4vhpomS74jL6Qxw4lbbiY7GxA', 'RH', 'RH');
            -- login: user2@company.com | password: Password2! | role: RH | team: RH
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user3@company.com', '$pbkdf2-sha512$25000$SCkl5PzfO2esFeKckzIm5A$T5MO8uGzDp831BLDw1pj9vtZdvpmDxM3Nx7Gx8TJVU47BnGk8aztjF.g0OHL5Gt68IvnypZIcLU3w/iDqWZdBw', 'MANAGEMENT', 'manager');
            -- login: user3@company.com | password: Password3! | role: manager | team: MANAGEMENT
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user4@company.com', '$pbkdf2-sha512$25000$G0Po3Tvn/B9jDOHcO2csZQ$qLmgs6bui2Fk4pkugS41/d/Iw6cuyqhIXHiWrEish7NwfA9jBH9rn0XKGosoVLmMfObnZOURbG0D3DCboJFnaA', 'VENTE', 'VENTE');
            -- login: user4@company.com | password: Password4! | role: VENTE | team: VENTE
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user5@company.com', '$pbkdf2-sha512$25000$2bvXurcWojQGgLBWirGWEg$bqHRAEYL6WaEvrjAl0.PlFjuT5EDASzPyXIEJ6Q/cLiS4ypC.RNuQkHNPxw1tn2chhWlLJpCQsEvbX2urNWweA', 'RH', 'user');
            -- login: user5@company.com | password: Password5! | role: user | team: RH
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user6@company.com', '$pbkdf2-sha512$25000$cW4NoRQi5Nx777333ltLaQ$Rpg2V6fDkx82arrytXjohRuxv05upNPnNBknEq/I52qe70Yt4hgR1JBn.tVAFT.KJSkII.Z96FPA0lpJV3Uprw', 'VENTE', 'user');
            -- login: user6@company.com | password: Password6! | role: user | team: VENTE
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user7@company.com', '$pbkdf2-sha512$25000$JaS0NoaQMkYoRUiptTbGOA$2PhQ6uCm5NPDE.6M/q3u8PYK6HHdud7mguyAV02ILauJ64qYkFS3cnt7EiW3.7bKrnLIf8Ybz4VOZhyiEpk11g', 'VENTE', 'manager');
            -- login: user7@company.com | password: Password7! | role: manager | team: VENTE
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user8@company.com', '$pbkdf2-sha512$25000$XguhdA4BAOB8jxGCEMJ47w$OAkznKaxrMCPH.S95d4XknmqCk.5mhAoBUY1KgH9toAqfC0N2UGjtRt2GGbBMDOBRj.2xg7Il0bO5LQN2vLSeg', 'MANAGEMENT', 'admin');
            -- login: user8@company.com | password: Password8! | role: admin | team: MANAGEMENT
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user9@company.com', '$pbkdf2-sha512$25000$H2MsBWCMcU7J2ZvTuleqdQ$2S4Ac8R7xqQwi0NGWJiHr2E3Ti8PMw./Z85GhxNw0moHKhlGST3BkfD1ypJsDgq322IIMnuBk7Ie8xgC8YK5fg', 'IT', 'RH');
            -- login: user9@company.com | password: Password9! | role: RH | team: IT
            
            INSERT INTO users (login, password, team_id, role) VALUES ('user10@company.com', '$pbkdf2-sha512$25000$XgshxFiLcW6NUap1rvXeew$ILa6l5CFR8kvZrPIS3fbTeAJ2eVScZn9sm.YVeE5SEsLaFWzf7T6KthEb5lVR5KgnVG5VbDHSBJdZmSVHYLqGg', 'IT', 'user');
            -- login: user10@company.com | password: Password10! | role: user | team: IT

            INSERT INTO users (login, password, team_id, role) VALUES ('admin@company.com', '$pbkdf2-sha512$25000$XgshxFiLcW6NUap1rvXeew$ILa6l5CFR8kvZrPIS3fbTeAJ2eVScZn9sm.YVeE5SEsLaFWzf7T6KthEb5lVR5KgnVG5VbDHSBJdZmSVHYLqGg', 'IT', 'admin');
            -- login: admin@company.com | password: Password10! | role: admin | team: IT



            -- New Team Users for Obystech
            INSERT INTO users (login, password, team_id, role) VALUES ('Ayoub.JBIILI@obystech.com', '$pbkdf2-sha512$25000$Nsa49967t7a2di6llJISYg$nVrTGVkGMjDxYKxdwCKtuCJF3dw1g9w1MGmC0FfLYW7PftezWh/A6W9xyUbSE1uUvYL0ibRHMMSycZXnyfXPDA', 'IT', 'user');
            -- login: Ayoub.JBIILI@obystech.com | password: PasswordAyoub!35

            INSERT INTO users (login, password, team_id, role) VALUES ('Tarik.BENFANNA@obystech.com', '$pbkdf2-sha512$25000$.l/rndOaE4LQeq/1HsP4Xw$4Srta5mgimydJa1D1bm5rslBTk4GSfsH0qxpmqTYsXQxJqda2t02O1OUn8QiknbJfZdq/pTA05Xfc.UuEddReQ', 'IT', 'user');
            -- login: Tarik.BENFANNA@obystech.com | password: PasswordTarik!11

            INSERT INTO users (login, password, team_id, role) VALUES ('Abdeslam.KARJOUT@obystech.com', '$pbkdf2-sha512$25000$05rT2ntvrfV.zzknxNh7zw$nXkIm7Es7cgot4rfAmZIH9e1Rb88CU6X7tlcKgus6QzLZLqv4bp4KN7os/mrGKvC1PssQM/PhN0IbzojPp3ulA', 'IT', 'user');
            -- login: Abdeslam.KARJOUT@obystech.com | password: PasswordAbdeslam!360

            INSERT INTO users (login, password, team_id, role) VALUES ('Marouane.ASSEMAR@obystech.com', '$pbkdf2-sha512$25000$0/rfm7P2fu8dY8xZC2Hs3Q$sbGpgQLrWHnDtkYMtIAxtDi40MRKTAZiNGKJ6ZwbFfG9sCNSEHMUjIIxqJSpAvrvHmtJtB46kE8vHHGy9IGdSw', 'IT', 'user');
            -- login: Marouane.ASSEMAR@obystech.com | password: PasswordMarouane!36

            INSERT INTO users (login, password, team_id, role) VALUES ('Imane.ELMAZOUZ@obystech.com', '$pbkdf2-sha512$25000$Tsk5pxRizHkvRYhxDqHUeg$EaFCRYYUa2TTAE6QsSGnfFAJKdY1P7yTHR9KjjjrhCvLtn2QfOzJ3QHNiNDcwK.3UeGa11wMMXuXxU.ncjhcTA', 'IT', 'user');
            -- login: Imane.ELMAZOUZ@obystech.com | password: PasswordImane!00

            INSERT INTO users (login, password, team_id, role) VALUES ('Sanaa.DAOUDI@obystech.com', '$pbkdf2-sha512$25000$R2itVap1DgGAUErJGSNk7A$7btnsfokDZlxoGJKo9rt0lgUZgEZk4ZDW8I16P5iWvzzm2lifA1.LkaoyS3OUgCvzXE4z2sOBTNsj.zXBsfAnA', 'IT', 'user');
            -- login: Sanaa.DAOUDI@obystech.com | password: PasswordSanaa!12
            """)
                conn.commit()
    # print(f"User count: {user_count}")

    
    
OLLAMA_URL = os.getenv("OLLAMA_URL")

# Configure PBKDF2-SHA512 with 25000 iterations (same as in database seed data)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha512"],
    pbkdf2_sha512__default_rounds=25000,
    deprecated="auto"
)



# Initialize vector store and embeddings
embedding_model = OllamaEmbeddings(
    model="llama3.2:latest",
    base_url=OLLAMA_URL
)




# # Initialize LLM
# ollama_llm= OllamaLLM(model="llama3.2:latest", base_url=OLLAMA_URL)

# ollama_llm2 = ChatOllama(model="llama3.2:latest", base_url=OLLAMA_URL)

# gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)

# # Initialize Groq model
groq_api_key = os.getenv('GROQ_API_KEY')
# groq_model = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

groq_api_key = os.getenv('GROQ_API_KEY')
groq_api_key2 = os.getenv('GROQ_API_KEY2')
groq_api_key3 = os.getenv('GROQ_API_KEY3')


# # llm=ChatGroq(groq_api_key=groq_api_key,model_name="llama3-70b-8192")
# llm_groq3 = ChatGroq(groq_api_key=groq_api_key, model_name="gemma2-9b-it")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Add this line

OPEN_ROUTER = os.getenv("OPEN_ROUTER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

AVAILABLE_MODELS = {
    # Ollama Models
    "Ollama/llama3.2:latest": ChatOllama(model="llama3.2:latest", base_url=OLLAMA_URL),
    "Ollama/deepseek-r1:7b": ChatOllama(model="deepseek-r1:7b", base_url=OLLAMA_URL),
    "Ollama/llama3.2:1b": ChatOllama(model="llama3.2:1b", base_url=OLLAMA_URL),

    # Gemini Models
    "Gemini/gemini-2.5-flash": ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY),

    # Groq Models
    "Groq/llama-3.1-8b-instant": ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant"),
    "Groq/llama-3.1-8b-instant": ChatGroq(groq_api_key=groq_api_key2, model_name="llama-3.1-8b-instant"),
    "Groq/llama-3.3-70b-versatile": ChatGroq(groq_api_key=groq_api_key3, model_name="llama-3.3-70b-versatile"),
    "Groq/qwen/qwen3-32b": ChatGroq(groq_api_key=groq_api_key3, model_name="qwen/qwen3-32b"),
    "Groq/deepseek-r1-distill-llama-70b": ChatGroq(groq_api_key=groq_api_key, model_name="deepseek-r1-distill-llama-70b"),
    "Groq/gpt-oss-20b": ChatGroq(groq_api_key=groq_api_key, model_name="openai/gpt-oss-20b"),
    "Groq/gpt-oss-120b": ChatGroq(groq_api_key=groq_api_key, model_name="openai/gpt-oss-120b"),


    # OpenAI Models
    "OpenAI/deepseek-chat-v3-0324:free": ChatOpenAI(base_url="https://openrouter.ai/api/v1",model="deepseek/deepseek-chat-v3-0324:free", openai_api_key=OPEN_ROUTER),
    "OpenAI/gpt-4o": ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY),
    "OpenAI/o4-mini-2025-04-16": ChatOpenAI(model="o4-mini-2025-04-16", openai_api_key=OPENAI_API_KEY),
    # OpenRouter Models
    "OpenRouter/gpt-4o": ChatOpenAI(base_url="https://openrouter.ai/api/v1",model="deepseek/deepseek-chat-v3-0324:free", openai_api_key=OPEN_ROUTER),
    "GitHub/gpt-4o": ChatOpenAI(base_url="https://models.github.ai/inference", model="openai/gpt-4.1", openai_api_key=GITHUB_TOKEN),
    "GitHub/qwen/qwen3-32b": ChatOpenAI(base_url="https://api.groq.com/openai/v1", model="qwen/qwen3-32b", openai_api_key=groq_api_key3),
    "GitHub/openai/gpt-oss-120b": ChatOpenAI(base_url="https://api.groq.com/openai/v1", model="openai/gpt-oss-120b", openai_api_key=groq_api_key3)


    
}

# Define a default model for fallback purposes
groq_model = AVAILABLE_MODELS.get("Groq/llama-3.1-8b-instant")
llm_groq3 = AVAILABLE_MODELS.get("Groq/llama-3.1-8b-instant") # Keep this for compatibility if it's used elsewhere
ollama_llm2 = AVAILABLE_MODELS.get("Ollama/llama3.2:latest")
gemini_llm = AVAILABLE_MODELS.get("Gemini/gemini-2.5-flash")




from models.embed_gemini import GeminiEmbeddings

embedding_model2 = GeminiEmbeddings(api_key=GEMINI_API_KEY)

client = chromadb.HttpClient(host="chromadb", port=8000)

vectorstore3 = Chroma(
    client=client,
    collection_name="RAG_enterprise_docs2", # It's important to name your collection
    embedding_function=hf_embedder
)


# vectorstore = Chroma(persist_directory="./vectorstore2", 
#                      embedding_function=embedding_model,
#                      collection_name="enterprise_docs")

# vectorstore2 = Chroma(
#     persist_directory="./vectorstore2",
#     embedding_function=embedding_model2,
#     collection_name="enterprise_docs"
# )

# vectorstore3 = Chroma(
#     persist_directory="./vectorstore2",
#     embedding_function=hf_embedder,
#     collection_name="enterprise_docs"
# )



class LLMRequest(BaseModel):
    prompt: str

class LLMResponse(BaseModel):
    response: str

class Message(BaseModel):
    role: str
    content: str

class LLMRequest2(BaseModel):
    messages: List[Message]


# 3. Convert to LangChain messages
def to_lc_message(msg):
    if msg["role"] == "user":
        return HumanMessage(content=msg["content"])
    elif msg["role"] == "assistant":
        return AIMessage(content=msg["content"])
    elif msg["role"] == "system":
        return SystemMessage(content=msg["content"])
    else:
        return HumanMessage(content=msg["content"])
    



### checkpointer init 