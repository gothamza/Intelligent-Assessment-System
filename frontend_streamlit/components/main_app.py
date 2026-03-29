import streamlit as st
import requests
from components.sidebar import sidebar
from components.uploader import uploader
from components.document_list import document_list
from components.document_detail import document_detail
from components.auth import clear_session
from components.auth import fetch_user_info, clear_session , set_token

from components.llm_chat import show_chat, show_rag_chat, show_groq_chat ,display_chat_selector
from components.chats_manager import handle_chat_delete, handle_chat_create, handle_chat_load_failure 
import os

# Removed: prompt_management_ui, prompt_editor_ui, collection_manager
# These features are not needed for the math tutor application

# ────────────────────────────────
# Main application logic
# ────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL")


def show_main_app():
    """Main application interface after successful login"""
    sidebar(on_logout=clear_session)

    view = st.session_state.current_view
    if view == "chat":
        show_chat_ui()
    elif view == "upload":
        uploader()
    elif view == "documents":
        document_list()
    elif view == "doc_detail":
        document_detail()
    elif view == "exam_generation":
        # Import and show exam generation page
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from pages.exam_generation import generate_exam_with_percentages
        generate_exam_with_percentages()
    elif view == "exam_taking":
        # Import and show exam taking page
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from pages.exam_taking import take_exam_page
        take_exam_page()
    elif view == "models_info":
        # Import and show models info page
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from pages.models_info import models_info_page
        models_info_page()
    elif view == "groq_models_info":
        # Import and show Groq models info page
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from pages.groq_models_info import groq_models_info_page
        groq_models_info_page()
    elif view == "diagrams":
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from pages.diagrams import diagrams_page
        diagrams_page()
    else:
        show_home()


# ────────────────────────────────
# Smaller modular functions below
# ────────────────────────────────

def show_chat_ui():
    """Math Tutor Chat Interface"""
    option = st.sidebar.radio(
        "Choose Chat Mode:",
        ("RAG Chat (with Documents)", "Simple Chat")
    )
    if option == "RAG Chat (with Documents)":
        show_rag_chat_ui()
    else:
        show_simple_chat_ui()


