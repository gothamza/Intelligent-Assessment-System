from models.models import * 


router_RAG_graph= APIRouter(tags=["📝RAG with langgraph "])

  
### RAG query with memory using VectorStoreRetrieverMemory ###
from langchain.memory import VectorStoreRetrieverMemory



@router_RAG_graph.post("/query_rag_memory", response_model=QueryResponse)
async def rag_graph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    RAG query using VectorStoreRetrieverMemory for chat history.
    """
    # 1. Filter docs as before
    filter = {"doc_id": {"$in": list(request.doc_ids)}}
    retriever = vectorstore3.as_retriever(
        search_kwargs={"k": 5, "filter": filter}
    )

    # 2. Set up memory for this chat
    memory = VectorStoreRetrieverMemory(
        retriever=vectorstore3.as_retriever(search_kwargs={"filter": {"chat_id": request.chat_id}}),
        memory_key="chat_history"
    )

    # 3. Add current question to memory (optional, if you want to persist it)
    memory.save_context({"input": request.question}, {"output": ""})

    # 4. Set up QA chain
    qa = RetrievalQA.from_chain_type(
        llm=groq_model,
        chain_type="stuff",
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    # 5. Execute query
    result = qa.invoke({"query": request.question})

    # 6. Extract sources
    source_docs = result.get("source_documents", [])
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in source_docs))

    return {
        "answer": result["result"],
        "sources": sources
    }





# 1. Define your RAG node for LangGraph
def rag_node(state: MessagesState):
    # Retrieve chat history from vectorstore using chat_id
    chat_id = state["chat_id"]
    retriever = vectorstore3.as_retriever(search_kwargs={"filter": {"chat_id": chat_id}})
    # Get previous messages (as Document objects)
    history_docs = retriever.get_relevant_documents("history")  # "history" can be any string, it's ignored if filter is used
    # Convert docs to LangChain messages
    history_messages = []
    for doc in history_docs:
        role = doc.metadata.get("role", "user")
        if role == "user":
            history_messages.append(HumanMessage(content=doc.page_content))
        elif role == "assistant":
            history_messages.append(AIMessage(content=doc.page_content))
        elif role == "system":
            history_messages.append(SystemMessage(content=doc.page_content))
    # Add the current user message
    user_message = state["messages"][-1]
    # Build the prompt/context for RAG
    context = "\n".join([d.page_content for d in history_docs])
    prompt = f"{user_message.content}\n\nContext:\n{context}"
    # Call your LLM (e.g., Groq)
    response = llm_groq3.invoke(prompt)
    # Save the assistant response to the vectorstore for future memory
    doc = Document(
        page_content=response.content,
        metadata={
            "chat_id": chat_id,
            "role": "assistant",
            "user_id": state.get("user_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    vectorstore3.add_documents([doc])
    return {"messages": state["messages"] + [response]}

# 2. Build the LangGraph workflow
workflow2 = StateGraph(state_schema=MessagesState)
workflow2.add_node("rag", rag_node)
workflow2.add_edge(START, "rag")

# 3. Use persistent checkpointer (PostgresSaver)
postgres_url = os.getenv("DATABASE_URL")
memory_cm = PostgresSaver.from_conn_string(postgres_url)
memory = memory_cm.__enter__()
workflow2_compiled = workflow2.compile(checkpointer=memory)

# 4. Endpoint to use LangGraph for RAG chat

# ####

# # 1. Create combined filter for both documents and chat history
#     combined_filter = {
#         "$or": [
#             {"doc_id": {"$in": list(doc_ids)}},
#             {"chat_id": chat_id}
#         ]
#     }

#     # 2. Create single retriever that handles both docs and memory
#     retriever = vectorstore3.as_retriever(
#         search_kwargs={
#             "k": 10,  # Increase to get both context and memory
#             "filter": combined_filter
#         }
#     )
####


@router_RAG_graph.post("/rag_graph", response_model=QueryResponse)
async def rag_graph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    RAG query using VectorStoreRetrieverMemory for chat history.
    """
    question = request.question
    doc_ids = request.doc_ids or []
    chat_id = request.chat_id

    # 1. Filter docs as before
    filter = {"doc_id": {"$in": list(doc_ids)}}
    retriever = vectorstore3.as_retriever(
        search_kwargs={"k": 20, "filter": filter}
    )

    # 2. Set up memory for this chat
    memory = VectorStoreRetrieverMemory(
        retriever=vectorstore3.as_retriever(search_kwargs={"filter": {"chat_id": chat_id}}),
        memory_key="chat_history"
    )

    # 3. Add current question to memory (optional)
    memory.save_context({"input": question}, {"output": ""})

    # 4. Set up QA chain
    qa = RetrievalQA.from_chain_type(
        llm=groq_model,
        chain_type="stuff",
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    # 5. Execute query
    result = qa.invoke({"query": question})

    # 6. Extract sources
    source_docs = result.get("source_documents", [])
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in source_docs))

    return {
        "answer": result["result"],
        "sources": sources
    }
    
    
    
 

@router_RAG_graph.post("/rag_graph_memory_buffer", response_model=QueryResponse)
async def rag_graph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    RAG query using ConversationBufferMemory for chat history (in-memory, not persistent).
    """
    question = request.question
    doc_ids = request.doc_ids or []
    chat_id = request.chat_id

    # 1. Filter docs as before
    filter = {"doc_id": {"$in": list(doc_ids)}}
    retriever = vectorstore3.as_retriever(
        search_kwargs={"k": 20, "filter": filter}
    )

    # 2. Use only ConversationBufferMemory (not persistent)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # 3. Set up QA chain
    qa = RetrievalQA.from_chain_type(
        llm=groq_model,
        chain_type="stuff",
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    # 4. Execute query
    result = qa({"query": question})

    # 5. Extract sources
    source_docs = result.get("source_documents", [])
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in source_docs))

    return {
        "answer": result["result"],
        "sources": sources
    }