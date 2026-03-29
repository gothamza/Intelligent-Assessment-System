# Plan d'Application Streamlit - Projet PFE

## Application de Résumé de Texte et Assistant Éducatif Intelligent

**Projet :** Modèles de Traitement Automatique des Langues pour l'Analyse et la Génération de Texte  
**Étudiant :** Abdelatif Berramou  
**Superviseur :** Pr. Youssef Fakhri

---

## Vue d'Ensemble de l'Application

L'application Streamlit sera divisée en **deux modules principaux** :

1. **Module Résumé de Texte** : Démonstration des modèles fine-tunés pour le résumé automatique
2. **Module Assistant Éducatif** : Interface interactive avec LLM pour génération de contenu pédagogique avec RAG

---

## ARCHITECTURE GLOBALE DE L'APPLICATION

```
app/
├── streamlit_app.py              # Application principale avec navigation
├── pages/
│   ├── 1_🏠_Accueil.py           # Page d'accueil
│   ├── 2_📝_Résumé_Simple.py    # Génération basique
│   ├── 3_🔄_Comparaison.py      # Comparaison multi-modèles
│   ├── 4_📊_Évaluation.py       # Métriques détaillées
│   └── 5_🎓_Assistant_Éducatif.py  # Nouveau module LLM éducatif
├── utils/
│   ├── visualization.py          # Visualisations
│   ├── rag_system.py             # Système RAG (nouveau)
│   ├── vector_store.py           # Gestion base vectorielle (nouveau)
│   └── llm_interface.py          # Interface LLM (nouveau)
└── data/
    └── vector_db/                # Base de données vectorielle (nouveau)
```

---

## PARTIE 1 : MODULE RÉSUMÉ DE TEXTE

### Page 1 : 🏠 Accueil

**Objectif :** Présenter le projet et guider l'utilisateur

**Contenu :**
- Titre principal : "Système de Résumé Automatique de Textes en Français"
- Description du projet
- Vue d'ensemble des fonctionnalités
- Informations sur les modèles disponibles
- Guide de démarrage rapide
- Liens vers les autres pages

**Éléments visuels :**
- Cards pour chaque modèle (mT5-small, mT5-base, BART)
- Statistiques du projet (nombre de modèles, taille des datasets)
- Schéma de l'architecture

---

### Page 2 : 📝 Résumé Simple

**Objectif :** Génération basique de résumé avec un modèle sélectionné

**Fonctionnalités :**

1. **Zone de saisie :**
   - Textarea pour texte à résumer (hauteur ajustable)
   - Bouton "Charger un exemple" avec exemples prédéfinis
   - Compteur de mots en temps réel

2. **Sélection du modèle :**
   - Dropdown : mT5-small, mT5-base, BART
   - Option : Utiliser modèle fine-tuné ou base
   - Indicateur de statut (chargé/disponible)

3. **Paramètres de génération :**
   - Slider : Longueur maximale (50-200 mots)
   - Slider : Longueur minimale (10-100 mots)
   - Slider : Nombre de beams (1-10)
   - Slider : Température (0.1-2.0)
   - Bouton "Réinitialiser aux valeurs par défaut"

4. **Génération et affichage :**
   - Bouton "Générer le résumé" (primaire, large)
   - Indicateur de chargement pendant la génération
   - Zone d'affichage du résumé généré (avec style distinct)
   - Statistiques :
     - Nombre de mots original vs résumé
     - Ratio de compression
     - Temps de génération

5. **Actions supplémentaires :**
   - Bouton "Copier le résumé"
   - Bouton "Télécharger en TXT"
   - Bouton "Comparer avec un autre modèle" (redirige vers page Comparaison)

**Layout :**
- Colonne gauche : Saisie et paramètres
- Colonne droite : Résultat et statistiques

---

### Page 3 : 🔄 Comparaison

**Objectif :** Comparer les résumés générés par plusieurs modèles

**Fonctionnalités :**

1. **Zone de saisie :**
   - Textarea pour texte à résumer
   - Boutons d'exemples rapides

