from models.models import *

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import  HumanMessage
from langchain_core.output_parsers import StrOutputParser
from models.image_generator_hf import generate_image_with_hf
from langgraph.checkpoint.memory import InMemorySaver
import asyncio # Add this import
from collections import defaultdict

# Define the state for our graph
class GraphState(TypedDict):
    """
    Represents the state of our graph.
    
    Attributes:
    - messages: List of messages in the conversation
    - chat_id: Unique ID for the conversation
    - doc_ids: List of document IDs for RAG context
    - user_id: ID of the current user
    - context: Retrieved RAG context
    - subject: Subject being studied (e.g., "Mathématiques", "Physique")
    - grade: Grade level (e.g., "7ème année", "8ème année")
    - course: Specific course/topic being studied
    - custom_instructions: Custom instructions from the user
    - language: Language for LLM response (Français, English, العربية)
    """
    messages: List[Union[HumanMessage, AIMessage]]

    chat_id: str
    doc_ids: List[str]
    user_id: str
    context: List[Document]
    model_name: Optional[str]
    subject: Optional[str]
    grade: Optional[str]
    course: Optional[str]
    custom_instructions: Optional[str]
    language: Optional[str] 


############ langgraph work flow for a simple chat with memory PostgresSaver
# LangGraph node function
# LangGraph node function
def call_groq_model(state: GraphState):
    """
    Generates a response for general chat, correctly handling message history and model selection.
    """
    # Get subject, grade, course, custom_instructions, and language from state
    subject = state.get("subject", "Mathématiques")
    grade = state.get("grade", "7ème année")
    course = state.get("course", "")
    custom_instructions = state.get("custom_instructions", "")
    language = state.get("language", "Français")
    
    # Language instruction mapping
    language_instructions = {
        "Français": "You MUST respond ONLY in French. All explanations, examples, and text must be in French.",
        "English": "You MUST respond ONLY in English. All explanations, examples, and text must be in English.",
        "العربية": "You MUST respond ONLY in Arabic. All explanations, examples, and text must be in Arabic. Use proper Arabic script (العربية)."
    }
    language_instruction = language_instructions.get(language, language_instructions["Français"])
    
    # Build personalized system prompt
    course_context = f" focusing specifically on: {course}" if course else ""
    custom_instructions_text = f"\n\nAdditional Instructions:\n{custom_instructions}" if custom_instructions else ""
    
    system_prompt = f"""You are an expert tutor specialized in {subject} for {grade} level students{course_context}.

IMPORTANT: {language_instruction}

Your role:
- Provide clear, age-appropriate explanations tailored to {grade} level
- Use pedagogical methods suitable for {grade} students
- Focus specifically on {subject} concepts and curriculum{course_context}
- Adapt your language and examples to the student's level
- Be encouraging and supportive{custom_instructions_text}

Remember: You are teaching {subject} to a {grade} student. Keep explanations clear, engaging, and appropriate for their level. Always respond in {language}."""
    
    # Define a robust prompt template that handles the message history
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    thread_id = state.get("chat_id")
    # Select the model based on the state
    model_name = state.get("model_name")
    
    selected_llm = AVAILABLE_MODELS.get(model_name)
        
    # Fallback to a default model if the selected one isn't found
    if not selected_llm:
        print(f"Warning: Model '{model_name}' not found. Falling back to default Groq model.")
        selected_llm = groq_model
    # Create the chain
    chain = prompt | selected_llm
    
    # Invoke the chain with the message history from the state
    #let show the chats length
    # print("______ the leng of the msgs are :", len(state["messages"]))
    # response = chain.invoke({"messages": state["messages"]}, config={"configurable": {"thread_id":thread_id}})
    response = chain.invoke({"messages": state["messages"]})
    # Correctly append the new AI message to the history
    return {"messages": state["messages"] + [response]} 

# def rewrite_image_prompt_node(state: GraphState):
#     """
#     Rewrites the user's prompt to be more descriptive for image generation models.
#     """
#     user_prompt = state["messages"][-1].content
    
