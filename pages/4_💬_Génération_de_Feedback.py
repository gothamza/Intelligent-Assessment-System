import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Génération de Feedback", layout="wide")

st.title("💬 Génération de Feedback Pédagogique")

# Sidebar controls: provider and generation params
with st.sidebar:
    st.header("⚙️ Paramètres de Génération")
    temperature = st.slider("Température", 0.0, 1.0, 0.3, 0.05)
    max_tokens = st.slider("Max tokens", 50, 800, 200, 10)
    st.caption("Ajustez la créativité (température) et la longueur de sortie (tokens).")
    
    # API Key Management
    st.header("🔑 Gestion des Clés API")
    use_custom_keys = st.checkbox("Utiliser mes propres clés API", value=False)
    
    custom_api_keys = {}
    if use_custom_keys:
        st.caption("Laissez vide pour utiliser les clés de l'environnement")
        custom_api_keys["groq"] = st.text_input("Clé Groq", type="password", placeholder="gsk_...")
        custom_api_keys["openai"] = st.text_input("Clé OpenAI", type="password", placeholder="sk-...")
        custom_api_keys["openrouter"] = st.text_input("Clé OpenRouter", type="password", placeholder="sk-or-...")
    else:
        st.caption("Utilisation des clés configurées dans .env")

# Simple in-session cache for generated feedbacks
if "feedback_cache" not in st.session_state:
    st.session_state.feedback_cache = {}

# Helper: cached generate with enhanced retry logic
import time
def generate_feedback_with_cache(llm_manager, chain, question_text: str, answer_text: str, cache_key_prefix: str = "default"):
    key = f"{cache_key_prefix}::{question_text[:200]}::{answer_text[:200]}"
    if key in st.session_state.feedback_cache:
        return st.session_state.feedback_cache[key]
    
    # Use the enhanced manager's invoke_with_retry method
    try:
        return_value = llm_manager.invoke_with_retry(chain, {
            "question": question_text,
            "reponse_eleve": answer_text
        })
        st.session_state.feedback_cache[key] = return_value
        return return_value
    except Exception as e:
        st.error(f"❌ Échec de génération après commutation de tous les fournisseurs: {e}")
        raise e

# Check if API keys are available
def check_api_keys():
    groq_key = os.getenv("GROQ_API_KEY2")
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    return {
        "groq": groq_key is not None,
        "openai": openai_key is not None,
        "openrouter": openrouter_key is not None
    }

api_keys = check_api_keys()

if not any(api_keys.values()):
    st.error("""
    ⚠️ **Clés API manquantes**
    
    Pour tester la génération de feedback, vous devez configurer vos clés API dans le fichier `.env`:
    
    ```
    GROQ_API_KEY2=votre_clé_groq
    OPENAI_API_KEY=votre_clé_openai
    OPENROUTER_API_KEY=votre_clé_openrouter
    ```
    """)
    
    # Demo with mock feedback
    st.header("�� Démo avec Feedback Simulé")
    
    sample_feedback = [
        {
            "question": "Calculez l'aire d'un cercle de rayon 5 cm.",
            "answer": "L'aire est 25 cm²",
            "feedback": "Bravo pour avoir identifié la formule de l'aire d'un cercle ! Cependant, tu as oublié le facteur π. L'aire d'un cercle est π × r², donc pour un rayon de 5 cm, l'aire est π × 5² = 25π cm². Peux-tu me rappeler pourquoi on utilise π dans cette formule ?"
        },
        {
            "question": "Résolvez l'équation 2x + 3 = 7",
            "answer": "x = 5",
            "feedback": "Excellent travail pour avoir essayé de résoudre cette équation ! Tu as bien commencé en isolant x, mais il y a une petite erreur dans tes calculs. Souviens-toi : pour isoler x, tu dois d'abord soustraire 3 des deux côtés. Peux-tu refaire le calcul étape par étape ?"
        },
        {
            "question": "Qu'est-ce qu'une médiatrice ?",
            "answer": "C'est une droite qui coupe un segment en deux",
            "feedback": "Tu as raison que la médiatrice coupe le segment en deux, c'est un bon début ! Mais il manque un élément important : la médiatrice doit être perpendiculaire au segment. Peux-tu dessiner un segment et essayer de tracer sa médiatrice ?"
        }
    ]
    
    for i, item in enumerate(sample_feedback, 1):
        with st.expander(f"Exemple {i}: {item['question'][:50]}..."):
            st.write(f"**Question:** {item['question']}")
            st.write(f"**Réponse de l'élève:** {item['answer']}")
            st.write(f"**Feedback généré:** {item['feedback']}")
    
    st.info("💡 **Note:** Ces feedbacks sont simulés. Avec les vrais LLMs, vous obtiendriez des feedbacks personnalisés et contextuels.")

