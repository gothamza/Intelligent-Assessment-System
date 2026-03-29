import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(page_title="Classification de Réponses", layout="wide")

st.title("🔍 Classification de Qualité des Réponses")
st.markdown("**Classification avec LLM (Groq)** - Analyse automatique de la qualité des réponses d'élèves")

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

# ============================================================================
# LLM Classification Function
# ============================================================================

def classify_with_llm(question, answer):
    """Classify answer quality using LLM. Returns dict with label and reasoning."""
    try:
        import os
        from langchain_groq import ChatGroq
        from langchain.prompts import ChatPromptTemplate
        
        # Check for API keys
        groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY2") or os.getenv("GROQ_API_KEY3")
        
        if not groq_key:
            return {
                "label": "Erreur",
                "score": 0.0,
                "reasoning": "Aucune clé API Groq trouvée. Configurez GROQ_API_KEY dans .env"
            }
        
        # Initialize LLM
        llm = ChatGroq(
            temperature=0.1,
            groq_api_key=groq_key,
            model_name="llama-3.3-70b-versatile"
        )
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en évaluation pédagogique. 
Analyse la réponse de l'élève et classe sa qualité en 3 catégories:
- Correcte: Réponse mathématiquement exacte et complète
- Partielle: Réponse avec des éléments corrects mais incomplète ou partiellement incorrecte
- Incorrecte: Réponse fausse ou complètement hors sujet

Réponds UNIQUEMENT avec ce format JSON:
{"label": "Correcte/Partielle/Incorrecte", "reasoning": "Explication courte de ton évaluation"}"""),
            ("human", "Question: {question}\n\nRéponse de l'élève: {answer}")
        ])
        
        # Get response
        chain = prompt | llm
        response = chain.invoke({"question": question, "answer": answer})
        
        # Parse JSON response
        result_text = response.content.strip()
        
        # Extract JSON if wrapped in code blocks
        if "```" in result_text:
            result_text = result_text.split("```")[1].replace("json", "").strip()
        
        result = json.loads(result_text)
        
        # Map to score for display
        label_to_score = {"Correcte": 0.95, "Partielle": 0.75, "Incorrecte": 0.15}
        result["score"] = label_to_score.get(result.get("label", "Incorrecte"), 0.5)
        
        return result
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract label from text
        result_text = response.content if 'response' in locals() else str(e)
        label = "Incorrecte"
        if "correcte" in result_text.lower() and "partielle" not in result_text.lower():
            label = "Correcte"
        elif "partielle" in result_text.lower():
            label = "Partielle"
        
        return {
            "label": label,
            "score": label_to_score.get(label, 0.5),
            "reasoning": result_text[:200] if len(result_text) > 200 else result_text
        }
    except Exception as e:
        return {
            "label": "Erreur",
            "score": 0.0,
            "reasoning": f"Erreur: {str(e)}"
        }

# ============================================================================
# Tabs for classification modes
# ============================================================================

st.markdown("---")
st.markdown("""
### 🎯 **Modes de classification disponibles**