2. **Sélection des modèles :**
   - Checkboxes pour sélectionner plusieurs modèles
   - Options : mT5-small, mT5-base, BART
   - Possibilité de sélectionner tous les modèles

3. **Paramètres communs :**
   - Sliders pour paramètres de génération (appliqués à tous les modèles)

4. **Affichage des résultats :**
   - Colonnes côte à côte pour chaque modèle sélectionné
   - Résumé généré par chaque modèle
   - Métriques pour chaque modèle :
     - Longueur du résumé
     - Temps de génération
     - Score de confiance (si disponible)

5. **Comparaison visuelle :**
   - Tableau comparatif des métriques
   - Graphique en barres : longueurs comparées
   - Graphique en barres : temps de génération comparés
   - Highlighting des différences entre résumés

6. **Analyse :**
   - Similarité entre les résumés (si plusieurs modèles)
   - Points communs identifiés
   - Différences principales

**Layout :**
- Layout large pour afficher plusieurs colonnes
- Section de visualisation en bas

---

### Page 4 : 📊 Évaluation

**Objectif :** Évaluer la qualité des résumés avec métriques détaillées

**Fonctionnalités :**

1. **Saisie des données :**
   - Zone 1 : Texte original
   - Zone 2 : Résumé généré (par un modèle)
   - Zone 3 : Résumé de référence (optionnel, pour comparaison)

2. **Sélection du modèle :**
   - Dropdown pour indiquer quel modèle a généré le résumé
   - Option : Résumé manuel (pas de modèle)

3. **Calcul des métriques :**
   - Bouton "Calculer les métriques"
   - Si référence fournie :
     - ROUGE-1 (Précision, Rappel, F1)
     - ROUGE-2 (Précision, Rappel, F1)
     - ROUGE-L (Précision, Rappel, F1)
     - BLEU score
     - BERTScore (Précision, Rappel, F1)
   - Si pas de référence :
     - Métriques intrinsèques (longueur, diversité lexicale, etc.)

4. **Affichage des résultats :**
   - Cards avec métriques principales
   - Graphiques :
     - Bar chart : Scores ROUGE
     - Bar chart : Scores BERTScore
     - Radar chart : Vue d'ensemble des métriques
   - Tableau détaillé avec toutes les métriques

5. **Analyse qualitative :**
   - Identification des points forts du résumé
   - Identification des points faibles
   - Suggestions d'amélioration

6. **Export :**
   - Bouton "Exporter le rapport" (PDF/JSON)
   - Sauvegarde des résultats dans l'historique

**Layout :**
- Layout en colonnes pour saisie
- Section métriques avec visualisations
- Section analyse en bas

---

## PARTIE 2 : MODULE ASSISTANT ÉDUCATIF INTELLIGENT

### Page 5 : 🎓 Assistant Éducatif

**Objectif :** Interface interactive avec LLM pour génération de contenu pédagogique avec RAG

---

### Architecture du Module Éducatif

```
Assistant Éducatif
├── Sidebar (Configuration)
│   ├── Sélection Matière
│   ├── Sélection Niveau
│   ├── Sélection Cours
│   └── Gestion Documents RAG
├── Zone de Chat Principal
│   ├── Historique de conversation
│   ├── Zone de saisie
│   └── Boutons d'actions rapides
└── Zone RAG
    ├── Upload de documents
    ├── Visualisation documents indexés
    └── Gestion base vectorielle
```

---

### SIDEBAR : Configuration et Paramètres

#### Section 1 : Configuration Pédagogique

**1.1 Sélection de la Matière**
- Dropdown ou boutons : 
  - Mathématiques
  - Physique
  - Chimie
  - Biologie
  - Histoire
  - Géographie
  - Français
  - Anglais
  - Autre (saisie libre)

**1.2 Sélection du Niveau d'Éducation**
- Dropdown :
  - Primaire (CP, CE1, CE2, CM1, CM2)
  - Collège (6ème, 5ème, 4ème, 3ème)
  - Lycée (2nde, 1ère, Terminale)
  - Supérieur (L1, L2, L3, Master)
  - Autre (saisie libre)

