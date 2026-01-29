# LEARNING.md - Journal d'Apprentissage Fullstack

Ce document retrace le processus de développement, les obstacles techniques rencontrés et la collaboration avec l'IA pour la réalisation du Ticketing System.

---

## 1. Prompts Clés Utilisés

Voici trois exemples de prompts structurants qui ont permis de faire évoluer l'application :

### A. Implémentation de règles métier (Cycle de vie du ticket)
> **Prompt :** *"Je veux que lorsqu'un ticket est closed qu'il ne puisse plus être réouvert et le bouton 'supprimer' de sa case devienne 'SOLDER'"*
* **Résultat :** L'IA a intégré une condition `disabled={isClosed}` sur le selecteur et une condition ternaire sur le texte du bouton.
* **Apprentissage :** Comment traduire une règle de gestion ("ne plus rouvrir") en contrainte d'interface utilisateur (désactivation d'input).

### B. Évolution vers des filtres complexes (Itération)
> **Prompt :** *"revois ta zone de filtre. Je veux pouvoir filtrer selon le statut, la priorité ou par la description (exemple: si je mets "Ordinateur", qu'il affiche TOUS les tickets où le mot "Ordinateur" apparait en description)"*
* **Résultat :** Passage d'un filtre simple à un constructeur de filtres dynamiques qui adapte l'interface (menu déroulant vs champ texte) selon le critère choisi.
* **Apprentissage :** Gestion de conditions multiples dans la fonction `.filter()` de JavaScript (logique AND).

### C. Déploiement et Versionning (Git)
> **Prompt :** *"Ok, maintenant je veux push la partie frontend (...) et UNIQUEMENT la partie frontend. Indique moi comment, pas à pas"*
* **Résultat :** Procédure pour initialiser un dépôt Git dans un sous-dossier spécifique sans inclure le backend ni les `node_modules`.

---

## 2. Erreurs Rencontrées et Solutions

### Erreur #1 : Problème de PATH Python sur Windows
* **Le Bug :**
    ```powershell
    uvicorn : Le terme «uvicorn» n'est pas reconnu comme nom d'applet de commande...
    ```
* **L'Analyse :** Même si la librairie était installée, Windows ne trouvait pas l'exécutable car le dossier `Scripts` de Python n'était pas dans les variables d'environnement.
* **La Correction :** Au lieu d'essayer de réparer le PATH Windows (complexe), nous avons contourné le problème en appelant le module via l'exécutable Python :
    `py -m uvicorn main:app --reload`

### Erreur #2 : Vite 404 Not Found au lancement
* **Le Bug :** Le serveur se lançait (`npm run dev`), mais affichait une page blanche avec une erreur 404, car il ne trouvait pas `index.html`.
* **L'Analyse :** Le fichier `index.html` était manquant ou mal placé (dans `src/` au lieu de la racine), ou masqué par la synchronisation OneDrive.
* **La Correction :**
    1. Création manuelle d'un `index.html` propre à la racine du projet.
    2. Liaison correcte avec le point d'entrée React : `<script type="module" src="/src/main.jsx"></script>`.

---

## 3. Erreur de l'IA et Vérification Humaine

C'est l'exemple le plus flagrant où la logique "par défaut" de l'IA a échoué face à la logique "métier".

* **Le Contexte :** J'ai demandé à l'IA d'implémenter un tri par **Priorité**.
* **L'Erreur de l'IA :** Le code généré utilisait un tri alphabétique standard (`localeCompare`).
    * Résultat du tri IA : **H**igh -> **L**ow -> **M**edium (Ordre alphabétique).
* **Ma Vérification :** J'ai testé l'application et remarqué que les tickets "Low" passaient avant les "Medium", ce qui est illogique pour une gestion d'urgence.
* **Mon Feedback :** *"Attention, ton tri par priorité fait un tri avec High > Low > Medium"*
* **La Correction :** Nous avons dû implémenter un système de **poids numériques** pour forcer l'ordre sémantique :
    ```javascript
    const priorityWeights = { 'High': 1, 'Medium': 2, 'Low': 3 };
    // Tri basé sur la soustraction des poids
    return priorityWeights[a.priority] - priorityWeights[b.priority];
    ```

---

## Synthèse des Apprentissages

1.  **Architecture Fullstack :** Compréhension claire que le Frontend (Port 5173) et le Backend (Port 8000) sont deux programmes distincts qui communiquent par HTTP.
2.  **Rigueur des Données :** L'importance de transformer des données textuelles (High, Medium) en données numériques (1, 2) pour les traiter logiquement.
3.  **Environnement de Dév :** La nécessité de maîtriser son terminal (PowerShell) et de comprendre où sont installés les outils (`node_modules`, `pip`).
