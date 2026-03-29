# Chapitre I : Introduction et État de l'Art sur les Transformateurs

## I. Introduction Générale

### 1.1 Contexte et Motivation

L'émergence des architectures Transformer, introduites par Vaswani et al. en 2017 dans leur article fondateur "Attention Is All You Need", a profondément transformé le paysage du traitement automatique des langues (TAL). Ces architectures révolutionnaires, incarnées par des modèles emblématiques tels que BERT (Devlin et al., 2018), GPT (Radford et al., 2018), T5 (Raffel et al., 2019) et Mistral (Jiang et al., 2023), offrent des performances remarquables en matière de compréhension et de génération textuelle, ouvrant des perspectives prometteuses pour de nombreux domaines d'application.

Dans le contexte francophone, des modèles pré-entraînés tels que FrenchGPT et Mistral constituent des fondations solides pour le traitement du français. Néanmoins, leur adaptation à des tâches pédagogiques fines, telles que la génération automatique de résumés et de questions dans un contexte éducatif, soulève des défis considérables. La richesse morphosyntaxique du français, caractérisée par des systèmes d'accords complexes, une variation importante des registres de langue et des structures syntaxiques élaborées, exige des modèles capables de saisir ces subtilités linguistiques avec précision.

La génération automatique de résumés, tâche centrale dans l'enseignement et l'apprentissage, requiert non seulement une compréhension approfondie du contenu source, mais également la capacité à produire des textes cohérents, concis et fidèles sémantiquement. Or, les approches traditionnelles de résumé automatique présentent des limitations significatives en termes d'adaptation contextuelle, de cohérence sémantique et de pertinence pédagogique.

Par ailleurs, le manque criant de corpus annotés spécifiquement conçus pour la génération de résumés en contexte éducatif francophone constitue un obstacle majeur. Les benchmarks existants privilégient généralement des critères techniques au détriment de considérations pédagogiques et ne reflètent pas la diversité des profils d'apprenants ni la variabilité des attentes curriculaires.

Enfin, l'intégration de ces technologies en milieu scolaire impose des exigences strictes en termes d'interprétabilité, d'équité et de transparence algorithmique. Les enseignants et les élèves doivent pouvoir comprendre les générations produites et s'assurer que les systèmes ne reproduisent pas de biais linguistiques ou sociaux susceptibles de pénaliser certains groupes d'apprenants.

Face à ces constats, le présent travail vise à explorer le potentiel du fine-tuning de modèles Transformer francophones pour la génération automatique de résumés en contexte éducatif, en développant une approche qui conjugue performance technique, pertinence pédagogique et responsabilité éthique.

### 1.2 Problématique

La génération automatique de texte en contexte éducatif français représente un défi majeur pour l'enseignement et l'apprentissage assisté par l'intelligence artificielle. Les approches traditionnelles de résumé automatique et de génération de questions présentent des limitations significatives en termes d'adaptation contextuelle, de cohérence sémantique et de pertinence pédagogique. Face à la rareté des ressources spécialisées en français et à la complexité des besoins éducatifs, le développement de modèles capables de produire des contenus pédagogiques de qualité devient une nécessité.

Dans ce contexte, l'application des modèles de langage de type Transformer au domaine éducatif francophone ouvre des perspectives prometteuses, mais soulève plusieurs questions fondamentales :

**Comment adapter et spécialiser des modèles de langage de type Transformer pour la génération contextuelle de texte en français, notamment le résumé automatique et la génération de questions dépendantes du même texte, tout en assurant la cohérence sémantique, la pertinence éducative et l'efficacité computationnelle du modèle ?**

### 1.3 Objectifs de la Recherche

#### Objectif Général

Développer et valider un système de génération de texte éducatif francophone, fondé sur l'architecture Transformer et spécialisé grâce à des techniques de fine-tuning efficaces, capable de produire automatiquement des résumés contextuels et des questions pédagogiques cohérentes à partir d'un même texte source, avec des applications directes dans l'analyse linguistique et les environnements d'apprentissage.

#### Objectifs Spécifiques

