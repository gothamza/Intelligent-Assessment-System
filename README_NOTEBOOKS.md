# 📓 Notebooks d'Analyse - Système de Feedback Pédagogique

## 🚀 Setup Rapide avec UV (Recommandé)

### Pourquoi UV ?
`uv` est un gestionnaire de packages Python ultra-rapide qui permet d'isoler l'environnement des notebooks sans conflits avec votre système principal ou l'application Streamlit.

### Installation de UV
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou avec pip
pip install uv
```

### Configuration de l'environnement des notebooks
```bash
# 1. Créer un environnement virtuel dédié aux notebooks
uv venv notebooks-env

# 2. Activer l'environnement
# Windows PowerShell:
.\notebooks-env\Scripts\Activate.ps1
# Linux/macOS:
source notebooks-env/bin/activate

# 3. Installer les dépendances avec uv (ultra-rapide)
uv pip install -r requirements_notebooks.txt

# Alternative : installer manuellement les packages essentiels
# uv pip install jupyter notebook jupyterlab
# uv pip install transformers torch pandas numpy
# uv pip install scikit-learn matplotlib seaborn plotly
# uv pip install requests beautifulsoup4 tqdm
# uv pip install openai python-dotenv langchain langchain-openai
# uv pip install ipywidgets

# 4. Lancer Jupyter depuis cet environnement
jupyter notebook
# ou
jupyter lab
```

### Configuration des clés API
Créez un fichier `.env` à la racine du projet :
```bash
# Clés API pour les LLMs
GROQ_API_KEY2=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### Ordre d'exécution des notebooks
```bash
cd notebooks

# 1. Collecte de données depuis Alloprof
jupyter notebook 1_collecte_questions.ipynb

# 2. Génération de réponses d'élèves simulées
jupyter notebook 2_generation_reponses_eleves.ipynb

# 3. Annotation de qualité assistée par LLM
jupyter notebook 3_etiquetage_qualite_assiste_llm.ipynb

# 4. Entraînement du modèle CamemBERT
jupyter notebook 3b_entrainement_camembert.ipynb

# 5. Génération de feedback pédagogique
jupyter notebook 4_generation_feedback.ipynb

# 6. Structuration du dataset final
jupyter notebook 5_structuration_jeu_donnees.ipynb

# 7. Évaluation du système complet
jupyter notebook 6_evaluation_systeme.ipynb
```

### Alternative : Installation classique (sans UV)
```bash
# Créer un environnement virtuel classique
python -m venv notebooks-env
.\notebooks-env\Scripts\Activate.ps1  # Windows
# source notebooks-env/bin/activate  # Linux/macOS

# Installer avec pip classique
pip install -r requirements_notebooks.txt
```

### 📦 Contenu du fichier requirements_notebooks.txt
Le fichier `requirements_notebooks.txt` contient toutes les dépendances nécessaires :
- **Jupyter** : notebook, jupyterlab, ipywidgets
- **ML/NLP** : transformers, torch, scikit-learn
- **Data** : pandas, numpy
- **Visualisation** : matplotlib, seaborn, plotly
- **Web scraping** : requests, beautifulsoup4
- **LLM APIs** : openai, langchain, langchain-openai
- **Évaluation** : bert-score, rouge-score, nltk (evaluate est optionnel)
- **Utilitaires** : python-dotenv, tqdm

### 🔧 Résolution des problèmes d'installation

**Problème 1: Timeout UV avec certains packages**
```bash
# Solution 1: Augmenter le timeout
$env:UV_HTTP_TIMEOUT = "300"  # Windows PowerShell
uv pip install -r requirements_notebooks.txt

# Solution 2: Installer les packages problématiques séparément avec pip
pip install evaluate sqlalchemy

# Solution 3: Utiliser pip classique pour tout
pip install -r requirements_notebooks.txt --timeout=300
```

**Problème 2: Erreur de réseau persistante**
```bash
# Installer en plusieurs étapes
uv pip install jupyter notebook jupyterlab ipywidgets
uv pip install pandas numpy matplotlib seaborn plotly
uv pip install transformers torch scikit-learn
uv pip install openai langchain langchain-openai
uv pip install requests beautifulsoup4 tqdm python-dotenv
uv pip install bert-score rouge-score nltk
# Optionnel: uv pip install evaluate
```

