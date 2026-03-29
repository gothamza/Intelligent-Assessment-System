import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL")
def handle_chat_delete(chat_id, headers, use_delete_func=False):
    if st.session_state.get("confirm_delete_chat") == chat_id and chat_id is not None:
        st.sidebar.warning("Are you sure you want to delete this chat?")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Yes, delete", key=f"confirm_yes_{chat_id}"):
                if use_delete_func:
                    delete_chat(chat_id)
                else:
                    requests.delete(f"{BACKEND_URL}/chats/{chat_id}", headers=headers)
                st.session_state.confirm_delete_chat = None
                st.switch_page("app.py")
        with col2:
            if st.button("Cancel", key=f"confirm_no_{chat_id}"):
                st.session_state.confirm_delete_chat = None
                st.switch_page("app.py")


def handle_chat_create(headers, chat_type=None):
    with st.sidebar.expander("➕ New Chat"):
        new_title = st.text_input("Chat title", key=f"{chat_type or 'groq'}_new_chat_title")
        if st.button("Create Chat", key=f"{chat_type or 'groq'}_create_chat_btn") and new_title:
            payload = {"chat_title": new_title}
            if chat_type:
                payload["chat_type"] = chat_type
            requests.post(f"{BACKEND_URL}/chats/create", json=payload, headers=headers)
            st.switch_page("app.py")



def handle_chat_load_failure():
    st.error("Failed to load chats. Please log in again.")
    st.session_state.token = None
    st.session_state.user_info = None
    st.session_state.current_view = "home"
    st.switch_page("app.py")


      
def delete_chat(chat_id):
    
    try:
        response = requests.delete(
            f"{BACKEND_URL}/chats/{chat_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code in (200, 204):
            st.success("🗑️ Chat deleted successfully!")
            wait_time = 2  # seconds
            st.info(f"Refreshing in {wait_time} second{'s' if wait_time > 2 else ''}...")
            st.rerun()
        else:
            st.error(f"❌ Failed to delete chat: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"⚠️ Network error: {str(e)}")