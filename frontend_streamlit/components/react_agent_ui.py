import streamlit as st
import requests
import os
import re

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def react_chat_selector():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(
        f"{BACKEND_URL}/chats/list",
        params={"chat_type": "react"},
        headers=headers
    )
    chats = resp.json()
    chat_titles = [c["chat_title"] for c in chats]
    chat_ids = [c["chat_id"] for c in chats]

    # Select chat
    selected = st.sidebar.selectbox("Select ReAct Chat", chat_titles, key="react_chat_selector")
    chat_id = chat_ids[chat_titles.index(selected)] if selected in chat_titles else None

    # Delete chat
    if chat_id and st.sidebar.button("🗑️ Delete ReAct Chat", key=f"delete_react_chat_{chat_id}"):
        resp = requests.delete(
            f"{BACKEND_URL}/chats/{chat_id}",
            headers=headers
        )
        if resp.status_code in (200, 204):
            st.success("Chat deleted!")
            st.rerun()
        else:
            st.error("Failed to delete chat.")

    # Create new chat
    with st.sidebar.expander("➕ New ReAct Chat"):
        title = st.text_input("Chat title", key="new_react_chat_title")
        if st.button("Create Chat", key="create_react_chat_btn") and title:
            resp = requests.post(
                f"{BACKEND_URL}/chats/create",
                json={"chat_title": title, "chat_type": "react"},
                headers=headers
            )
            if resp.status_code == 200:
                st.success("Chat created!")
                st.rerun()
            else:
                st.error("Failed to create chat.")

    return chat_id
def show_react_agent_chat():
    st.subheader("🤖 ReAct Agent")
    st.markdown("---")

    chat_id = react_chat_selector()
    if not chat_id:
        st.info("Select or create a chat.")
        return

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    # Fetch and display chat history
    resp = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        messages = data["messages"]  # <-- FIX: get the list of dicts
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    else:
        st.error("Could not load chat history.")
        return

    # Chat input
    prompt = st.chat_input("Ask the ReAct agent...", key="react_agent_input")
    if prompt:
        # Save user message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "user", "content": prompt},
            headers=headers
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call ReAct agent backend
        try:
            res = requests.post(
                f"{BACKEND_URL}/tavily_agent_prime",
                params={"query": prompt, "chat_id": chat_id},
                headers=headers,
                timeout=120
            )
            if res.status_code == 200:
                answer = res.json().get("answer", "")
            else:
                answer = "Agent error."
        except Exception as e:
            answer = f"Network error: {e}"

        # Save assistant message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "assistant", "content": answer},
            headers=headers
        )
        with st.chat_message("assistant"):
            st.markdown(answer)

            # Extract image URLs via Markdown and HTML patterns
            # Extract both types of image links
            md_links = re.findall(
                r'!\[.*?\]\((https?://[^\s)]+\.(?:jpg|jpeg|png|gif|webp))\)',
                answer, flags=re.IGNORECASE
            )
            bracket_links = [
                url for (alt, url) in re.findall(
                    r'\[([^\]]*?)\]\((https?://[^\s)]+\.(?:jpg|jpeg|png|gif|webp))\)',
                    answer, flags=re.IGNORECASE
                )
            ]
            image_links = md_links + bracket_links


            if image_links:
                st.markdown("**Images:**")
                cols = st.columns(3)
                for idx, url in enumerate(image_links):
                    col = cols[idx % 3]
                    col.image(url, use_column_width=True)

        st.rerun()