#     # Create a prompt template for the rewriting task
#     rewrite_prompt = ChatPromptTemplate.from_messages([
#         ("system", "You are an expert prompt engineer for text-to-image models. Rewrite the following user prompt to be more descriptive, detailed, and visually rich. Focus on adding details about style (e.g., photorealistic, cinematic, watercolor), lighting, composition, and mood. Output only the rewritten prompt."),
#         ("human", "{user_prompt}")
#     ])
    
#     # Use a fast model for the rewriting task
#     rewriter_chain = rewrite_prompt | groq_model | StrOutputParser()
    
#     rewritten_prompt_content = rewriter_chain.invoke({"user_prompt": user_prompt})
    
#     # Replace the last message with the new, enhanced prompt
#     updated_messages = state["messages"][:-1] + [HumanMessage(content=rewritten_prompt_content)]
    
#     return {"messages": updated_messages}


def rewrite_image_prompt_node(state: GraphState):
    """
    Rewrites the user's prompt to be more descriptive for image generation models,
    using the conversation history for context.
    """
    # Create a prompt template that instructs the model to use the conversation history
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert prompt engineer for text-to-image models. Your task is to rewrite the user's latest request into a single, detailed, and visually rich prompt for an image generation model.

        Use the entire conversation history for context. Combine the user's latest request with relevant details from previous messages (like subjects, styles, or settings) to create a cohesive and complete prompt.

        For example, if the history is about "a knight" and the latest message is "put him on a dragon", you should generate a prompt like "A cinematic, detailed portrait of a knight in shining armor riding a majestic, fire-breathing dragon through a stormy sky."

        Focus on adding details about style (e.g., photorealistic, cinematic, watercolor), lighting, composition, and mood.

        Output only the final, rewritten prompt.if there is no detail dont add them relative to the promt dont add them"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Use a fast model for the rewriting task
    rewriter_chain = rewrite_prompt | groq_model | StrOutputParser()
    
    # Invoke the chain with the full message history from the state
    rewritten_prompt_content = rewriter_chain.invoke({"messages": state["messages"]})
    
    # Replace the last message with the new, enhanced prompt for the next node
    updated_messages = state["messages"][:-1] + [HumanMessage(content=rewritten_prompt_content)]
    
    return {"messages": updated_messages}

def generate_image_node(state: GraphState):
    """
    Calls the Hugging Face image generation model with the enhanced prompt.
    """
    prompt = state["messages"][-1].content
    chat_id = state["chat_id"]
    model_name = state["model_name"]
    
    # Call the existing HF image generation function
    relative_path = generate_image_with_hf(prompt, chat_id, model_name)
    
    if not relative_path:
        image_url = "Failed to generate image."
    else:
        # Construct the full URL to return to the user
        public_url = os.getenv("PUBLIC_BACKEND_URL", "http://localhost:8000")
        url_path = relative_path.replace("data/", "")
        image_url = f"{public_url}/{url_path}"
        # Create a structured dictionary with the image URL and the prompt
        # Format the content as a single string with a clear separator
        content_string = f"{prompt}\n\nimage : {image_url}"
        
    # The final message should be the URL of the image
    ai_message = AIMessage(content=content_string)

    return {"messages": [ai_message]}

def route_by_model_type(state: GraphState):
    """
    Inspects the state and decides whether to generate an image, run RAG, or have a general chat.
    """
    model_name = state.get("model_name") or ""
    doc_ids = state.get("doc_ids") or []
    
    # Check if the selected model is an image generation model
    if model_name and "stabilityai" in model_name:
        return "rewrite_prompt"  # Path 1: Image Generation
    elif doc_ids:
        return "retrieve"  # Path 2: RAG (documents are selected)
    else:
        return "general_chat" # Path 3: General Chat (no docs, no image model)


# Convert to LangChain format
def to_lc_message(msg):
    role = msg["role"]
    content = msg["content"]
    return {
        "user": HumanMessage,
        "assistant": AIMessage,
        "system": SystemMessage
    }.get(role, HumanMessage)(content=content)


def msg_to_dict(m):
    if isinstance(m, dict):
        return {"role": m.get("role", "user"), "content": m.get("content", "")}
    return {"role": getattr(m, "role", "user"), "content": getattr(m, "content", str(m))}







