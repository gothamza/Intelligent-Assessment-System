# Plan de Travail - Projet de Fin d'Études

## Modèles de Traitement Automatique des Langues pour l'Analyse et la Génération de Texte : Méthodes et Applications

**Étudiant :** Abdelatif Berramou  
**Superviseur :** Pr. Youssef Fakhri  
**Année Universitaire :** 2025/2026  
**Master :** Génie Logiciel et Cloud Computing

---

## 1. Introduction et Objectifs

### 1.1 Contexte du Projet

Ce projet s'inscrit dans le domaine du traitement automatique des langues (TAL) et vise à développer des modèles avancés pour la génération automatique de résumés de textes en français, avec une application particulière au domaine éducatif. L'objectif principal est d'adapter et de fine-tuner des modèles Transformer pré-entraînés pour produire des résumés de qualité optimale en français.

### 1.2 Objectifs Généraux

- Développer et valider un système de génération de résumés automatiques en français
- Comparer les performances de différents modèles Transformer (mT5-small, mT5-base, BART)
- Adapter les modèles au domaine éducatif francophone
- Créer une application interactive pour démontrer les résultats

### 1.3 Objectifs Spécifiques

1. **Adaptation et spécialisation des modèles**
   - Fine-tuning de mT5-small, mT5-base et BART sur corpus francophone
   - Optimisation des hyperparamètres pour maximiser les performances
   - Utilisation de techniques d'adaptation efficaces (LoRA) pour réduire les coûts computationnels

2. **Développement d'un pipeline d'évaluation**
   - Implémentation de métriques multiples (ROUGE, BLEU, BERTScore)
   - Analyse comparative des modèles
   - Évaluation qualitative avec exemples concrets

3. **Application interactive**
   - Développement d'une application Streamlit pour la démonstration
   - Interface permettant la comparaison des modèles
   - Visualisation des résultats et métriques

---

## 2. Méthodologie et Étapes du Projet

### Phase 1 : Préparation et Exploration des Données (Semaine 1-2)

#### Étape 1.1 : Collecte des Données

**Actions :**
- Chargement du corpus MLSUM-FR (425 000 articles de presse français avec résumés)
- Intégration du corpus ALECTOR (79 textes éducatifs pour enfants de 7-9 ans)
- Exploration de la structure et des statistiques des données

**Justification :**
- **MLSUM-FR** : Corpus volumineux et de qualité, idéal pour l'entraînement initial et la généralisation. Les résumés sont rédigés par des journalistes professionnels, garantissant une haute qualité linguistique.
- **ALECTOR** : Corpus spécialisé dans le domaine éducatif, permettant l'adaptation du domaine et l'évaluation de la capacité de transfert des modèles vers le contexte pédagogique.

**Livrables :**
- Notebook d'exploration des données (`01_data_preparation.ipynb`)
- Rapport statistique sur les caractéristiques des corpus
- Visualisations des distributions de longueur et ratios de compression

#### Étape 1.2 : Prétraitement et Formatage

**Actions :**
- Nettoyage et normalisation des textes
- Tokenisation adaptée à chaque modèle (mT5, BART)
- Création des splits train/validation/test (80/10/10)
- Formatage des données selon les spécificités de chaque architecture

**Justification :**
- Le prétraitement adapté est crucial car mT5 nécessite un préfixe "summarize: " tandis que BART utilise des paires texte-résumé directes. Cette étape garantit la compatibilité avec les architectures choisies.
- La création de splits appropriés permet une évaluation rigoureuse et évite le surapprentissage.

**Livrables :**
- Datasets préprocessés sauvegardés localement
- Fonctions de prétraitement réutilisables
- Documentation du format des données

---

### Phase 2 : Entraînement des Modèles (Semaine 3-5)

#### Étape 2.1 : Fine-tuning de mT5-small

**Actions :**
- Chargement du modèle pré-entraîné `google/mt5-small` (~300M paramètres)
- Configuration des hyperparamètres d'entraînement
- Entraînement sur MLSUM-FR avec validation périodique
- Sauvegarde des checkpoints et du modèle final

