# 🧠 Système de Feedback Pédagogique Intelligent

> **Génération automatique de feedback pédagogique en mathématiques**  
> Projet de Fin d'Études (PFE) - Master Informatique et Intelligence Artificielle  
> Université Ibn Tofail, Faculté des Sciences, Kénitra

---

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture du Système](#-architecture-du-système)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Pages de l'Application](#-pages-de-lapplication)
- [Technologies Utilisées](#-technologies-utilisées)
- [Documentation](#-documentation)
- [Performance](#-performance)
- [Contribuer](#-contribuer)

---

## 🎯 Vue d'ensemble

Ce projet propose un **système automatisé et intelligent** pour générer du feedback pédagogique personnalisé sur des exercices de mathématiques de niveau collège et lycée. Il combine:

- **Classification automatique** des réponses d'élèves (CamemBERT fine-tuné)
- **Génération de feedback** adaptatif via LLMs (GPT-4, Groq, etc.)
- **Création d'examens** intelligente avec questions uniques
- **Interface interactive** pour étudiants et enseignants
- **Tuteur virtuel** basé sur l'IA pour aide personnalisée

### 🎓 Contexte Académique

**Auteur:** Ibtissam Fadili  
**Encadrante:** Dr. Zineb Goutti  
**Institution:** Faculté des Sciences de Kénitra - Université Ibn Tofail  
**Formation:** Master Informatique et Intelligence Artificielle  
**Année:** 2024-2025

---

## 🚀 Fonctionnalités

### 1. **📊 Exploration des Données**
- Visualisation interactive du dataset
- Statistiques détaillées par niveau, cours et difficulté
- Analyse de la distribution des questions

### 2. **🔍 Classification de Réponses**
- Classification automatique en 3 catégories:
  - ✅ **Correcte**
  - ⚠️ **Partielle**
  - ❌ **Incorrecte**
- Modèle CamemBERT fine-tuné (F1-Score: 0.91)
- Comparaison avec classification LLM

### 3. **💬 Génération de Feedback**
- Feedback personnalisé et constructif
- Adaptation au niveau de l'élève
- Suggestions d'amélioration ciblées
- Multi-providers LLM (Groq, OpenAI, OpenRouter)

### 4. **📈 Métriques d'Évaluation**
- Calcul automatique de: BLEU, ROUGE-1, ROUGE-L, BERTScore
- Comparaison feedback généré vs. feedback humain
- Analyse de similarité sémantique

### 5. **📝 Création d'Examens** (Enseignants)
- Génération automatique de questions uniques
- Répartition intelligente par cours (auto-normalisation)
- Questions groupées par thème
- Support de pourcentages flexibles
- Export en PDF, Word, JSON

### 6. **📝 Passage d'Examens** (Étudiants)
- Interface intuitive avec timer
- Upload de fichiers (PDF, Word, JSON)
- Extraction automatique de questions
- Feedback instantané après soumission
- Génération de cours personnalisés

### 7. **💬 Tuteur Interactif** (IA)
- Assistant virtuel pour aide en mathématiques
- Génération de questions adaptées
- Exercices avec solutions complètes
- Cours complets sur demande
- Historique de conversation sauvegardé

---

## 🏗️ Architecture du Système

### Diagramme d'Architecture Global

```
┌─────────────────────────────────────────────────────────┐
│                   Interface Streamlit                    │
│  (7 pages: Exploration, Classification, Feedback, etc.) │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼──────┐         ┌──────▼──────┐
    │ CamemBERT │         │     LLMs    │
    │ Classifier│         │  (Feedback) │
    └───────────┘         └─────────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼────────┐
              │   Feedback    │
              │   Generation  │
              └───────────────┘
```

### Diagrammes de Classe Détaillés

#### 1️⃣ Architecture Système Complet
![Diagramme d'Architecture](./images/diagram-export.png)
*Figure 1: Diagramme d'architecture complète du système avec tous les composants*

#### 2️⃣ Modèle de Classes - Backend & Services
![Diagramme de Classes](./images/class%20diagram.png)
*Figure 2: Diagramme de classes montrant la structure des services backend*

### Pipeline de Traitement

1. **Collecte** → Scraping de questions (Alloprof)
2. **Génération** → Simulation de réponses d'élèves (LLM)
3. **Étiquetage** → Classification CamemBERT
4. **Entraînement** → Fine-tuning du classificateur
5. **Feedback** → Génération via LLMs
6. **Évaluation** → Métriques automatiques

---

## 💻 Installation

### Prérequis

- Python 3.9+
- pip ou uv
- Clés API (Groq, OpenAI, ou OpenRouter)

### Installation Rapide

```bash
# Cloner le repository
git clone https://github.com/gothamza/Intelligent-Assessment-System.git
cd Intelligent-Assessment-System

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API
cp env.example .env
# Éditez .env et ajoutez vos clés API

# Lancer l'application
streamlit run main.py
```

### Avec Docker

```bash
# Construire et lancer tous les services
docker-compose up --build

# Accéder à l'application
# Frontend Streamlit:  http://localhost:8501
# Backend API:         http://localhost:8000
# API Docs:            http://localhost:8000/docs
```

**Services lancés automatiquement:**
- ✅ Frontend Streamlit
- ✅ Backend FastAPI
- ✅ Base de données PostgreSQL
- ✅ Vector Store (Chroma)

**Pour arrêter:**
```bash
docker-compose down
```

**Pour voir les logs:**
```bash
docker-compose logs -f frontend  # Logs Streamlit
docker-compose logs -f backend   # Logs FastAPI
```

### Configuration des Clés API

Créez un fichier `.env` à la racine:

```env
# Groq (Recommandé - Gratuit)
GROQ_API_KEY=votre-groq-api-key
GROQ_API_KEY2=autre-clé-optionnelle

# OpenAI (Optionnel)
OPENAI_API_KEY=votre-openai-api-key

# OpenRouter (Alternatif - Gratuit)
OPENROUTER_API_KEY=votre-openrouter-api-key

# LangSmith (Tracing - Optionnel)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=votre-langsmith-api-key
LANGSMITH_PROJECT=mon-projet
```

💡 **Astuce:** Vous pouvez utiliser uniquement Groq (gratuit) pour démarrer!

---

## 🎮 Utilisation

### Démarrage

```bash
streamlit run main.py
```

L'application s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`

### Navigation

L'application comporte **7 pages** accessibles via la sidebar:

1. **📊 Exploration des Données** - Visualisation du dataset
2. **🔍 Classification de Réponses** - Test du classificateur
3. **💬 Génération de Feedback** - Test de génération
4. **📈 Métriques d'Évaluation** - Résultats et performances
5. **📝 Création d'Examens** - Pour enseignants
6. **📝 Passer Examen** - Pour étudiants
7. **💬 Tuteur Interactif** - Assistant IA

---

## 📱 Pages de l'Application

### 1. Exploration des Données
- **Objectif:** Comprendre le dataset
- **Fonctionnalités:**
  - Statistiques par niveau/cours
  - Distribution des questions
  - Visualisations interactives

### 2. Classification de Réponses
- **Objectif:** Classifier la qualité des réponses
- **Fonctionnalités:**
  - Classification CamemBERT
  - Comparaison avec LLM
  - Analyse du raisonnement

### 3. Génération de Feedback
- **Objectif:** Générer du feedback personnalisé
- **Fonctionnalités:**
  - Feedback adaptatif
  - Multi-providers LLM
  - Configuration température/tokens

### 4. Métriques d'Évaluation
- **Objectif:** Évaluer la qualité du feedback
- **Fonctionnalités:**
  - BLEU, ROUGE, BERTScore
  - Comparaison avec référence humaine
  - Résultats d'entraînement

### 5. Création d'Examens
- **Objectif:** Créer des examens personnalisés
- **Fonctionnalités:**
  - Génération automatique de questions **uniques**
  - Répartition par cours (auto-normalisation)
  - Questions **groupées par thème**
  - Export multi-formats

### 6. Passer Examen
- **Objectif:** Interface pour étudiants
- **Fonctionnalités:**
  - Upload PDF/Word/JSON
  - **Extraction automatique de durée**
  - Timer avec countdown
  - Feedback instantané
  - Génération de cours personnalisés

### 7. Tuteur Interactif
- **Objectif:** Assistant virtuel personnalisé
- **Fonctionnalités:**
  - Génération de questions adaptées
  - Classification de réponses en temps réel
  - Exercices avec solutions
  - Cours complets sur demande
  - Historique de conversation

---

## 🎬 Application en Action

### 📸 Interface Utilisateur - Capture d'écrans

#### 1️⃣ Création d'Examens (Vue 1)
![Création d'Examen - Interface 1](./images/Cr%C3%A9ation%20d%27Examen1.png)
*Figure 4: Interface de création d'examens - Sélection des cours et configuration*

#### 2️⃣ Création d'Examens (Vue 2) - Résultat Généré
![Création d'Examen - Interface 2](./images/Cr%C3%A9ation%20d%27Examen2.png)
*Figure 5: Interface de création d'examens - Examen généré avec questions*

#### 3️⃣ Passer un Examen - Interface Étudiante
![Passer un Examen](./images/PasserunExamen.png)
*Figure 6: Interface pour passer un examen - Environnement de travail*

---

## 🐳 Infrastructure & Déploiement

### Architecture Docker

![Docker Architecture](./images/docker.jpeg)
*Figure 7: Architecture Docker - Orchestration des services*

**Services disponibles:**
- 🎯 **Frontend Streamlit** (Port 8501)
- 🔧 **Backend FastAPI** (Port 8000)
- 🗄️ **PostgreSQL Database** (Port 5432)
- 📊 **Vector Store (Chroma)** (Port 8001)

---

## 🛠️ Technologies Utilisées

### Intelligence Artificielle

| Technologie | Utilisation | Performance |
|-------------|-------------|-------------|
| **CamemBERT** | Classification de réponses | F1: 0.91, Accuracy: 0.89 |
| **GPT-4 / Groq** | Génération de feedback | BLEU: 0.42, ROUGE-L: 0.58 |
| **BERTScore** | Évaluation sémantique | Précision: 0.85 |
| **LangChain** | Orchestration LLM | - |

### Backend & Framework

- **Python 3.9+** - Langage principal
- **Streamlit** - Framework d'interface
- **Transformers (Hugging Face)** - Modèles NLP
- **PyTorch** - Deep learning
- **Pandas** - Manipulation de données
- **NumPy** - Calculs numériques

### Visualisation

- **Plotly** - Graphiques interactifs
- **Matplotlib** - Visualisations statiques
- **Seaborn** - Visualisations statistiques

### Déploiement

- **Docker** - Containerisation
- **Streamlit Cloud** - Hébergement cloud
- **Git** - Versioning

---

## 📚 Documentation

- [README.md](./README.md) - English version
- [README_NOTEBOOKS.md](README_NOTEBOOKS.md) - Guide des notebooks
- [TRAINING_RESULTS.md](TRAINING_RESULTS.md) - Résultats d'entraînement
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Guide d'installation détaillé

---

## 📊 Performance

### Métriques du Classificateur CamemBERT

| Métrique | Score |
|----------|-------|
| **Accuracy** | 0.89 |
| **F1-Score (Macro)** | 0.91 |
| **Précision** | 0.90 |
| **Rappel** | 0.89 |

### Métriques de Génération de Feedback

| Métrique | Score Moyen |
|----------|-------------|
| **BLEU** | 0.42 |
| **ROUGE-1** | 0.51 |
| **ROUGE-L** | 0.58 |
| **BERTScore F1** | 0.85 |

---

## 🤝 Contribuer

Les contributions sont les bienvenues! Pour contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add: Amazing Feature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 License

Ce projet est développé dans le cadre d'un Projet de Fin d'Études (PFE).

---

## 👥 Contact

**Auteur:** Ibtissam Fadili  
**Encadrante:** Dr. Zineb Goutti  
**Institution:** Faculté des Sciences de Kénitra - Université Ibn Tofail  
**Repository:** https://github.com/gothamza/Intelligent-Assessment-System

---

## 🙏 Remerciements

- **Dr. Zineb Goutti** - Encadrement et soutien académique
- **Hugging Face** - Modèles et infrastructure
- **Groq** - API LLM gratuite et performante
- **Streamlit** - Framework d'interface web

---

<div align="center">

**🧠 Développé avec ❤️ en Python & Streamlit**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()

</div>
