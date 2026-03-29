import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Add services to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import API client
from services.api_client import APIClient

st.set_page_config(page_title="Tuteur Interactif", layout="wide", page_icon="💬")

# Custom CSS for sticky input and scrollable chat
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 10px 0;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

def get_subjects_by_level(niveau):
    """Get available subjects based on the educational level"""
    niveau_lower = niveau.lower()
    
    if "7ème" in niveau_lower or "8ème" in niveau_lower:
        # Collège - Niveaux débutants
        return [
            "Arithmétique", "Géométrie de base", "Fractions", "Pourcentages", 
            "Unités de mesure", "Symétrie", "Angles"
        ]
    elif "9ème" in niveau_lower:
        # Collège - Niveau intermédiaire
        return [
            "Algèbre de base", "Géométrie", "Fonctions linéaires", "Probabilités simples",
            "Statistiques de base", "Théorème de Pythagore", "Trigonométrie de base"
        ]
    elif "10ème" in niveau_lower or "11ème" in niveau_lower:
        # Lycée - Niveau avancé
        return [
            "Algèbre avancée", "Géométrie analytique", "Fonctions", "Trigonométrie",
            "Probabilités", "Statistiques", "Calcul différentiel", "Suites numériques"
        ]
    elif "12ème" in niveau_lower:
        # Terminale - Niveau expert
        return [
            "Calcul intégral", "Géométrie dans l'espace", "Fonctions exponentielles", 
            "Fonctions logarithmiques", "Nombres complexes", "Probabilités conditionnelles",
            "Statistiques inférentielles", "Équations différentielles"
        ]
    else:
        # Par défaut - tous les sujets
        return [
            "Algèbre", "Géométrie", "Fonctions", "Trigonométrie", "Probabilités", 
            "Statistiques", "Calcul", "Arithmétique"
        ]

def format_exercise_content(content):
    """Format exercise content for better display"""
    import re
    
    # Remove any <think> tags that might have slipped through
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    
    if "📚 **Exercice:**" in content:
        exercise_content = content.split("📚 **Exercice:**\n\n", 1)[1] if "📚 **Exercice:**\n\n" in content else content
        
        # Add better formatting
        formatted = f"""
### 📚 Exercice

{exercise_content}

---
💡 **Conseil:** Essayez de résoudre l'exercice étape par étape. Si vous avez besoin d'aide, demandez un indice !
        """
        return formatted.strip()
    elif "❓ **Question:**" in content:
        question_content = content.split("❓ **Question:**\n\n", 1)[1] if "❓ **Question:**\n\n" in content else content
        
        # Add better formatting for questions
        formatted = f"""
### ❓ Question

{question_content}

---
💭 **Réfléchissez:** Prenez votre temps pour analyser la question. Vous pouvez demander un indice si nécessaire !
        """
        return formatted.strip()
    return content

def save_chat_history(messages):
    """Save last 20 messages to session and JSON"""
    st.session_state.chat_history = messages[-20:]
    
    try:
        data_dir = Path("Data")
        data_dir.mkdir(exist_ok=True)
        
        history_file = data_dir / "chat_history.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.chat_history
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")

# ============================================================================
# Initialize Session State
# ============================================================================

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_client' not in st.session_state:
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    st.session_state.api_client = APIClient(base_url=api_base_url)

if 'stats' not in st.session_state:
    st.session_state.stats = {
        "total_questions": 0,
        "correct": 0,
        "partial": 0,
        "incorrect": 0
    }

# ============================================================================
# Main UI
# ============================================================================

st.title("💬 Tuteur Interactif de Mathématiques")

