import streamlit as st
import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def show_prompt_editor():
    """
    Renders a form to create or edit a prompt template.
    Determines mode based on `st.session_state.current_prompt_id`.
    """
    prompt_id = st.session_state.get("current_prompt_id")
    is_edit_mode = prompt_id is not None
    
    headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
    
    prompt_data = {}
    if is_edit_mode:
        st.title("✏️ Edit Prompt Template")
        try:
            response = requests.get(f"{BACKEND_URL}/prompts/{prompt_id}", headers=headers)
            response.raise_for_status()
            prompt_data = response.json()
        except requests.RequestException as e:
            st.error(f"Failed to load prompt data: {e}")
            return
    else:
        st.title("➕ Create New Prompt Template")

    with st.form("prompt_editor_form"):
        title = st.text_input(
            "Title", 
            value=prompt_data.get("title", ""),
            placeholder="e.g., 'Customer Support Email Responder'"
        )
        content = st.text_area(
            "Content", 
            value=prompt_data.get("content", ""), 
            height=250,
            placeholder="You are a helpful assistant. Respond to the following customer query: {{customer_query}}",
            help="Use double curly braces like {{variable_name}} to define variables."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            type_options = ["simple", "system", "rag"]
            type_index = type_options.index(prompt_data.get("type", "simple"))
            type = st.selectbox("Type", type_options, index=type_index)
        with col2:
            visibility_options = ["public", "private", "team"]
            visibility_index = visibility_options.index(prompt_data.get("visibility", "public"))
            visibility = st.selectbox("Visibility", visibility_options, index=visibility_index)
        
        tags_input = st.text_input(
            "Tags (comma-separated)", 
            value=", ".join(prompt_data.get("tags", [])),
            placeholder="email, support, customer-service"
        )
        
        submitted = st.form_submit_button("Save Prompt")
        
        if submitted:
            if not title or not content:
                st.warning("Title and Content fields cannot be empty.")
            else:
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                payload = {
                    "title": title, "content": content, "type": type, 
                    "tags": tags, "visibility": visibility, "variables": {}
                }
                
                try:
                    if is_edit_mode:
                        response = requests.put(f"{BACKEND_URL}/prompts/{prompt_id}", json=payload, headers=headers)
                    else:
                        response = requests.post(f"{BACKEND_URL}/prompts/", json=payload, headers=headers)
                    
                    response.raise_for_status()
                    st.success(f"Prompt successfully {'updated' if is_edit_mode else 'created'}!")
                    st.session_state.current_view = "prompts"
                    st.rerun()
                except requests.RequestException as e:
                    st.error(f"Failed to save prompt: {e.response.json().get('detail', str(e))}")

    if st.button("← Back to List"):
        st.session_state.current_view = "prompts"
        st.rerun()