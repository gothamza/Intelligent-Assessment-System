from fastapi import BackgroundTasks
import asyncio

@app.post("/rag_graph", response_model=QueryResponse)
async def rag_graph(
    request: RAGMemoryRequest,
    current_user: dict = Depends(get_current_user)
):
    question = request.question
    doc_ids = request.doc_ids or []
    chat_id = request.chat_id

    # --- 1. Define async retrieval functions ---
    async def get_docs():
        filter = {"doc_id": {"$in": list(doc_ids)}}
        retriever = vectorstore2.as_retriever(search_kwargs={"k": 5, "filter": filter})
        return retriever.get_relevant_documents(question)

    async def get_memory():
        # Fetch chat history from Postgres
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT role, content FROM rag_chat_messages WHERE chat_id = %s ORDER BY timestamp ASC LIMIT 10",
                    (chat_id,)
                )
                messages = cur.fetchall()
        finally:
            conn.close()
        return messages

    # --- 2. Run both retrievals in parallel ---
    docs_task = asyncio.to_thread(get_docs)
    memory_task = asyncio.to_thread(get_memory)
    docs, memory = await asyncio.gather(docs_task, memory_task)

    # --- 3. Prepare context ---
    docs_context = "\n".join([doc.page_content for doc in docs])
    memory_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])

    # --- 4. Build prompt for LLM ---
    prompt = (
        f"Chat history:\n{memory_context}\n\n"
        f"Relevant documents:\n{docs_context}\n\n"
        f"User question: {question}"
    )

    # --- 5. Call LLM ---
    result = llm_groq3.invoke(prompt)

    # --- 6. Return answer (sources can be extracted from docs if needed) ---
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in docs))
    return {
        "answer": result,
        "sources": sources
    }