import streamlit as st
import requests
import os
from streamlit_option_menu import option_menu 
import re
import json 
BACKEND_URL = os.getenv("BACKEND_URL")

FILE_TYPE_EMOJIS = {
    "pdf": "📕",
    "csv": "📈",
    "xlsx": "📈",
    "xls": "📈",
    "docx": "📘",
    "txt": "📝",
    "md": "📄🖋️",
    "unknown": "📄"
}

def render_message_with_reasoning(content):
    """
    Renders a message, handling special image formats and <think> blocks.
    """
    # Check for the special image format first
    if "image :" in content and "/generated_images/" in content:
        try:
            prompt_part, url_part = content.split("image :", 1)
            prompt = prompt_part.strip()
            image_url = url_part.strip()
            
            # Display the prompt in a copyable code block and the image
            st.code(prompt, language='text')
            st.image(image_url)
            return # Stop further processing
        except ValueError:
            # If splitting fails, fall through to default rendering
            pass

    # Use a regex to find the <think> block and capture its content
    think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
    match = think_pattern.search(content)

    if match:
        # Extract the thinking part and the main response
        thinking_part = match.group(1).strip()
        main_response = think_pattern.sub("", content).strip()

        # Display the thinking part in a collapsible expander
        with st.expander("🧠 View Reasoning"):
            st.info(thinking_part)

        # Display the rest of the response
        if main_response:
            st.markdown(main_response)
    else:
        # If no <think> block is found, render the content as usual
        st.markdown(content)
# ─── 5) RENDER MESSAGE WITH COPY BUTTON ──────────────────────
def render_message_with_copy(role, content, idx):
    with st.chat_message(role):
        st.markdown(content)
        copy_btn_id = f"copy_btn_{role}_{idx}"
        st.markdown(
            f"""
            
            <button id="{copy_btn_id}" data-content="{content.replace('"', '&quot;')}" style="margin-top:4px; font-size:0.85em; padding:2px 8px; border-radius:5px; border:1px solid #ccc; background:#222; color:#eee; cursor:pointer;">
                📋 Copier
            </button>
            """,
            unsafe_allow_html=True,
        )


# # Example usage in your chat loop:
# for idx, msg in enumerate(messages):
#     render_message_with_copy(msg["role"], msg["content"], idx)
    
  
# ─── 6) CHAT INTERFACE ──────────────────────────────────────
def show_chat():
    """Display chat interface"""
    st.subheader("💬 Your Personal Chatbot")
    st.markdown("---")
    idx = 0
    # # # Display chat messages
    # for idx, msg in enumerate(st.session_state.messages):
    #     render_message_with_copy(msg["role"], msg["content"], idx)
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # st.code(msg["content"], language='text')

            
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # render_message_with_copy("user",prompt, idx+1)
        with st.chat_message("user"):
            # st.code(prompt, language='text')
            st.markdown(prompt)
        
        # Simulate AI response (replace with actual backend call)
        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            try:
                # Example of calling your backend
                response = requests.post(
                f"{BACKEND_URL}/llm",
                json={"prompt": prompt},
                headers=headers,
                timeout=180
            )
                if response.status_code == 200:
                    ai_response = response.json().get("response")
                else:
                    ai_response = "Sorry, I couldn't process your request"
            except Exception:
                ai_response = "Network error. Please try again."
            
            # st.code(ai_response, language='text')
            st.markdown(ai_response)
        
        # Add AI response to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