**1.3 Sélection du Cours/Thème**
- Dropdown dynamique (selon matière et niveau) :
  - Liste de cours prédéfinis
  - Option "Autre thème" (saisie libre)
- Exemples :
  - Mathématiques > Collège > 4ème > Algèbre, Géométrie, Statistiques
  - Physique > Lycée > Terminale > Mécanique, Électricité, Optique

**1.4 Paramètres LLM**
- Modèle LLM à utiliser :
  - Mistral 7B (fine-tuné si disponible)
  - mT5-base (adapté)
  - Autre modèle disponible
- Paramètres de génération :
  - Température (0.1-2.0)
  - Max tokens (100-2000)
  - Top-p (0.1-1.0)

---

#### Section 2 : Gestion RAG (Retrieval-Augmented Generation)

**2.1 Upload de Documents**
- Zone de drag & drop pour fichiers :
  - Formats acceptés : PDF, DOCX, TXT, MD
  - Bouton "Parcourir les fichiers"
  - Affichage de la progression d'upload

**2.2 Documents Indexés**
- Liste des documents dans la base vectorielle :
  - Nom du document
  - Matière associée
  - Niveau associé
  - Date d'ajout
  - Taille
  - Actions : Voir, Supprimer, Ré-indexer

**2.3 Configuration RAG**
- Nombre de chunks à récupérer (slider 1-10)
- Similarity threshold (slider 0.0-1.0)
- Méthode de chunking :
  - Par paragraphe
  - Par taille fixe
  - Par nombre de tokens
- Bouton "Ré-indexer tous les documents"

**2.4 Statistiques RAG**
- Nombre total de documents
- Nombre de chunks indexés
- Taille de la base vectorielle
- Matières couvertes

---

### ZONE PRINCIPALE : Interface de Chat

#### Zone de Chat (Partie Gauche - 70% de largeur)

**1. Historique de Conversation**
- Affichage des messages :
  - Messages utilisateur (à droite, bleu)
  - Réponses LLM (à gauche, gris)
  - Messages système (centré, info)
- Scroll automatique vers le bas
- Bouton "Effacer l'historique"
- Bouton "Exporter la conversation" (TXT/JSON)

**2. Zone de Saisie**
- Textarea pour saisie de message
- Bouton "Envoyer" (Enter pour envoyer)
- Compteur de caractères
- Indicateur de statut (typing...)

**3. Boutons d'Actions Rapides (Short Buttons)**
- Layout en grille 2x2 ou 3 colonnes
- Boutons avec icônes :
  
  **Génération de Contenu :**
  - 📚 "Générer un cours"
  - 📝 "Créer un examen"
  - ✏️ "Générer des exercices"
  - 📖 "Résumer le cours"
  - 🎯 "Créer un QCM"
  - 📊 "Générer un schéma explicatif"
  
  **Actions sur Documents :**
  - 🔍 "Rechercher dans mes documents"
  - 📄 "Résumer ce document"
  - ❓ "Poser une question sur ce document"
  
  **Aide :**
  - 💡 "Expliquer ce concept"
  - 🔗 "Donner des exemples"
  - 📚 "Suggestions de ressources"

**4. Mode RAG Actif**
- Indicateur visuel quand RAG est utilisé
- Affichage des sources utilisées :
  - "Sources : Document1.pdf (page 3), Document2.pdf (page 1)"
  - Liens cliquables vers les documents sources
  - Scores de similarité affichés

---

#### Zone RAG et Documents (Partie Droite - 30% de largeur)

**1. Documents Actifs pour cette Session**
- Liste des documents pertinents pour la matière/niveau sélectionnés
- Badges : Matière, Niveau
- Bouton "Utiliser ce document" pour focus sur un document spécifique

**2. Résultats de Recherche RAG**
- Quand RAG est déclenché :
  - Affichage des chunks récupérés
  - Score de similarité pour chaque chunk
  - Extrait du texte avec highlighting
  - Bouton "Voir le document complet"