**Configuration :**
- Taille de batch : 8 (avec accumulation de gradient = batch effectif de 32)
- Taux d'apprentissage : 5e-5
- Nombre d'époques : 3
- Optimisations mémoire : FP16, gradient checkpointing

**Justification :**
- **mT5-small** : Modèle léger adapté aux ressources limitées (Colab gratuit). Permet de valider rapidement la méthodologie et sert de baseline pour les comparaisons.
- Les optimisations mémoire permettent l'entraînement sur GPU gratuit tout en maintenant la qualité.

**Livrables :**
- Modèle fine-tuné sauvegardé (`models/mt5_small_finetuned/`)
- Logs d'entraînement et métriques
- Notebook d'entraînement documenté (`02_mt5_small_training.ipynb`)

#### Étape 2.2 : Fine-tuning de mT5-base

**Actions :**
- Chargement du modèle `google/mt5-base` (~580M paramètres)
- Application de LoRA (Low-Rank Adaptation) pour réduire la mémoire
- Entraînement avec batch size réduit (4) et accumulation de gradient
- Comparaison avec mT5-small

**Configuration LoRA :**
- Rank : 8
- Alpha : 32
- Dropout : 0.1
- Modules ciblés : couches d'attention (q, v, k, o)

**Justification :**
- **mT5-base** : Modèle plus performant que mT5-small, offrant un meilleur équilibre entre qualité et ressources. La technique LoRA permet de fine-tuner efficacement sans nécessiter de GPU haute performance.
- Cette approche démontre l'utilisation de méthodes d'adaptation paramétriquement efficaces, pertinentes pour les contraintes computationnelles réelles.

**Livrables :**
- Modèle fine-tuné avec LoRA (`models/mt5_base_finetuned/`)
- Analyse de l'impact de LoRA sur les performances
- Notebook d'entraînement (`03_mt5_base_training.ipynb`)

#### Étape 2.3 : Fine-tuning de BART

**Actions :**
- Chargement du modèle `facebook/mbart-large-cc25` (multilingue incluant le français)
- Adaptation du format de données pour BART
- Entraînement avec paramètres similaires aux modèles mT5
- Comparaison avec les modèles mT5

**Justification :**
- **BART** : Architecture différente (encodeur-décodeur) permettant de comparer différentes approches architecturales. mBART est pré-entraîné sur plusieurs langues incluant le français, offrant une base solide.
- La comparaison entre architectures (T5 vs BART) enrichit l'analyse et permet d'identifier les forces de chaque approche.

**Livrables :**
- Modèle BART fine-tuné (`models/bart_finetuned/`)
- Notebook d'entraînement (`04_bart_training.ipynb`)

---

### Phase 3 : Évaluation et Comparaison (Semaine 6-7)

#### Étape 3.1 : Évaluation Quantitative

**Actions :**
- Chargement des trois modèles fine-tunés
- Génération de résumés sur l'ensemble de test
- Calcul des métriques automatiques :
  - ROUGE-1, ROUGE-2, ROUGE-L (précision, rappel, F1)
  - BLEU score
  - BERTScore (similarité sémantique)
- Mesure du temps d'inférence et de la consommation mémoire

**Justification :**
- Les métriques multiples permettent une évaluation complète : ROUGE mesure le chevauchement lexical, BLEU évalue la qualité de traduction, et BERTScore capture la similarité sémantique. Cette combinaison offre une vision multidimensionnelle de la qualité.
- L'analyse des ressources (temps, mémoire) est cruciale pour évaluer la faisabilité de déploiement en production.

**Livrables :**
- Tableaux comparatifs des métriques
- Fichiers CSV/JSON avec résultats détaillés
- Notebook d'évaluation (`05_model_evaluation.ipynb`)

#### Étape 3.2 : Analyse Comparative Approfondie

