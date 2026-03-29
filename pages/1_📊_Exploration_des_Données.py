import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

st.set_page_config(page_title="Exploration des Données", layout="wide")

st.title("📊 Exploration des Données")
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; color: white;">
    <h2 style="color: white; margin-bottom: 1rem;">🔍 Analyse Complète du Dataset</h2>
    <p style="color: white; font-size: 1.1rem; margin: 0;">
        Exploration approfondie de votre dataset pédagogique avec visualisations interactives et insights détaillés
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Data Loading Functions (NO STREAMLIT CALLS INSIDE!)
# ============================================================================

@st.cache_data
def load_main_dataset():
    """Load the main labeled dataset. Returns (df, path_used, error_msg)"""
    import os
    
    # Get script directory (where this file is located)
    script_dir = Path(__file__).parent.parent  # Go up to project root
    
    # Try multiple possible paths
    possible_paths = [
        script_dir / "Data" / "labeled_qna_dataset.csv",
        Path("Data/labeled_qna_dataset.csv"),
        Path("./Data/labeled_qna_dataset.csv"),
        Path.cwd() / "Data" / "labeled_qna_dataset.csv",
    ]
    
    for csv_path in possible_paths:
        try:
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                return df, str(csv_path), None
        except Exception:
            continue
    
    # If not found, try to find any CSV in Data folder using script_dir
    try:
        data_path = script_dir / "Data"
        if data_path.exists():
            csv_files = list(data_path.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                return df, str(csv_files[0]), None
    except Exception as e:
        pass
    
    # Also try relative to current working directory
    try:
        data_path = Path("Data")
        if data_path.exists():
            csv_files = list(data_path.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                return df, str(csv_files[0]), None
    except:
        pass
    
    # Return debug info
    cwd = os.getcwd()
    paths_tried = "\n".join([f"  - {p} (exists: {p.exists()})" for p in possible_paths])
    return None, None, f"Aucun fichier CSV trouvé.\n\nRépertoire actuel: {cwd}\n\nChemins testés:\n{paths_tried}"

@st.cache_data
def load_json_datasets():
    """Load JSON datasets. Returns dict of datasets"""
    # Get script directory
    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "Data"
    
    # Fallback to relative path if script_dir doesn't work
    if not data_path.exists():
        data_path = Path("Data")
    
    datasets = {}
    
    json_files = [
        "alloprof_college_lycee_qna.json",
        "generated_qna_dataset_first_100_fr.json",
        "etiquetage_100_reponses.json"
    ]
    
    for json_file in json_files:
        try:
            json_path = data_path / json_file
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    datasets[json_file.replace('.json', '')] = json.load(f)
        except Exception:
            pass  # Silently skip failed files
    
    return datasets

# ============================================================================
# Load Data
# ============================================================================

# Load main dataset
df, csv_path, load_error = load_main_dataset()

# File uploader in sidebar
with st.sidebar:
    st.header("📂 Gestion des Données")
    
    uploaded_file = st.file_uploader(
        "📥 Télécharger un nouveau dataset (CSV)",
        type=["csv"],
        help="Chargez un fichier CSV pour remplacer ou comparer avec le dataset principal"
    )
    
    if uploaded_file is not None:
        try:
            # Load uploaded file
            df_uploaded = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Fichier chargé: {uploaded_file.name}")
            st.info(f"📊 {len(df_uploaded)} lignes, {len(df_uploaded.columns)} colonnes")
            
            # Option to use uploaded file
            use_uploaded = st.checkbox("Utiliser ce fichier pour l'analyse", value=True)
            
            if use_uploaded:
                df = df_uploaded
                csv_path = uploaded_file.name
                load_error = None
            
            # Option to save uploaded file
            if st.button("💾 Sauvegarder dans Data/"):
                try:
                    save_path = Path("Data") / uploaded_file.name
                    save_path.parent.mkdir(exist_ok=True)
                    df_uploaded.to_csv(save_path, index=False)
                    st.success(f"✅ Sauvegardé: {save_path}")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur de chargement: {e}")

# Display loading status
if df is not None:
    st.success(f"✅ Dataset chargé: **{len(df)}** lignes depuis `{csv_path}`")
else:
    st.error(f"❌ Impossible de charger le dataset")
    if load_error:
        st.error(f"Erreur: {load_error}")
    st.info("💡 Utilisez le menu latéral pour télécharger un fichier CSV")
    st.stop()

# ============================================================================
# Dataset Overview
# ============================================================================

st.header("📋 Aperçu du Dataset")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Réponses", f"{len(df):,}")

with col2:
    if 'question' in df.columns:
        st.metric("❓ Questions Uniques", f"{df['question'].nunique():,}")
    else:
        st.metric("❓ Questions", "N/A")

with col3:
    if 'niveau' in df.columns:
        st.metric("📚 Niveaux", df['niveau'].nunique())
    else:
        st.metric("📚 Niveaux", "N/A")

with col4:
    if 'label_qualite' in df.columns:
        correct_pct = (df['label_qualite'] == 0).mean() * 100
        st.metric("✅ Correctes", f"{correct_pct:.1f}%")
    else:
        st.metric("✅ Correctes", "N/A")

# Data preview
st.subheader("👀 Aperçu des Données")

# Show column info
st.markdown(f"**Colonnes disponibles:** {', '.join([f'`{col}`' for col in df.columns])}")

# Display first rows
st.dataframe(df.head(10), use_container_width=True)

# ============================================================================
# Data Quality Analysis
# ============================================================================

st.markdown("---")
st.header("🔬 Analyse de la Qualité des Données")

col1, col2 = st.columns(2)

with col1:
    # Missing values
    st.subheader("📉 Valeurs Manquantes")
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df) * 100).round(2)
    
    missing_df = pd.DataFrame({
        'Colonne': missing_data.index,
        'Manquantes': missing_data.values,
        'Pourcentage': missing_pct.values
    })
    missing_df = missing_df[missing_df['Manquantes'] > 0].sort_values('Manquantes', ascending=False)
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("✅ Aucune valeur manquante!")