**3. Visualisation de la Base Vectorielle**
- Graphique de similarité (si applicable)
- Statistiques des recherches RAG
- Métadonnées des documents indexés

---

### FONCTIONNALITÉS AVANCÉES

#### 1. Génération Contextuelle

**Génération de Cours :**
- Prompt automatique : "Génère un cours sur [thème] pour niveau [niveau] en [matière]"
- Utilisation du RAG pour enrichir avec documents disponibles
- Format structuré : Introduction, Développement, Conclusion, Exercices

**Génération d'Examen :**
- Options :
  - Type : QCM, Questions ouvertes, Mixte
  - Difficulté : Facile, Moyen, Difficile
  - Durée estimée
- Génération avec barème suggéré

**Génération d'Exercices :**
- Options :
  - Nombre d'exercices (1-20)
  - Type : Application, Problème, Démonstration
  - Niveau de difficulté
- Génération avec corrigés (optionnel)

---

#### 2. Système RAG Complet

**2.1 Architecture de la Base Vectorielle**

**Technologie :**
- Option 1 : ChromaDB (léger, facile à déployer)
- Option 2 : FAISS (performant, nécessite plus de mémoire)
- Option 3 : Pinecone (cloud, nécessite compte)
- **Recommandation :** ChromaDB pour simplicité

**Structure des Données :**
```python
Document {
    id: str (UUID)
    filename: str
    content: str (texte extrait)
    chunks: List[Chunk]
    metadata: {
        subject: str (matière)
        level: str (niveau)
        course: str (cours/thème)
        upload_date: datetime
        file_type: str (PDF, DOCX, etc.)
        file_size: int
        language: str (fr, en, etc.)
    }
}

Chunk {
    id: str
    document_id: str
    text: str
    embedding: List[float] (vecteur)
    chunk_index: int
    start_char: int
    end_char: int
    metadata: {
        page_number: int (si PDF)
        section: str
    }
}
```

**2.2 Processus d'Indexation**

1. **Upload du Document :**
   - Extraction du texte (PDF → texte, DOCX → texte)
   - Nettoyage et normalisation
   - Détection de la langue

2. **Chunking :**
   - Découpage en chunks de taille appropriée (512-1024 tokens)
   - Overlap entre chunks (50-100 tokens) pour contexte
   - Préservation de la structure (paragraphes, sections)

3. **Embedding :**
   - Génération d'embeddings pour chaque chunk
   - Modèle d'embedding : `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingue, français inclus)
   - Stockage des embeddings dans la base vectorielle

4. **Indexation avec Métadonnées :**
   - Association des métadonnées (matière, niveau, cours)
   - Indexation dans ChromaDB/FAISS
   - Sauvegarde de la référence du document

**2.3 Processus de Recherche RAG**

1. **Requête Utilisateur :**
   - Récupération de la question/message de l'utilisateur
   - Contexte : matière, niveau, cours sélectionnés

2. **Recherche Vectorielle :**
   - Embedding de la requête avec le même modèle
   - Recherche de similarité cosinus dans la base
   - Filtrage par métadonnées (matière, niveau) si spécifié
   - Récupération des top-K chunks (K = 3-5)

3. **Construction du Contexte :**
   - Agrégation des chunks récupérés
   - Ajout du contexte au prompt LLM
   - Format : "Contexte : [chunks]\n\nQuestion : [requête utilisateur]"

4. **Génération avec LLM :**
   - Envoi du prompt enrichi au LLM
   - Génération de la réponse
   - Affichage avec sources citées

---

#### 3. Gestion de la Conversation

**3.1 Historique Persistant**
- Stockage de l'historique dans `st.session_state`
- Sauvegarde optionnelle dans fichier JSON
- Chargement de conversations précédentes

**3.2 Contexte de Session**
- Maintien du contexte matière/niveau/cours
- Adaptation automatique des réponses selon le contexte
- Référence aux documents uploadés dans la conversation

**3.3 Personnalisation**
- Style de réponse : Formel, Décontracté, Technique
- Longueur des réponses : Court, Moyen, Détaillé
- Langue : Français, Anglais, Bilingue