else:
    st.success("✅ Clés API configurées!")
    
    # Initialize enhanced LLM chains with provider switching
    try:
        from enhanced_chains import create_enhanced_llm_manager, create_feedback_chain_enhanced, create_global_summary_chain_enhanced
        
        # Create enhanced LLM manager with custom API keys if provided
        llm_manager = create_enhanced_llm_manager(custom_api_keys if use_custom_keys else None)
        
        # Create feedback chains with enhanced manager
        feedback_chain = create_feedback_chain_enhanced(llm_manager, temperature, max_tokens)
        global_summary_chain = create_global_summary_chain_enhanced(llm_manager, temperature, max_tokens)
        
        st.success("✅ Chaînes de génération avec commutation automatique initialisées!")
        
        # Show current provider in sidebar
        with st.sidebar:
            st.header("🤖 Fournisseur LLM")
            current_provider = llm_manager.providers[llm_manager.current_provider_index]
            st.success(f"**Actuel:** {current_provider['name']}")
            
            # Show all available providers
            st.caption("**Fournisseurs disponibles:**")
            for i, provider in enumerate(llm_manager.providers):
                status = "🟢" if i == llm_manager.current_provider_index else "⚪"
                api_key = llm_manager.get_api_key(provider)
                key_status = "✅" if api_key else "❌"
                st.caption(f"{status} {key_status} {provider['name']}")
            
            if st.button("🔄 Forcer le changement de fournisseur"):
                try:
                    llm_manager.switch_llm()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation des chaînes: {e}")
        st.stop()

    # Prompt editor (optional override)
    st.subheader("🧩 Prompt de Génération (optionnel)")
    with st.expander("Afficher / Modifier le prompt (avancé)", expanded=False):
        default_prompt = (
            "Tu es un professeur de mathématiques bienveillant, patient et encourageant.\n"
            "Ton objectif est de fournir un feedback constructif à un élève qui a fait une erreur.\n\n"
            "**Question :**\n{question}\n\n"
            "**Réponse de l'élève :**\n{reponse_eleve}\n\n"
            "**Instructions :**\n"
            "1. Démarre positivement.\n"
            "2. Identifie l'erreur principale.\n"
            "3. Donne un indice pour corriger.\n"
            "4. 2-3 phrases maximum.\n\n"
            "**Feedback :**"
        )
        if "custom_feedback_prompt" not in st.session_state:
            st.session_state.custom_feedback_prompt = default_prompt
        prompt_text = st.text_area("Prompt", value=st.session_state.custom_feedback_prompt, height=220)
        cols_pe = st.columns([1,1])
        with cols_pe[0]:
            if st.button("✅ Utiliser ce prompt"):
                st.session_state.custom_feedback_prompt = prompt_text
                st.success("Prompt mis à jour.")
        with cols_pe[1]:
            if st.button("↩️ Réinitialiser le prompt"):
                st.session_state.custom_feedback_prompt = default_prompt
                st.rerun()

    # Build override chain if custom prompt changed
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    custom_prompt = PromptTemplate(input_variables=["question", "reponse_eleve"], template=st.session_state.custom_feedback_prompt)
    llm_override = llm_manager.create_llm_with_params(temperature, max_tokens)
    feedback_chain_override = custom_prompt | llm_override | StrOutputParser()

    # Interactive feedback generation
    st.header("🎮 Génération Interactive de Feedback")
    
    # Test mode selection
    test_mode = st.radio(
        "Choisissez le mode de test:",
        ["Génération Manuelle", "Test avec Données d'Exemple", "Génération en Lot"]
    )
    
    if test_mode == "Génération Manuelle":
        st.subheader("✍️ Saisie Manuelle")
        
        question = st.text_area("Entrez la question:", height=100)
        answer = st.text_area("Entrez la réponse de l'élève:", height=150)
        
        if st.button("💬 Générer Feedback") and question and answer:
            with st.spinner("Génération du feedback en cours..."):
                try:
                    feedback = generate_feedback_with_cache(llm_manager, feedback_chain_override, question, answer, cache_key_prefix="manual")
                    
                    st.success("✅ Feedback généré avec succès!")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write("**Question:**")
                        st.write(question)
                        st.write("**Réponse de l'élève:**")
                        st.write(answer)
                    
                    with col2:
                        st.write("**Feedback Pédagogique:**")
                        st.info(feedback)
                        
                        # Download feedback
                        feedback_data = {
                            "question": question,
                            "reponse_eleve": answer,
                            "feedback": feedback,
                            "timestamp": pd.Timestamp.now().isoformat()
                        }
                        
                        st.download_button(
                            label="📥 Télécharger le Feedback",
                            data=json.dumps(feedback_data, ensure_ascii=False, indent=2),
                            file_name="feedback.json",
                            mime="application/json"
                        )
                
                except Exception as e:
                    st.error(f"Erreur lors de la génération: {e}")
    
    elif test_mode == "Test avec Données d'Exemple":
        st.subheader("📊 Test avec Données d'Exemple")
        
        # Load sample data
        @st.cache_data
        def load_feedback_data():
            try:
                csv_path = Path("Data/labeled_qna_dataset.csv")
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    # Filter for incorrect or partially correct answers
                    df_feedback = df[df['label_qualite'] != 0].sample(min(5, len(df)), random_state=42)
                    return df_feedback
                return None
            except:
                return None
        
        sample_df = load_feedback_data()
        
        if sample_df is not None:
            if st.button("�� Choisir un Exemple Aléatoire"):
                st.session_state.feedback_example = sample_df.sample(1).iloc[0]
            
            if 'feedback_example' in st.session_state:
                example = st.session_state.feedback_example
                
                st.write(f"**Question:** {example['question']}")
                st.write(f"**Réponse:** {example['reponse']}")
                
                if st.button("💬 Générer Feedback pour cet Exemple"):
                    with st.spinner("Génération en cours..."):
                        try:
                            feedback = generate_feedback_with_cache(llm_manager, feedback_chain_override, example['question'], example['reponse'], cache_key_prefix="example")
                            
                            st.success("✅ Feedback généré!")
                            st.info(feedback)
                            
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        else:
            st.warning("Aucune donnée d'exemple disponible.")
    
    else:  # Génération en Lot
        st.subheader("📦 Génération en Lot")
        
        # Load data for batch processing
        @st.cache_data
        def load_batch_data():
            try:
                csv_path = Path("Data/labeled_qna_dataset.csv")
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    # Filter for answers needing feedback
                    df_feedback = df[df['label_qualite'] != 0].head(10)  # Limit to 10 for demo
                    return df_feedback
                return None
            except:
                return None
        
        batch_df = load_batch_data()
        
        if batch_df is not None:
            st.write(f"**Données disponibles:** {len(batch_df)} réponses nécessitant un feedback")
            
            # Option to continue on errors
            continue_on_error = st.checkbox("Continuer le traitement même en cas d'erreur", value=False, 
                                          help="Si décoché, le traitement s'arrêtera au premier échec")
            
            if st.button("🚀 Générer Feedback en Lot"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Initialize session state for batch results
                if "batch_feedbacks" not in st.session_state:
                    st.session_state.batch_feedbacks = []
                if "batch_errors" not in st.session_state:
                    st.session_state.batch_errors = []
                
                # Clear previous results
                st.session_state.batch_feedbacks = []
                st.session_state.batch_errors = []
                
                feedbacks = st.session_state.batch_feedbacks
                errors = st.session_state.batch_errors
                
                for i, (idx, row) in enumerate(batch_df.iterrows()):
                    current_provider = llm_manager.providers[llm_manager.current_provider_index]['name']
                    status_text.text(f"Génération du feedback {i+1}/{len(batch_df)}... (Provider: {current_provider})")
                    
                    try:
                        feedback = generate_feedback_with_cache(llm_manager, feedback_chain_override, row['question'], row['reponse'], cache_key_prefix="batch")
                        
                        feedbacks.append({
                            "question": row['question'],
                            "reponse_eleve": row['reponse'],
                            "feedback": feedback,
                            "qualite_originale": row.get('label_qualite', 'N/A')
                        })
                        errors.append("")
                        
                    except Exception as e:
                        err_msg = str(e)
                        
                        # Add the failed item with empty feedback
                        feedbacks.append({
                            "question": row['question'],
                            "reponse_eleve": row['reponse'],
                            "feedback": "",
                            "qualite_originale": row.get('label_qualite', 'N/A')
                        })
                        errors.append(f"ERREUR: {err_msg}")
                        
                        if continue_on_error:
                            st.warning(f"⚠️ Erreur pour l'exemple {i+1}: {err_msg} (continuation...)")
                        else:
                            st.error(f"❌ **Erreur fatale pour l'exemple {i+1}:** {err_msg}")
                            st.error("🛑 **Arrêt du traitement en lot.** Veuillez vérifier vos clés API ou réessayer plus tard.")
                            # Stop processing - don't continue to next question
                            break
                    
                    progress_bar.progress((i + 1) / len(batch_df))
                
                if len(feedbacks) == len(batch_df):
                    status_text.text("✅ Génération terminée avec succès!")
                else:
                    status_text.text(f"⚠️ Génération interrompue après {len(feedbacks)}/{len(batch_df)} éléments")
                
                # Store results in session state for persistence
                st.session_state.batch_feedbacks = feedbacks
                st.session_state.batch_errors = errors
        
        else:
            st.warning("Aucune donnée disponible pour la génération en lot.")
    
    # Display persisted batch results (survives page refresh)
    if "batch_feedbacks" in st.session_state and st.session_state.batch_feedbacks:
        st.subheader("📋 Résultats de la Génération (Persistants)")
        
        # Show results table
        results_df = pd.DataFrame(st.session_state.batch_feedbacks)
        if "batch_errors" in st.session_state:
            results_df["erreur"] = st.session_state.batch_errors
        st.dataframe(results_df.head(50), use_container_width=True)
        
        # Show summary stats
        total_items = len(st.session_state.batch_feedbacks)
        successful_items = len([f for f in st.session_state.batch_feedbacks if f.get('feedback', '').strip()])
        failed_items = total_items - successful_items
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", total_items)
        with col2:
            st.metric("Succès", successful_items)
        with col3:
            st.metric("Échecs", failed_items)
        
        # Generate global summary
        if st.button("📊 Générer Résumé Global"):
            with st.spinner("Génération du résumé global..."):
                try:
                    individual_feedbacks = "\n".join([
                        f"Q: {item['question']}\nR: {item['reponse_eleve']}\nF: {item['feedback']}"
                        for item in st.session_state.batch_feedbacks
                        if item.get('feedback', '').strip()  # Only include successful feedbacks
                    ])
                    
                    if individual_feedbacks:
                        global_summary = global_summary_chain.invoke({
                            "individual_feedbacks": individual_feedbacks
                        })
                        
                        st.success("✅ Résumé global généré!")
                        st.markdown(global_summary)
                    else:
                        st.warning("⚠️ Aucun feedback valide trouvé pour générer le résumé.")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la génération du résumé: {e}")
        
        # Download results
        st.download_button(
            label="📥 Télécharger Tous les Feedbacks",
            data=json.dumps(st.session_state.batch_feedbacks, ensure_ascii=False, indent=2),
            file_name="feedbacks_batch.json",
            mime="application/json"
        )
        
        # Clear results button
        if st.button("🗑️ Effacer les Résultats"):
            st.session_state.batch_feedbacks = []
            st.session_state.batch_errors = []
            st.rerun()

# Feedback generation information
st.header("🤖 Informations sur la Génération de Feedback")

st.markdown("""
**Système de Génération de Feedback Pédagogique**

**Modèles Utilisés:**
- **Groq Llama-3.3-70B:** Modèle principal pour la génération
- **DeepSeek:** Modèle alternatif via OpenRouter

**Caractéristiques du Feedback:**
- ✅ **Encourageant:** Commence toujours par une phrase positive
- 🎯 **Constructif:** Identifie clairement l'erreur
- 💡 **Guidant:** Fournit des indices sans donner la réponse
- 📝 **Concis:** 2-3 phrases maximum
- �� **Pédagogique:** Aide l'élève à comprendre et progresser

**Processus de Génération:**
1. Analyse de la question et de la réponse
2. Identification du type d'erreur
3. Génération de feedback personnalisé
4. Application des règles pédagogiques
5. Validation de la qualité du feedback
""")

# API configuration info
st.header("⚙️ Configuration des APIs")

api_status = {
    "Groq": "✅" if api_keys["groq"] else "❌",
    "OpenAI": "✅" if api_keys["openai"] else "❌", 
    "OpenRouter": "✅" if api_keys["openrouter"] else "❌"
}

for api, status in api_status.items():
    st.write(f"{status} {api}")

st.info("💡 **Conseil:** Utilisez Groq pour de meilleures performances et des coûts réduits.")
