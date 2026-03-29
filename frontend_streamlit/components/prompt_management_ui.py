import streamlit as st
import requests
import os
import json

# Use Docker-friendly default for BACKEND_URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def get_prompts(headers):
    """Fetches accessible prompts from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/prompts/", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load prompts: {e}")
        return []

def delete_prompt(prompt_id, headers):
    """Deletes a specific prompt."""
    try:
        response = requests.delete(f"{BACKEND_URL}/prompts/{prompt_id}", headers=headers, timeout=10)
        response.raise_for_status()
        st.success("Prompt deleted successfully!")
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to delete prompt: {e.response.json().get('detail', str(e))}")

def create_prompt(payload, headers):
    """Creates a new prompt."""
    try:
        response = requests.post(f"{BACKEND_URL}/prompts/", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        st.success("Prompt created successfully!")
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create prompt: {e.response.json().get('detail', str(e))}")

def show_prompt_management():
    """
    Renders the prompt management UI for listing, filtering, and navigating prompts.
    """
    token = st.session_state.get("token")
    if not token:
        st.warning("Please log in to manage prompts.")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # --- Title with New Prompt Button ---
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title("📝 Prompt Templates")
    with col2:
        if st.button("➕", use_container_width=True):
            st.session_state.current_view = "prompt_editor"
            if "current_prompt_id" in st.session_state:
                del st.session_state["current_prompt_id"]
            st.rerun()

    # --- Filter UI (remains the same) ---
    st.subheader("Filters")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All", "simple", "system", "rag"], key="prompt_filter_type")
    with col2:
        filter_visibility = st.selectbox("Filter by Visibility", ["All", "public", "private", "team"], key="prompt_filter_visibility")
    with col3:
        filter_search = st.text_input("Search by Title/Content", key="prompt_filter_search")

    # --- Filtering Logic (remains the same) ---
    all_prompts = get_prompts(headers)
    filtered_prompts = all_prompts
    if filter_type != "All":
        filtered_prompts = [p for p in filtered_prompts if p.get('type') == filter_type]
    if filter_visibility != "All":
        filtered_prompts = [p for p in filtered_prompts if p.get('visibility') == filter_visibility]
    if filter_search:
        search_term = filter_search.lower()
        filtered_prompts = [p for p in filtered_prompts if search_term in p.get('title', '').lower() or search_term in p.get('content', '').lower()]

    # --- Display Filtered Prompts ---
    st.markdown("---")
    if not filtered_prompts:
        st.info("No prompt templates match your filters.")
    
    for p in filtered_prompts:
        with st.container(border=True):
            col_title, col_edit, col_delete = st.columns([0.8, 0.1, 0.1])
            with col_title:
                st.subheader(p['title'])
                st.caption(f"Type: {p['type']} | Visibility: {p['visibility']} | ID: {p['id']}")
            with col_edit:
                if st.button("✏️", key=f"edit_{p['id']}", help="Edit Prompt"):
                    st.session_state.current_view = "prompt_editor"
                    st.session_state.current_prompt_id = p['id']
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{p['id']}", help="Delete Prompt"):
                    delete_prompt(p['id'], headers)
            
            with st.expander("View Content"):
                st.code(p['content'], language='text')
                

def display_prompt_selector(prompts, key):
    """
    Displays a selectbox in the sidebar for choosing a prompt.
    Returns the content of the selected prompt.
    """
    if not prompts:
        st.sidebar.caption("No prompts available.")
        return None

    # Create display options and a parallel list of contents
    # Create display options with tags and a parallel list of contents
    prompt_options = []
    for p in prompts:
        tags = p.get("tags", [])
        if tags:
            tag_str = ", ".join(tags)
            prompt_options.append(f"{p['title']} ({tag_str})")
        else:
            prompt_options.append(p['title'])
    prompt_contents = [p["content"] for p in prompts]

    # Add a placeholder option
    options_with_placeholder = [""] + prompt_options
    
    selected_option = st.sidebar.selectbox("Prompt Shortcuts", options_with_placeholder, key=key)

    if selected_option != "":
        # Find the content of the selected prompt
        selected_index = options_with_placeholder.index(selected_option) - 1
        st.session_state.chat_input_value = prompt_contents[selected_index]
        return prompt_contents[selected_index]
    
    return None