**Problème 3: Torch/CUDA (si vous avez une GPU)**
```bash
# Pour GPU avec CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Pour GPU avec CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121

# CPU seulement (plus léger)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## 📋 Vue d'ensemble

Ce document explique les notebooks Jupyter utilisés pour développer et analyser le système de feedback pédagogique. Ces notebooks contiennent toutes les étapes de développement, de la collecte de données à l'évaluation des modèles.

## 🗂️ Structure des Notebooks
### 1. 📥 `1_collecte_questions.ipynb` - Collecte de Données
**Objectif**: Collecter des données éducatives depuis Alloprof

**Contenu**:
- Web scraping des questions/réponses Alloprof
- Nettoyage et structuration des données
- Sauvegarde en format JSON
- Gestion des niveaux scolaires (7ème à 11ème)

**Données générées**:
- `Data/alloprof_college_lycee_qna.json` - Dataset principal
- Questions et réponses par niveau scolaire
- Métadonnées éducatives

**Technologies utilisées**:
- `requests` - Requêtes HTTP
- `BeautifulSoup` - Parsing HTML
- `json` - Sérialisation des données

### 2. 🤖 `2_generation_reponses_eleves.ipynb` - Génération de Réponses d'Élèves
**Objectif**: Générer automatiquement des réponses d'élèves simulées

**Contenu**:
- Génération de 3 types de réponses par question : correcte, partielle, incorrecte
- Utilisation de LLMs (OpenRouter/Groq) avec des prompts dédiés
- Configuration des chaînes de génération
- Sauvegarde des résultats

**Processus**:
1. Chargement des questions Alloprof
2. Définition des prompts spécialisés
3. Génération des réponses variées
4. Structuration et export

**Technologies utilisées**:
- `langchain_openai` - Intégration LLM
- `langchain.prompts` - Gestion des prompts
- `tqdm` - Barre de progression

### 3. 🏷️ `3_etiquetage_qualite_assiste_llm.ipynb` - Annotation Assistée par LLM
**Objectif**: Étiqueter la qualité des réponses avec assistance LLM

**Contenu**:
- Annotation automatique avec LLM (Groq/OpenAI)
- Classification en 3 classes : 0 (Correct), 1 (Partiel), 2 (Incorrect)
- Validation manuelle recommandée
- Export du dataset annoté

**Données générées**:
- `Data/labeled_qna_dataset.csv` - Dataset annoté
- Labels de qualité pour chaque réponse
- Métriques d'annotation

**Technologies utilisées**:
- `openai` - API OpenAI
- `python-dotenv` - Gestion des variables d'environnement

### 4. 🧠 `3b_entrainement_camembert.ipynb` - Entraînement du Modèle CamemBERT
**Objectif**: Fine-tuner CamemBERT pour la classification de qualité

**Contenu**:
- Préparation des données d'entraînement
- Configuration du modèle CamemBERT
- Entraînement avec validation
- Évaluation des performances
- Sauvegarde du modèle

**Modèle entraîné**:
- **Architecture**: CamemBERT (BERT français)
- **Classes**: 3 (Correcte, Partielle, Incorrecte)
- **Métriques**: Précision, Rappel, F1-Score
- **Sauvegarde**: `models/camembert-quality-classifier/`

**Technologies utilisées**:
- `transformers` - Hugging Face Transformers
- `torch` - PyTorch
- `scikit-learn` - Métriques d'évaluation
- `pandas` - Manipulation des données

### 5. 💬 `4_generation_feedback.ipynb` - Génération de Feedback Pédagogique
**Objectif**: Générer du feedback pédagogique pour les réponses incorrectes

**Contenu**:
- Filtrage des réponses nécessitant un feedback (labels 1/2)
- Génération de feedback constructif et bienveillant
- Utilisation de prompts pédagogiques optimisés
- Export des résultats enrichis

**Processus**:
1. Chargement du dataset annoté
2. Filtrage des réponses problématiques
3. Génération avec prompts optimisés
4. Validation et export

**Technologies utilisées**:
- `openai` - API OpenAI
- `tqdm` - Barre de progression

### 6. 📊 `5_structuration_jeu_donnees.ipynb` - Structuration du Dataset Final
**Objectif**: Fusionner et structurer le jeu de données complet

**Contenu**:
- Fusion des questions, réponses et labels
- Préparation des colonnes finales
- Export en formats CSV/JSON
- Validation de la cohérence des données

**Colonnes finales**:
- `question` - Question originale
- `reponse` - Réponse de l'élève
- `label_qualite` - Classification (0/1/2)
- `feedback` - Feedback généré (optionnel)
- `source` - Source des données

### 7. 📈 `6_evaluation_systeme.ipynb` - Évaluation du Système
**Objectif**: Évaluer la qualité des réponses et feedbacks générés

**Contenu**:
- Comparaison des réponses générées vs. références humaines
- Métriques BLEU, ROUGE, BERTScore
- Analyse comparative des modèles
- Visualisation des performances

**Métriques calculées**:
- **BLEU Score** - Similarité n-gram
- **ROUGE-L** - Longest Common Subsequence
- **BERTScore** - Similarité sémantique
- **Métriques personnalisées** - Qualité pédagogique

## 💡 Conseils d'Utilisation

### Prérequis système
- **Python 3.11+** recommandé
- **GPU** recommandée pour l'entraînement du modèle CamemBERT (notebook 3b)
- **8GB RAM minimum** pour les opérations de ML
- **Connexion Internet** pour le scraping et les API LLM

### Exécution en lot (avancé)
```bash
# Convertir et exécuter tous les notebooks automatiquement
cd notebooks
jupyter nbconvert --to script --execute *.ipynb