def _generate_content_helper(chat_id, messages, doc_options, prompt_type, headers):
    """
    Helper function to generate exercises or course content.
    
    Args:
        chat_id: Chat ID
        messages: Current chat messages
        doc_options: Dictionary mapping document titles to IDs
        prompt_type: "exercises" or "course"
        headers: Request headers with authorization
    
    Returns:
        None (triggers rerun after generation)
    """
    course = st.session_state.get("selected_course", "")
    subject = st.session_state.get("selected_subject", "Mathématiques")
    grade = st.session_state.get("selected_grade", "7ème année")
    language = st.session_state.get("selected_language", "Français")
    
    # Language-specific prompts
    exercise_prompts = {
        "Français": f"Génère-moi des exercices sur le cours '{course}' en {subject} pour le niveau {grade}. Inclus différents types d'exercices (faciles, moyens, difficiles) avec les solutions détaillées.",
        "English": f"Generate exercises on the topic '{course}' in {subject} for {grade} level. Include different types of exercises (easy, medium, hard) with detailed solutions.",
        "العربية": f"أعطني تمارين حول الموضوع '{course}' في مادة {subject} لمستوى {grade}. شمل أنواعًا مختلفة من التمارين (سهلة، متوسطة، صعبة) مع الحلول المفصلة."
    }
    
    course_prompts = {
        "Français": f"Crée-moi un cours complet et détaillé sur '{course}' en {subject} pour le niveau {grade}. Inclus les concepts principaux, des exemples clairs, des explications étape par étape, et des applications pratiques.",
        "English": f"Create a complete and detailed course on '{course}' in {subject} for {grade} level. Include main concepts, clear examples, step-by-step explanations, and practical applications.",
        "العربية": f"أنشئ لي درسًا كاملًا ومفصلًا حول '{course}' في مادة {subject} لمستوى {grade}. شمل المفاهيم الرئيسية وأمثلة واضحة وشرحًا خطوة بخطوة وتطبيقات عملية."
    }
    
    prompts_map = {
        "exercises": exercise_prompts,
        "course": course_prompts
    }
    
    prompt = prompts_map[prompt_type].get(language, prompts_map[prompt_type]["Français"])
    
    # Save user message
    requests.post(
        f"{BACKEND_URL}/chats/{chat_id}/add_message",
        json={"chat_id": chat_id, "role": "user", "content": prompt},
        headers=headers
    )
    
    # Prepare messages for backend
    history = messages
    chat_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    chat_msgs.append({"role": "user", "content": prompt})
    
    # Call RAG backend
    try:
        selected_ids = [doc_options[k] for k in st.session_state.selected_doc_keys] if st.session_state.selected_doc_keys else []
        
        spinner_text = "🤔 Génération des exercices..." if prompt_type == "exercises" else "🤔 Génération du cours..."
        with st.spinner(spinner_text):
            body = {
                "doc_ids": selected_ids if selected_ids else [],
                "chat_id": chat_id,
                "messages": chat_msgs,
                "use_web_search": False,
                "model_name": st.session_state.get("selected_model", "Groq/llama-3.1-8b-instant"),
                "subject": subject,
                "grade": grade,
                "course": course,
                "custom_instructions": st.session_state.get("custom_instructions", ""),
                "language": language
            }
            res = requests.post(
                f"{BACKEND_URL}/rag_langgraph2",
                json=body,
                headers=headers,
                timeout=300
            )
        if res.status_code == 200:
            # Response will be saved by backend, just rerun to show it
            st.rerun()
        else:
            error_detail = res.json().get("detail", res.text) if res.content else res.text
            st.error(f"Erreur: {error_detail}")
            # Save error message to DB
            requests.post(
                f"{BACKEND_URL}/chats/{chat_id}/add_message",
                json={"chat_id": chat_id, "role": "assistant", "content": f"Error: {error_detail}"},
                headers=headers
            )
            st.rerun()
    except Exception as e:
        st.error(f"Erreur réseau: {str(e)}")
        # Save error to DB
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "assistant", "content": f"Network error: {str(e)}"},
            headers=headers
        )
        st.rerun()


