# Guide d'Intégration dans Overleaf

## Structure Recommandée

Pour intégrer vos chapitres dans Overleaf, vous avez deux options :

---

## ✅ OPTION 1 : Fichier Principal avec Inclusion (RECOMMANDÉE)

### Structure des fichiers dans Overleaf :

```
Votre Projet Overleaf/
├── main.tex                    (Fichier principal - à compiler)
├── Chapitre1_Introduction_et_État_de_l_Art.tex
├── Chapitre2_Fondements_Theoriques_TAL_et_Resume.tex
└── (autres chapitres à venir)
```

### Étapes :

1. **Créez `main.tex`** dans Overleaf (déjà créé pour vous)

2. **Modifiez `Chapitre1_Introduction_et_État_de_l_Art.tex`** :
   - **SUPPRIMEZ** les lignes 1-58 (tout le préambule jusqu'à `\begin{document}`)
   - **SUPPRIMEZ** la ligne `\begin{document}`
   - **GARDEZ** tout le contenu du chapitre (à partir de `\chapter{...}`)
   - **SUPPRIMEZ** la bibliographie à la fin (lignes 374-409) - on la mettra dans le fichier principal
   - **SUPPRIMEZ** `\end{document}` à la fin

3. **Modifiez `Chapitre2_Fondements_Theoriques_TAL_et_Resume.tex`** :
   - **SUPPRIMEZ** les lignes 1-58 (tout le préambule jusqu'à `\begin{document}`)
   - **SUPPRIMEZ** la ligne `\begin{document}`
   - **GARDEZ** tout le contenu du chapitre (à partir de `\chapter{...}`)
   - **SUPPRIMEZ** la bibliographie à la fin
   - **SUPPRIMEZ** `\end{document}` à la fin

4. **Dans Overleaf** :
   - Définissez `main.tex` comme fichier principal (Menu → Compiler → Fichier principal)
   - Compilez `main.tex`

### Avantages :
- ✅ Structure modulaire et organisée
- ✅ Facile d'ajouter/supprimer des chapitres
- ✅ Une seule bibliographie à la fin
- ✅ Numérotation continue des pages et chapitres

---

## ⚠️ OPTION 2 : Documents Séparés (Alternative)

Si vous préférez garder chaque chapitre comme document autonome :

1. **Gardez chaque chapitre tel quel** (avec `\documentclass`, `\begin{document}`, etc.)
2. **Compilez chaque chapitre séparément** dans Overleaf
3. **Utilisez `pdfpages`** pour combiner les PDFs à la fin

### Dans `main.tex` (modifié) :

```latex
\documentclass[12pt,a4paper]{report}
\usepackage{pdfpages}

\begin{document}
\includepdf[pages=-]{Chapitre1_Introduction_et_État_de_l_Art.pdf}
\includepdf[pages=-]{Chapitre2_Fondements_Theoriques_TAL_et_Resume.pdf}
\end{document}
```

### Inconvénients :
- ❌ Numérotation des pages non continue
- ❌ Table des matières non automatique
- ❌ Plus difficile à gérer

---

## 📝 Instructions Détaillées pour l'Option 1

### Pour Chapitre 1 :

**À SUPPRIMER :**
- Lignes 1-58 : Tout le préambule
- Ligne 59 : `\begin{document}`
- Lignes 374-409 : La bibliographie (on la mettra dans `main.tex`)
- Dernière ligne : `\end{document}`

**À GARDER :**
- Tout le reste (à partir de `\chapter{Introduction et État de l'Art...}`)

### Pour Chapitre 2 :

**À SUPPRIMER :**
- Lignes 1-58 : Tout le préambule
- Ligne 59 : `\begin{document}`
- La bibliographie à la fin
- Dernière ligne : `\end{document}`

**À GARDER :**
- Tout le reste (à partir de `\chapter{Fondements Théoriques...}`)

---

## 🔧 Configuration dans Overleaf

1. **Téléchargez tous les fichiers** dans votre projet Overleaf
2. **Définissez `main.tex` comme fichier principal** :
   - Menu → Compiler → Fichier principal → `main.tex`
3. **Compilez** : Cliquez sur "Recompiler"

---

## 📚 Bibliographie Unifiée

Pour une bibliographie unifiée à la fin du document, vous pouvez :

1. **Créer un fichier `references.bib`** avec toutes les références
2. **Utiliser BibTeX** dans `main.tex` :
   ```latex
   \bibliographystyle{plain}
   \bibliography{references}
   ```

OU

3. **Garder les bibliographies dans chaque chapitre** (moins élégant mais fonctionne)

---

## ✅ Vérification

Après modification, votre `Chapitre1_Introduction_et_État_de_l_Art.tex` devrait commencer par :
```latex
\chapter{Introduction et État de l'Art sur les Transformateurs}
```

Et votre `Chapitre2_Fondements_Theoriques_TAL_et_Resume.tex` devrait commencer par :
```latex
\chapter{Fondements Théoriques du Traitement Automatique des Langues et du Résumé Automatique}
```

---

## 🆘 En cas de problème

Si vous avez des erreurs de compilation :
1. Vérifiez que tous les packages sont dans `main.tex`
2. Vérifiez qu'il n'y a pas de `\documentclass` ou `\begin{document}` dans les chapitres
3. Vérifiez que les chemins des fichiers sont corrects dans `\input{}`