# Ou exécuter un notebook spécifique en ligne de commande
jupyter nbconvert --to notebook --execute 1_collecte_questions.ipynb
```

### Notes importantes
- ⚠️ Le notebook 1 effectue du web scraping : respectez les délais entre requêtes
- ⚠️ Les notebooks 2, 3, 4 nécessitent des clés API valides (coûts potentiels)
- ⚠️ Le notebook 3b nécessite une GPU pour un entraînement efficace
- 💡 Commencez avec de petits échantillons pour tester avant le traitement complet

## 📊 Données et Résultats

### Datasets générés
- `Data/alloprof_college_lycee_qna.json` - Questions/réponses Alloprof
- `Data/labeled_qna_dataset.csv` - Dataset annoté avec labels de qualité
- `Data/generated_qna_dataset_first_100_fr.json` - Réponses générées
- `Data/etiquetage_100_reponses.json` - Annotations de validation

### Modèles entraînés
- `models/camembert-quality-classifier/` - Modèle de classification
- Checkpoints d'entraînement (50, 100, 150, 195 époques)
- Métriques de performance sauvegardées
- Logs d'entraînement et courbes d'apprentissage

### Résultats d'évaluation
- Métriques BLEU, ROUGE, BERTScore
- Matrices de confusion
- Analyses d'erreur détaillées
- Comparaisons de modèles

## 🔧 Personnalisation

### Modifier les paramètres d'entraînement
```python
# Dans 3b_entrainement_camembert.ipynb
training_args = TrainingArguments(
    output_dir='./models/camembert-quality-classifier',
    num_train_epochs=10,  # Modifier le nombre d'époques
    per_device_train_batch_size=16,  # Taille du batch
    learning_rate=2e-5,  # Taux d'apprentissage
    # ... autres paramètres
)
```

### Adapter les prompts de génération
```python
# Dans 2_generation_reponses_eleves.ipynb
correct_prompt = """
Tu es un élève qui répond correctement à une question de mathématiques.
Question: {question}
Réponse correcte:
"""

partial_prompt = """
Tu es un élève qui donne une réponse partiellement correcte.
Question: {question}
Réponse partielle:
"""
```

### Modifier les métriques d'évaluation
```python
# Dans 6_evaluation_systeme.ipynb
def custom_metric(predictions, references):
    # Implémenter vos métriques personnalisées
    return score
```

## 📈 Monitoring et Logs

### Suivi de l'entraînement
- Logs TensorBoard intégrés
- Métriques en temps réel
- Sauvegarde automatique des checkpoints

### Monitoring des performances
- Graphiques de performance
- Alertes sur les dégradations
- Comparaison avec les baselines

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de mémoire GPU**
   ```python
   # Réduire la taille du batch
   per_device_train_batch_size=8
   ```

2. **Problème de dépendances**
   ```bash
   # Réinstaller les dépendances
   pip install -r requirements_notebooks.txt --force-reinstall
   ```

3. **Erreur d'API**
   ```python
   # Vérifier les clés API
   import os
   print(os.getenv("GROQ_API_KEY2"))
   ```

4. **Problème de scraping**
   ```python
   # Ajouter des délais entre les requêtes
   time.sleep(1)  # 1 seconde entre chaque requête
   ```

## 📚 Ressources et Documentation

### Documentation des bibliothèques
- [Transformers](https://huggingface.co/docs/transformers/)
- [LangChain](https://python.langchain.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### Modèles pré-entraînés
- [CamemBERT](https://huggingface.co/camembert-base)
- [Groq Models](https://console.groq.com/docs/models)
- [OpenRouter Models](https://openrouter.ai/models)

### Sources de données
- [Alloprof](https://www.alloprof.qc.ca/) - Questions/réponses éducatives

## 🎯 Prochaines Étapes

1. **Optimisation des modèles**
   - Fine-tuning plus poussé
   - Architecture personnalisée
   - Optimisation des prompts

2. **Extension des données**
   - Collecte de nouveaux datasets
   - Annotation de plus d'échantillons
   - Validation croisée

3. **Amélioration de l'évaluation**
   - Métriques personnalisées
   - Évaluation humaine
   - Tests A/B

4. **Déploiement**
   - Intégration dans l'application Streamlit
   - API REST pour les services
   - Monitoring en production

---

**📓 Ces notebooks constituent la base technique de votre PFE et peuvent être utilisés pour reproduire tous les résultats.**