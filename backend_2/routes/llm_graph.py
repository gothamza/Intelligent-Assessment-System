from models.langgraph_models import *
from models.models import *
from langsmith import Client
from routes.scraping_agent import agent_graph_tavily

# from slowapi import Limiter
# from slowapi.util import get_remote_address

# limiter = Limiter(key_func=get_remote_address)
client = Client()
router_llm_graph= APIRouter(tags=["🧠LLM Graph "])

# Compile the graph with PostgresSaver (no app state)
# Initialize memory_cm lazily on first use
if memory_cm is None:
    from models.langgraph_models import get_memory_cm
    memory_cm = get_memory_cm()

memory = memory_cm.__enter__()
memory.setup()
app_graph = workflow.compile(checkpointer=memory )
# @limiter.limit("5/minute")

@router_llm_graph.post("/llm_groq_graph", response_model=LLMResponse)
async def llm_groq_graph(
    request: LLMRequest2,
    chat_id: Optional[str] = Query(None, description="Chat ID for memory"),
    current_user: dict = Depends(get_current_user)
):
    """
    Chat endpoint using LangGraph memory and Groq LLM.
    Messages are stored persistently in Postgres.
    """
   
    # Normalize and trim history
    messages = [msg_to_dict(m) for m in request.messages]
    messages = messages[-1:]  # Keep only last message (adjustable)
 


    lc_messages = [to_lc_message(m) for m in messages]

    try:
        result = app_graph.invoke(
            {"messages": lc_messages},
            config={"configurable": {"thread_id": chat_id}}
        )
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        # Persist assistant message server-side before responding (so switching chats doesn't lose it)
        try:
            if chat_id and ai_messages:
                ai_content = ai_messages[-1].content
                conn = get_db_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO chat_messages (chat_id, role, content) VALUES (%s, %s, %s)",
                            (chat_id, "assistant", ai_content)
                        )
                    conn.commit()
                finally:
                    conn.close()
        except Exception as db_err:
            # Log and continue; do not fail the response if DB write has an issue
            print("Warning: failed to save assistant message:", db_err)

        return LLMResponse(response=ai_messages[-1].content if ai_messages else "No response from LLM.")
    except Exception as e:
        print("LLM error (graph):", e)
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")
    

   


# Initialize memory for workflow_rag2 if not already done
if memory_cm is None:
    from models.langgraph_models import get_memory_cm
    memory_cm = get_memory_cm()
    memory = memory_cm.__enter__()
    memory.setup()

workflow_rag2 = workflow_rag2.compile(checkpointer=memory)

# 6. Corrected endpoint implementation
@router_llm_graph.post("/rag_langgraph2", response_model=QueryResponse)
async def rag_langgraph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    # Get thread ID (use chat_id as thread_id)
    thread_id = request.chat_id

    # If request has messages, use them; else, use just the current question
    # Limit to last 4 messages (2 exchanges) to reduce token usage
    if hasattr(request, "messages") and request.messages:
        messages = [msg_to_dict(m) for m in request.messages]
        messages = messages[-4:]  # Keep only last 4 messages (2 exchanges)
    else:
        # Fallback: create a message from the question if available
        messages = [{"role": "user", "content": getattr(request, "question", "Hello")}]
        
    lc_messages = [to_lc_message(m) for m in messages]
        # Prepare initial state
    initial_state = {
        "messages": lc_messages,
        "context": [],
        "chat_id": request.chat_id,
        "user_id": current_user["user_id"],
        "doc_ids": request.doc_ids or [],
        "use_web_search": request.use_web_search,
        "model_name": request.model_name,
        "subject": request.subject or "Mathématiques",
        "grade": request.grade or "7ème année",
        "course": request.course or "",
        "custom_instructions": request.custom_instructions or "",
        "language": request.language or "Français"
    }
    # Create config with thread_id
    # config = RunnableConfig(
    #     configurable={
    #         "thread_id": thread_id,
    #         # Add this if using multiple users
    #         "user_id": current_user["user_id"]
    #     }
    # )
    try:
        # Execute the graph based on the request type
        if request.use_web_search:
            # --- Call Web Search Agent ---
            # The Tavily agent expects just the last user message
            last_user_message = lc_messages[-1]
            tavily_state = {"messages": [last_user_message]}
            result = agent_graph_tavily.invoke(tavily_state)
            
            # Extract the final response from the Tavily agent's state
            ai_response = result["messages"][-1]
            
            # Format for QueryResponse
            return {
                "answer": ai_response.content,
                "sources": []  # Tavily agent doesn't provide structured sources here
            }

        # elif request.doc_ids:
        #     # --- Call RAG Agent ---
            
        #     final_state = workflow_rag2.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})
        
        # else:
        #     # --- Call General Chat Agent ---
        #     final_state = app_graph.invoke(
        #         initial_state,
        #         config={"configurable": {"thread_id": thread_id}}
        #     )  
        else:
            # final_state =workflow_rag2.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})
            final_state = await asyncio.to_thread(
                    workflow_rag2.invoke,
                initial_state,
                config={"configurable": {"thread_id": thread_id}}
                )
        # Extract response
        ai_messages = [msg for msg in final_state["messages"] if isinstance(msg, AIMessage)]
        ai_message = ai_messages[-1] if ai_messages else None
        if not ai_message:
            raise HTTPException(500, "No AI response generated")
        
        # Extract reasoning if it exists in additional_kwargs
        reasoning = None
        if hasattr(ai_message, 'additional_kwargs') and ai_message.additional_kwargs:
            reasoning = ai_message.additional_kwargs.get('reasoning_content')

        # Extract sources
        context_docs = final_state.get("context", [])
        sources = list(set(
            doc.metadata.get("source", "Unknown")
            for doc in context_docs
            if hasattr(doc, "metadata") and "doc_id" in doc.metadata
        ))
        # Persist assistant message to SQL before responding (protect against chat switch)
        try:
            if request.chat_id and ai_message and ai_message.content:
                conn = get_db_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO chat_messages (chat_id, role, content) VALUES (%s, %s, %s)",
                            (request.chat_id, "assistant", ai_message.content)
                        )
                    conn.commit()
                finally:
                    conn.close()
        except Exception as db_err:
            print("Warning: failed to save assistant message (rag_langgraph2):", db_err)

        return {
            "answer": ai_message.content,
            "sources": sources ,
            "reasoning": reasoning
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"LangGraph execution failed: {str(e)}")