def show_simple_chat_ui():
    """Simple chat without RAG"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(f"{BACKEND_URL}/chats/list", params={"chat_type": "llm"}, headers=headers)
    if resp.status_code != 200:
        handle_chat_load_failure()
        return
    chats = resp.json()
    chat_id = display_chat_selector(chats, "simple_chat_selector")
    handle_chat_delete(chat_id, headers)
    handle_chat_create(headers, chat_type="llm")
    if not chat_id:
        st.info("Select or create a chat to begin.")
        return
    show_groq_chat(chat_id=chat_id, prompt="")

def show_rag_chat_ui():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(f"{BACKEND_URL}/chats/list", params={"chat_type": "rag"}, headers=headers)
    if resp.status_code != 200:
        handle_chat_load_failure()
        return

    chats = resp.json()
    chat_id = display_chat_selector(chats, "rag_chat_selector")
    handle_chat_delete(chat_id, headers)
    handle_chat_create(headers, chat_type="rag")
    show_rag_chat(chat_id=chat_id)


# Removed show_groq_chat_ui - now using show_simple_chat_ui

def show_home():
    """Math Tutor Home Page - Projet PFE"""
    
    # Header with project title
    st.markdown("""
    <div style="text-align:center;padding:20px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:15px;margin-bottom:30px;color:white;">
        <h1 style="color:white;margin:0;font-size:2.5em;">🎓 Système de Génération Automatisée de Feedbacks Pédagogiques</h1>
        <p style="font-size:1.2em;margin-top:10px;color:#f0f0f0;">Assistant Intelligent pour l'Enseignement des Mathématiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    if st.session_state.user_info:
        username = st.session_state.user_info.get('sub', st.session_state.user_info.get('username', 'User'))
        st.markdown(f"### 👋 Bienvenue **{username}**!")
    
    st.markdown("---")
    
    # Project Information Section
    st.markdown("## 📋 Informations du Projet")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        **🎓 Étudiant:**  
        Abdelatif Berramou
        
        **🏛️ Université:**  
        Université Ibn Tofail  
        Faculté des Sciences Kénitra
        
        **📚 Niveau:**  
        Master en Informatique et Intelligence Artificielle
        
        **📅 Année Académique:**  
        2024-2025
        """)
    
    with col_info2:
        st.markdown("""
        **👨‍🏫 Superviseur:**  
        Dr. Zineb Goutti
        
        **🎯 Domaine:**  
        Mathématiques (Collège et Lycée)
        
        **🌐 Langues Supportées:**  
        Français, English, العربية
        """)
    
    st.markdown("---")
    
    # Project Description
    st.markdown("## 🎯 Objectif du Projet")
    st.markdown("""
    Ce projet développe un **système automatisé pour générer des feedbacks pédagogiques personnalisés** 
    en mathématiques pour les niveaux collège et lycée. Le système utilise les technologies d'Intelligence 
    Artificielle (NLP, LLMs) pour fournir des retours adaptés et constructifs aux étudiants.
    
    **Problématique principale:**
    Comment adapter et spécialiser des modèles de langage de type Transformer pour la génération contextuelle 
    de texte en français, notamment le résumé automatique et la génération de questions dépendantes du même texte, 
    tout en assurant la cohérence sémantique, la pertinence éducative et l'efficacité computationnelle du modèle ?
    """)
    
    st.markdown("---")
    
    # Theoretical Framework
    st.markdown("## 📖 Cadre Théorique")
    st.markdown("""
    Le projet est basé sur le **modèle de feedback de Hattie & Timperley** (effect size d=0.79), 
    qui démontre que le feedback efficace peut avoir un impact presque double de l'influence moyenne 
    de l'école (d=0.40).
    
    **Le feedback efficace répond à trois questions:**
    - **Feed Up** (Où vais-je ?) - Objectifs d'apprentissage
    - **Feed Back** (Comment je m'en sors ?) - Performance actuelle
    - **Feed Forward** (Où aller ensuite ?) - Prochaines étapes
    
    **Niveaux de feedback:**
    - **Task (FT)** - Feedback sur la tâche
    - **Process (FP)** - Feedback sur le processus
    - **Self-Regulation (FR)** - Feedback sur l'auto-régulation
    - **Self (FS)** - Feedback personnel (souvent contre-productif)
    """)
    
    st.markdown("---")
    
    # Technologies Used
    st.markdown("## 🔧 Technologies Utilisées")
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        **🤖 Intelligence Artificielle:**
        - Llama 3.1 / 3.3 (Groq)
        - Qwen 3-32B (Groq)
        - GPT-OSS 20B / 120B (Groq)
        - Autres modèles Groq compatibles (sélectionnables dans l'application)
        """)
    
    with tech_col2:
        st.markdown("""
        **🔗 Frameworks & Orchestration:**
        - LangChain
        - LangGraph
        - FastAPI (Backend REST API)
        - Streamlit (Frontend)
        """)
    
    with tech_col3:
        st.markdown("""
        **💾 Infrastructure:**
        - PostgreSQL (Base de données)
        - ChromaDB (Vector Store)
        - Docker & Docker Compose
        - Python 3.9+
        """)
    
    st.markdown("---")
    
    # System Architecture
    st.markdown("## 🏗️ Architecture du Système")
    
    with st.expander("📊 Architecture Technique Complète", expanded=False):
        st.markdown("""
        **Architecture Microservices avec Docker:**
        
        **1. Frontend (Streamlit)**
        - Interface utilisateur interactive
        - Gestion des sessions utilisateur
        - Upload et visualisation de documents
        - Chat interactif avec l'IA
        
        **2. Backend (FastAPI)**
        - API REST pour toutes les opérations
        - Authentification JWT
        - Gestion des chats et messages
        - Orchestration LangGraph pour RAG
        - Intégration avec modèles Groq
        
        **3. Base de Données (PostgreSQL)**
        - Stockage des utilisateurs
        - Historique des conversations
        - Métadonnées des documents
        
        **4. Vector Store (ChromaDB)**
        - Indexation vectorielle des documents
        - Recherche sémantique
        - Embeddings multilingues
        
        **5. Processus RAG (Retrieval-Augmented Generation)**
        - Upload de documents (PDF, Word, TXT)
        - Extraction et chunking du texte
        - Indexation dans ChromaDB
        - Recherche sémantique pour contexte
        - Génération de réponses avec contexte
        """)
    
    st.markdown("---")
    
    # Main Features
    st.markdown("## ✨ Fonctionnalités Principales")
    
    feat_col1, feat_col2 = st.columns(2)
    
    with feat_col1:
        st.markdown("""
        **💬 Tuteur IA Interactif**
        - Chat intelligent avec support multilingue (FR, EN, AR)
        - Génération d'exercices personnalisés
        - Création de contenu de cours adapté
        - Support RAG avec documents uploadés
        - Sélection de modèles Groq (Llama, Qwen, etc.)
        - Instructions personnalisées par utilisateur
        
        **📝 Génération d'Examens**
        - Création d'examens personnalisés par niveau
        - Distribution par cours avec pourcentages
        - Support de plusieurs niveaux de difficulté
        - Export en JSON, PDF, Word
        - Support multilingue pour les examens
        """)
    
    with feat_col2:
        st.markdown("""
        **📚 Gestion de Documents**
        - Upload de documents (PDF, Word, TXT)
        - Indexation vectorielle automatique avec ChromaDB
        - Recherche sémantique dans les documents
        - Contexte adaptatif pour les réponses IA
        - Filtrage par document sélectionné
        
        **📊 Évaluation et Feedback**
        - Passage d'examens interactifs
        - Classification automatique des réponses
        - Feedback détaillé par question
        - Feedback global avec suggestions d'amélioration
        - Export des résultats en PDF/Word
        """)
    
    st.markdown("---")
    
    # System Workflow
    st.markdown("## 🔄 Processus du Système")
    
    workflow_col1, workflow_col2 = st.columns(2)
    
    with workflow_col1:
        st.markdown("""
        **Pour les Enseignants:**
        1. 📤 Upload de documents pédagogiques
        2. 📝 Génération d'examens personnalisés
        3. 📊 Suivi des performances des étudiants
        4. 💬 Utilisation du tuteur IA pour créer du contenu
        """)
    
    with workflow_col2:
        st.markdown("""
        **Pour les Étudiants:**
        1. 📄 Passage d'examens interactifs
        2. 📊 Réception de feedback automatique
        3. 💬 Interaction avec le tuteur IA
        4. 📚 Consultation de documents indexés
        """)

    st.markdown("---")
    
    # Quick Actions
    st.markdown("## 🚀 Actions Rapides")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("💬 Tuteur IA", use_container_width=True, type="primary"):
            st.session_state.current_view = "chat" 
            st.rerun()
    
    with action_col2:
        if st.button("📤 Upload Documents", use_container_width=True):
            st.session_state.current_view = "upload"
            st.rerun()
    
    with action_col3:
        if st.button("📝 Créer Examen", use_container_width=True):
            st.session_state.current_view = "exam_generation"
            st.rerun()
    
    with action_col4:
        if st.button("📄 Passer Examen", use_container_width=True):
            st.session_state.current_view = "exam_taking"
            st.rerun()

    st.markdown("---")
    
    # Additional Information
    st.markdown("## 📚 Ressources et Documentation")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        **📖 Modèle de Feedback:**
        - Hattie, J., & Timperley, H. (2007). The Power of Feedback.
        - Effect size: d=0.79 (presque double de l'influence moyenne de l'école)
        
        **🤖 Modèles IA Utilisés:**
        - **Modèles Groq (LLMs hébergés)** pour génération et feedback
          - Llama 3.1 / 3.3 (8B, 70B) : généralistes, multilingues
          - Qwen 3-32B : multilingue, bon raisonnement
          - GPT-OSS 20B / 120B : haute capacité, Mixture-of-Experts
        """)
    
    with info_col2:
        st.markdown("""
        **🏗️ Architecture Technique:**
        - **Backend**: FastAPI avec endpoints REST
        - **Frontend**: Streamlit avec interface interactive
        - **Database**: PostgreSQL pour données structurées
        - **Vector Store**: ChromaDB pour recherche sémantique
        - **Orchestration**: LangChain/LangGraph pour workflows
        
        **📊 Métriques d'Évaluation:**
        - BLEU Score
        - ROUGE Score
        - BERTScore
        - Comparaison avec feedbacks de référence humains
        """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;padding:20px;background-color:#f0f0f0;border-radius:10px;margin-top:30px;">
        <p style="color:#666;margin:0;">
            <strong>Projet de Fin d'Études</strong> | Master en Informatique et IA | Université Ibn Tofail | 2024-2025
        </p>
        <p style="color:#999;margin-top:5px;font-size:0.9em;">
            Développé par Abdelatif Berramou | Supervisé par Dr. Zineb Goutti
        </p>
    </div>
    """, unsafe_allow_html=True)