##########################################################################
##### langgraph with RAG and PostgresSaver







# Build the workflow graph
workflow = StateGraph(GraphState)
workflow.add_node("model", call_groq_model)
workflow.add_edge(START, "model")

# Compile the graph with PostgresSaver (no app state)
postgres_url = os.getenv("DATABASE_URL")

# Lazy initialization of memory_cm with retry logic
def get_memory_cm():
    """Get or create PostgresSaver with retry logic"""
    import time
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            return PostgresSaver.from_conn_string(postgres_url)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Failed to connect to PostgreSQL (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to PostgreSQL after {max_retries} attempts: {e}")
                raise

memory_cm = None  # Will be initialized on first use

# 1. Define the RAG node
def retrieve_node(state: GraphState):
    """Node to retrieve relevant context from vector store"""
    chat_id = state["chat_id"]
    doc_ids = state["doc_ids"]
    
    # Create combined filter for both documents and chat history
    combined_filter = {"doc_id": {"$in": list(doc_ids)}}

    print()
    # Retrieve relevant context - limit to 5 chunks for small documents
    # For a 1-2 page PDF, 5 chunks should be more than enough
    retriever = vectorstore3.as_retriever(
        search_kwargs={"k": 5, "filter": combined_filter}
    )
    if state["messages"] and len(state["messages"]) >= 3:
        # context = retriever.get_relevant_documents(
        #     state["messages"][-3].content  # Last user message
        # )
        context = retriever.invoke(state["messages"][-3].content)
    else:
        # context = retriever.get_relevant_documents(
        #     state["messages"][-1].content  # Last user message
        # )
        context = retriever.invoke(state["messages"][-1].content)
        # 3. Récupère la dernière question
    # last_message = state["messages"][-3].content if len(state["messages"]) >= 3 else state["messages"][-1].content

    # # 4. Utilise get_relevant_documents, pas invoke
    # context = retriever.get_relevant_documents(last_message)

    return {
        "context": context,
        "messages": state["messages"]
    }


def select_model_based_on_context(context_text: str) -> str:
    """
    Selects an appropriate LLM model based on the estimated token count of the context.
    """
    # Rule of thumb: ~4 characters per token.
    estimated_tokens = len(context_text) / 4
    print(f"--- Estimated context token count: {int(estimated_tokens)} ---")

    # Define model tiers based on context window size.
    if estimated_tokens > 5000:
        # Use a model with a very large context window for huge contexts.
        model_key = "Groq/llama-3.1-70b-versatile" 
        print(f"--- Context is large ({int(estimated_tokens)} tokens). Switching to model: {model_key} ---")
    elif estimated_tokens > 2000:
        # Use a capable model with a standard context window.
        model_key = "Groq/llama-3.1-70b-versatile"  # Use 70b for medium contexts too to avoid token limits
        print(f"--- Context is medium ({int(estimated_tokens)} tokens). Using model: {model_key} ---")
    else:
        # Use a fast, smaller model for short contexts only.
        model_key = "Groq/llama-3.1-8b-instant"
        print(f"--- Context is small ({int(estimated_tokens)} tokens). Using fast model: {model_key} ---")
    
    return model_key
# 2. Define the LLM generation node

def generate_node(state: GraphState):
    """Node to generate AI response using context"""
    messages = state["messages"]
    context = state["context"]
    thread_id = state.get("chat_id")  # Get thread_id from state
    model_name = state.get("model_name")
    # Format the context

    # Limit chat history to last 2 exchanges (4 messages max) to reduce token usage
    # This keeps context but prevents token overflow
    all_messages = state["messages"]
    if len(all_messages) > 4:
        chat_history = all_messages[-4:-1]  # Last 3 messages (excluding current)
    else:
        chat_history = all_messages[:-1] if len(all_messages) > 1 else []
    current_question = state["messages"][-1].content

    # 1. Group chunks by their unique document ID.
    # This correctly handles documents that may have the same filename.
    grouped_docs = defaultdict(lambda: {'chunks': [], 'source_name': 'Unknown Document'})
    for doc in context:
        doc_id = doc.metadata.get("doc_id", "unknown_id")
        source_name = os.path.basename(doc.metadata.get("source", "Unknown Document"))
        
        grouped_docs[doc_id]['chunks'].append(doc.page_content)
        grouped_docs[doc_id]['source_name'] = source_name

    # 2. Format the grouped context into clean, separate blocks.
    # Limit total context to ~3000 tokens (12000 chars) to avoid token limits
    MAX_CONTEXT_CHARS = 12000  # ~3000 tokens
    context_blocks = []
    current_context_size = 0
    
    for doc_id, data in grouped_docs.items():
        source_name = data['source_name']
        # Join all chunks from the same document into a single text block.
        full_doc_text = "\n\n".join(data['chunks'])
        
        # Truncate if too long
        if len(full_doc_text) > 5000:  # Limit each document to ~1250 tokens
            full_doc_text = full_doc_text[:5000] + "... [truncated]"
        
        block = (
            f"--- START OF CONTEXT FROM DOCUMENT: {source_name} ---\n"
            f"{full_doc_text}\n"
            f"--- END OF CONTEXT FROM DOCUMENT: {source_name} ---"
        )
        
        # Check if adding this block would exceed limit
        if current_context_size + len(block) > MAX_CONTEXT_CHARS:
            # Add partial block if there's space
            remaining_space = MAX_CONTEXT_CHARS - current_context_size - 100
            if remaining_space > 500:
                truncated_text = full_doc_text[:remaining_space] + "... [truncated]"
                block = (
                    f"--- START OF CONTEXT FROM DOCUMENT: {source_name} ---\n"
                    f"{truncated_text}\n"
                    f"--- END OF CONTEXT FROM DOCUMENT: {source_name} ---"
                )
                context_blocks.append(block)
            break  # Stop adding more documents
        
        context_blocks.append(block)
        current_context_size += len(block)
    
    context_text = "\n\n".join(context_blocks)
    
    # Estimate tokens before selecting model
    estimated_tokens = len(context_text) / 4
    print(f"--- Total context tokens estimated: {int(estimated_tokens)} (limited to ~3000) ---")

    # 3. Create the prompt with instructions to cite sources and include subject/grade context.
    # Get subject, grade, course, custom_instructions, and language from state
    subject = state.get("subject", "Mathématiques")
    grade = state.get("grade", "7ème année")
    course = state.get("course", "")
    custom_instructions = state.get("custom_instructions", "")
    language = state.get("language", "Français")
    
    # Language instruction mapping
    language_instructions = {
        "Français": "You MUST respond ONLY in French. All explanations, examples, and text must be in French.",
        "English": "You MUST respond ONLY in English. All explanations, examples, and text must be in English.",
        "العربية": "You MUST respond ONLY in Arabic. All explanations, examples, and text must be in Arabic. Use proper Arabic script (العربية)."
    }
    language_instruction = language_instructions.get(language, language_instructions["Français"])
    
    # Build personalized system prompt based on subject, grade, course, custom instructions, and language
    course_context = f" focusing specifically on: {course}" if course else ""
    custom_instructions_text = f"\n\nAdditional Instructions:\n{custom_instructions}" if custom_instructions else ""
    
    system_prompt = f"""You are an expert tutor specialized in {subject} for {grade} level students{course_context}.

IMPORTANT: {language_instruction}

Your role:
- Provide clear, age-appropriate explanations tailored to {grade} level
- Use pedagogical methods suitable for {grade} students
- Focus specifically on {subject} concepts and curriculum{course_context}
- Adapt your language and examples to the student's level
- Be encouraging and supportive

When answering:
- Base your response on the provided context documents when available
- Cite the document name when using information from documents
- If the answer isn't in the context, use your knowledge of {subject} at {grade} level
- Break down complex concepts into simpler steps appropriate for {grade}
- Use examples and analogies suitable for the student's age group{custom_instructions_text}

Remember: You are teaching {subject} to a {grade} student. Keep explanations clear, engaging, and appropriate for their level. Always respond in {language}."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", "Context from documents:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    # Dynamically select the LLM based on the model name in the state or context size
    # print("___ we are in RAG with model name : ",model_name)
    
    # If no model specified or model not found, auto-select based on context size
    if not model_name or model_name == "None" or model_name not in AVAILABLE_MODELS:
        model_key = select_model_based_on_context(context_text)
        selected_llm = AVAILABLE_MODELS.get(model_key)
        if not selected_llm:
            print(f"Warning: Auto-selected model '{model_key}' not found. Falling back to llama-3.1-70b-versatile.")
            selected_llm = AVAILABLE_MODELS.get("Groq/llama-3.1-70b-versatile") or groq_model
    else:
        selected_llm = AVAILABLE_MODELS.get(model_name)
        if not selected_llm:
            print(f"Warning: Model '{model_name}' not found. Falling back to default Groq model.")
            selected_llm = groq_model  # Fallback to a default model
        
    # 5. Create and invoke the chain with the separated parts.
    chain = prompt | selected_llm | StrOutputParser()
    response = chain.invoke({
        "context": context_text,
        "chat_history": chat_history,
        "question": current_question
    }, config={"configurable": {"thread_id": thread_id}})

    # Create AI message
    ai_message = AIMessage(content=response)

    return {
        "messages": state["messages"] + [ai_message],
        "context": context  # Pass context through
    }
    
  
# 3. Define memory update node
def update_memory_node(state: GraphState):
    """Node to save conversation to vector store memory"""
    messages = state["messages"]
    chat_id = state["chat_id"]
    user_id = state["user_id"]
    
    # Only save the latest exchange (user + AI)
    if len(messages) >= 2:
        user_msg = messages[-1]
        ai_msg = messages[-1]
        
        # Create documents for vector store
        docs_to_save = [
            Document(
                page_content=user_msg.content,
                metadata={
                    "chat_id": chat_id,
                    "role": "user",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ),
            Document(
                page_content=ai_msg.content,
                metadata={
                    "chat_id": chat_id,
                    "role": "assistant",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        ]
        
        # Save to vector store
        vectorstore3.add_documents(docs_to_save)
    
    return state

# 4. Build the LangGraph workflow
workflow_rag = StateGraph(GraphState)

# Define nodes
workflow_rag.add_node("retrieve", retrieve_node)
workflow_rag.add_node("generate", generate_node)
workflow_rag.add_node("update_memory", update_memory_node)

# Set up edges
workflow_rag.set_entry_point("retrieve")
workflow_rag.add_edge("retrieve", "generate")
workflow_rag.add_edge("generate", "update_memory")
workflow_rag.add_edge("update_memory", END)


### RAG WORKFLOW 2 

# # 4. Build the graph
# workflow_rag2 = StateGraph(GraphState)
# workflow_rag2.add_node("retrieve", retrieve_node)
# workflow_rag2.add_node("generate", generate_node)
# # workflow_rag2.add_node("update_memory", update_memory_node)

# workflow_rag2.set_entry_point("retrieve")
# workflow_rag2.add_edge("retrieve", "generate")
# workflow_rag2.add_edge("generate", END)
# # workflow_rag2.add_edge("update_memory", END)


### RAG WORKFLOW 3

# 4. Build the graph
workflow_rag2 = StateGraph(GraphState)

# Add all nodes to the graph
workflow_rag2.add_node("retrieve", retrieve_node)
workflow_rag2.add_node("generate", generate_node)
workflow_rag2.add_node("rewrite_prompt", rewrite_image_prompt_node)
workflow_rag2.add_node("generate_image", generate_image_node)
workflow_rag2.add_node("general_chat", call_groq_model)
# Set the conditional entry point
workflow_rag2.add_conditional_edges(
    START,
    route_by_model_type,
    {
        "rewrite_prompt": "rewrite_prompt",
        "retrieve": "retrieve",
        "general_chat": "general_chat"
    }
)

# Define the edges for both paths
workflow_rag2.add_edge("retrieve", "generate")
workflow_rag2.add_edge("rewrite_prompt", "generate_image")

# Define the end points for both paths
workflow_rag2.add_edge("generate", END)
workflow_rag2.add_edge("generate_image", END)
workflow_rag2.add_edge("general_chat", END)