**Actions :**
- Analyse qualitative avec exemples concrets
- Catégorisation des erreurs (hallucinations, omissions, répétitions)
- Comparaison des performances par domaine (news vs éducatif)
- Visualisations des résultats (graphiques, tableaux comparatifs)

**Justification :**
- L'analyse qualitative complète les métriques automatiques en identifiant les types d'erreurs spécifiques à chaque modèle. Cette analyse guide les améliorations futures.
- La comparaison domaine-spécifique évalue la capacité de généralisation et d'adaptation des modèles.

**Livrables :**
- Rapport d'analyse comparative
- Exemples annotés de résumés générés
- Visualisations pour le rapport final
- Notebook d'analyse (`06_model_comparison.ipynb`)

---

### Phase 4 : Développement de l'Application Interactive (Semaine 8-9)

#### Étape 4.1 : Application Streamlit

**Actions :**
- Développement de l'interface utilisateur avec Streamlit
- Intégration des trois modèles fine-tunés
- Implémentation de la génération de résumés en temps réel
- Ajout de contrôles pour les paramètres de génération (longueur, température, beams)

**Fonctionnalités :**
- Page d'accueil avec présentation du projet
- Page de résumé avec sélection de modèle
- Page de comparaison multi-modèles
- Visualisation des métriques de performance

**Justification :**
- Une application interactive démontre concrètement les résultats du projet et facilite l'évaluation qualitative par des utilisateurs non techniques.
- L'interface permet d'explorer l'impact des différents paramètres de génération, enrichissant la compréhension du comportement des modèles.

**Livrables :**
- Application Streamlit fonctionnelle (`app/streamlit_app.py`)
- Documentation d'utilisation
- Guide de déploiement

#### Étape 4.2 : Optimisations et Tests

**Actions :**
- Optimisation du chargement des modèles (caching)
- Gestion des erreurs et états de chargement
- Tests de l'application avec différents textes
- Amélioration de l'expérience utilisateur

**Justification :**
- Les optimisations garantissent une expérience utilisateur fluide malgré la taille des modèles. Le caching évite de recharger les modèles à chaque requête.
- Les tests permettent d'identifier et corriger les problèmes avant la démonstration finale.

**Livrables :**
- Application optimisée et testée
- Rapport de tests

---

### Phase 5 : Documentation et Rapport Final (Semaine 10)

#### Étape 5.1 : Documentation Technique

**Actions :**
- Documentation complète du code source
- README avec instructions d'installation et d'utilisation
- Commentaires dans les notebooks
- Guide de reproduction des résultats

**Justification :**
- Une documentation complète garantit la reproductibilité du projet, critère essentiel en recherche. Elle facilite également la maintenance et l'extension future du travail.

**Livrables :**
- README.md complet
- Documentation du code
- Guide de reproduction

#### Étape 5.2 : Rédaction du Rapport

**Actions :**
- Mise à jour du rapport avec les résultats expérimentaux
- Analyse et interprétation des résultats
- Discussion des limitations et perspectives futures
- Préparation de la présentation finale

**Justification :**
- Le rapport final synthétise tout le travail effectué et présente les contributions du projet. L'analyse critique des résultats et l'identification des limitations démontrent une compréhension approfondie du sujet.

**Livrables :**
- Rapport de mémoire complet et mis à jour
- Présentation PowerPoint
- Code source final organisé

---

## 3. Justification des Choix Techniques

### 3.1 Choix des Modèles

**mT5-small et mT5-base :**
- Architectures T5 spécialement conçues pour les tâches de génération de texte
- Pré-entraînement multilingue incluant le français
- Architecture encodeur-décodeur adaptée au résumé
- Différentes tailles permettant d'évaluer le compromis performance/ressources

**BART :**
- Architecture différente permettant la comparaison
- Pré-entraînement sur dénoisage de texte, particulièrement adapté au résumé
- Support multilingue avec mBART

### 3.2 Choix des Datasets

**MLSUM-FR :**
- Corpus volumineux (425K exemples) permettant un entraînement robuste
- Résumés de qualité professionnelle
- Diversité thématique favorisant la généralisation

