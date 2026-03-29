import streamlit as st
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add services to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import API client
from services.api_client import APIClient

st.set_page_config(page_title="Gestion Documents", layout="wide", page_icon="📚")

# ============================================================================
# Initialize Session State
# ============================================================================

if 'api_client' not in st.session_state:
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    st.session_state.api_client = APIClient(base_url=api_base_url)

if 'selected_documents' not in st.session_state:
    st.session_state.selected_documents = []

if 'all_documents' not in st.session_state:
    st.session_state.all_documents = []

# ============================================================================
# Helper Functions
# ============================================================================

def load_documents_list():
    """Load list of documents from backend"""
    try:
        response = st.session_state.api_client.list_documents()
        st.session_state.all_documents = response.get("documents", [])
        return st.session_state.all_documents
    except Exception as e:
        st.error(f"Erreur lors du chargement des documents: {str(e)}")
        return []

def upload_document(file, metadata: Dict[str, Any] = None):
    """Upload document to backend"""
    try:
        # Use the API client's upload_document method
        return st.session_state.api_client.upload_document(file, metadata)
    except Exception as e:
        raise Exception(f"Erreur lors de l'upload: {str(e)}")

def delete_document(doc_id: str):
    """Delete document from backend"""
    try:
        return st.session_state.api_client.delete_document(doc_id)
    except Exception as e:
        raise Exception(f"Erreur lors de la suppression: {str(e)}")

# ============================================================================
# Main UI
# ============================================================================

st.title("📚 Gestion des Documents")

st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
    <h3 style='color: white; margin: 0;'>📖 Base de Connaissances RAG</h3>
    <p style='margin: 10px 0 0 0;'>
        Téléchargez des documents (PDF, Word, TXT) pour enrichir le contexte du tuteur IA.
        Les documents seront indexés et utilisables dans les conversations.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar: Document Selection for Chat
# ============================================================================

with st.sidebar:
    st.header("📋 Documents Sélectionnés")
    st.markdown("Sélectionnez les documents à utiliser comme contexte dans le chat.")
    
    # Load documents
    if st.button("🔄 Actualiser la liste", use_container_width=True):
        load_documents_list()
        st.rerun()
    
    # Auto-load on page load
    if not st.session_state.all_documents:
        load_documents_list()
    
    if st.session_state.all_documents:
        st.markdown("---")
        st.markdown("**Documents disponibles:**")
        
        # Select all checkbox
        select_all = st.checkbox("✅ Sélectionner tous les documents", value=False)
        
        if select_all:
            st.session_state.selected_documents = [doc["id"] for doc in st.session_state.all_documents]
        else:
            # Individual selection
            selected = []
            for doc in st.session_state.all_documents:
                is_selected = st.checkbox(
                    f"📄 {doc.get('name', 'Document sans nom')}",
                    value=doc["id"] in st.session_state.selected_documents,
                    key=f"doc_{doc['id']}"
                )
                if is_selected:
                    selected.append(doc["id"])
            st.session_state.selected_documents = selected
        
        # Show selected count
        if st.session_state.selected_documents:
            st.success(f"✅ {len(st.session_state.selected_documents)} document(s) sélectionné(s)")
            st.info("💡 Ces documents seront utilisés comme contexte dans le chat")
        else:
            st.warning("⚠️ Aucun document sélectionné")
    else:
        st.info("📭 Aucun document disponible. Téléchargez des documents ci-dessous.")
    
    st.markdown("---")
    st.markdown("**💡 Astuce:** Les documents sélectionnés seront automatiquement utilisés lors des conversations dans le tuteur interactif.")

