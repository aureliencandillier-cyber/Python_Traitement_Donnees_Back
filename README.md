# Ticket Management System - Backend

Ce projet concerne la création d'une infrastructure backend 
complète pour la gestion de tickets de support technique. 
Il combine manipulation de données brutes et API REST.

---

## Sommaire
1. [Objectifs du projet](#-objectifs-du-projet)
2. [Structure des fichiers](#-structure-des-fichiers)
3. [Installation rapide](#-installation-rapide)
4. [Détails du traitement de données](#-détails-du-traitement-de-données)
5. [Documentation de l'API](#-documentation-de-lapi)
6. [Méthodologie de travail](#-méthodologie-de-travail)

---

## Objectifs du projet

Ce projet s'inscrit dans un cadre d'apprentissage pratique :
* **Traitement de données** : Automatiser des calculs 
  sur un fichier JSON via Python.
* **Architecture API** : Transformer ces traitements 
  en services web accessibles via FastAPI.
* **Apprentissage LLM** : Utiliser l'IA pour monter en 
  compétence et résoudre des bugs complexes.
* **Pair Programming** : Alterner les rôles de 
  Développeur et de Guide chaque heure.

---

## Structure des fichiers

Le dépôt est organisé comme suit :

* `tickets.json` : Notre base de données plate 
  contenant au moins 10 tickets structurés.
* `script.py` : Le moteur logique qui traite 
  et manipule les tickets en Python.
* `main.py` : L'interface FastAPI qui expose 
  les données au monde extérieur.
* `LEARNING.md` : Le journal de bord de nos 
  interactions avec le LLM.

---

## Installation rapide

### 1. Prérequis
Vous devez disposer de **Python 3.10+** et de l'outil **pip**.

### 2. Installation des dépendances
Exécutez la commande suivante pour installer 
le framework et le serveur :

pip install fastapi uvicorn
Lancement du serveur
Démarrez l'API en mode développement :

bash
uvicorn main:app --reload
Le serveur écoute sur : http://127.0.0.1:8000

Détails du traitement de données
Le fichier script.py contient la logique métier critique. Il permet de :

Lire l'intégralité du fichier JSON.

Calculer les statistiques : Nombre de tickets "ouverts", "en cours" et "fermés".

Filtrer et Trier les données selon la priorité ou l'ID.

Ajouter / Mettre à jour : Fonctions dédiées à la modification des tickets avec persistance immédiate dans le JSON.

Documentation de l'API
L'API suit les standards REST avec une gestion stricte des codes d'erreur HTTP.

Endpoints minimum implémentés :

Méthode	Route	Action	Code Succès

GET	/tickets	Liste tous les tickets	200

POST	/tickets	Création d'un ticket	201

PATCH	/tickets/{id}	Changer le statut	200

DELETE	/tickets/{id}	Supprimer un ticket	204

Note technique : L'API renvoie un code 404 si l'ID du ticket est inexistant et un code 400 si les données envoyées sont invalides.