---

## IMPLÉMENTATION TECHNIQUE

### Dépendances Additionnelles

```python
# Pour RAG et base vectorielle
chromadb>=0.4.0          # Base de données vectorielle
sentence-transformers>=2.2.0  # Modèles d'embedding
pypdf>=3.0.0             # Extraction PDF
python-docx>=0.8.11      # Extraction DOCX
langchain>=0.1.0         # Framework RAG (optionnel mais recommandé)
langchain-community>=0.0.20  # Intégrations LangChain

# Pour LLM
transformers>=4.30.0     # Déjà inclus
torch>=2.0.0             # Déjà inclus
accelerate>=0.20.0       # Déjà inclus

# Pour interface
streamlit>=1.25.0        # Déjà inclus
streamlit-chat>=0.1.1    # Composant chat amélioré (optionnel)
plotly>=5.14.0           # Déjà inclus
```

### Structure des Fichiers à Créer

```
app/
├── streamlit_app.py                    # Application principale (modifier)
├── pages/
│   ├── 1_🏠_Accueil.py                # Existant (modifier)
│   ├── 2_📝_Résumé_Simple.py          # Existant (modifier)
│   ├── 3_🔄_Comparaison.py            # Existant (modifier)
│   ├── 4_📊_Évaluation.py             # Existant (modifier)
│   └── 5_🎓_Assistant_Éducatif.py     # NOUVEAU
├── utils/
│   ├── visualization.py                # Existant
│   ├── rag_system.py                   # NOUVEAU - Système RAG complet
│   ├── vector_store.py                 # NOUVEAU - Gestion base vectorielle
│   ├── document_processor.py          # NOUVEAU - Traitement documents
│   ├── llm_interface.py                # NOUVEAU - Interface LLM éducatif
│   └── educational_prompts.py          # NOUVEAU - Templates de prompts
└── data/
    └── vector_db/                      # NOUVEAU - Base vectorielle
        ├── chroma_db/                   # Dossier ChromaDB
        └── documents/                  # Documents uploadés (optionnel)
```

---

## DÉTAILS D'IMPLÉMENTATION PAR COMPOSANT

### 1. Système RAG (`utils/rag_system.py`)

**Classes et Fonctions :**

```python
class RAGSystem:
    """Système RAG complet pour documents éducatifs"""
    
    def __init__(self, vector_store_path: str):
        # Initialisation ChromaDB
        # Chargement modèle d'embedding
        # Configuration
        
    def add_document(self, file_path: str, metadata: dict):
        """Ajouter un document à la base vectorielle"""
        # Extraction texte
        # Chunking
        # Génération embeddings
        # Indexation
        
    def search(self, query: str, filters: dict, top_k: int = 5):
        """Rechercher dans la base vectorielle"""
        # Embedding de la requête
        # Recherche avec filtres
        # Retourner chunks + scores
        
    def get_context_for_llm(self, query: str, filters: dict):
        """Construire le contexte pour le LLM"""
        # Recherche
        # Formatage des chunks
        # Retourner contexte formaté
        
    def delete_document(self, doc_id: str):
        """Supprimer un document"""
        
    def list_documents(self, filters: dict = None):
        """Lister tous les documents avec filtres"""
```

### 2. Gestion Base Vectorielle (`utils/vector_store.py`)

**Fonctions :**

```python
def initialize_vector_store(path: str):
    """Initialiser ChromaDB"""
    
def get_embedding_model():
    """Charger le modèle d'embedding"""
    
def chunk_text(text: str, chunk_size: int, overlap: int):
    """Découper le texte en chunks"""
    
def extract_text_from_file(file_path: str):
    """Extraire texte selon type de fichier"""
    
def add_metadata_to_chunks(chunks: List[str], metadata: dict):
    """Ajouter métadonnées aux chunks"""
```

### 3. Interface LLM Éducatif (`utils/llm_interface.py`)

**Classes :**