1. **Adaptation et spécialisation du modèle de langage**
   - Implémenter un fine-tuning efficace de modèles Transformer (mT5-small, mT5-base, BART) sur des corpus francophones spécialisés
   - Optimiser les hyperparamètres d'entraînement pour maximiser les performances en génération de texte en français
   - Adapter l'architecture du modèle aux spécificités linguistiques et stylistiques du français éducatif

2. **Développement d'un pipeline multitâche intégré**
   - Concevoir et mettre en œuvre un système unifié de génération combinée de résumés et de questions
   - Établir des mécanismes de préservation de la cohérence sémantique entre les résumés générés et les questions associées
   - Implémenter des contraintes de génération pour assurer la pertinence pédagogique des outputs

3. **Évaluation multidimensionnelle des performances**
   - Mesurer la qualité technique via des métriques automatiques (ROUGE, BLEU, BERTScore)
   - Évaluer la pertinence pédagogique à travers des protocoles d'analyse qualitative avec des experts du domaine éducatif
   - Tester la robustesse linguistique sur différents registres de français (académique, journalistique, littéraire)

4. **Validation de la généralisation et optimisation**
   - Tester la capacité de généralisation du modèle sur divers domaines thématiques (éducation, actualité, littérature, sciences)
   - Analyser les performances cross-domain et identifier les limites de transfert
   - Proposer des améliorations architecturales et méthodologiques pour réduire les coûts computationnels tout en maintenant la qualité

---

## II. État de l'Art sur les Transformateurs

### 2.1 Introduction aux Transformateurs

Les transformateurs ont révolutionné le domaine du traitement automatique du langage naturel (TALN) en offrant des performances inégalées dans diverses tâches linguistiques. Introduits par Vaswani et al. en 2017, les transformateurs sont des architectures de réseaux neuronaux conçues pour traiter des séquences de données, notamment le texte, en exploitant des mécanismes d'attention. Contrairement aux réseaux neuronaux récurrents (RNN) qui traitent les données de manière séquentielle, les transformateurs permettent un traitement parallèle des séquences, améliorant ainsi l'efficacité et la capacité à capturer des dépendances à long terme dans les données.

Un **Transformer** est un modèle d'apprentissage profond qui adopte le mécanisme d'attention, pondérant différemment l'importance de chaque partie des données d'entrée. Il est utilisé principalement dans le domaine du traitement automatique du langage naturel (TALN) et en vision par ordinateur. Il s'agit d'un modèle d'apprentissage profond dans lequel chaque sortie est connectée à chaque élément et où les pondérations entre eux sont calculées dynamiquement en fonction de leurs connexions.

### 2.2 Pourquoi les Transformateurs dans le TALN ?

La comparaison entre les architectures CNN, RNN et Transformers révèle que les Transformers sont le meilleur modèle pour traiter de grandes séquences en TALN. Les RNN et CNN peuvent traiter de courtes séquences mais ne sont pas efficaces pour traiter de grandes séquences. Les Transformers résolvent plusieurs problèmes fondamentaux des architectures précédentes :

1. **Problème du gradient qui disparaît** : Contrairement aux RNN qui souffrent de la perte d'information sur de longues séquences, les Transformers peuvent capturer des dépendances à très long terme grâce au mécanisme d'attention.

2. **Traitement parallèle** : Contrairement aux RNN qui traitent les séquences séquentiellement, les Transformers permettent un traitement parallèle de tous les tokens, réduisant considérablement le temps d'entraînement.

3. **Capacité de modélisation** : Les Transformers peuvent modéliser des relations complexes entre tous les éléments d'une séquence simultanément, sans être limités par la distance temporelle.

### 2.3 Architecture Fondamentale des Transformateurs

#### 2.3.1 Principe Fondamental : "Attention Is All You Need"

Le principe fondamental des Transformers repose sur le mécanisme d'attention, résumé par la célèbre phrase "Attention is all you need". Ce mécanisme permet au modèle de se concentrer sur les parties pertinentes de l'entrée lors du traitement de chaque élément.

#### 2.3.2 Mécanismes d'Attention

