import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL")

def chat_selector():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(f"{BACKEND_URL}/chats/list", headers=headers)
    chats = resp.json()
    chat_titles = [c["chat_title"] for c in chats]
    chat_ids = [c["chat_id"] for c in chats]
    selected = st.sidebar.selectbox("Select chat", chat_titles)
    chat_id = chat_ids[chat_titles.index(selected)] if selected in chat_titles else None
    if st.sidebar.button("New Chat"):
        title = st.sidebar.text_input("Chat title", key="new_chat_title")
        if title:
            resp = requests.post(f"{BACKEND_URL}/chats/create", json={"chat_title": title}, headers=headers)
            st.experimental_rerun()
    return chat_id

def show_rag_chat():
    st.subheader("🔎 Chat with Your Documents (RAG)")
    st.markdown("---")
    chat_id = chat_selector()
    if not chat_id:
        st.info("Select or create a chat.")
        return

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    # Fetch available docs
    docs = requests.get(f"{BACKEND_URL}/docs/list", headers=headers).json()
    doc_options = {f"{doc['doc_title']} ({doc['visibility']})": doc["doc_id"] for doc in docs}
    if "selected_doc_keys" not in st.session_state:
        st.session_state.selected_doc_keys = list(doc_options.keys())

    # Load chat history
    resp = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
    messages = resp.json()
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Ask about your selected documents...", key="rag_chat_input")
    if prompt:
        # Save user message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "user", "content": prompt},
            headers=headers
        )
        selected_ids = [doc_options[k] for k in st.session_state.selected_doc_keys]
        params = {"question": prompt, "doc_ids": selected_ids, "chat_id": chat_id}
        with st.chat_message("assistant"):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/query_groq",
                    params=params,
                    headers=headers,
                    timeout=180
                )
                if res.status_code == 200:
                    data = res.json()
                    ai_response = data.get("answer", "No answer.")
                    sources = data.get("sources", [])
                    st.markdown(ai_response)
                    if sources:
                        st.markdown("**Sources:**")
                        for s in sources:
                            st.markdown(f"- {s}")
                else:
                    ai_response = "Error: failed to process request."
                    st.markdown(ai_response)
            except Exception:
                ai_response = "Network error. Please try again."
                st.markdown(ai_response)
        # Save assistant message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "assistant", "content": ai_response},
            headers=headers
        )
        st.experimental_rerun()

    # Document selector at the bottom
    with st.container():
        st.session_state.selected_doc_keys = st.multiselect(
            "Choose context docs:",
            options=list(doc_options.keys()),
            default=st.session_state.selected_doc_keys,
        )