```python
class EducationalLLM:
    """Interface LLM spécialisée pour éducation"""
    
    def __init__(self, model_name: str, rag_system: RAGSystem):
        # Charger modèle LLM
        # Initialiser RAG
        
    def generate_course(self, subject: str, level: str, topic: str, use_rag: bool):
        """Générer un cours"""
        # Construire prompt
        # Utiliser RAG si activé
        # Générer avec LLM
        
    def generate_exam(self, subject: str, level: str, topic: str, exam_type: str):
        """Générer un examen"""
        
    def generate_exercises(self, subject: str, level: str, topic: str, count: int):
        """Générer des exercices"""
        
    def chat(self, message: str, context: dict, use_rag: bool):
        """Chat interactif avec contexte"""
        # Récupérer contexte RAG si nécessaire
        # Construire prompt avec contexte
        # Générer réponse
        # Retourner réponse + sources
        
    def format_response(self, response: str, sources: List[dict]):
        """Formater la réponse avec citations"""
```

### 4. Templates de Prompts (`utils/educational_prompts.py`)

**Fonctions :**

```python
def get_course_prompt(subject: str, level: str, topic: str, context: str = ""):
    """Template pour génération de cours"""
    return f"""
    Tu es un enseignant expert en {subject} pour le niveau {level}.
    Génère un cours complet sur le thème : {topic}
    
    Structure attendue :
    - Introduction
    - Développement avec exemples
    - Conclusion
    - Exercices pratiques
    
    Contexte additionnel :
    {context}
    """

def get_exam_prompt(subject: str, level: str, topic: str, exam_type: str):
    """Template pour génération d'examen"""
    
def get_exercise_prompt(subject: str, level: str, topic: str, difficulty: str):
    """Template pour génération d'exercices"""
    
def get_chat_prompt(message: str, context: dict, rag_context: str = ""):
    """Template pour chat avec contexte"""
```

### 5. Traitement de Documents (`utils/document_processor.py`)

**Fonctions :**

```python
def extract_text_from_pdf(file_path: str):
    """Extraire texte d'un PDF"""
    
def extract_text_from_docx(file_path: str):
    """Extraire texte d'un DOCX"""
    
def extract_text_from_txt(file_path: str):
    """Extraire texte d'un TXT"""
    
def process_uploaded_file(file, metadata: dict):
    """Traiter un fichier uploadé"""
    # Détecter type
    # Extraire texte
    # Retourner texte + métadonnées
```

---

## FLUX DE TRAVAIL UTILISATEUR

### Scénario 1 : Génération de Cours

1. **Configuration (Sidebar) :**
   - Utilisateur sélectionne : Mathématiques > Collège > 4ème > Algèbre

2. **Action :**
   - Utilisateur clique sur bouton "📚 Générer un cours"

3. **Traitement :**
   - Système construit le prompt avec contexte
   - Si documents RAG disponibles pour cette matière/niveau :
     - Recherche dans base vectorielle
     - Récupération de chunks pertinents
     - Enrichissement du prompt avec contexte RAG
   - Envoi au LLM
   - Génération du cours

4. **Affichage :**
   - Cours généré dans le chat
   - Si RAG utilisé : Affichage des sources
   - Options : Copier, Télécharger, Modifier

### Scénario 2 : Chat avec RAG

1. **Upload de Document :**
   - Utilisateur upload un PDF de cours de mathématiques
   - Sélection : Mathématiques > Collège > 4ème
   - Système indexe le document

2. **Question :**
   - Utilisateur tape : "Explique-moi les équations du second degré"

3. **Recherche RAG :**
   - Système recherche dans documents indexés (filtre : Mathématiques, Collège)
   - Récupère chunks pertinents sur les équations

4. **Génération :**
   - LLM génère réponse en utilisant les chunks comme contexte
   - Réponse cite les sources utilisées

5. **Affichage :**
   - Réponse dans le chat
   - Section "Sources utilisées" avec liens vers documents

### Scénario 3 : Génération d'Examen

1. **Configuration :**
   - Matière : Physique
   - Niveau : Terminale
   - Cours : Mécanique