**Attention :**
Les Transformers apprennent à pondérer la relation entre chaque élément d'entrée et chaque élément de sortie. Cela permet au modèle de déterminer quels éléments de l'entrée sont les plus importants pour générer chaque élément de sortie.

**Auto-Attention (Self-Attention) :**
Les Transformers apprennent à pondérer la relation entre chaque élément de la séquence d'entrée et tous les autres éléments de la séquence de sortie. Il s'agit d'une relation "Un-vers-plusieurs" où chaque token peut "regarder" tous les autres tokens de la séquence.

**Multi-Head Self-Attention :**
Les Transformers apprennent plusieurs façons de pondérer la relation de chaque élément de la séquence d'entrée avec tous les autres éléments de l'entrée. Il s'agit d'une relation "Plusieurs-vers-plusieurs" où le modèle peut capturer différents types de relations simultanément.

#### 2.3.3 Composants Principaux de l'Architecture

L'architecture Transformer se compose de trois parties principales :

**1. Encodeur (Encoder) :**
Les encodeurs sont identiques en structure. Chaque encodeur consiste en une couche d'auto-attention multi-têtes et un réseau feed-forward. Les entrées de l'encodeur passent d'abord par une couche d'auto-attention — une couche qui aide l'encodeur à regarder les autres mots de la phrase d'entrée lorsqu'il encode un mot spécifique. Les sorties de la couche d'auto-attention sont ensuite transmises à un réseau de neurones feed-forward. Le même réseau feed-forward est appliqué indépendamment à chaque position.

**2. Décodeur (Decoder) :**
Les décodeurs sont également identiques en structure. Chaque décodeur consiste en une couche d'auto-attention, une couche d'attention encodeur-décodeur et une couche feed-forward. La couche d'attention encodeur-décodeur aide le décodeur à se concentrer sur les endroits appropriés de la séquence d'entrée. La couche d'auto-attention du décodeur est modifiée pour éviter d'assister aux positions suivantes (masquage causal).

**3. Embeddings :**
Les embeddings sont des représentations numériques des mots, généralement sous forme de vecteurs. Ces vecteurs permettent de représenter le sens sémantique et syntaxique des mots dans un espace vectoriel continu.

### 2.4 Classification des Modèles de Langage Transformer

Les modèles Transformer peuvent être classés en plusieurs catégories selon leur architecture et leur méthode de pré-entraînement :

#### 2.4.1 Modèles Autoregressifs

Ces modèles s'appuient sur la partie décodeur du Transformer original et utilisent un masque d'attention pour qu'à chaque position, le modèle ne puisse regarder que les tokens précédents. Les modèles autoregressifs sont optimisés pour la génération de texte séquentielle.

**Exemples :**
- **GPT (Generative Pre-trained Transformer)** : Modèle unidirectionnel qui génère du texte de gauche à droite
- **GPT-2, GPT-3, GPT-4** : Évolutions successives avec des capacités croissantes
- **Mistral 7B** : Modèle français autoregressif optimisé pour le français

#### 2.4.2 Modèles Auto-Encodage (Autoencoding)

Ces modèles s'appuient sur la partie encodeur du Transformer original et n'utilisent pas de masque, permettant au modèle de regarder tous les tokens dans les têtes d'attention. Pour le pré-entraînement, les cibles sont les phrases originales et les entrées sont leurs versions corrompues.

**Exemples :**
- **BERT (Bidirectional Encoder Representations from Transformers)** : Modèle bidirectionnel qui peut voir tout le contexte simultanément
- **RoBERTa** : Version améliorée de BERT avec un pré-entraînement optimisé
- **CamemBERT** : Variante française de BERT

#### 2.4.3 Modèles Sequence-to-Sequence

Ces modèles conservent à la fois l'encodeur et le décodeur du Transformer original. Ils sont optimisés pour les tâches de transformation de séquences, telles que la traduction automatique et le résumé.

**Exemples :**
- **T5 (Text-To-Text Transfer Transformer)** : Modèle qui traite toutes les tâches comme une conversion texte-à-texte
- **mT5 (multilingual T5)** : Version multilingue de T5, incluant le français
- **BART (Bidirectional and Auto-Regressive Transformer)** : Modèle qui combine les avantages de BERT et GPT
- **mBART** : Version multilingue de BART

