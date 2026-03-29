# Guide de Compilation dans Overleaf

## Problème Résolu ✅

Le problème où seul le premier chapitre s'affichait était dû au fait que chaque fichier de chapitre contenait son propre préambule (`\documentclass`, `\begin{document}`, `\end{document}`), ce qui en faisait des documents complets indépendants au lieu de fichiers à inclure.

## Solution Appliquée

Tous les fichiers de chapitres ont été nettoyés :
- ✅ Suppression de `\documentclass` et de tout le préambule
- ✅ Suppression de `\begin{document}` et `\end{document}`
- ✅ Les chapitres commencent maintenant directement par `\chapter{...}`

## Structure du Projet dans Overleaf

```
Votre projet Overleaf/
├── main.tex                    ← Fichier principal (à compiler)
├── Chapitre1_Introduction_et_État_de_l_Art.tex
├── Chapitre2_Fondements_Theoriques_TAL_et_Resume.tex
└── Chapitre3_Methodologie_et_Conception.tex
```

## Étapes pour Compiler dans Overleaf

### 1. Vérifier que `main.tex` est le fichier principal

1. Dans Overleaf, cliquez sur le menu en haut à gauche (icône ☰)
2. Sélectionnez **"Main document"**
3. Choisissez **`main.tex`**

### 2. Compiler le document

1. Cliquez sur le bouton **"Recompile"** (ou utilisez Ctrl/Cmd + Enter)
2. Tous les chapitres devraient maintenant apparaître dans le PDF généré

### 3. Vérifier la Table des Matières

La table des matières devrait maintenant afficher :
- Chapitre 1 : Introduction et État de l'Art sur les Transformateurs
- Chapitre 2 : Fondements Théoriques du Traitement Automatique des Langues et du Résumé Automatique
- Chapitre 3 : Méthodologie et Conception du Système

## Structure du Fichier `main.tex`

Le fichier `main.tex` contient :
- Le préambule complet avec tous les packages nécessaires
- La configuration de la page, des titres, etc.
- Les commandes `\input{}` pour inclure chaque chapitre

```latex
\documentclass[12pt,a4paper]{report}
% ... préambule ...

\begin{document}
\maketitle
\tableofcontents

\input{Chapitre1_Introduction_et_État_de_l_Art}
\input{Chapitre2_Fondements_Theoriques_TAL_et_Resume}
\input{Chapitre3_Methodologie_et_Conception}

\end{document}
```

## Vérification

Si vous voyez toujours un problème :

1. **Vérifiez les erreurs de compilation** : Regardez le journal de compilation pour voir s'il y a des erreurs
2. **Vérifiez que les noms de fichiers correspondent** : Les noms dans `\input{}` doivent correspondre exactement aux noms des fichiers (sans l'extension `.tex`)
3. **Vérifiez que `main.tex` est bien défini comme document principal**

## Ajouter de Nouveaux Chapitres

Pour ajouter un nouveau chapitre (par exemple Chapitre 4) :

1. Créez le fichier `Chapitre4_...tex` (sans préambule, commençant directement par `\chapter{...}`)
2. Ajoutez `\input{Chapitre4_...}` dans `main.tex` après les autres chapitres

## Notes Importantes

- ⚠️ **Ne compilez jamais directement les fichiers de chapitres** - ils ne contiennent plus de préambule
- ✅ **Toujours compiler `main.tex`** - c'est le seul fichier qui doit être compilé
- ✅ Les bibliographies de chaque chapitre sont conservées dans leurs fichiers respectifs

## Résolution de Problèmes

### Si un chapitre ne s'affiche toujours pas :

1. Vérifiez qu'il n'y a pas d'erreurs de syntaxe dans le chapitre
2. Vérifiez que le nom du fichier dans `\input{}` correspond exactement au nom du fichier
3. Essayez de commenter temporairement les autres chapitres pour isoler le problème

### Si vous voyez des erreurs de packages :

Assurez-vous que tous les packages nécessaires sont dans le préambule de `main.tex` :
- `booktabs` et `tabularx` (pour les tableaux dans le Chapitre 3)

