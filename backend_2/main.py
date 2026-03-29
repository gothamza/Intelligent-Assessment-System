

from models.models import *
from routes.auth import router_auth
from routes.docs import router_docs
from routes.chat import router_chat
from routes.llm import router_llm
from routes.llm_graph import router_llm_graph
from routes.rag_graph import router_RAG_graph
# from routes.RAG import router_rag
from routes.rag_langgraph import *
from routes.react_agent import router_react
from routes.scraping_agent import Tavily_react
from routes.prompts import router_prompts
from routes.image_generator_hf import router_image_generator_hf
from routes.collections import router_collections
from routes.models import router_models

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime 
import os





async def cleanup_session_documents_from_db():
    """
    Deletes all document records from the PostgreSQL database
    that have the visibility set to 'session'.
    """
    print("--- RUNNING DAILY CLEANUP OF SESSION DOCUMENTS FROM DATABASE ---")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Execute the SQL command to delete rows with 'session' visibility
            cur.execute("DELETE FROM documents WHERE visibility = 'session'")
            
            # Commit the transaction to make the changes permanent
            conn.commit()
            
            print(f"--- DATABASE CLEANUP SUCCESSFUL")
            
    except (Exception) as error:
        print(f"--- ERROR DURING DATABASE CLEANUP: {error} ---")
    finally:
        if conn is not None:
            conn.close()
# # File readers
# from PyPDF2 import PdfReader
# from docx import Document as DocxDocument
async def cleanup_session_vectors():
    """
    Deletes all vectors from ChromaDB that have the 'session' visibility.
    This function is scheduled to run daily.
    """
    print("--- RUNNING DAILY CLEANUP OF SESSION VECTORS ---")
    try:
        # This is the core logic: delete all documents where visibility is 'session'
        vectorstore3.delete(where={"visibility": "session"})
        print("--- SESSION VECTOR CLEANUP SUCCESSFUL ---")
    except Exception as e:
        print(f"--- ERROR DURING SESSION VECTOR CLEANUP: {e} ---")
    # Second, clean up the main database
    await cleanup_session_documents_from_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- DAILY CLEANUP TASK FINISHED ---[{now}] ")
    
    
app = FastAPI()


# Mount the directory for serving generated images
os.makedirs("data/generated_images", exist_ok=True)
# This makes files in 'data/generated_images' accessible under the '/generated_images' URL path
app.mount("/generated_images", StaticFiles(directory="data/generated_images"), name="generated_images")


# CORS middleware configuration
# In production, this should be the specific URL of your Streamlit app
# For local development with Docker, the frontend is accessible via http://localhost:8501
allowed_origins = [
    "http://localhost:8501",  # Streamlit frontend
    "http://localhost:3000",  # Next.js frontend
    "https://ea994f8cfbc8.ngrok-free.app",
    "http://10.0.28.6:3000",
    "http://10.10.77.8:3000",
    "http://10.10.77.8",
    "http://10.10.77.8:8501"  # Streamlit on VPS
    # Add the production URL of your frontend here when you deploy
    # e.g., "https://your-app-domain.com" 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # In production, replace with specific origins
    allow_origin_regex=r"^http://10\.10\.77\.8(?::\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Lifespan Events (Startup and Shutdown) ---
@app.on_event("startup")
async def startup_event():
    """

    Actions to perform on application startup.
    """
     
    # Create documents table if not exists
    init_db()
        
    # Initialize and start the scheduler
    scheduler = AsyncIOScheduler()
    # Schedule the cleanup function to run every day at 8:00 AM
    scheduler.add_job(
        cleanup_session_vectors, 
        trigger=IntervalTrigger(hours=1),
        id="hourly_cleanup_job",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started. Daily cleanup job scheduled every 1H.")


# scheduler.add_job(
#         cleanup_session_vectors, 
#         trigger=CronTrigger(hour=8, minute=0, second=0),
#         id="daily_cleanup_job",
#         replace_existing=True
#     )

@app.get("/")
async def root():
    return {"message": "Welcome to the Langchain Groq RAG API!"}
# route for 
app.include_router(router_auth)
app.include_router(router_docs)
app.include_router(router_chat)
app.include_router(router_prompts)
app.include_router(router_llm)
# app.include_router(router_rag)
app.include_router(router_llm_graph)
app.include_router(router_RAG_graph)
app.include_router(router_RAG_graph2)
app.include_router(router_react)
app.include_router(Tavily_react)
app.include_router(router_image_generator_hf)
app.include_router(router_collections)
app.include_router(router_models)




