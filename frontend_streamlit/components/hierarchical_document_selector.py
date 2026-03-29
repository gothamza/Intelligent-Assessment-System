# components/hierarchical_document_selector.py
import streamlit as st
import requests
from typing import List, Dict, Set

def get_user_collections(headers: dict, backend_url: str) -> List[Dict]:
    """Get all collections for the current user"""
    try:
        response = requests.get(f"{backend_url}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching collections: {e}")
        return []

def get_collection_documents(collection_id: str, headers: dict, backend_url: str) -> List[Dict]:
    """Get all documents in a collection (including subcollections)"""
    try:
        response = requests.get(f"{backend_url}/collections/{collection_id}/documents", 
                              headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'doc_ids' in data:
                doc_ids = data['doc_ids']
                if doc_ids:
                    # Get document details
                    docs_response = requests.get(f"{backend_url}/docs/list", 
                                               headers=headers, timeout=5)
                    if docs_response.status_code == 200:
                        all_docs = docs_response.json()
                        return [doc for doc in all_docs if doc.get('doc_id') in doc_ids]
        return []
    except Exception as e:
        st.error(f"Error fetching collection documents: {e}")
        return []

def get_collection_subcollections(collection_id: str, headers: dict, backend_url: str) -> List[Dict]:
    """Get direct subcollections of a collection"""
    try:
        response = requests.get(f"{backend_url}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            all_collections = response.json()
            return [col for col in all_collections if str(col.get('parent_id')) == str(collection_id)]
        return []
    except Exception as e:
        st.error(f"Error fetching subcollections: {e}")
        return []

def build_collection_tree(collections: List[Dict], parent_id: str = None) -> List[Dict]:
    """Build hierarchical tree structure from flat collection list"""
    tree = []
    for collection in collections:
        if str(collection.get('parent_id')) == str(parent_id):
            children = build_collection_tree(collections, collection.get('id'))
            collection['children'] = children
            tree.append(collection)
    return tree

def render_collection_tree(collections: List[Dict], headers: dict, backend_url: str, 
                         selected_docs: Set[str], indent_level: int = 0, parent_path: str = "") -> Set[str]:
    """Render collection tree with checkboxes and return updated selected documents"""
    indent = "  " * indent_level
    
    for collection in collections:
        collection_id = str(collection.get('id'))
        collection_name = collection.get('name', 'Unnamed')
        current_path = f"{parent_path}_{collection_id}" if parent_path else collection_id
        
        # Check if this collection is selected (all documents inside are selected)
        collection_docs = get_collection_documents(collection_id, headers, backend_url)
        collection_doc_ids = {doc.get('doc_id') for doc in collection_docs}
        is_collection_selected = collection_doc_ids.issubset(selected_docs)
        
        # Get subcollections to determine if we should show expand/collapse
        subcollections = get_collection_subcollections(collection_id, headers, backend_url)
        has_subcollections = len(subcollections) > 0
        has_documents = len(collection_docs) > 0
        
        # Collection checkbox and name
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            collection_key = f"collection_{current_path}"
            if st.checkbox("Select", value=is_collection_selected, key=collection_key, label_visibility="collapsed"):
                # Collection selected - add all documents
                selected_docs.update(collection_doc_ids)
            else:
                # Collection deselected - remove all documents
                selected_docs.difference_update(collection_doc_ids)
        
        with col2:
            st.write(f"{indent}📁 **{collection_name}** ({len(collection_docs)} docs)")
        
        with col3:
            # Show chevron toggle only if there are subcollections or documents
            if has_subcollections or has_documents:
                expand_key = f"expand_{current_path}"
                current_expanded = st.session_state.get(expand_key, False)
                chevron_label = "▼" if current_expanded else "▶"
                if st.button(chevron_label, key=f"btn_{expand_key}", help="Expand / Collapse"):
                    st.session_state[expand_key] = not current_expanded
                    st.rerun()
                is_expanded = st.session_state.get(expand_key, False)
            else:
                is_expanded = False
        
        # Show documents and subcollections only if expanded
        if is_expanded:
            # First, show subcollections (folders)
            if subcollections:
                selected_docs = render_collection_tree(subcollections, headers, backend_url, 
                                                     selected_docs, indent_level + 1, current_path)
            
            # Then, show documents in this collection
            if collection_docs:
                for doc in collection_docs:
                    doc_id = doc.get('doc_id')
                    doc_name = doc.get('doc_title', 'Untitled')
                    file_type = doc.get('file_type', 'unknown')
                    
                    # File type emojis
                    FILE_TYPE_EMOJIS = {
                        'pdf': '📕', 'docx': '📘', 'doc': '📘', 'txt': '📄', 
                        'xlsx': '📊', 'csv': '📈', 'json': '📋', 'md': '📝',
                        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️'
                    }
                    emoji = FILE_TYPE_EMOJIS.get(file_type, "📄")
                    
                    doc_indent = "  " * (indent_level + 1)
                    doc_col1, doc_col2 = st.columns([1, 4])
                    
                    with doc_col1:
                        # Make doc key unique by including the collection path
                        doc_key = f"doc_{current_path}_{doc_id}"
                        if st.checkbox(" ", value=doc_id in selected_docs, key=doc_key, label_visibility="collapsed"):
                            selected_docs.add(doc_id)
                        else:
                            selected_docs.discard(doc_id)
                    
                    with doc_col2:
                        st.write(f"{doc_indent}{emoji} {doc_name}")
    
    return selected_docs

def hierarchical_document_selector(headers: dict, backend_url: str) -> List[str]:
    """
    Main function to render hierarchical document selector for RAG
    Returns list of selected document IDs
    """
    st.subheader("📁 Select Documents for RAG")
    st.caption("Select collections (folders) to include all documents inside, or select individual documents")
    
    # Initialize selected documents in session state
    if 'selected_rag_docs' not in st.session_state:
        st.session_state.selected_rag_docs = set()
    
    # Get all collections
    collections = get_user_collections(headers, backend_url)
    if not collections:
        st.info("No collections found. Create collections to organize your documents.")
        return []
    
    # Build tree structure
    root_collections = build_collection_tree(collections, None)
    
    # Render the tree
    with st.container(height=400, border=True):
        selected_docs = render_collection_tree(root_collections, headers, backend_url, 
                                             st.session_state.selected_rag_docs, 0, "")
        st.session_state.selected_rag_docs = selected_docs
    
    # Show selected documents summary
    if selected_docs:
        st.success(f"✅ {len(selected_docs)} document(s) selected for RAG")
        
        # Show selected document names
        with st.expander("📋 Selected Documents", expanded=False):
            for doc_id in selected_docs:
                # Get document name (we could cache this for better performance)
                try:
                    docs_response = requests.get(f"{backend_url}/docs/list", 
                                               headers=headers, timeout=5)
                    if docs_response.status_code == 200:
                        all_docs = docs_response.json()
                        doc = next((d for d in all_docs if d.get('doc_id') == doc_id), None)
                        if doc:
                            doc_name = doc.get('doc_title', 'Untitled')
                            file_type = doc.get('file_type', 'unknown')
                            FILE_TYPE_EMOJIS = {
                                'pdf': '📕', 'docx': '📘', 'doc': '📘', 'txt': '📄', 
                                'xlsx': '📊', 'csv': '📈', 'json': '📋', 'md': '📝',
                                'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️'
                            }
                            emoji = FILE_TYPE_EMOJIS.get(file_type, "📄")
                            st.write(f"{emoji} {doc_name}")
                except:
                    st.write(f"📄 Document {doc_id}")
    else:
        st.info("No documents selected. Select collections or individual documents above.")
    
    return list(selected_docs)
