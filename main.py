import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🧠 PFE - Système de Feedback Pédagogique",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit's default navigation elements
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        div[data-testid="stToolbar"] {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .project-description {
        font-size: 1.2rem;
        line-height: 1.8;
        color: #2c3e50;
        text-align: justify;
        margin-bottom: 2rem;
        padding: 0 2rem;
    }
    .feature-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
    }
    .feature-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .feature-list {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .tech-stack {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
    }
    .footer {
        text-align: center;
        color: #666;
        margin-top: 4rem;
        padding: 2rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Système de Feedback Pédagogique</h1>', unsafe_allow_html=True)
    
    # Project Description - Clean and Modern
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #1f77b4; font-size: 2rem; margin-bottom: 1.5rem;">🚀 Révolutionnez l'Éducation avec l'IA</h2>
        <p style="font-size: 1.3rem; color: #2c3e50; margin-bottom: 1rem; font-weight: 500;">
            Un système intelligent qui transforme l'évaluation pédagogique
        </p>
        <p style="font-size: 1.1rem; color: #666; line-height: 1.6; max-width: 800px; margin: 0 auto;">
            Analyse automatique des réponses • Feedback personnalisé • Amélioration continue
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; color: white;">
        <h2 style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem; text-align: center; color: white;">🚀 Fonctionnalités Principales</h2>
        <div style="font-size: 1.1rem; line-height: 1.6;">
            <ul style="color: white;">
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📊 Exploration des Données :</strong> Visualisation interactive du dataset et statistiques détaillées</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>🔍 Classification Intelligente :</strong> Analyse automatique de la qualité des réponses avec CamemBERT fine-tuné</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>💬 Génération de Feedback :</strong> Commentaires personnalisés générés par des LLMs avancés (GPT-4, Groq, etc.)</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📈 Métriques d'Évaluation :</strong> BLEU, ROUGE, BERTScore et autres indicateurs de qualité</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📝 Création d'Examens :</strong> Génération intelligente d'examens avec questions uniques groupées par cours</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📝 Passage d'Examens :</strong> Interface interactive pour passer des examens avec timer et feedback automatique</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>💬 Tuteur IA Interactif :</strong> Assistant virtuel intelligent pour aide personnalisée en mathématiques</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technical Stack
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; color: white;">
        <h2 style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem; text-align: center; color: white;">🛠️ Stack Technique</h2>
        <div style="font-size: 1.1rem; line-height: 1.6;">
            <ul style="color: white;">
                <li style="margin-bottom: 0.8rem; color: white;"><strong>🤖 Intelligence Artificielle :</strong> CamemBERT, GPT-4, Llama, FlauBERT</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>🐍 Backend :</strong> Python, Streamlit, Transformers, PyTorch</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📊 Données :</strong> 2,400+ exemples de questions/réponses étiquetées</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>🎯 Métriques :</strong> BLEU, ROUGE, BERTScore, Accuracy, F1-Score</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>☁️ Déploiement :</strong> Docker, Streamlit Cloud</li>
                <li style="margin-bottom: 0.8rem; color: white;"><strong>📚 Langues :</strong> Optimisé pour le français (mathématiques niveau lycée/collège)</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Impact Section
    st.markdown('<div class="project-description">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #1f77b4; margin-bottom: 1.5rem;">🎯 Impact Pédagogique</h2>', unsafe_allow_html=True)
    
    st.markdown("**Notre système révolutionne l'évaluation formative en proposant :**")
    
    st.markdown("""
    - **⚡ Feedback Instantané :** Évaluation et commentaires en temps réel
    - **🎯 Personnalisation :** Adaptation aux besoins spécifiques de chaque élève
    - **📈 Amélioration Continue :** Suggestions d'amélioration constructives et motivantes
    - **⏰ Gain de Temps :** Automatisation des tâches répétitives pour les enseignants
    - **🔬 Objectivité :** Évaluation cohérente et non-biaisée
    - **📚 Apprentissage Adaptatif :** Identification des lacunes et points forts
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    
    st.markdown("**🧠 Système de Feedback Pédagogique Intelligent**")
    st.markdown("Projet de Fin d'Études - Développé avec ❤️ en Python & Streamlit")
    
    st.markdown("""
    Cette application démontre l'utilisation avancée de l'IA dans le domaine éducatif, 
    combinant machine learning, traitement du langage naturel et méthodologies pédagogiques.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()