# ============================================================================
# Main Content: Document Upload
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📤 Télécharger un Document")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier",
        type=["pdf", "docx", "txt", "doc"],
        help="Formats supportés: PDF, Word (.docx, .doc), Texte (.txt)"
    )
    
    if uploaded_file:
        st.info(f"📄 Fichier sélectionné: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        # Metadata form
        with st.expander("📝 Métadonnées (Optionnel)", expanded=False):
            col_meta1, col_meta2 = st.columns(2)
            
            with col_meta1:
                doc_topic = st.selectbox(
                    "📚 Sujet:",
                    ["Algèbre", "Géométrie", "Fonctions", "Trigonométrie", "Probabilités", 
                     "Statistiques", "Calcul", "Arithmétique", "Autre"],
                    help="Sujet principal du document"
                )
                
                doc_niveau = st.selectbox(
                    "🎯 Niveau:",
                    ["7ème année", "8ème année", "9ème année", "10ème année", "11ème année", "12ème année", "Tous"],
                    help="Niveau scolaire ciblé"
                )
            
            with col_meta2:
                doc_source = st.text_input(
                    "📖 Source:",
                    placeholder="Ex: Manuel scolaire, Cours en ligne...",
                    help="Source du document"
                )
                
                doc_description = st.text_area(
                    "📝 Description:",
                    placeholder="Description courte du contenu...",
                    help="Description du document"
                )
        
        # Upload button
        if st.button("🚀 Télécharger et Indexer", type="primary", use_container_width=True):
            try:
                with st.spinner("📤 Téléchargement et indexation en cours..."):
                    metadata = {
                        "topic": doc_topic if doc_topic != "Autre" else "",
                        "niveau": doc_niveau if doc_niveau != "Tous" else "",
                        "source": doc_source,
                        "description": doc_description
                    }
                    
                    result = upload_document(uploaded_file, metadata)
                    
                    st.success(f"✅ Document téléchargé avec succès!")
                    st.json(result)
                    
                    # Refresh document list
                    load_documents_list()
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

with col2:
    st.header("📊 Statistiques")
    
    try:
        # Get document stats
        if st.session_state.all_documents:
            total_docs = len(st.session_state.all_documents)
            total_size = sum(doc.get("size", 0) for doc in st.session_state.all_documents)
            
            st.metric("📚 Documents", total_docs)
            st.metric("💾 Taille totale", f"{total_size / 1024 / 1024:.2f} MB")
            
            # Document types
            doc_types = {}
            for doc in st.session_state.all_documents:
                doc_type = doc.get("type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            if doc_types:
                st.markdown("**Types de documents:**")
                for doc_type, count in doc_types.items():
                    st.write(f"- {doc_type.upper()}: {count}")
        else:
            st.info("Aucune statistique disponible")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

# ============================================================================
# Document List
# ============================================================================

st.markdown("---")
st.header("📚 Documents Indexés")

# Refresh button
if st.button("🔄 Actualiser", key="refresh_list"):
    load_documents_list()
    st.rerun()

if st.session_state.all_documents:
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        filter_topic = st.selectbox(
            "Filtrer par sujet:",
            ["Tous"] + list(set(doc.get("topic", "") for doc in st.session_state.all_documents if doc.get("topic"))),
            key="filter_topic"
        )
    
    with col_filter2:
        filter_niveau = st.selectbox(
            "Filtrer par niveau:",
            ["Tous"] + list(set(doc.get("niveau", "") for doc in st.session_state.all_documents if doc.get("niveau"))),
            key="filter_niveau"
        )
    
    with col_filter3:
        search_query = st.text_input("🔍 Rechercher:", placeholder="Nom du document...")
    
    # Filter documents
    filtered_docs = st.session_state.all_documents
    if filter_topic != "Tous":
        filtered_docs = [doc for doc in filtered_docs if doc.get("topic") == filter_topic]
    if filter_niveau != "Tous":
        filtered_docs = [doc for doc in filtered_docs if doc.get("niveau") == filter_niveau]
    if search_query:
        filtered_docs = [doc for doc in filtered_docs if search_query.lower() in doc.get("name", "").lower()]
    
    # Display documents
    if filtered_docs:
        for doc in filtered_docs:
            with st.container():
                col_doc1, col_doc2, col_doc3 = st.columns([3, 2, 1])
                
                with col_doc1:
                    st.markdown(f"### 📄 {doc.get('name', 'Document sans nom')}")
                    if doc.get("description"):
                        st.caption(doc.get("description"))
                    
                    # Metadata badges
                    metadata_badges = []
                    if doc.get("topic"):
                        metadata_badges.append(f"📚 {doc['topic']}")
                    if doc.get("niveau"):
                        metadata_badges.append(f"🎯 {doc['niveau']}")
                    if doc.get("source"):
                        metadata_badges.append(f"📖 {doc['source']}")
                    
                    if metadata_badges:
                        st.markdown(" ".join(metadata_badges))
                
                with col_doc2:
                    st.caption(f"**Type:** {doc.get('type', 'N/A').upper()}")
                    st.caption(f"**Taille:** {doc.get('size', 0) / 1024:.1f} KB")
                    if doc.get("uploaded_at"):
                        st.caption(f"**Ajouté:** {doc['uploaded_at']}")
                    if doc.get("chunks"):
                        st.caption(f"**Chunks:** {doc['chunks']}")
                
                with col_doc3:
                    if st.button("🗑️ Supprimer", key=f"delete_{doc['id']}", type="secondary"):
                        try:
                            with st.spinner("Suppression..."):
                                delete_document(doc["id"])
                                st.success("✅ Document supprimé")
                                load_documents_list()
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {str(e)}")
                
                st.divider()
    else:
        st.info("🔍 Aucun document ne correspond aux filtres")
else:
    st.info("📭 Aucun document indexé. Téléchargez votre premier document ci-dessus!")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.caption("💡 **Astuce:** Les documents sélectionnés dans la sidebar seront utilisés comme contexte RAG dans le tuteur interactif. Assurez-vous de sélectionner les documents pertinents pour votre conversation!")

