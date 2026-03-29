import streamlit as st
import requests
import os
from typing import Optional

def collection_manager():
    """Collection Manager page for creating and managing collections"""
    
    # Get backend URL
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    
    st.title("📁 Collection Manager")
    
    # Get user info to determine role and team
    user_info = get_user_info(headers, BACKEND_URL)
    if not user_info:
        st.error("Failed to load user information")
        return
    
    user_role = user_info.get('role', 'employee')
    user_team_id = user_info.get('team_id')
    user_team_name = user_info.get('team_name', 'Unknown Team')
    
    st.info(f"👤 **Logged in as:** {user_info.get('email', 'Unknown')} | **Role:** {user_role.title()} | **Team:** {user_team_name}")
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📂 My Collections")
        display_user_collections(headers, BACKEND_URL, user_info)
    
    with col2:
        st.subheader("➕ Create New Collection")
        create_collection_form(headers, BACKEND_URL, user_info)

def get_user_info(headers: dict, backend_url: str) -> Optional[dict]:
    """Get current user information"""
    try:
        response = requests.get(f"{backend_url}/users/me", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get user info: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error getting user info: {e}")
        return None

def display_user_collections(headers: dict, backend_url: str, user_info: dict):
    """Display user's collections in a tree structure"""
    try:
        response = requests.get(f"{backend_url}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            collections = response.json()
            
            if collections:
                # Separate root collections and subcollections
                root_collections = [col for col in collections if col.get('parent_id') is None]
                subcollections = [col for col in collections if col.get('parent_id') is not None]
                
                if root_collections:
                    st.markdown("#### 📁 Root Collections")
                    for collection in root_collections:
                        display_collection_item(collection, collections, subcollections, headers, backend_url, 0)
                else:
                    st.info("No root collections found. Create your first collection!")
            else:
                st.info("No collections found. Create your first collection!")
        else:
            st.error(f"Failed to load collections: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading collections: {e}")

def display_collection_item(collection, all_collections, subcollections, headers, backend_url, indent_level=0):
    """Display a single collection item with proper indentation and subcollections"""
    indent = "  " * indent_level
    collection_id = collection.get('id')
    
    # Get subcollections for this collection
    child_collections = [col for col in subcollections if col.get('parent_id') == collection_id]
    
    # Create expander for the collection
    with st.expander(f"{indent}📁 {collection.get('name', 'Unnamed')}", expanded=False):
        st.write(f"**Description:** {collection.get('description', 'No description')}")
        st.write(f"**Visibility:** {collection.get('visibility', 'private')}")
        st.write(f"**Created:** {collection.get('created_at', 'Unknown')}")
        
        # Collection actions
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📂", key=f"open_{collection_id}", help="Open collection"):
                st.session_state.selected_collection_id = collection_id
                st.session_state.current_view = "collection_contents"
                st.rerun()
        
        with col_b:
            if st.button("📁", key=f"new_sub_{collection_id}", help="Create subcollection"):
                st.session_state.parent_collection_id = collection_id
                st.session_state.parent_collection_name = collection.get('name', 'Selected Collection')
                st.session_state.current_view = "collection_manager"
                st.rerun()
        
        with col_c:
            if st.button("🗑️", key=f"delete_{collection_id}"):
                delete_collection(collection_id, headers, backend_url)
        
        # Display subcollections if any (without nested expanders)
        if child_collections:
            st.markdown("**Subcollections:**")
            for child in child_collections:
                child_indent = "  " * (indent_level + 1)
                st.markdown(f"{child_indent}📁 **{child.get('name', 'Unnamed')}**")
                
                # Subcollection actions
                col_d, col_e, col_f = st.columns(3)
                with col_d:
                    if st.button("📂", key=f"open_sub_{child.get('id')}", help="Open subcollection"):
                        st.session_state.selected_collection_id = child.get('id')
                        st.session_state.current_view = "collection_contents"
                        st.rerun()
                
                with col_e:
                    if st.button("📁", key=f"new_sub_sub_{child.get('id')}", help="Create subcollection"):
                        st.session_state.parent_collection_id = child.get('id')
                        st.session_state.parent_collection_name = child.get('name', 'Selected Collection')
                        st.session_state.current_view = "collection_manager"
                        st.rerun()
                
                with col_f:
                    if st.button("🗑️", key=f"delete_sub_{child.get('id')}"):
                        delete_collection(child.get('id'), headers, backend_url)

def create_collection_form(headers: dict, backend_url: str, user_info: dict):
    """Create collection form with role-based options"""
    user_role = user_info.get('role', 'employee')
    user_team_id = user_info.get('team_id')
    user_team_name = user_info.get('team_name', 'Unknown Team')
    
    with st.form("create_collection_form", clear_on_submit=True):
        # Collection name
        collection_name = st.text_input("Collection Name *", placeholder="Enter collection name")
        
        # Description
        description = st.text_area("Description", placeholder="Enter collection description (optional)")
        
        # Parent collection selection (for subcollections)
        parent_collection_id = None
        if 'parent_collection_id' in st.session_state:
            parent_collection_id = st.session_state.parent_collection_id
            st.info(f"📁 **Creating subcollection in:** {st.session_state.get('parent_collection_name', 'Selected Collection')}")
        else:
            # Get available collections for parent selection
            collections = get_user_collections(headers, backend_url)
            if collections:
                collection_options = {"None (Root Collection)": None}
                collection_options.update({f"{col.get('name', 'Unnamed')}": col.get('id') 
                                         for col in collections})
                selected_parent = st.selectbox("Parent Collection", list(collection_options.keys()))
                parent_collection_id = collection_options[selected_parent]
        
        # Visibility options based on role
        if user_role in ['manager', 'admin']:
            visibility_options = ['private', 'team', 'public']
            visibility = st.selectbox("Visibility *", visibility_options, 
                                    help="Private: Only you can see | Team: Your team can see | Public: Everyone can see")
        else:
            visibility_options = ['private', 'team']
            visibility = st.selectbox("Visibility *", visibility_options,
                                    help="Private: Only you can see | Team: Your team can see")
        
        # Team selection (only for managers/admins)
        target_team_id = None
        if user_role in ['manager', 'admin'] and visibility == 'team':
            # Get available teams
            teams = get_available_teams(headers, backend_url)
            if teams:
                team_options = {f"{team.get('name', 'Unknown')} (ID: {team.get('id')})": team.get('id') 
                              for team in teams}
                selected_team = st.selectbox("Target Team", list(team_options.keys()))
                target_team_id = team_options[selected_team]
            else:
                st.warning("No teams available")
        elif visibility == 'team':
            # Regular users can only create for their own team
            target_team_id = user_team_id
            st.info(f"Collection will be visible to your team: {user_team_name}")
        
        # Submit button
        submitted = st.form_submit_button("Create Collection", type="primary")
        
        if submitted:
            if not collection_name:
                st.error("Collection name is required!")
            else:
                create_collection(collection_name, description, visibility, target_team_id, parent_collection_id, headers, backend_url)

def get_user_collections(headers: dict, backend_url: str) -> list:
    """Get user's collections for parent selection"""
    try:
        response = requests.get(f"{backend_url}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

def get_document_details(doc_ids: list, headers: dict, backend_url: str) -> list:
    """Get document details for a list of document IDs"""
    try:
        # Get all documents and filter by the ones in the collection
        response = requests.get(f"{backend_url}/docs/list", headers=headers, timeout=5)
        if response.status_code == 200:
            all_documents = response.json()
            # Filter documents that are in the collection
            collection_documents = [doc for doc in all_documents if doc.get('doc_id') in doc_ids]
            return collection_documents
        else:
            return []
    except Exception as e:
        return []

def get_available_teams(headers: dict, backend_url: str) -> list:
    """Get available teams for managers/admins"""
    try:
        response = requests.get(f"{backend_url}/teams/", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to load teams: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error loading teams: {e}")
        return []

def create_collection(name: str, description: str, visibility: str, target_team_id: Optional[str], 
                     parent_collection_id: Optional[int], headers: dict, backend_url: str):
    """Create a new collection"""
    try:
        data = {
            "name": name,
            "description": description,
            "visibility": visibility
        }
        
        # Add team_id if specified
        if target_team_id:
            data["team_id"] = target_team_id
        
        # Add parent_id if specified (for subcollections)
        if parent_collection_id:
            data["parent_id"] = parent_collection_id
        
        response = requests.post(f"{backend_url}/collections/", 
                               headers=headers, 
                               json=data, 
                               timeout=5)
        
        if response.status_code == 201:
            st.success(f"✅ Collection '{name}' created successfully!")
            
            # If we were creating a subcollection, return to the parent collection
            if 'parent_collection_id' in st.session_state:
                parent_id = st.session_state.parent_collection_id
                del st.session_state.parent_collection_id
                st.session_state.selected_collection_id = parent_id
                st.session_state.current_view = "collection_contents"
                st.rerun()
            else:
                # For root collections, just clear the form
                st.rerun()
        else:
            st.error(f"Failed to create collection: {response.text}")
    except Exception as e:
        st.error(f"Error creating collection: {e}")

def delete_collection(collection_id: str, headers: dict, backend_url: str):
    """Delete a collection"""
    try:
        response = requests.delete(f"{backend_url}/collections/{collection_id}", 
                                 headers=headers, 
                                 timeout=5)
        
        if response.status_code == 200:
            st.success("✅ Collection deleted successfully!")
            st.rerun()
        else:
            st.error(f"Failed to delete collection: {response.text}")
    except Exception as e:
        st.error(f"Error deleting collection: {e}")

def collection_contents():
    """Display contents of a selected collection"""
    if 'selected_collection_id' not in st.session_state:
        st.error("No collection selected")
        return
    
    collection_id = st.session_state.selected_collection_id
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    
    # Get collection details from the list of collections
    try:
        response = requests.get(f"{BACKEND_URL}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            collections = response.json()
            collection = None
            for col in collections:
                if str(col.get('id')) == str(collection_id):
                    collection = col
                    break
            
            if not collection:
                st.error("Collection not found")
                return
        else:
            st.error("Failed to load collections")
            return
    except Exception as e:
        st.error(f"Error loading collection: {e}")
        return
    
    # Breadcrumb navigation
    display_breadcrumb_navigation(collection, collections, headers, BACKEND_URL)
    
    # Collection header
    st.title(f"📁 {collection.get('name', 'Unnamed Collection')}")
    st.write(f"**Description:** {collection.get('description', 'No description')}")
    st.write(f"**Visibility:** {collection.get('visibility', 'private')}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # st.subheader(f"📄 Documents")
        display_collection_documents(collection_id, headers, BACKEND_URL)
    
    with col2:
        st.subheader("📂 Subcollections")
        display_subcollections(collection_id, headers, BACKEND_URL)
    
    # Upload section
    st.subheader("📤 Add Content")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Upload Document"):
            st.session_state.upload_to_collection = collection_id
            st.session_state.current_view = "upload"
            st.rerun()
    
    with col2:
        if st.button("📁 Create Subcollection"):
            st.session_state.parent_collection_id = collection_id
            st.session_state.parent_collection_name = collection.get('name', 'Selected Collection')
            st.session_state.current_view = "collection_manager"
            st.rerun()

def display_breadcrumb_navigation(collection, collections, headers, backend_url):
    """Display breadcrumb navigation for easy folder navigation"""
    # Build breadcrumb path
    breadcrumb_path = []
    current_collection = collection
    
    # Traverse up the hierarchy to build the path
    while current_collection:
        breadcrumb_path.insert(0, current_collection)
        parent_id = current_collection.get('parent_id')
        if parent_id:
            # Find parent collection
            parent_collection = None
            for col in collections:
                if col.get('id') == parent_id:
                    parent_collection = col
                    break
            current_collection = parent_collection
        else:
            current_collection = None
    
    # Display breadcrumb navigation
    if len(breadcrumb_path) > 1:
        st.markdown("### 🧭 Navigation")
        
        # Create breadcrumb with clickable links
        breadcrumb_parts = []
        for i, col in enumerate(breadcrumb_path):
            if i == len(breadcrumb_path) - 1:
                # Current collection (not clickable)
                breadcrumb_parts.append(f"**{col.get('name', 'Unnamed')}**")
            else:
                # Parent collections (clickable)
                breadcrumb_parts.append(f"[{col.get('name', 'Unnamed')}](javascript:void(0))")
        
        breadcrumb_text = " > ".join(breadcrumb_parts)
        st.markdown(f"🏠 **Root** > {breadcrumb_text}")
        
        # Add navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏠 Root Collections", key="nav_root"):
                st.session_state.current_view = "collection_manager"
                if 'selected_collection_id' in st.session_state:
                    del st.session_state.selected_collection_id
                st.rerun()
        
        with col2:
            if len(breadcrumb_path) > 1:
                parent_collection = breadcrumb_path[-2]  # Second to last item
                if st.button(f"⬅️ Back to {parent_collection.get('name', 'Parent')}", key="nav_back"):
                    st.session_state.selected_collection_id = parent_collection.get('id')
                    st.rerun()
        
        with col3:
            if st.button("🔄 Refresh", key="nav_refresh"):
                st.rerun()
        
        st.markdown("---")
    else:
        # Single level - just show back to root button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ Back to Collections", key="nav_back_root"):
                st.session_state.current_view = "collection_manager"
                if 'selected_collection_id' in st.session_state:
                    del st.session_state.selected_collection_id
                st.rerun()
        with col2:
            if st.button("🔄 Refresh", key="nav_refresh_single"):
                st.rerun()
        st.markdown("---")

def display_collection_documents(collection_id: str, headers: dict, backend_url: str):
    """Display documents in the collection"""
    try:
        response = requests.get(f"{backend_url}/collections/{collection_id}/documents", 
                              headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Handle the API response format: {"doc_ids": [...]}
            if isinstance(data, dict) and 'doc_ids' in data:
                doc_ids = data['doc_ids']
                
                if doc_ids:
                    # Get document details for each doc_id
                    documents = get_document_details(doc_ids, headers, backend_url)
                    
                    if documents:
                        st.subheader(f"📄Documents ({len(documents)})")
                        
                        # Scrollable container for documents (same as document_list.py)
                        with st.container(height=350, border=True):
                            for doc in documents:
                                doc_id = doc.get('doc_id')
                                doc_name = doc.get('doc_title', doc.get('filename', 'Unknown'))
                                file_type = doc.get('file_type', 'unknown')
                                
                                # File type emojis (same as document_list.py)
                                FILE_TYPE_EMOJIS = {
                                    'pdf': '📕', 'docx': '📘', 'doc': '📘', 'txt': '📄', 
                                    'xlsx': '📊', 'csv': '📈', 'json': '📋', 'md': '📝',
                                    'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️'
                                }
                                emoji = FILE_TYPE_EMOJIS.get(file_type, "📄")
                                
                                with st.expander(f"{emoji} {doc_name}", expanded=False):
                                    st.caption(f"Type: {file_type.upper()} | Visibility: {doc.get('visibility', 'private').capitalize()}")
                                    st.caption(f"Uploaded: {doc.get('uploaded_at', 'Unknown')}")
                                    
                                    col1, col2, col3 = st.columns([1, 1,1])
                                    with col1:
                                        if st.button("👁️", key=f"view_{doc_id}"):
                                            st.session_state.selected_doc = doc
                                            st.session_state.current_view = "doc_detail"
                                            st.rerun()
                                    with col3:
                                        if st.button("🗑️", key=f"delete_{doc_id}"):
                                            remove_document_from_collection(collection_id, doc_id, headers, backend_url)
                    else:
                        st.info("No documents in this collection")
                else:
                    st.info("No documents in this collection")
            else:
                st.error("Unexpected API response format")
        else:
            st.error(f"Failed to load documents: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading documents: {e}")

def display_subcollections(collection_id: str, headers: dict, backend_url: str):
    """Display subcollections"""
    try:
        # Get all collections and filter by parent_id
        response = requests.get(f"{backend_url}/collections/", headers=headers, timeout=5)
        if response.status_code == 200:
            all_collections = response.json()
            subcollections = [col for col in all_collections if str(col.get('parent_id')) == str(collection_id)]
            
            if subcollections:
                for subcollection in subcollections:
                    with st.expander(f"📁 {subcollection.get('name', 'Unnamed')}", expanded=False):
                        st.write(f"**Description:** {subcollection.get('description', 'No description')}")
                        st.write(f"**Visibility:** {subcollection.get('visibility', 'private')}")
                        
                        if st.button("📂 Open", key=f"open_sub_{subcollection.get('id')}"):
                            st.session_state.selected_collection_id = subcollection.get('id')
                            st.rerun()
            else:
                st.info("No subcollections")
        else:
            st.error(f"Failed to load collections: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading subcollections: {e}")

def remove_document_from_collection(collection_id: str, doc_id: str, headers: dict, backend_url: str):
    """Remove document from collection"""
    try:
        response = requests.delete(f"{backend_url}/collections/{collection_id}/documents", 
                                 headers=headers,
                                 json={"doc_ids": [doc_id]},
                                 timeout=5)
        
        if response.status_code == 200:
            st.success("✅ Document removed from collection!")
            st.rerun()
        else:
            st.error(f"Failed to remove document: {response.text}")
    except Exception as e:
        st.error(f"Error removing document: {e}")