2. **Action :**
   - Clic sur "📝 Créer un examen"
   - Popup : Type d'examen (QCM, Questions ouvertes, Mixte)
   - Sélection : QCM

3. **Génération :**
   - Prompt spécialisé pour QCM
   - Utilisation RAG si documents disponibles
   - Génération de 10 questions QCM avec réponses

4. **Affichage :**
   - Examen formaté avec questions et réponses
   - Option : Masquer les réponses (mode étudiant)
   - Export PDF possible

---

## CONSIDÉRATIONS TECHNIQUES

### Performance

1. **Chargement des Modèles :**
   - Utiliser `@st.cache_resource` pour LLM et embedding model
   - Chargement lazy (seulement quand nécessaire)

2. **Base Vectorielle :**
   - ChromaDB en mode persistant (disque)
   - Indexation asynchrone pour gros documents
   - Cache des recherches fréquentes

3. **Génération LLM :**
   - Streaming des réponses (affichage progressif)
   - Timeout pour éviter blocage
   - Gestion des erreurs robuste

### Sécurité et Données

1. **Upload de Fichiers :**
   - Validation du type de fichier
   - Limite de taille (ex: 10MB par fichier)
   - Scan pour contenu malveillant (optionnel)

2. **Stockage :**
   - Documents stockés localement (pas de cloud par défaut)
   - Option de chiffrement pour données sensibles
   - Gestion des permissions

3. **Données Utilisateur :**
   - Historique de conversation optionnel (avec consentement)
   - Possibilité d'effacer toutes les données
   - Conformité RGPD

### Expérience Utilisateur

1. **Interface :**
   - Design moderne et intuitif
   - Feedback visuel pour toutes les actions
   - Messages d'erreur clairs
   - Tooltips et aide contextuelle

2. **Responsive :**
   - Adaptation mobile (si nécessaire)
   - Layout flexible selon taille écran

3. **Accessibilité :**
   - Contraste de couleurs approprié
   - Navigation au clavier
   - Textes alternatifs pour icônes

---

## PLAN D'IMPLÉMENTATION PAR PHASES

### Phase 1 : Structure de Base (Semaine 1)

**Objectifs :**
- Créer la structure de fichiers
- Implémenter la navigation entre pages
- Mettre en place la sidebar de configuration

**Tâches :**
1. Modifier `streamlit_app.py` pour navigation multipages
2. Créer page `5_🎓_Assistant_Éducatif.py` (squelette)
3. Implémenter sidebar avec sélections (matière, niveau, cours)
4. Créer structure de base pour chat

**Livrables :**
- Navigation fonctionnelle
- Sidebar configurée
- Page Assistant Éducatif vide mais accessible

---

### Phase 2 : Système RAG de Base (Semaine 2)

**Objectifs :**
- Implémenter le système RAG complet
- Gestion de la base vectorielle
- Upload et indexation de documents

**Tâches :**
1. Créer `utils/vector_store.py` avec ChromaDB
2. Créer `utils/document_processor.py` pour extraction
3. Créer `utils/rag_system.py` avec classe RAGSystem
4. Implémenter upload de documents dans Streamlit
5. Tester indexation et recherche

**Livrables :**
- Système RAG fonctionnel
- Upload de documents opérationnel
- Recherche vectorielle testée

---

### Phase 3 : Interface LLM (Semaine 3)

**Objectifs :**
- Intégrer LLM pour génération
- Créer l'interface de chat
- Implémenter les boutons d'actions rapides

**Tâches :**
1. Créer `utils/llm_interface.py`
2. Créer `utils/educational_prompts.py`
3. Implémenter zone de chat dans Streamlit
4. Créer boutons d'actions rapides
5. Intégrer RAG avec LLM

**Livrables :**
- Chat fonctionnel
- Génération de contenu opérationnelle
- RAG intégré avec LLM

---

### Phase 4 : Fonctionnalités Avancées (Semaine 4)

**Objectifs :**
- Implémenter toutes les fonctionnalités de génération
- Améliorer l'interface utilisateur
- Optimiser les performances

