import streamlit as st
import pandas as pd

def models_info_page():
    """Page displaying information about the AI models used in the system"""
    
    st.title("🤖 Modèles d'Intelligence Artificielle")
    st.markdown("---")
    
    st.markdown("""
    Cette page présente les modèles de langage (LLMs) disponibles dans notre système. 
    Ces modèles sont utilisés pour la génération de contenu pédagogique, le feedback automatique, 
    et les interactions avec le tuteur IA.
    """)
    
    st.markdown("---")
    
    # Main Comparison Table
    st.markdown("## 📊 Comparaison des Modèles")
    st.markdown("""
    **Note:** Les benchmarks varient selon les datasets (mathématiques, codage, raisonnement, MMLU, etc.) 
    et les résultats exacts dépendent des paramètres, de la quantification et des conditions d'évaluation. 
    Considérez ceci comme un résumé comparatif approximatif.
    """)
    
    # Create comparison table
    comparison_data = {
        "Modèle": [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "deepseek-r1-distill-llama-70b",
            "qwen/qwen3-32b",
            "gpt-oss-20b",
            "gpt-oss-120b"
        ],
        "Paramètres": [
            "~8B",
            "~70B",
            "~70B",
            "~32B",
            "~20B",
            "~120B"
        ],
        "Mathématiques": [
            "Modeste / Faible",
            "Bon",
            "**94.5% MATH-500** / **86.7% AIME**",
            "~88.7% MATH (Milieu)",
            "Bon, souvent > o3-mini",
            "Très fort"
        ],
        "Codage": [
            "Modeste",
            "Bon",
            "Compétitif (GPQA ~65)",
            "Bon, compétitif",
            "Décent",
            "Fort"
        ],
        "Raisonnement": [
            "Faible-Moyen",
            "Fort",
            "Excellent (GPQA ~57.5)",
            "Indicateurs forts",
            "Moyen",
            "Fort"
        ],
        "Caractéristiques": [
            "Efficace & rapide",
            "Grand contexte, polyvalent",
            "Top pour math & raisonnement",
            "128k contexte, multilingue",
            "Mixture-of-Experts efficace",
            "Top modèle open-weight"
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Detailed Model Information
    st.markdown("## 📋 Détails par Modèle")
    
    # Model 1: llama-3.1-8b-instant
    with st.expander("🦙 llama-3.1-8b-instant", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~8 milliards
            - **Type:** Modèle léger et rapide
            - **Performance Math:** Modeste / Faible
            - **Performance Codage:** Modeste
            - **Performance Raisonnement:** Faible à Moyen
            
            **Avantages:**
            - ⚡ Très rapide et efficace
            - 💰 Coût réduit pour l'inférence
            - 🎯 Idéal pour les tâches en temps réel où la précision maximale n'est pas nécessaire
            
            **Utilisation recommandée:**
            - Conversations simples
            - Génération de contenu basique
            - Tâches nécessitant une réponse rapide
            """)
        with col2:
            st.metric("Paramètres", "8B")
            st.metric("Vitesse", "⭐⭐⭐⭐⭐")
            st.metric("Précision", "⭐⭐⭐")
    
    # Model 2: llama-3.1-70b-versatile
    with st.expander("🦙 llama-3.1-70b-versatile", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~70 milliards
            - **Type:** Modèle polyvalent à grande capacité
            - **Performance Math:** Bon
            - **Performance Codage:** Bon
            - **Performance Raisonnement:** Fort
            
            **Avantages:**
            - 🧠 Grande capacité de contexte
            - 📈 Amélioration générale par rapport au modèle 8B
            - 🎯 Modèle polyvalent à usage général
            - 🔄 Capable de gérer des tâches complexes
            
            **Utilisation recommandée:**
            - Génération d'examens complexes
            - Feedback pédagogique détaillé
            - Raisonnement mathématique avancé
            """)
        with col2:
            st.metric("Paramètres", "70B")
            st.metric("Vitesse", "⭐⭐⭐")
            st.metric("Précision", "⭐⭐⭐⭐")
    
    # Model 3: deepseek-r1-distill-llama-70b
    with st.expander("🧠 deepseek-r1-distill-llama-70b", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~70 milliards
            - **Type:** Modèle distillé spécialisé en mathématiques et raisonnement
            - **Performance Math:** **94.5% MATH-500** / **86.7% AIME** (excellent)
            - **Performance Codage:** Compétitif (GPQA ~65)
            - **Performance Raisonnement:** Excellent (GPQA ~57.5)
            
            **Avantages:**
            - 🏆 **Top performer pour les tests mathématiques**
            - 🧮 Excellente capacité de raisonnement mathématique
            - 🎯 Meilleur parmi les modèles distills pour les tests math
            - 💪 Fort en raisonnement vs de nombreux modèles open-source
            
            **Utilisation recommandée:**
            - Résolution de problèmes mathématiques complexes
            - Génération d'exercices avec raisonnement
            - Feedback sur les erreurs mathématiques
            - Évaluation de réponses mathématiques
            """)
        with col2:
            st.metric("Paramètres", "70B")
            st.metric("Math Score", "94.5%")
            st.metric("Précision", "⭐⭐⭐⭐⭐")
    
    # Model 4: qwen/qwen3-32b
    with st.expander("🌏 qwen/qwen3-32b", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~32 milliards
            - **Type:** Modèle dense avec grand contexte
            - **Performance Math:** ~88.7% MATH (Milieu de gamme)
            - **Performance Codage:** Bon, compétitif
            - **Performance Raisonnement:** Indicateurs forts
            - **Contexte:** 128k tokens
            
            **Avantages:**
            - 🌍 **Forte capacité multilingue**
            - 📏 **Fenêtre de contexte de 128k tokens** (très grande)
            - ⚖️ Équilibre entre vitesse et performance
            - 🎯 Fort sur les tâches de raisonnement
            
            **Utilisation recommandée:**
            - Contenu multilingue (FR, EN, AR)
            - Documents longs nécessitant un grand contexte
            - Génération de cours complets
            - Tâches nécessitant une compréhension contextuelle étendue
            """)
        with col2:
            st.metric("Paramètres", "32B")
            st.metric("Contexte", "128k")
            st.metric("Précision", "⭐⭐⭐⭐")
    
    # Model 5: gpt-oss-20b
    with st.expander("🤖 gpt-oss-20b", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~20 milliards
            - **Type:** Modèle Mixture-of-Experts (MoE) d'OpenAI
            - **Performance Math:** Bon, souvent > o3-mini
            - **Performance Codage:** Décent
            - **Performance Raisonnement:** Moyen
            
            **Avantages:**
            - 🏗️ **Architecture Mixture-of-Experts** - efficacité élevée
            - 💪 Performance forte vs modèles de poids similaire
            - ⚡ Efficace en termes de calcul
            - 🎯 Bon rapport performance/coût
            
            **Utilisation recommandée:**
            - Tâches nécessitant un bon équilibre performance/coût
            - Génération de contenu pédagogique
            - Applications nécessitant une efficacité computationnelle
            """)
        with col2:
            st.metric("Paramètres", "20B")
            st.metric("Efficacité", "⭐⭐⭐⭐")
            st.metric("Précision", "⭐⭐⭐⭐")
    
    # Model 6: gpt-oss-120b
    with st.expander("🤖 gpt-oss-120b", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **Caractéristiques:**
            - **Paramètres:** ~120 milliards
            - **Type:** Top modèle open-weight d'OpenAI
            - **Performance Math:** Très fort, rivalise avec les modèles propriétaires
            - **Performance Codage:** Fort
            - **Performance Raisonnement:** Fort
            
            **Avantages:**
            - 🏆 **Top modèle open-weight d'OpenAI**
            - 💪 Compétitif avec les petits modèles propriétaires
            - 🧠 Très forte capacité de raisonnement
            - 🎯 Performance exceptionnelle sur les benchmarks
            
            **Utilisation recommandée:**
            - Tâches nécessitant la plus haute précision
            - Génération d'examens complexes
            - Feedback pédagogique de qualité supérieure
            - Évaluation approfondie des réponses
            """)
        with col2:
            st.metric("Paramètres", "120B")
            st.metric("Vitesse", "⭐⭐")
            st.metric("Précision", "⭐⭐⭐⭐⭐")
    
    st.markdown("---")
    
    # Summary by Tier
    st.markdown("## 🏆 Classement par Capacité")
    
    tier_data = {
        "Niveau": [
            "Haute Raisonnement & Math",
            "Fort Général & Équilibré",
            "Moyen / Efficace",
            "Rapide / Léger"
        ],
        "Modèles": [
            "deepseek-r1-distill-llama-70b, gpt-oss-120b",
            "qwen3-32b, llama-3.1-70b-versatile",
            "gpt-oss-20b",
            "llama-3.1-8b-instant"
        ]
    }
    
    df_tiers = pd.DataFrame(tier_data)
    st.dataframe(df_tiers, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Highlights Section
    st.markdown("## ✨ Points Clés")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🧮 Raisonnement Mathématique**
        
        - **DeepSeek-R1-Distill-Llama-70B** obtient des scores très élevés: 
          **94.5% MATH-500 et forte performance AIME** — excellent pour les benchmarks mathématiques.
        - **Qwen3-32B** montre également de bons résultats mathématiques (haut-80s) 
          mais légèrement en dessous du modèle distillé 70B dans certaines évaluations.
        - **GPT-OSS modèles**: Les évaluations internes d'OpenAI rapportent une forte 
          performance math/compétition pour les 20B et 120B (surtout 120B).
        """)
    
    with col2:
        st.markdown("""
        **💻 Codage & Résolution de Problèmes**
        
        - DeepSeek distill montre des **scores compétitifs sur les benchmarks de code** 
          vs autres modèles de raisonnement.
        - Qwen3-32B et les modèles GPT-OSS promettent une forte performance générale 
          en codage, souvent comparable aux baselines de modèles open-source communautaires.
        """)
    
    st.markdown("---")
    
    # Efficiency Section
    st.markdown("## ⚡ Efficacité & Utilisation")
    
    efficiency_data = {
        "Modèle": [
            "llama-3.1-8b-instant",
            "gpt-oss-20b / gpt-oss-120b",
            "qwen3-32b"
        ],
        "Avantage": [
            "Vitesse et coût, idéal pour inférence en temps réel",
            "Efficacité Mixture-of-Experts — débit plus élevé par budget de calcul",
            "Équilibre vitesse/performance avec fenêtre de contexte de 128k tokens"
        ]
    }
    
    df_efficiency = pd.DataFrame(efficiency_data)
    st.dataframe(df_efficiency, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Notes & Caveats
    with st.expander("⚠️ Notes & Avertissements", expanded=False):
        st.markdown("""
        - **Les benchmarks varient beaucoup**: De nombreux résultats proviennent de rapports communautaires 
          ou d'affirmations de vendeurs (Groq), pas toujours standardisés tête-à-tête (par ex., différentes 
          qualités de quantification de tokens, fenêtres de contexte, ou tâches).
        - Les modèles comme `llama-3.1-70b-versatile` et `llama-3.1-8b-instant` n'ont pas de scores 
          agrégés publics officiels comme DeepSeek ou GPT-OSS (souvent seulement benchmarks locaux / partiels).
        - Certains modèles peuvent être dépréciés ou remplacés sur Groq (par ex., DeepSeek-R1-Distill-Llama-70B).
        """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;padding:20px;background-color:#f0f0f0;border-radius:10px;margin-top:30px;">
        <p style="color:#666;margin:0;font-size:0.9em;">
            <strong>Sources:</strong> GroqCloud, Markaicode, LLM Stats, OpenAI | 
            Dernière mise à jour: 2024-2025
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    models_info_page()

