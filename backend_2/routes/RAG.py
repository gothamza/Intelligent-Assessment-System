from models.models import *

router_rag= APIRouter(tags=["📄🤖RAG "])


# RAG query endpoint
@router_rag.post("/query", response_model=QueryResponse)
async def query_documents(
    question: str = Query(..., description="Question to ask about your documents"),
    doc_ids: Optional[List[str]] = Query(None, description="Filter by specific document IDs"),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform RAG query with access control based on document visibility
    """
    # 1. Get allowed document IDs based on user permissions
    allowed_doc_ids = set()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get all accessible documents
            cur.execute("""
            SELECT doc_id FROM documents
            WHERE visibility = 'public'
               OR (visibility = 'team' AND team_id = %s)
               OR (visibility = 'private' AND user_id = %s)
            """, (current_user.get("team_id"), current_user["user_id"]))
            allowed_doc_ids = {row["doc_id"] for row in cur.fetchall()}
    finally:
        conn.close()
    
    # 2. Apply document filter if provided
    if doc_ids:
        # Only keep doc_ids that user has access to
        doc_ids = [did for did in doc_ids if did in allowed_doc_ids]
        if not doc_ids:
            return {"answer": "No accessible documents match your query", "sources": []}
        filter = {"doc_id": {"$in": doc_ids}}
    else:
        filter = {"doc_id": {"$in": list(allowed_doc_ids)}}
    
    # 3. Configure retriever with access filters
    retriever = vectorstore2.as_retriever(
        search_kwargs={
            "k": 5,  # Number of documents to retrieve
            "filter": filter
        }
    )
    
    # 4. Set up QA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # 5. Execute query
    result = qa({"query": question})
    
    # 6. Extract sources from retrieved documents
    source_docs = result.get("source_documents", [])
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in source_docs))
    
    return {
        "answer": result["result"],
        "sources": sources
    }



###########################################################"
# LLM endpoints using Groq LLM
###########################################################"

@router_rag.post("/llm_groq", response_model=LLMResponse)
async def llm_groq(
    request: LLMRequest2,
    chat_id: Optional[str] = Query(None, description="Chat ID for memory"),
    current_user: dict = Depends(get_current_user)
):
    try:
        
        # 1. Fetch chat history from DB if chat_id is provided
        print("getting chat history for chat_id::\n")
        messages = request.messages.copy()
        if chat_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT role, content FROM chat_messages WHERE chat_id = %s ORDER BY timestamp ASC LIMIT 20",
                        (chat_id,)
                    )
                    history = cur.fetchall()
            finally:
                conn.close()
            history_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
            messages = history_msgs + messages
        print("messages after fetching chat history::\n")
        messages = [m for m in messages if isinstance(m, dict)]
        # 2. Ensure a system message exists
        has_system = any(msg["role"] == "system" for msg in messages)
        if not has_system:
            messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

        # 3. Convert messages to LangChain format
        def to_lc_message(msg):
            if msg["role"] == "user":
                return HumanMessage(content=msg["content"])
            elif msg["role"] == "assistant":
                return AIMessage(content=msg["content"])
            elif msg["role"] == "system":
                return SystemMessage(content=msg["content"])
            else:
                return HumanMessage(content=msg["content"])
        lc_messages = [to_lc_message(m) for m in messages]

        # 4. Create memory buffer and set messages
        memory = ConversationBufferMemory(return_messages=True)
        memory.chat_memory.messages = lc_messages
        print("memory messages::\n")

        # 5. Run the LLM with memory (no RAG, just chat)
        from langchain.chains import ConversationChain
        conversation = ConversationChain(
            llm=llm_groq3,
            memory=memory,
            verbose=False
        )
        # The latest user message is the last HumanMessage in lc_messages
        user_input = [m.content for m in lc_messages if isinstance(m, HumanMessage)][-1]
        print("user_input:\n", user_input)
        result = conversation.invoke({"input": user_input})
        response = result["response"] if "response" in result else result["text"]

        print("GROQ RESULT:", response)
        if not response:
            raise HTTPException(status_code=500, detail="No response from LLM")
        return LLMResponse(response=response)
    except Exception as e:
        print("LLM error:", e)
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")



@router_rag.post("/query_groq", response_model=QueryResponse)
async def query_groq_documents(
    question: str = Query(..., description="Question to ask about your documents"),
    doc_ids: Optional[List[str]] = Query(None, description="Filter by specific document IDs"),
    chat_id: str = Query(..., description="Chat ID for memory"),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform RAG query with Groq LLM, using chat history from the specified chat_id.
    """
    # 1. Filter documents (reuse your existing logic)
    filter = {"doc_id": {"$in": list(doc_ids)}}

    retriever = vectorstore2.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": filter
        }
    )

    # 2. Fetch last 10 messages for this chat_id
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, content FROM chat_messages WHERE chat_id = %s ORDER BY timestamp ASC LIMIT 10",
                (chat_id,)
            )
            messages = cur.fetchall()
    finally:
        conn.close()


    lc_messages = [to_lc_message(m) for m in messages]

    # 4. Add the current user question to the memory
    lc_messages.append(HumanMessage(content=question))

    # 5. Create memory buffer
    memory = ConversationBufferMemory(return_messages=True)
    memory.chat_memory.messages = lc_messages

    # 6. Set up QA chain with Groq LLM
    qa = RetrievalQA.from_chain_type(
        llm=llm_groq3,
        chain_type="stuff",
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        chain_type_kwargs={"output_key": "result"}
    )

    # 7. Execute query
    result = qa({"query": question})

    # 8. Extract sources
    source_docs = result.get("source_documents", [])
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in source_docs))

    return {
        "answer": result["result"],
        "sources": sources
    }