with col2:
    # Data types
    st.subheader("📊 Types de Données")
    dtypes_df = pd.DataFrame({
        'Colonne': df.dtypes.index,
        'Type': df.dtypes.values.astype(str)
    })
    st.dataframe(dtypes_df, use_container_width=True)

# ============================================================================
# Quality Distribution Analysis
# ============================================================================

if 'label_qualite' in df.columns:
    st.markdown("---")
    st.header("🏷️ Distribution de la Qualité")

    quality_labels = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}
    df_temp = df.copy()
    df_temp['qualite_label'] = df_temp['label_qualite'].map(quality_labels)

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart
        quality_counts = df_temp['qualite_label'].value_counts()

        fig_pie = px.pie(
            values=quality_counts.values,
            names=quality_counts.index,
            title="Répartition des Réponses par Qualité",
            color=quality_counts.index,
            color_discrete_map={
                'Correcte': '#2E8B57',
                'Partielle': '#FFD700',
                'Incorrecte': '#DC143C'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart
        fig_bar = px.bar(
            x=quality_counts.index,
            y=quality_counts.values,
            title="Nombre de Réponses par Qualité",
            labels={'x': 'Qualité', 'y': 'Nombre'},
            color=quality_counts.index,
            color_discrete_map={
                'Correcte': '#2E8B57',
                'Partielle': '#FFD700',
                'Incorrecte': '#DC143C'
            }
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Quality statistics
    st.subheader("📊 Statistiques par Qualité")

    quality_stats = []
    for label, name in quality_labels.items():
        count = (df['label_qualite'] == label).sum()
        pct = count / len(df) * 100 if len(df) > 0 else 0
        quality_stats.append({
            'Qualité': name,
            'Nombre': count,
            'Pourcentage': f"{pct:.1f}%"
        })

    stats_df = pd.DataFrame(quality_stats)
    st.dataframe(stats_df, use_container_width=True)
else:
    st.markdown("---")
    st.info("⚠️ La colonne `label_qualite` est absente du dataset.")

# ============================================================================
# Response Length Analysis
# ============================================================================

if 'reponse' in df.columns:
    st.markdown("---")
    st.header("📏 Analyse de la Longueur des Réponses")

    df_temp = df.copy()
    df_temp['longueur_reponse'] = df_temp['reponse'].astype(str).str.len()
    df_temp['nb_mots'] = df_temp['reponse'].astype(str).str.split().str.len()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Longueur Moyenne", f"{df_temp['longueur_reponse'].mean():.0f} chars")
    with col2:
        st.metric("Mots Moyens", f"{df_temp['nb_mots'].mean():.0f} mots")
    with col3:
        st.metric("Longueur Max", f"{df_temp['longueur_reponse'].max():.0f} chars")

    # Histogram
    fig_len = px.histogram(
        df_temp,
        x='longueur_reponse',
        nbins=30,
        title="Distribution de la Longueur des Réponses (caractères)",
        labels={'longueur_reponse': 'Nombre de caractères', 'count': 'Fréquence'}
    )
    st.plotly_chart(fig_len, use_container_width=True)

    # Box plot by quality if available
    if 'label_qualite' in df.columns:
        quality_labels = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}
        df_temp['qualite_label'] = df_temp['label_qualite'].map(quality_labels)

        fig_box = px.box(
            df_temp,
            x='qualite_label',
            y='longueur_reponse',
            title="Longueur des Réponses par Qualité",
            labels={'qualite_label': 'Qualité', 'longueur_reponse': 'Longueur (caractères)'},
            color='qualite_label',
            color_discrete_map={
                'Correcte': '#2E8B57',
                'Partielle': '#FFD700',
                'Incorrecte': '#DC143C'
            }
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
else:
    st.markdown("---")
    st.info("⚠️ La colonne `reponse` est absente du dataset.")

# ============================================================================
# Level Distribution (if available)
# ============================================================================

if 'niveau' in df.columns:
    st.markdown("---")
    st.header("📚 Distribution par Niveau Scolaire")

    niveau_counts = df['niveau'].value_counts().sort_index()

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart
        fig_niveau = px.bar(
            x=niveau_counts.index,
            y=niveau_counts.values,
            title="Nombre de Réponses par Niveau",
            labels={'x': 'Niveau', 'y': 'Nombre de réponses'},
            color=niveau_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_niveau, use_container_width=True)

    with col2:
        # Quality by level heatmap
        if 'label_qualite' in df.columns:
            quality_labels = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}

            # Create crosstab
            ct = pd.crosstab(df['niveau'], df['label_qualite'])
            ct.columns = [quality_labels.get(c, str(c)) for c in ct.columns]

            fig_heat = px.imshow(
                ct.values,
                x=ct.columns,
                y=ct.index,
                labels={'x': 'Qualité', 'y': 'Niveau', 'color': 'Nombre'},
                title="Heatmap: Niveau × Qualité",
                color_continuous_scale='Blues',
                text_auto=True
            )
            st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.markdown("---")
    st.info("⚠️ La colonne `niveau` est absente du dataset.")

# ============================================================================
# Advanced Visualizations
# ============================================================================

st.markdown("---")
st.header("📊 Visualisations Avancées")

if 'label_qualite' in df.columns and 'niveau' in df.columns:
    # Treemap
    quality_labels = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}
    df_treemap = df.copy()
    df_treemap['Qualité'] = df_treemap['label_qualite'].map(quality_labels)

    treemap_data = df_treemap.groupby(['niveau', 'Qualité']).size().reset_index(name='count')

    fig_tree = px.treemap(
        treemap_data,
        path=['niveau', 'Qualité'],
        values='count',
        title='Répartition Hiérarchique: Niveau → Qualité',
        color='count',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("ℹ️ Les colonnes `label_qualite` et `niveau` sont nécessaires pour la treemap.")

# Correlation analysis (if numeric columns available)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) > 1:
    st.subheader("🔗 Matrice de Corrélation")

    corr_matrix = df[numeric_cols].corr()

    fig_corr = px.imshow(
        corr_matrix,
        text_auto='.2f',
        title="Corrélations entre Variables Numériques",
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ============================================================================
# Data Export
# ============================================================================

st.markdown("---")
st.header("💾 Export des Données")

col1, col2, col3 = st.columns(3)

with col1:
    # Export full dataset
    csv_full = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger Dataset Complet (CSV)",
        data=csv_full,
        file_name="dataset_complet.csv",
        mime="text/csv"
    )

with col2:
    # Export summary statistics
    if 'label_qualite' in df.columns:
        summary_stats = df.groupby('label_qualite').agg({
            'question': 'count',
            'reponse': lambda x: x.str.len().mean() if 'reponse' in df.columns else 0
        }).reset_index()
        summary_stats.columns = ['label_qualite', 'count', 'avg_length']

        summary_csv = summary_stats.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger Statistiques (CSV)",
            data=summary_csv,
            file_name="statistiques.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Colonne `label_qualite` manquante pour générer les statistiques.")

with col3:
    # Export sample
    sample_df = df.sample(min(100, len(df)))
    sample_csv = sample_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger Échantillon (CSV)",
        data=sample_csv,
        file_name="echantillon_100.csv",
        mime="text/csv"
    )