- **📝 Classification Manuelle:** Saisissez une question et une réponse pour obtenir une prédiction en temps réel
- **📚 Exemples Prédéfinis:** Testez avec des exemples intégrés dans l'application
- **📊 Classification par Lot (CSV):** Téléchargez un fichier CSV pour classifier plusieurs paires Q&A
""")

tab1, tab2, tab3 = st.tabs(["📝 Classification Manuelle", "📚 Exemples Prédéfinis", "📊 Classification par Lot (CSV)"])

# ============================================================================
# TAB 1: Manual Classification
# ============================================================================
with tab1:
    st.header("📝 Classification Manuelle")
    st.markdown("Entrez une question et la réponse d'un élève pour obtenir une évaluation automatique de la qualité.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question_input = st.text_area(
            "🔹 Question:",
            placeholder="Ex: Qu'est-ce qu'une médiatrice ?",
            height=120,
            key="manual_question"
        )
    
    with col2:
        answer_input = st.text_area(
            "🔹 Réponse de l'élève:",
            placeholder="Ex: Une médiatrice est une droite qui passe par le milieu d'un segment...",
            height=120,
            key="manual_answer"
        )
    
    if st.button("🔍 Classifier la Réponse", type="primary", use_container_width=True):
        if not question_input or not answer_input:
            st.warning("⚠️ Veuillez saisir à la fois une question et une réponse.")
        else:
            st.markdown("---")
            st.subheader("📊 Résultat de Classification")
            
            with st.spinner("🔄 Classification avec LLM..."):
                result = classify_with_llm(question_input, answer_input)
            
            if 'error' in result or result.get('label') == 'Erreur':
                st.error(f"❌ {result.get('reasoning', 'Erreur inconnue')}")
            else:
                label = result['label']
                score = result['score']
                reasoning = result.get('reasoning', '')
                
                # Display label
                if label == "Correcte":
                    st.success(f"**✅ {label}**")
                elif label == "Partielle":
                    st.warning(f"**⚠️ {label}**")
                elif label == "Incorrecte":
                    st.error(f"**❌ {label}**")
                else:
                    st.info(f"**{label}**")
                
                # Display score
                st.metric("Confiance", f"{score:.2%}")
                st.progress(score)
                
                # Display reasoning
                if reasoning:
                    st.markdown("**💡 Raisonnement:**")
                    st.info(reasoning)

# ============================================================================
# TAB 2: Predefined Examples
# ============================================================================
with tab2:
    st.header("📚 Exemples Prédéfinis")
    st.markdown("Testez la classification avec des exemples prédéfinis.")
    
    examples = [
        {
            "question": "Qu'est-ce qu'une médiatrice ?",
            "answer": "Une médiatrice est une droite qui passe par le milieu d'un segment et qui est perpendiculaire à ce segment.",
            "expected": "Correcte"
        },
        {
            "question": "Résoudre: 2x + 5 = 13",
            "answer": "x = 4",
            "expected": "Correcte"
        },
        {
            "question": "Qu'est-ce qu'un triangle rectangle ?",
            "answer": "Un triangle avec un angle droit, mais je ne me souviens plus de la formule de Pythagore.",
            "expected": "Partielle"
        },
        {
            "question": "Calculer l'aire d'un cercle de rayon 5 cm",
            "answer": "L'aire est 25 cm²",
            "expected": "Partielle"
        },
        {
            "question": "Qu'est-ce qu'une fonction ?",
            "answer": "C'est quelque chose qui fait des calculs en informatique.",
            "expected": "Incorrecte"
        }
    ]
    
    selected_example = st.selectbox(
        "Choisissez un exemple:",
        options=range(len(examples)),
        format_func=lambda x: f"{x+1}. {examples[x]['question'][:50]}..."
    )
    
    example = examples[selected_example]
    
    st.markdown("**Question:**")
    st.info(example['question'])
    
    st.markdown("**Réponse de l'élève:**")
    st.info(example['answer'])
    
    st.markdown("**Label attendu:**")
    if example['expected'] == "Correcte":
        st.success(f"✅ {example['expected']}")
    elif example['expected'] == "Partielle":
        st.warning(f"⚠️ {example['expected']}")
    else:
        st.error(f"❌ {example['expected']}")
    
    if st.button("🔍 Classifier cet exemple", type="primary"):
        with st.spinner("🔄 Classification avec LLM..."):
            result = classify_with_llm(example['question'], example['answer'])
        
        st.markdown("---")
        st.subheader("📊 Résultat")
        
        label = result['label']
        score = result['score']
        reasoning = result.get('reasoning', '')
        
        # Display label
        if label == "Correcte":
            st.success(f"**✅ {label}**")
        elif label == "Partielle":
            st.warning(f"**⚠️ {label}**")
        elif label == "Incorrecte":
            st.error(f"**❌ {label}**")
        
        # Check if matches expected
        if label == example['expected']:
            st.success("✅ **Prédiction correcte!**")
        else:
            st.warning(f"⚠️ **Prédiction différente de l'attendu** (Attendu: {example['expected']})")
        
        st.metric("Confiance", f"{score:.2%}")
        st.progress(score)
        
        if reasoning:
            st.markdown("**💡 Raisonnement:**")
            st.info(reasoning)

# ============================================================================
# TAB 3: Batch Classification (CSV)
# ============================================================================
with tab3:
    st.header("📊 Classification par Lot (CSV)")
    st.markdown("Téléchargez un fichier CSV avec des colonnes 'question' et 'reponse' pour classifier plusieurs paires Q&A.")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier CSV",
        type=['csv'],
        help="Le CSV doit contenir les colonnes 'question' et 'reponse'"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Check required columns
            if 'question' not in df.columns or 'reponse' not in df.columns:
                st.error("❌ Le CSV doit contenir les colonnes 'question' et 'reponse'")
            else:
                st.success(f"✅ Fichier chargé: {len(df)} lignes")
                st.dataframe(df.head())
                
                if st.button("🔍 Classifier toutes les réponses", type="primary"):
                    progress_bar = st.progress(0)
                    results = []
                    
                    for idx, row in df.iterrows():
                        result = classify_with_llm(row['question'], row['reponse'])
                        results.append({
                            'question': row['question'],
                            'reponse': row['reponse'],
                            'label_predite': result['label'],
                            'score': result['score'],
                            'reasoning': result.get('reasoning', '')
                        })
                        progress_bar.progress((idx + 1) / len(df))
                    
                    results_df = pd.DataFrame(results)
                    
                    st.markdown("---")
                    st.subheader("📊 Résultats")
                    st.dataframe(results_df)
                    
                    # Summary statistics
                    st.markdown("---")
                    st.subheader("📈 Statistiques")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total", len(results_df))
                    with col2:
                        correct_count = len(results_df[results_df['label_predite'] == 'Correcte'])
                        st.metric("✅ Correctes", correct_count, f"{(correct_count/len(results_df)*100):.1f}%")
                    with col3:
                        partial_count = len(results_df[results_df['label_predite'] == 'Partielle'])
                        st.metric("⚠️ Partielles", partial_count, f"{(partial_count/len(results_df)*100):.1f}%")
                    with col4:
                        incorrect_count = len(results_df[results_df['label_predite'] == 'Incorrecte'])
                        st.metric("❌ Incorrectes", incorrect_count, f"{(incorrect_count/len(results_df)*100):.1f}%")
                    
                    # Download results
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger les résultats (CSV)",
                        data=csv,
                        file_name="classification_results.csv",
                        mime="text/csv"
                    )
                    
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement du fichier: {str(e)}")