def show_rag_chat(chat_id=None):
    st.subheader("🎓 Math Tutor avec Documents (RAG)")
    st.markdown("---")
    st.markdown("Chattez avec le tuteur IA en utilisant vos documents de cours comme contexte. Sélectionnez les documents à utiliser ci-dessous.")
    # --- Custom CSS for text wrapping in st.code ---
    st.markdown("""
        <style>
            pre {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    if not chat_id:
        st.info("Please select or create a chat.")
        return

    # Initialize session state for RAG chat pagination
    if "rag_chat_history_offset" not in st.session_state:
        st.session_state.rag_chat_history_offset = 0
    if "rag_chat_history_limit" not in st.session_state:
        st.session_state.rag_chat_history_limit = 20
    if "current_rag_chat_id" not in st.session_state:
        st.session_state.current_rag_chat_id = None
    # Reset pagination state if the chat_id changes
    if st.session_state.get("current_rag_chat_id") != chat_id:
        st.session_state.rag_chat_history_offset = 0
        st.session_state.rag_chat_history_limit = 20
        st.session_state.current_rag_chat_id = chat_id
    # Fetch and display chat history
    resp = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages",        
            params={
            "limit": st.session_state.rag_chat_history_limit,
            "offset": st.session_state.rag_chat_history_offset }, 
            headers=headers)
    
    if resp.status_code == 200:
        
        data = resp.json()
        messages = data["messages"]
        total_messages = data.get("total", 0)
        
        # Display "Show more history" button if there are more messages to load
        if len(messages) + st.session_state.rag_chat_history_offset < total_messages:
            if st.button("Show more history", key="rag_show_more"):
                st.session_state.rag_chat_history_limit += 10
                st.rerun()
        elif total_messages > 0:
            st.info("No more messages to show.")
            
        for msg in messages:
            with st.chat_message(msg["role"]):
                # st.markdown(msg["content"])
                # Check if the content is a URL to a generated image
                render_message_with_reasoning(msg["content"])

    else:
        st.error("Could not load chat history.")
        return

    # Fetch available documents
    try:
        res = requests.get(f"{BACKEND_URL}/docs/list", headers=headers, timeout=10)
        res.raise_for_status()
        docs = res.json()
    except Exception as e:
        st.error(f"Could not fetch documents: {e}")
        return

    doc_options = {f"{doc['doc_title']} ({doc['visibility']})": doc["doc_id"] for doc in docs}
    # Create a helper map to easily find a doc's details from its title
    doc_map = {
        f"{doc['doc_title']} ({doc['visibility']})": doc
        for doc in docs
    }
    if "selected_doc_keys" not in st.session_state:
        st.session_state.selected_doc_keys = []
    
    # --- Chat input ---
    prompt = st.chat_input("Posez votre question sur les documents sélectionnés...", key="rag_chat_input")
    if prompt:
        # Save user message to backend (DB + vector store) FIRST
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "user", "content": prompt},
            headers=headers
        )
        # Don't display user message here - it will be shown after rerun from DB
  
        # Prepare messages for backend (last 20 for context, like Groq)
        history = messages
        chat_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
        chat_msgs.append({"role": "user", "content": prompt})

        # Call RAG backend (don't display in chat_message - will show after rerun)
        try:
                selected_ids = [doc_options[k] for k in st.session_state.selected_doc_keys] if st.session_state.selected_doc_keys else []
                
                # Use backend_2's /rag_langgraph2 endpoint
                with st.spinner("🤔 Le tuteur réfléchit..."):
                    # Format for backend_2 /rag_langgraph2 endpoint
                    body = {
                        "doc_ids": selected_ids if selected_ids else [],
                        "chat_id": chat_id,
                        "messages": chat_msgs,  # All messages including current prompt
                        "use_web_search": False,
                        "model_name": st.session_state.get("selected_model", "Groq/llama-3.1-8b-instant"),  # Use selected model from sidebar
                        "subject": st.session_state.get("selected_subject", "Mathématiques"),
                        "grade": st.session_state.get("selected_grade", "7ème année"),
                        "course": st.session_state.get("selected_course", ""),  # Selected course/topic
                        "custom_instructions": st.session_state.get("custom_instructions", ""),  # Custom instructions from user
                        "language": st.session_state.get("selected_language", "Français")  # Selected language for LLM response
                    }
                    res = requests.post(
                        f"{BACKEND_URL}/rag_langgraph2",
                        json=body,
                        headers=headers,
                        timeout=300
                    )
                if res.status_code == 200:
                    data = res.json()
                    ai_response = data.get("answer", "No answer.")  # 'answer' instead of 'response'
                    sources = data.get("sources", [])
                    reasoning = data.get("reasoning")
                    
                    # Combine response and reasoning for the renderer
                    if reasoning:
                        # Format the content to match what render_message_with_reasoning expects
                        ai_response = f"<think>{reasoning}</think>\n\n{ai_response}"
                    
                    # Backend already saves the assistant message (see llm_graph.py line 183)
                    # No need to save again from frontend
                    
                    # Rerun to refresh and show all messages from DB (including user and assistant messages)
                    # Sources will be shown in the message content from DB
                    st.rerun()
                else:
                    error_detail = res.json().get("detail", res.text) if res.content else res.text
                    ai_response = f"Error: {error_detail}"
                    st.error(ai_response)
                    # Save error message to DB
                    requests.post(
                        f"{BACKEND_URL}/chats/{chat_id}/add_message",
                        json={"chat_id": chat_id, "role": "assistant", "content": ai_response},
                        headers=headers
                    )
                    st.rerun()
        except Exception as e:
            ai_response = f"Network error: {str(e)}"
            st.error(ai_response)
            # Save error to DB and rerun
            requests.post(
                f"{BACKEND_URL}/chats/{chat_id}/add_message",
                json={"chat_id": chat_id, "role": "assistant", "content": ai_response},
                headers=headers
            )
            st.rerun()

    # --- Document selector at the bottom ---
    with st.container():
        # Adjust column layout based on whether course is selected
        has_course = st.session_state.get("selected_course")
        
        if has_course:
            # Layout with shortcut buttons: [📑] [📝] [📚] [📤] [space]
            col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 6])
        else:
            # Layout without shortcut buttons: [📑] [space] [📤] [space]
            col1, col_spacer, col4, _ = st.columns([1, 2, 1, 6])
            col2 = None
            col3 = None
        
        with col1:
            # Conditionally set the popover icon based on selection state
            if st.session_state.get("selected_doc_keys"):
                popover_label = "📑"  # Icon indicates documents are selected
            else:
                popover_label = "🔗"  # Default icon for attaching documents
            with st.popover(popover_label, use_container_width=True,help="Sélectionnez les documents à utiliser comme contexte pour le tuteur IA."):
                # Document selection
                def on_doc_selection_change():
                    st.session_state.selected_doc_keys = st.session_state.rag_doc_selector
                
                # Use current selected_doc_keys as default
                current_selection = st.session_state.get('selected_doc_keys', [])
                
                new_selection = st.multiselect(
                    "Choisir les documents de contexte:",
                    options=list(doc_options.keys()),
                    key="rag_doc_selector",
                    default=current_selection,
                    on_change=on_doc_selection_change
                )
                
                # Update the session state with the current selection
                st.session_state.selected_doc_keys = new_selection
                
                if new_selection:
                    st.info(f"✅ {len(new_selection)} document(s) sélectionné(s)")
        
        # Shortcut buttons (only show if course is selected)
        if has_course and col2 and col3:
            with col2:
                if st.button("📝", use_container_width=True, 
                            help=f"Générer des exercices pour: {st.session_state.get('selected_course', 'cours sélectionné')}",
                            key="generate_exercises_btn"):
                    _generate_content_helper(chat_id, messages, doc_options, "exercises", headers)
            
            with col3:
                if st.button("📚", use_container_width=True,
                            help=f"Générer le contenu du cours pour: {st.session_state.get('selected_course', 'cours sélectionné')}",
                            key="generate_course_btn"):
                    _generate_content_helper(chat_id, messages, doc_options, "course", headers)
        
        # Upload button (always visible)
        with col4:
            if st.button("📤", use_container_width=True, help="Télécharger des documents"):
                st.session_state.current_view = "upload"
                st.rerun()
        
    # Show selected files right below input (sticky)
    if st.session_state.selected_doc_keys:
        with st.container():
            st.caption("📌 Documents sélectionnés comme contexte:")
            # Scrollable container to avoid pushing the chat when many docs are selected
            with st.container(height=150, border=True):
                for title in st.session_state.selected_doc_keys:
                    # Look up the document details from the title
                    doc = doc_map.get(title)
                    if doc:
                        # Find the emoji and add it as a prefix
                        file_type = doc.get("file_type", "unknown")
                        emoji = FILE_TYPE_EMOJIS.get(file_type, "📄")
                        st.markdown(f"- {emoji} {title}")
                    else:
                        # Fallback for any case where the doc isn't found
                        st.markdown(f"- {title}")


def groq_chat_selector(type="llm"):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(
            f"{BACKEND_URL}/chats/list",
            params={"chat_type": type},
            headers=headers
        )
    chats = resp.json()
    chat_titles = [c["chat_title"] for c in chats]
    chat_ids = [c["chat_id"] for c in chats]
    selected = st.sidebar.selectbox("Select Groq Chat", chat_titles, key="groq_chat_selector")
    chat_id = chat_ids[chat_titles.index(selected)] if selected in chat_titles else None
    if st.sidebar.button("New Groq Chat"):
        title = st.sidebar.text_input("Chat title", key="new_groq_chat_title")
        if title:
            resp = requests.post(f"{BACKEND_URL}/chats/create", json={"chat_title": title}, headers=headers)
            st.rerun()
    return chat_id



def display_chat_selector(chats, key, use_gif=False):
    if not chats:
        st.sidebar.info("No chats yet. Create one below.")
        return None

    ##########fixing for later bug when creating new chats with the same title at the same minute ##########
    chat_options = [f"{c['chat_title']} ({c['created_at'][:16]})" for c in chats]
    chat_ids = [c["chat_id"] for c in chats]

    # Use a unique session state key to store the index for this specific selector
    session_state_key = f"{key}_selected_index"

    # Initialize the session state if it doesn't exist
    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = 0
    
    # Ensure the stored index is valid (e.g., after a chat deletion)
    if st.session_state[session_state_key] >= len(chat_options):
        st.session_state[session_state_key] = 0

    # Callback to update the session state when the selection changes
    def update_selected_chat():
        st.session_state[session_state_key] = chat_options.index(st.session_state[key])

    # Use the stored index to set the default value of the selectbox
    selected = st.sidebar.selectbox(
        "Select chat", 
        chat_options, 
        key=key, 
        index=st.session_state[session_state_key],
        on_change=update_selected_chat
    )
    
    # Get the chat_id from the currently selected index in session state
    chat_id = chat_ids[st.session_state[session_state_key]]

    if use_gif:
        display_delete_with_gif(chat_id)
    else:
        if st.sidebar.button("🗑️ Delete Chat", key=f"delete_chat_btn_{chat_id}"):
            st.session_state.confirm_delete_chat = chat_id

    return chat_id

def display_delete_with_gif(chat_id):
    st.markdown("""
        <style>
        .element-container:has(img[src*="Animation.gif"]) {
            display: flex;
            align-items: center;
            height: 100%;
            padding-top: 6px;
        }
        button[kind="secondary"] {
            margin-top: 6px;
        }
        </style>
    """, unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        st.image("src/img/Animation.gif", use_column_width=True)
    with col2:
        if st.button("🗑️ Delete Chat", key=f"delete_chat_btn_{chat_id}", help="This will delete the conversation permanently"):
            st.session_state.confirm_delete_chat = chat_id






def show_groq_chat(chat_id=None,prompt=""):
    st.subheader("💬 Math Tutor Chat")
    st.markdown("---")
    st.markdown("Chat with the Math Tutor AI. Ask questions about mathematics, get explanations, and practice problems.")
    if not chat_id:
        st.info("Select or create a chat.")
        return

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    if "chat_history_offset" not in st.session_state:
        st.session_state.chat_history_offset = 0
    if "chat_history_limit" not in st.session_state:
        st.session_state.chat_history_limit = 20
 

    # --- Inject JS to scroll to bottom after rendering messages ---
    st.markdown("""
        <script>
        window.scrollTo(0, document.body.scrollHeight);
        </script>
    """, unsafe_allow_html=True)
        

    # Fetch messages with pagination
    resp = requests.get(
        f"{BACKEND_URL}/chats/{chat_id}/messages",
        params={
            "limit": st.session_state.chat_history_limit,
            "offset": st.session_state.chat_history_offset
        },
        headers=headers
    )
    data = resp.json()
    messages = data["messages"]
    total = data["total"]
    # Only show the button if there are more messages to load
    if len(messages) + st.session_state.chat_history_offset < total:
        if st.button("Show more history"):
            st.session_state.chat_history_limit += 10
            st.rerun()
    elif total > 0:
        st.info("No more messages to show.")
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # # Chat input for Groq
    # if prompt := st.chat_input("Type your message (Groq)...", key="groq_chat_input"):
    #     # Save user message
    #     requests.post(
    #         f"{BACKEND_URL}/chats/{chat_id}/add_message",
    #         json={"chat_id": chat_id, "role": "user", "content": prompt},
    #         headers=headers
    #     )
    # Chat input
    if user_input := st.chat_input("Posez votre question de mathématiques...", key="groq_chat_input"):
        final_prompt = user_input

        # Save the final combined message to the database
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "user", "content": final_prompt},
            headers=headers
        )
        # Prepare messages for backend (last 20 for context)
        history = messages
        # history = messages[-19:] if len(messages) > 19 else messages

        chat_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
        chat_msgs.append({"role": "user", "content": final_prompt})

        with st.chat_message("assistant"):
            try:
                # Use backend_2's /llm_groq_graph endpoint for simple chat
                response = requests.post(
                    f"{BACKEND_URL}/llm_groq_graph",
                    json={
                        "messages": chat_msgs  # All messages including current prompt
                    },
                    params={"chat_id": chat_id},  # Pass chat_id as query parameter
                    headers=headers,
                    timeout=180
                )
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("response", "Sorry, I couldn't process your request.")
                else:
                    error_detail = response.json().get("detail", response.text) if response.content else response.text
                    ai_response = f"Error: {error_detail}"
            except Exception as e:
                ai_response = f"Network error: {str(e)}"
            st.markdown(ai_response)

        # Save assistant message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "assistant", "content": ai_response},
            headers=headers
        )
        # ... (rest of your message sending logic) ...
        st.session_state["scroll_to_bottom"] = True  # Set flag
        st.rerun()