# ============================================================================
# Data Insights Summary
# ============================================================================

st.markdown("---")
st.header("💡 Insights Clés")

insights = []

# Data completeness
missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
if missing_pct < 1:
    insights.append("✅ **Données complètes** - Moins de 1% de valeurs manquantes")
elif missing_pct < 5:
    insights.append("⚠️ **Données quasi-complètes** - Quelques valeurs manquantes à traiter")
else:
    insights.append("❌ **Données incomplètes** - Nettoyage recommandé")

# Quality distribution
if 'label_qualite' in df.columns:
    correct_pct = (df['label_qualite'] == 0).mean() * 100
    if correct_pct > 60:
        insights.append(f"🎯 **Bon équilibre** - {correct_pct:.1f}% de réponses correctes")
    elif correct_pct > 40:
        insights.append(f"⚖️ **Équilibre modéré** - {correct_pct:.1f}% de réponses correctes")
    else:
        insights.append(f"⚠️ **Déséquilibre** - Seulement {correct_pct:.1f}% de réponses correctes")

# Dataset size
if len(df) > 1000:
    insights.append(f"📊 **Dataset volumineux** - {len(df):,} réponses (excellent pour l'entraînement)")
elif len(df) > 500:
    insights.append(f"📊 **Dataset moyen** - {len(df):,} réponses (bon pour l'entraînement)")
else:
    insights.append(f"📊 **Dataset limité** - {len(df):,} réponses (considérer plus de données)")

# Display insights
for insight in insights:
    st.markdown(f"- {insight}")

# Recommendations
st.subheader("🚀 Recommandations")

recommendations = []

if missing_pct > 5:
    recommendations.append("🔧 **Nettoyer les données** - Traiter les valeurs manquantes avant l'entraînement")

if 'label_qualite' in df.columns:
    correct_pct = (df['label_qualite'] == 0).mean() * 100
    if correct_pct < 30 or correct_pct > 70:
        recommendations.append("⚖️ **Rééquilibrer le dataset** - Ajouter plus d'exemples de la classe minoritaire")

if len(df) < 500:
    recommendations.append("📈 **Augmenter le volume** - Collecter plus de données pour améliorer les performances")

if 'question' in df.columns:
    dup_count = df['question'].duplicated().sum()
    if dup_count > 0:
        recommendations.append(f"🧹 **Supprimer les doublons** - {dup_count} questions en doublon détectées")

if not recommendations:
    recommendations.append("✅ **Dataset prêt** - Qualité suffisante pour l'entraînement de modèles")

for rec in recommendations:
    st.markdown(f"- {rec}")
