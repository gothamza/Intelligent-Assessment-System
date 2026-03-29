# components/document_list.py
import streamlit as st
import requests
import os
from datetime import datetime
from requests.exceptions import RequestException

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

def delete_document_ui(doc_id, token):
    """Delete a document and refresh UI."""
    try:
        res = requests.delete(
            f"{BACKEND_URL}/docs/delete/{doc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.status_code == 200:  # Our backend returns 200, not 204
            st.success("✅ Document deleted successfully.")
            st.rerun()
        else:
            error_detail = res.json().get("detail", res.text) if res.content else res.text
            st.error(f"❌ Failed to delete document: {error_detail}")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

def document_list():
    """Document listing interface"""
    st.markdown("## 📄 Document Library")
    st.markdown("---")
    
    # Add filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_visibility = st.selectbox(
            "Filter by Visibility",
            ["All", "private", "team", "public",'session'],
            index=0
        )
    
    with col2:
        filter_user = st.selectbox(
            "Filter by Owner",
            ["All", "Me"],
            index=0
        )
    
    # --- Custom CSS for the scrollable container ---
    st.markdown("""
    <style>
    .scrollable-container {
        height: 400px; /* Adjust height as needed */
        overflow-y: auto;
        border: 1px solid #4A4A4A;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(height=450, border=True):
        try:
            # Fetch documents from backend
            response = requests.get(
                f"{BACKEND_URL}/docs/list",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                documents = response.json()
                
                # Apply filters
                if filter_visibility != "All":
                    documents = [doc for doc in documents if doc["visibility"] == filter_visibility]
                
                if filter_user == "Me":
                    user_id = st.session_state.user_info.get("user_id")
                    documents = [doc for doc in documents if doc.get("user_id") == user_id]
                
                # Display documents - no more st.markdown wrappers needed
                if documents:
                    for doc in documents:
                        file_type = doc.get("file_type", "unknown")
                        emoji = FILE_TYPE_EMOJIS.get(file_type, "📄")
                        
                        with st.expander(f"{emoji} {doc.get('doc_title', 'Untitled Document')}"):
                            st.caption(f"Type: {doc.get('file_type', 'unknown').upper()} | Visibility: {doc.get('visibility', 'private').capitalize()}")
                            if doc.get('upload_date'):
                                try:
                                    upload_date = datetime.fromisoformat(doc['upload_date'].replace('Z', '+00:00'))
                                    st.caption(f"Uploaded: {upload_date.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    st.caption(f"Uploaded: {doc.get('upload_date', 'Unknown')}")
                            
                            col1, col2, col3 = st.columns([1,1,2])
                            with col1:
                                if st.button("👁️ View", key=f"view_{doc['doc_id']}"):
                                    st.session_state.selected_doc = doc
                                    st.session_state.current_view = "doc_detail"
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Delete", key=f"delete_{doc['doc_id']}"):
                                    delete_document_ui(doc['doc_id'], st.session_state.token)
                else:
                    st.info("No documents found matching your filters")

            else:
                st.error(f"❌ Failed to fetch documents: {response.status_code} - {response.text}")
        except RequestException as e:
            st.error(f"⚠️ Network error: {str(e)}")
    
    
    
    st.markdown(
    """
    <style>
    div.stButton > button#upload_doc_btn {
        background-color: #22c55e;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    st.markdown("---")
    if st.button("📤 Upload Document", key="upload_doc_btn"):
        st.session_state.current_view = "upload"
        st.rerun()
    # Back to home button
    if st.button("← Back to Home"):
        st.session_state.current_view = "home"
        st.rerun()
    