st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
    <h3 style='color: white; margin: 0;'>🎓 Agent Tuteur Intelligent (ReAct)</h3>
    <p style='margin: 10px 0 0 0;'>
        Assistant IA avec accès à des outils spécialisés : génération de questions, 
        classification, feedback personnalisé et exercices de remédiation.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar: Configuration & Stats
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Level selection (moved up to influence subjects)
    niveau = st.selectbox(
        "🎯 Niveau:",
        ["7ème année", "8ème année", "9ème année", "10ème année", "11ème année", "12ème année"]
    )
    
    # Subject selection (now dynamic based on level)
    available_subjects = get_subjects_by_level(niveau)
    topic = st.selectbox(
        "📚 Sujet:",
        available_subjects,
        help=f"Sujets adaptés au niveau {niveau}"
    )
    
    # Show level-specific info
    st.info(f"🎯 **Niveau {niveau}**\n\n📚 {len(available_subjects)} sujets disponibles")
    
    # Difficulty
    difficulty = st.select_slider(
        "📊 Difficulté:",
        options=["Facile", "Moyen", "Difficile"],
        value="Moyen"
    )
    
    # Custom instructions
    st.markdown("---")
    st.markdown("**📝 Instructions Personnalisées (Optionnel)**")
    custom_instructions = st.text_area(
        "Ajoutez des instructions spécifiques:",
        placeholder="Ex: Utilise des nombres décimaux, inclus des graphiques, explique avec des exemples de la vie réelle...",
        height=100,
        help="Ces instructions seront prises en compte lors de la génération de questions, exercices et cours"
    )
    
    st.markdown("---")
    
    # Backend status
    st.header("🤖 Backend Status")
    try:
        health = st.session_state.api_client.health_check()
        st.success("✅ Backend connecté")
    except Exception as e:
        st.error(f"❌ Erreur de connexion: {str(e)}")
        st.info("💡 Assurez-vous que le backend FastAPI est en cours d'exécution")
    
    st.markdown("---")
    
    # Statistics
    st.header("📈 Statistiques")
    
    # Try to sync stats from backend
    try:
        backend_stats = st.session_state.api_client.get_stats()
        st.session_state.stats = backend_stats
    except:
        pass
    
    total = st.session_state.stats["total_questions"]
    if total > 0:
        correct_pct = (st.session_state.stats["correct"] / total) * 100
        
        st.metric("Questions", total)
        st.metric("✅ Correctes", f"{st.session_state.stats['correct']} ({correct_pct:.0f}%)")
        st.metric("⚠️ Partielles", f"{st.session_state.stats['partial']}")
        st.metric("❌ Incorrectes", f"{st.session_state.stats['incorrect']}")
    else:
        st.info("Aucune statistique")
    
    st.markdown("---")
    
    # Actions
    st.header("🎮 Actions")
    
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    if st.button("📊 Reset Stats", use_container_width=True):
        try:
            st.session_state.api_client.reset_stats()
            st.session_state.stats = {
                "total_questions": 0,
                "correct": 0,
                "partial": 0,
                "incorrect": 0
            }
            st.success("Statistiques réinitialisées")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        st.rerun()

# ============================================================================
# Chat Display
# ============================================================================

st.subheader("💬 Conversation")

# Show selected documents info
selected_doc_ids = st.session_state.get("selected_documents", [])
if selected_doc_ids:
    try:
        all_docs = st.session_state.api_client.list_documents().get("documents", [])
        selected_docs = [doc for doc in all_docs if doc["id"] in selected_doc_ids]
        if selected_docs:
            with st.expander("📚 Documents utilisés comme contexte RAG", expanded=False):
                for doc in selected_docs:
                    st.caption(f"📄 {doc.get('name', 'Unknown')}")
    except:
        pass

chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content'])
                if 'reasoning' in msg and msg['reasoning']:
                    with st.expander("🧠 Raisonnement"):
                        st.write(msg['reasoning'])
                if 'sources' in msg and msg['sources']:
                    with st.expander("📚 Sources RAG"):
                        for i, source in enumerate(msg['sources'], 1):
                            st.markdown(f"**Source {i}:** {source.get('document_name', 'Unknown')}")
                            if source.get('relevance_score'):
                                st.caption(f"Pertinence: {source['relevance_score']:.2%}")

st.markdown("---")

# ============================================================================
# Quick Action Buttons (Pre-filled prompts)
# ============================================================================

st.markdown("**🎯 Actions Rapides:**")

# Quick Action Buttons - Optimized for best UX
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("❓ Nouvelle Question", use_container_width=True, type="primary"):
        try:
            with st.spinner("🤖 Génération d'une question..."):
                question = st.session_state.api_client.generate_question(
                    context={"topic": topic, "niveau": niveau, "difficulty": difficulty, "custom_instructions": custom_instructions}
                )
                response = f"📝 **Question ({topic} - {niveau}):**\n\n{question}"
                
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": f"Génère-moi une question de {topic}",
                    "timestamp": datetime.now().isoformat()
                })
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                save_chat_history(st.session_state.chat_history)
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