**ALECTOR :**
- Corpus spécialisé éducatif pour l'adaptation de domaine
- Permet d'évaluer la capacité de transfert des modèles

### 3.3 Techniques d'Optimisation

**LoRA :**
- Réduction significative de la mémoire nécessaire
- Entraînement efficace sur ressources limitées
- Technique moderne et pertinente pour l'industrie

**FP16 et Gradient Checkpointing :**
- Permet l'entraînement sur GPU gratuit (Colab)
- Réduction de la consommation mémoire sans perte significative de qualité

### 3.4 Métriques d'Évaluation

**ROUGE :**
- Standard de l'industrie pour l'évaluation de résumés
- Mesure le chevauchement lexical avec les résumés de référence

**BLEU :**
- Métrique complémentaire évaluant la qualité de génération
- Permet la comparaison avec d'autres travaux

**BERTScore :**
- Capture la similarité sémantique au-delà du lexique
- Évalue la qualité sémantique des résumés générés

---

## 4. Planning et Jalons

| Phase | Semaine | Activités Principales | Jalons |
|-------|---------|----------------------|--------|
| **Phase 1** | 1-2 | Préparation données, exploration | Datasets préprocessés prêts |
| **Phase 2** | 3-5 | Entraînement des 3 modèles | 3 modèles fine-tunés sauvegardés |
| **Phase 3** | 6-7 | Évaluation et comparaison | Résultats d'évaluation complets |
| **Phase 4** | 8-9 | Développement application | Application Streamlit fonctionnelle |
| **Phase 5** | 10 | Documentation et rapport | Rapport final et présentation |

---

## 5. Risques et Mitigation

### 5.1 Risques Identifiés

1. **Ressources computationnelles limitées**
   - *Mitigation* : Utilisation de LoRA, FP16, et modèles de taille modérée

2. **Problèmes de chargement de datasets**
   - *Mitigation* : Solutions alternatives (downgrade datasets library si nécessaire)

3. **Temps d'entraînement long**
   - *Mitigation* : Utilisation de Colab Pro si nécessaire, ou entraînement sur sous-ensemble

4. **Qualité des résumés insuffisante**
   - *Mitigation* : Ajustement des hyperparamètres, augmentation du nombre d'époques si nécessaire

### 5.2 Contingences

- Si l'entraînement complet n'est pas possible, focus sur mT5-small et mT5-base
- Si ALECTOR n'est pas disponible, évaluation uniquement sur MLSUM-FR avec mention dans le rapport
- Si problèmes techniques majeurs, utilisation de modèles pré-entraînés disponibles avec analyse comparative

---

## 6. Livrables Finaux

1. **Code Source**
   - 6 notebooks Jupyter (préparation, 3 entraînements, évaluation, comparaison)
   - Code source Python organisé (`src/`)
   - Application Streamlit complète (`app/`)

2. **Modèles**
   - 3 modèles fine-tunés sauvegardés
   - Configurations et hyperparamètres documentés

3. **Résultats**
   - Fichiers d'évaluation (CSV/JSON)
   - Visualisations et graphiques
   - Exemples de résumés générés

4. **Documentation**
   - Rapport de mémoire complet
   - README avec instructions
   - Présentation finale

---

## 7. Conclusion

Ce plan de travail structure le projet en phases claires et justifiées, permettant un développement méthodique et rigoureux. L'approche hybride combinant corpus généraliste (MLSUM-FR) et spécialisé (ALECTOR) garantit à la fois la généralisation et l'adaptation au domaine éducatif. La comparaison de trois architectures différentes enrichit l'analyse et les contributions du projet.

Les techniques d'optimisation (LoRA, FP16) démontrent la capacité à travailler avec des contraintes computationnelles réelles, compétence essentielle pour le déploiement en production.

---

**Date de soumission :** [Date]  
**Signature de l'étudiant :** _________________  
**Signature du superviseur :** _________________