#### 2.4.4 Modèles Multimodaux

Ces modèles peuvent traiter plusieurs types de données simultanément (texte, images, audio). Ils n'ont généralement pas été pré-entraînés de manière auto-supervisée comme les autres modèles.

**Exemples :**
- **CLIP** : Modèle qui comprend les images et le texte
- **DALL-E** : Modèle de génération d'images à partir de texte

#### 2.4.5 Modèles Basés sur la Récupération (Retrieval-based)

Certains modèles utilisent la récupération de documents pendant le pré-entraînement et l'inférence pour des tâches telles que la réponse à des questions en domaine ouvert.

**Exemples :**
- **RAG (Retrieval-Augmented Generation)** : Modèle qui combine la récupération d'informations et la génération
- **REALM** : Modèle qui intègre la récupération dans le processus de pré-entraînement

### 2.5 Modèles Transformer pour le Français

#### 2.5.1 Modèles Pré-entraînés Francophones

**CamemBERT** (Martin et al., 2020) :
- Variante française de BERT
- Pré-entraîné sur un corpus français de 138 Go
- Disponible en versions base et large
- Performances excellentes sur les tâches de compréhension en français

**FlauBERT** (Le et al., 2020) :
- Modèle BERT pré-entraîné sur un corpus français diversifié
- Inclut des textes de Wikipédia, livres, actualités
- Optimisé pour le français métropolitain et variétés régionales

**mT5 (multilingual T5)** :
- Version multilingue de T5 incluant le français
- Modèle sequence-to-sequence optimisé pour la génération
- Disponible en versions small, base et large
- Adapté pour le résumé automatique en français

**mBART** :
- Version multilingue de BART
- Pré-entraîné sur 25 langues incluant le français
- Optimisé pour la génération de texte multilingue

**Mistral 7B** (Jiang et al., 2023) :
- Modèle autoregressif français de 7 milliards de paramètres
- Optimisé pour la génération de texte en français
- Architecture efficace permettant un entraînement et une inférence rapides

#### 2.5.2 Comparaison des Architectures pour le Résumé Automatique

Pour la tâche de résumé automatique en français, plusieurs architectures Transformer sont pertinentes :

**Modèles Encoder-Only (BERT, CamemBERT) :**
- Avantages : Excellente compréhension contextuelle bidirectionnelle
- Limites : Nécessitent une couche de classification supplémentaire pour la génération
- Utilisation : Principalement pour l'extraction de phrases ou la classification

**Modèles Decoder-Only (GPT, Mistral) :**
- Avantages : Génération naturelle de texte, apprentissage autoregressif
- Limites : Ne peuvent pas voir le contexte futur lors de la génération
- Utilisation : Génération de résumés avec fine-tuning

**Modèles Encoder-Decoder (T5, mT5, BART, mBART) :**
- Avantages : Architecture optimale pour les tâches sequence-to-sequence comme le résumé
- Capacité à comprendre l'entrée (encodeur) et générer la sortie (décodeur)
- Utilisation : Standard pour le résumé automatique

### 2.6 Techniques d'Adaptation et de Fine-tuning

#### 2.6.1 Fine-tuning Complet

Le fine-tuning complet consiste à entraîner tous les paramètres du modèle pré-entraîné sur une tâche spécifique. Cette approche offre les meilleures performances mais nécessite des ressources computationnelles importantes.

#### 2.6.2 Techniques d'Adaptation Efficaces

**LoRA (Low-Rank Adaptation)** :
- Technique qui ajoute des matrices de faible rang au modèle au lieu de modifier tous les paramètres
- Réduit considérablement le nombre de paramètres à entraîner
- Maintient des performances proches du fine-tuning complet

**QLoRA (Quantized LoRA)** :
- Combine la quantification (réduction de précision) avec LoRA
- Permet d'entraîner de très grands modèles sur des GPU limités
- Essentiel pour l'entraînement de modèles comme Mistral 7B sur des ressources limitées