with col2:
    if st.button("💡 Besoin d'un Indice?", use_container_width=True):
        if st.session_state.chat_history:
            try:
                with st.spinner("🤖 Génération d'un indice..."):
                    # Find last question
                    last_question = None
                    for msg in reversed(st.session_state.chat_history):
                        if msg.get('role') == 'assistant':
                            content = msg['content']
                            if "📝 **Question" in content or "Question (" in content:
                                lines = content.split('\n')
                                for line in lines:
                                    line = line.strip()
                                    if line and "?" in line and not line.startswith('📝') and not line.startswith('**') and not line.startswith('#') and not line.startswith('💡'):
                                        last_question = line
                                        break
                                if last_question:
                                    break
                    
                    if last_question:
                        hint = st.session_state.api_client.generate_hint(
                            question=last_question,
                            context={"topic": topic, "niveau": niveau, "custom_instructions": custom_instructions}
                        )
                        response = f"💡 **Indice:**\n\n{hint}"
                        
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        save_chat_history(st.session_state.chat_history)
                        st.rerun()
                    else:
                        st.warning("❌ Aucune question active. Génère d'abord une question en cliquant sur '❓ Nouvelle Question'!")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
        else:
            st.warning("❌ Aucune question active. Génère d'abord une question!")

with col3:
    if st.button("📚 Exercice + Solution", use_container_width=True, type="secondary"):
        try:
            with st.spinner("🤖 Génération d'un exercice avec solution..."):
                exercise = st.session_state.api_client.generate_exercise(
                    context={"topic": topic, "niveau": niveau}
                )
                response = f"📚 **Exercice:**\n\n{exercise}"
                
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": f"Génère un exercice de {topic} avec solution",
                    "timestamp": datetime.now().isoformat()
                })
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                save_chat_history(st.session_state.chat_history)
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

with col4:
    if st.button("📚 Cours Complet", use_container_width=True):
        try:
            with st.spinner("🤖 Génération du cours complet (cela peut prendre 10-20s)..."):
                course = st.session_state.api_client.generate_course(
                    context={"topic": topic, "niveau": niveau}
                )
                response = f"📖 **Cours Complet:**\n\n{course}"
                
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": f"Génère un cours complet sur {topic}",
                    "timestamp": datetime.now().isoformat()
                })
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                save_chat_history(st.session_state.chat_history)
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# ============================================================================
# Chat Input (Sticky at bottom)
# ============================================================================

if prompt := st.chat_input("💬 Posez votre question ou donnez votre réponse...", key="chat_input"):
    try:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get selected documents from session state (set in document management page)
        selected_doc_ids = st.session_state.get("selected_documents", [])
        
        # Run agent via API
        with st.spinner("🤖 L'agent réfléchit..."):
            context = {
                "topic": topic,
                "niveau": niveau,
                "difficulty": difficulty,
                "custom_instructions": custom_instructions
            }
            
            # Add document IDs if any are selected
            if selected_doc_ids:
                context["document_ids"] = selected_doc_ids
            
            result = st.session_state.api_client.chat(
                message=prompt,
                context=context,
                chat_history=st.session_state.chat_history[-5:],  # Last 5 messages
                use_rag=len(selected_doc_ids) > 0  # Enable RAG only if documents are selected
            )
            
            response = result["response"]
            reasoning = result.get("reasoning")
            
            # Check if it's an answer to classify and update stats
            if len(st.session_state.chat_history) >= 2:
                prev_msg = st.session_state.chat_history[-2]
                if "?" in prev_msg.get('content', ''):
                    # This might be an answer - update stats via backend
                    try:
                        if "correcte" in response.lower():
                            st.session_state.api_client.update_stats("correct")
                        elif "partielle" in response.lower():
                            st.session_state.api_client.update_stats("partial")
                        elif "incorrecte" in response.lower():
                            st.session_state.api_client.update_stats("incorrect")
                    except:
                        pass
            
            # Add assistant response with reasoning and sources if available
            assistant_msg = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            if reasoning:
                assistant_msg["reasoning"] = reasoning
            if result.get("sources"):
                assistant_msg["sources"] = result["sources"]
            
            st.session_state.chat_history.append(assistant_msg)
            
            save_chat_history(st.session_state.chat_history)
            st.rerun()
    except Exception as e:
        st.error(f"⚠️ Erreur: {str(e)}")
        st.info("💡 Assurez-vous que le backend FastAPI est en cours d'exécution")

# ============================================================================
# Footer
# ============================================================================

st.caption("💡 **Astuce:** Utilisez 'Cours Complet' pour générer un cours structuré avec exercices. Historique: 20 derniers messages.")
