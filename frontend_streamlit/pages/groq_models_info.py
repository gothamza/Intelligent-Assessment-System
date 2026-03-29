import streamlit as st
import pandas as pd

def groq_models_info_page():
    """Page displaying Groq-specific information about the AI models"""
    
    st.title("⚡ Informations Groq - Modèles et Tarification")
    st.markdown("---")
    
    st.markdown("""
    Cette page présente les informations spécifiques à **Groq** pour les modèles disponibles : 
    tarification, vitesse (tokens/seconde), contexte, capacités et statut (production vs déprécié).
    """)
    
    st.markdown("---")
    
    # Main Groq Summary Table
    st.markdown("## 📊 Tableau Récapitulatif Groq")
    
    groq_data = {
        "Modèle": [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "qwen/qwen3-32b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "deepseek-r1-distill-llama-70b"
        ],
        "Paramètres / Type": [
            "~8B (Léger)",
            "~70B (Général)",
            "~32B",
            "~20B",
            "~120B",
            "~70B (Raisonnement)"
        ],
        "Vitesse (TPS)": [
            "~560 TPS",
            "~280 TPS",
            "~660-700 TPS",
            "~1000 TPS ⚡",
            "~500 TPS",
            "~275 TPS"
        ],
        "Tarification (Input/Output)": [
            "$0.05 / $0.08 par 1M tokens",
            "$0.59 / $0.79 par 1M tokens",
            "~$0.29 / ~$0.59 par 1M tokens",
            "$0.075 / $0.30 par 1M tokens",
            "$0.15 / $0.60 par 1M tokens",
            "~$0.75 / ~$0.99 par 1M tokens"
        ],
        "Contexte & Notes": [
            "131K tokens; faible latence & coût-efficace",
            "131K tokens; meilleur modèle général polyvalent",
            "128K+ tokens; fort en instructions & multilingue",
            "Très haute vitesse avec coût relativement bas",
            "Grand modèle open-weight avec forte capacité",
            "128K tokens; fort raisonnement mais DÉPRÉCIÉ"
        ],
        "Statut": [
            "✅ Production",
            "✅ Production",
            "✅ Production",
            "✅ Production",
            "✅ Production",
            "⚠️ Déprécié"
        ]
    }
    
    df_groq = pd.DataFrame(groq_data)
    st.dataframe(df_groq, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Detailed Notes by Model
    st.markdown("## 🔎 Notes Détaillées par Modèle")
    
    # Model 1: llama-3.1-8b-instant
    with st.expander("🦙 llama-3.1-8b-instant", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~560 TPS", "Groq")
        with col2:
            st.metric("Input", "$0.05/1M", "tokens")
        with col3:
            st.metric("Output", "$0.08/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** ~560 tokens/seconde (documentation Groq)
        - **Tarification:** Très basse — **$0.05 input / $0.08 output par million de tokens** 
          (économique pour applications à haut débit)
        - **Contexte:** Fenêtre de contexte de **131K tokens** — excellent pour documents longs, 
          chat en temps réel, filtrage, résumé, etc.
        
        **✅ Idéal pour:**
        - Réponses rapides et économiques
        - Applications nécessitant un haut débit
        - Tâches où le raisonnement ultra-élevé n'est pas requis
        - Chat en temps réel
        - Traitement de documents longs
        """)
    
    # Model 2: llama-3.3-70b-versatile
    with st.expander("💡 llama-3.3-70b-versatile (Remplacement pour 3.1-70b)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~280 TPS", "Groq")
        with col2:
            st.metric("Input", "$0.59/1M", "tokens")
        with col3:
            st.metric("Output", "$0.79/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** ~280 TPS sur Groq
        - **Tarification:** **$0.59 input / $0.79 output par million de tokens** — milieu de gamme
        - **Contexte:** 131K tokens, support de sortie plus large (~32K max)
        
        **✅ Idéal pour:**
        - Tâches à usage général nécessitant un grand modèle capable
        - Génération de contenu complexe
        - Raisonnement avancé
        - Meilleur modèle général polyvalent sur Groq actuellement
        """)
    
    # Model 3: qwen/qwen3-32b
    with st.expander("🌐 qwen/qwen3-32b", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~660-700 TPS", "Groq")
        with col2:
            st.metric("Input", "~$0.29/1M", "tokens")
        with col3:
            st.metric("Output", "~$0.59/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** ~660-700 TPS (approximatif depuis la page de tarification)
        - **Tarification:** ~$0.29 / ~$0.59 par 1M tokens — performance/coût équilibré
        - **Contexte:** Support de **~128K tokens**
        
        **✅ Points forts:**
        - Excellent pour le suivi d'instructions
        - Tâches multilingues
        - Charges de travail IA générales
        - Bon équilibre vitesse/performance
        """)
    
    # Model 4: openai/gpt-oss-20b
    with st.expander("🚀 openai/gpt-oss-20b", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~1000 TPS ⚡", "Plus rapide sur Groq")
        with col2:
            st.metric("Input", "$0.075/1M", "tokens")
        with col3:
            st.metric("Output", "$0.30/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** **~1000 TPS — le plus rapide sur Groq actuellement** parmi les modèles principaux
        - **Tarification:** **$0.075 / $0.30 par 1M tokens** — faible latence + coût raisonnable
        
        **✅ Idéal pour:**
        - Environnements à haut débit où la latence est importante
        - Applications nécessitant des réponses ultra-rapides
        - Traitement en temps réel
        - Modèle de poids modéré avec excellente vitesse
        """)
    
    # Model 5: openai/gpt-oss-120b
    with st.expander("🧠 openai/gpt-oss-120b", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~500 TPS", "Groq")
        with col2:
            st.metric("Input", "$0.15/1M", "tokens")
        with col3:
            st.metric("Output", "$0.60/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** ~500 TPS
        - **Tarification:** **$0.15 / $0.60 par 1M tokens** — modèle plus lourd à coût plus élevé 
          mais capacité plus forte
        
        **✅ Idéal pour:**
        - Raisonnement complexe
        - Contenu long format
        - Tâches nécessitant une grande mémoire
        - Applications nécessitant la plus haute capacité
        """)
    
    # Model 6: deepseek-r1-distill-llama-70b (Deprecated)
    with st.expander("📉 deepseek-r1-distill-llama-70b (DÉPRÉCIÉ)", expanded=False):
        st.warning("⚠️ **Ce modèle est déprécié sur Groq depuis Oct 2025** — remplacé par des modèles plus récents.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitesse", "~275 TPS", "Ancien")
        with col2:
            st.metric("Input", "~$0.75/1M", "tokens")
        with col3:
            st.metric("Output", "~$0.99/1M", "tokens")
        
        st.markdown("""
        **📊 Caractéristiques:**
        - **Vitesse:** ~275 TPS (ancienne page de tarification)
        - **Tarification:** ~$0.75 / ~$0.99 par 1M tokens (coût plus élevé)
        - **Contexte:** 128K tokens
        - **Statut:** **Déprécié sur Groq** — remplacé par des modèles plus récents comme 
          *llama-3.3-70b-versatile* ou *gpt-oss-120b*
        
        **⚠️ Note:**
        C'était un distill spécialisé en raisonnement mais n'est plus suggéré pour de nouveaux déploiements.
        Utilisez plutôt **llama-3.3-70b-versatile** ou **gpt-oss-120b** pour des capacités similaires ou supérieures.
        """)
    
    st.markdown("---")
    
    # Context Window Summary
    st.markdown("## 📏 Résumé des Fenêtres de Contexte")
    
    context_data = {
        "Modèle": [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "qwen3-32b",
            "gpt-oss-20b",
            "gpt-oss-120b"
        ],
        "Fenêtre de Contexte": [
            "~128K tokens",
            "~128K tokens",
            "~128K tokens",
            "~128K tokens",
            "~128K tokens"
        ]
    }
    
    df_context = pd.DataFrame(context_data)
    st.dataframe(df_context, use_container_width=True, hide_index=True)
    
    st.info("💡 **Note:** Tous les modèles supportent une fenêtre de contexte d'environ **128K tokens**, permettant le traitement de documents très longs.")
    
    st.markdown("---")
    
    # Pricing Information
    st.markdown("## 💰 Comment Fonctionne la Tarification sur Groq")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💳 Facturation basée sur les tokens:**
        - Vous payez par **1M tokens** d'entrées et de sorties **séparément**
        - Les modèles à **TPS plus élevé** comme **gpt-oss-20b** offrent un débit plus rapide 
          mais la tarification par token varie
        
        **⚖️ Compromis contexte et débit:**
        - Modèles plus petits/rapides = TPS plus élevé et tokens moins chers
        - Grands modèles = plus lents et plus chers mais plus capables
        """)
    
    with col2:
        st.markdown("""
        **📊 Exemple de coût:**
        - **llama-3.1-8b-instant:** 
          - 1M tokens input = $0.05
          - 1M tokens output = $0.08
          - **Total pour 1M+1M = $0.13**
        
        - **gpt-oss-20b:**
          - 1M tokens input = $0.075
          - 1M tokens output = $0.30
          - **Total pour 1M+1M = $0.375**
        """)
    
    st.markdown("---")
    
    # Rate Limits
    st.markdown("## 🚦 Limites de Débit & Notes API")
    
    st.markdown("""
    Les limites de débit (tokens/minute, requêtes/minute) dépendent de votre plan :
    - Les plans **Developer** offrent des quotas plus élevés
    - Vérifiez les limites de débit de l'API Groq dans votre compte pour les valeurs exactes
    - Les limites peuvent varier selon le modèle utilisé
    """)
    
    st.markdown("---")
    
    # Best Uses Summary
    st.markdown("## 📝 Résumé - Meilleures Utilisations")
    
    best_uses_data = {
        "Objectif": [
            "Réponses ultra-rapides",
            "Coût bas / haut débit",
            "Grand contexte & tâches générales",
            "Performance équilibrée haute performance",
            "(Déprécié) Raisonnement spécifique"
        ],
        "Meilleur Modèle sur Groq": [
            "`openai/gpt-oss-20b`",
            "`llama-3.1-8b-instant`",
            "`llama-3.3-70b-versatile`, `gpt-oss-120b`",
            "`qwen/qwen3-32b`",
            "`deepseek-r1-distill-llama-70b` remplacé maintenant"
        ]
    }
    
    df_best_uses = pd.DataFrame(best_uses_data)
    st.dataframe(df_best_uses, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Speed Comparison Chart
    st.markdown("## ⚡ Comparaison de Vitesse")
    
    speed_comparison = {
        "Modèle": [
            "gpt-oss-20b",
            "qwen3-32b",
            "llama-3.1-8b-instant",
            "gpt-oss-120b",
            "llama-3.3-70b-versatile",
            "deepseek-r1-distill-llama-70b"
        ],
        "TPS (Tokens/Second)": [
            1000,
            680,
            560,
            500,
            280,
            275
        ]
    }
    
    df_speed = pd.DataFrame(speed_comparison)
    st.bar_chart(df_speed.set_index("Modèle"))
    
    st.markdown("---")
    
    # Cost Comparison
    st.markdown("## 💵 Comparaison des Coûts (Input + Output pour 1M+1M tokens)")
    
    cost_data = {
        "Modèle": [
            "llama-3.1-8b-instant",
            "gpt-oss-20b",
            "qwen3-32b",
            "gpt-oss-120b",
            "llama-3.3-70b-versatile",
            "deepseek-r1-distill-llama-70b"
        ],
        "Coût Total (1M+1M)": [
            "$0.13",
            "$0.375",
            "$0.88",
            "$0.75",
            "$1.38",
            "$1.74"
        ],
        "Rang Coût": [
            "1️⃣ Le moins cher",
            "2️⃣ Très économique",
            "3️⃣ Milieu de gamme",
            "4️⃣ Milieu de gamme",
            "5️⃣ Plus cher",
            "6️⃣ Le plus cher (déprécié)"
        ]
    }
    
    df_cost = pd.DataFrame(cost_data)
    st.dataframe(df_cost, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;padding:20px;background-color:#f0f0f0;border-radius:10px;margin-top:30px;">
        <p style="color:#666;margin:0;font-size:0.9em;">
            <strong>Sources:</strong> Groq Pricing, GroqCloud Documentation, Groq Console | 
            Dernière mise à jour: 2024-2025
        </p>
        <p style="color:#999;margin-top:5px;font-size:0.85em;">
            ⚠️ Les tarifs et spécifications peuvent changer. Vérifiez la documentation officielle Groq pour les informations les plus récentes.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    groq_models_info_page()