**Tâches :**
1. Implémenter génération de cours, examens, exercices
2. Améliorer l'affichage des résultats
3. Ajouter visualisations RAG
4. Optimiser le chargement des modèles
5. Ajouter gestion d'historique

**Livrables :**
- Toutes les fonctionnalités implémentées
- Interface polie et optimisée
- Documentation utilisateur

---

### Phase 5 : Tests et Finalisation (Semaine 5)

**Objectifs :**
- Tester toutes les fonctionnalités
- Corriger les bugs
- Finaliser la documentation

**Tâches :**
1. Tests unitaires des composants
2. Tests d'intégration
3. Tests utilisateur
4. Correction des bugs
5. Documentation finale

**Livrables :**
- Application testée et fonctionnelle
- Documentation complète
- Guide d'utilisation

---

## MÉTRIQUES DE SUCCÈS

### Fonctionnalités Techniques

- ✅ Upload et indexation de documents fonctionnels
- ✅ Recherche RAG avec filtres par matière/niveau
- ✅ Génération de contenu pédagogique de qualité
- ✅ Chat interactif avec contexte maintenu
- ✅ Intégration RAG-LLM opérationnelle

### Expérience Utilisateur

- ✅ Interface intuitive et facile à utiliser
- ✅ Temps de réponse acceptable (< 5 secondes pour génération)
- ✅ Affichage clair des sources RAG
- ✅ Génération de contenu adapté au niveau sélectionné

### Performance

- ✅ Chargement des modèles < 30 secondes
- ✅ Recherche RAG < 1 seconde
- ✅ Génération de réponse < 10 secondes
- ✅ Support de 100+ documents dans la base

---

## RISQUES ET MITIGATION

### Risque 1 : Performance LLM sur CPU

**Problème :** Génération lente si pas de GPU  
**Mitigation :**
- Utiliser modèles quantifiés (4-bit ou 8-bit)
- Implémenter streaming pour meilleure UX
- Option d'utiliser API externe (Hugging Face Inference API)

### Risque 2 : Taille de la Base Vectorielle

**Problème :** Base vectorielle trop grande pour mémoire  
**Mitigation :**
- ChromaDB avec persistance disque
- Indexation par batches
- Option de nettoyage périodique

### Risque 3 : Qualité des Réponses LLM

**Problème :** Réponses pas adaptées au niveau éducatif  
**Mitigation :**
- Prompts spécialisés et testés
- Fine-tuning sur données éducatives (si possible)
- Système de feedback pour amélioration

### Risque 4 : Complexité de l'Interface

**Problème :** Interface trop chargée, confuse  
**Mitigation :**
- Design épuré avec sections claires
- Guide d'utilisation intégré
- Tests utilisateur itératifs

---

## EXTENSIONS FUTURES (Optionnelles)

1. **Multi-utilisateurs :**
   - Système d'authentification
   - Bases vectorielles par utilisateur
   - Partage de documents entre utilisateurs

2. **Collaboration :**
   - Mode collaboratif pour enseignants
   - Partage de cours générés
   - Bibliothèque de ressources partagée

3. **Analytics :**
   - Statistiques d'utilisation
   - Qualité des générations
   - Suivi des documents les plus utilisés

4. **Intégrations :**
   - Export vers LMS (Moodle, etc.)
   - Intégration avec outils éducatifs existants
   - API REST pour intégrations externes

---

## CONCLUSION

Ce plan détaille l'implémentation complète d'une application Streamlit avec deux modules :

1. **Module Résumé de Texte** : Démonstration des modèles fine-tunés
2. **Module Assistant Éducatif** : Interface LLM interactive avec RAG

L'architecture proposée est modulaire, extensible et prend en compte les contraintes techniques (ressources limitées) tout en offrant une expérience utilisateur riche.

**Prochaines Étapes :**
- Validation du plan avec le superviseur
- Début de l'implémentation selon les phases définies
- Tests itératifs et améliorations continues

---

**Date de création du plan :** [Date]  
**Version :** 1.0

