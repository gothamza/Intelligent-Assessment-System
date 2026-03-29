# components/uploader.py
import streamlit as st
import requests
import os
from requests.exceptions import RequestException

BACKEND_URL = os.getenv("BACKEND_URL")

def add_documents_to_collection(collection_id: str, doc_ids: list):
    """Add uploaded documents to the specified collection"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        data = {"doc_ids": doc_ids}
        
        st.info(f"🔄 Adding {len(doc_ids)} documents to collection {collection_id}...")
        
        response = requests.post(
            f"{BACKEND_URL}/collections/{collection_id}/documents",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            st.success(f"✅ Documents added to collection successfully!")
        else:
            st.warning(f"⚠️ Documents uploaded but failed to add to collection: {response.status_code} - {response.text}")
    except Exception as e:
        st.warning(f"⚠️ Documents uploaded but failed to add to collection: {str(e)}")

def uploader():
    """Document upload interface for Math Tutor"""
    st.markdown("## 📤 Upload Document")
    st.markdown("---")
    st.markdown("Upload educational documents (PDF, Word, TXT) to use as context in the Math Tutor chat.")
    
    with st.form("upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Select one or more files", 
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, DOCX. Documents will be processed and indexed for RAG.",
            label_visibility="visible"
        )

        visibility = st.radio(
            "Document Visibility",
            ["private", "public"],
            horizontal=True,
            help=(
                "Private: Only you can see and use\n"
                "Public: All users can see and use"
            )
        )
        submit = st.form_submit_button("🚀 Upload and Process Document(s)", use_container_width=True, type="primary")
    
    if submit and uploaded_files:
        try:
            with st.spinner(f"📤 Uploading and processing {len(uploaded_files)} document(s)... This may take a moment."):
                # Create form data for multiple files
                files_to_upload = [
                    ("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files
                ]
                # Set save_permanently to True and visibility
                data = {"visibility": visibility, "save_permanently": "true"}
                
                # Send request to backend endpoint
                response = requests.post(
                    f"{BACKEND_URL}/docs/upload_for_chat",
                    files=files_to_upload,
                    data=data,
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=300  # 5 minutes for large uploads
                )
                
                if response.status_code == 200:
                    upload_result = response.json()
                    st.success(f"✅ {len(uploaded_files)} document(s) uploaded and processed successfully!")
                    
                    # Show uploaded documents
                    if 'documents' in upload_result:
                        st.markdown("### Uploaded Documents:")
                        for doc in upload_result['documents']:
                            st.info(f"📄 {doc.get('doc_title', 'Document')} (ID: {doc.get('doc_id', 'N/A')})")
                    
                    # Option to go to documents list or stay
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📄 View All Documents", use_container_width=True):
                            st.session_state.current_view = "documents"
                            st.rerun()
                    with col2:
                        if st.button("🏠 Back to Home", use_container_width=True):
                            st.session_state.current_view = "home"
                            st.rerun()
                else:
                    error_detail = response.json().get("detail", response.text) if response.content else response.text
                    st.error(f"❌ Upload failed: {error_detail}")
        except RequestException as e:
            st.error(f"⚠️ Network error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Back button
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.current_view = "home"
        st.rerun()