**Adapter Layers** :
- Ajoute des couches d'adaptation spécifiques à la tâche
- Permet de partager un modèle de base entre plusieurs tâches
- Efficace en termes de mémoire et de stockage

### 2.7 Applications des Transformers en TALN

Les Transformers ont révolutionné de nombreuses tâches en TALN :

1. **Résumé Automatique** : Les modèles comme T5, BART et mT5 ont atteint des performances state-of-the-art
2. **Traduction Automatique** : Les modèles sequence-to-sequence ont considérablement amélioré la qualité des traductions
3. **Réponse aux Questions** : BERT et ses variantes ont transformé cette tâche
4. **Classification de Texte** : Les représentations contextuelles ont amélioré toutes les tâches de classification
5. **Génération de Texte** : GPT et ses successeurs ont montré des capacités impressionnantes de génération

### 2.8 Défis et Limitations

Malgré leurs succès, les Transformers présentent plusieurs défis :

1. **Coût Computationnel** : L'entraînement de grands modèles nécessite des ressources importantes
2. **Besoins en Données** : Requièrent de grands corpus pour le pré-entraînement
3. **Interprétabilité** : Les mécanismes internes restent difficiles à comprendre
4. **Biais** : Peuvent amplifier les biais présents dans les données d'entraînement
5. **Longueur de Séquence** : Limités par la longueur maximale de séquence (généralement 512-2048 tokens)

### 2.9 Évolutions Récentes et Tendances Futures

Les Transformers continuent d'évoluer avec :

1. **Modèles Plus Efficaces** : Réduction de la taille et du coût computationnel
2. **Longueurs de Séquence Étendues** : Techniques pour gérer des documents plus longs
3. **Multimodalité** : Intégration de différents types de données
4. **Apprentissage Continu** : Adaptation aux nouvelles données sans réentraînement complet
5. **Optimisation pour Ressources Limitées** : Techniques comme la distillation et la quantification

---

## Conclusion du Chapitre

Ce chapitre a présenté l'introduction générale du projet et l'état de l'art sur les architectures Transformer. Nous avons vu comment les Transformers ont révolutionné le TALN en résolvant les limitations des architectures précédentes et en permettant des performances exceptionnelles sur diverses tâches.

Pour notre projet de génération de résumés automatiques en français dans un contexte éducatif, les modèles sequence-to-sequence comme mT5 et BART apparaissent comme les choix les plus appropriés. Leur architecture encodeur-décodeur est optimale pour les tâches de transformation de séquences, et leur disponibilité en versions multilingues incluant le français les rend particulièrement adaptés à notre contexte.

Le chapitre suivant présentera les fondements théoriques du traitement automatique des langues et l'évolution des méthodes de résumé automatique.

---

## Références Bibliographiques (à compléter)

1. Vaswani, A., et al. (2017). "Attention is all you need." Advances in neural information processing systems, 30.

2. Devlin, J., et al. (2018). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." arXiv preprint arXiv:1810.04805.

3. Raffel, C., et al. (2019). "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer." Journal of Machine Learning Research, 21(140), 1-67.

4. Lewis, M., et al. (2020). "BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension." Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics.

5. Jiang, A. Q., et al. (2023). "Mistral 7B." arXiv preprint arXiv:2310.06825.

6. Martin, L., et al. (2020). "CamemBERT: a Tasty French Language Model." Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics.

7. Le, H., et al. (2020). "FlauBERT: Unsupervised Language Model Pre-training for French." Proceedings of the 12th Language Resources and Evaluation Conference.

8. Radford, A., et al. (2018). "Improving Language Understanding by Generative Pre-Training." OpenAI blog.

9. Radford, A., et al. (2019). "Language Models are Unsupervised Multitask Learners." OpenAI blog.

10. Brown, T., et al. (2020). "Language Models are Few-Shot Learners." Advances in neural information processing systems, 33.

---

**Note :** Ce chapitre constitue la première partie du rapport. Il sera suivi par les chapitres sur les fondements théoriques du TAL, l'état de l'art sur le résumé automatique, la méthodologie, l'implémentation et les résultats.

