
from models.langgraph_models import *

router_RAG_graph2= APIRouter(tags=["📝RAG with langgraph test2"])


# Compile the graph with Postgres checkpointer
workflow_rag = workflow_rag.compile(checkpointer=memory_cm)

# 5. FastAPI endpoint for LangGraph RAG
@router_RAG_graph2.post("/rag_langgraph", response_model=QueryResponse)
async def rag_langgraph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    RAG query using LangGraph with Postgres memory
    """
    # Prepare initial state
    user_id = current_user["user_id"]
    # Convert incoming message dicts (role/content) to LangChain messages
    incoming_messages = request.messages or []
    lc_messages = [to_lc_message(m) for m in incoming_messages] if incoming_messages else []

    initial_state = {
        "messages": lc_messages,
        "chat_id": request.chat_id,
        "doc_ids": request.doc_ids or [],
        "user_id": user_id,
        "context": [],
        "model_name": request.model_name,
    }
    
    # Config for the graph
    config = RunnableConfig(configurable={"thread_id": request.chat_id})
    
    # Execute the graph
    final_state = workflow_rag.invoke(initial_state, config)
    
    # Extract the response
    ai_response = final_state["messages"][-1].content
    
    # Extract sources from context (filter out chat history)
    sources = list(set(
        doc.metadata.get("source", "Unknown")
        for doc in final_state["context"]
        if "doc_id" in doc.metadata  # Only include document sources
    ))
    
    return {
        "answer": ai_response,
        "sources": sources
    }
    
