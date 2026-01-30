⚙️ Ticketing System - Backend

Ce backend est une API REST robuste construite avec FastAPI. Il gère la persistance des données, la validation des modèles et la logique métier du système de gestion de tickets.
🏗️ Architecture

Le backend est divisé en deux modules principaux pour séparer les responsabilités :

    main.py : Point d'entrée de l'application FastAPI. Il gère les routes, le middleware CORS et la validation des données via Pydantic.

    script.py : Contient la logique métier "pure" (fonctions de tri, filtrage, calcul de stats) et la manipulation directe du fichier JSON.

🚀 Technologies utilisées

    Framework : FastAPI.

    Validation de données : Pydantic.

    Serveur ASGI : Uvicorn.

    Persistance : Fichier JSON (structure_ticket.json).

📡 Points de terminaison (API Endpoints)

L'API expose les routes suivantes pour permettre au Frontend de gérer les tickets :
Méthode	Route	Description
GET	/tickets	Récupère la liste complète des tickets.
GET	/tickets/{id}	Récupère un ticket spécifique par son ID (gère l'erreur 404).
POST	/tickets	Crée un nouveau ticket avec ID auto-incrémenté et date de création.
PATCH	/tickets/{id}	Met à jour uniquement le statut d'un ticket existant.
DELETE	/tickets/{id}	Supprime définitivement un ticket et met à jour le stockage.
💾 Gestion des données

    Persistance : Les données sont stockées de manière persistante dans structure_ticket.json.

    Validation : Chaque entrée est validée par le modèle TicketCreate (titre, description, priorité, statut, tags).

    Logique d'ID : Les identifiants sont générés automatiquement par incrémentation du dernier ID connu.

🛠️ Installation et Lancement

    Prérequis : Python 3.7+ installé.

    Installation des dépendances :
    PowerShell

    pip install fastapi uvicorn pydantic

    Lancement du serveur :
    PowerShell

    python -m uvicorn main:app --reload

    Le serveur sera accessible sur http://127.0.0.1:8000. La documentation interactive (Swagger) est disponible sur /docs.

🖥️ Mode Interface de Ligne de Commande (CLI)

Le module script.py peut être exécuté de manière autonome pour gérer les tickets directement dans le terminal. Il propose un menu interactif pour :

    Trier les tickets par critère (id, status, priority, etc.).

    Filtrer par valeur.

    Ajouter manuellement un ticket.

    Mettre à jour les champs d'un ticket existant.

    Consulter les statistiques par statut.

PowerShell

python script.py

🔒 Sécurité et CORS

Le backend inclut un CORSMiddleware configuré pour autoriser toutes les origines en développement, permettant ainsi au frontend (React/Vite) de communiquer sans restriction avec l'API.