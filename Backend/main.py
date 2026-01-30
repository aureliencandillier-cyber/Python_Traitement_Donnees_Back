from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
import json
import os

# --- INITIALISATION ---
# On choisit FastAPI car il est asynchrone par nature et génère automatiquement 
# une documentation interactive (Swagger) à l'adresse /docs.
app = FastAPI()

# --- CONFIGURATION CORS (Cross-Origin Resource Sharing) ---
# POURQUOI ? Par sécurité, un navigateur bloque les requêtes entre deux "origines" différentes.
# Ici, ton Front (port 5173) appelle ton Back (port 8000). 
# Sans ce middleware, le navigateur jetterait une erreur de sécurité.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # On autorise tout en dev. En prod, on mettrait l'URL précise du site.
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Autorise l'envoi de JSON dans les headers.
)

# On utilise un fichier JSON au lieu d'une base SQL (SQLite/Postgres) pour la simplicité :
# Pas besoin d'installer de serveur de base de données, les données sont lisibles à l'œil nu.
DATA_FILE = "structure_ticket.json"

# --- FONCTIONS UTILITAIRES (Le "Moteur" de données) ---

def load_tickets() -> List[Dict[str, Any]]:
    """
    RÔLE : Extraire les données du disque pour les mettre en mémoire vive (RAM).
    POURQUOI 'utf-8' ? Pour ne pas corrompre les accents français (é, à, è).
    """
    if not os.path.exists(DATA_FILE):
        return [] # Évite de faire planter l'app si le fichier n'existe pas encore.

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # RIGOUREUX : On vérifie que le JSON est bien une liste [] et non un objet {}.
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail="Structure JSON invalide.")

        return data

    except json.JSONDecodeError:
        # Si le fichier est mal édité à la main et contient une virgule en trop, on le signale.
        raise HTTPException(status_code=500, detail="Fichier JSON corrompu.")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Erreur système de fichier: {e}")


def save_tickets(tickets: List[Dict[str, Any]]) -> None:
    """
    RÔLE : Rendre les changements permanents (Persistance).
    POURQUOI indent=2 ? Pour que le fichier JSON soit "joli" et trié dans VS Code.
    POURQUOI ensure_ascii=False ? Force JSON à écrire 'é' au lieu de '\u00e9'.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tickets, f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Échec de l'écriture disque: {e}")


def next_id(tickets: List[Dict[str, Any]]) -> int:
    """
    RÔLE : Simuler l'auto-incrément d'une base de données.
    POURQUOI max + 1 au lieu de len + 1 ? 
    Si tu as 3 tickets (1, 2, 3), que tu supprimes le 2, len+1 te redonnerait l'ID 3 (doublon !).
    max() + 1 garantit que l'ID est toujours strictement nouveau.
    """
    if not tickets:
        return 1
    return max(int(t.get("id", 0)) for t in tickets) + 1


# --- MODÈLES DE DONNÉES (Contrat de confiance) ---

class TicketCreate(BaseModel):
    """
    Définit ce que le client DOIT envoyer pour créer un ticket.
    Pydantic valide les types (str, list) automatiquement.
    """
    title: str
    description: str
    priority: str = "Low" # Valeur par défaut si le front ne l'envoie pas.
    status: str = "Open"
    tags: List[str] = []


class TicketUpdate(BaseModel):
    """
    Définit ce que le client PEUT envoyer pour modifier (PATCH).
    On utilise Optional car on ne veut pas forcer l'utilisateur à renvoyer 
    tout le ticket s'il veut juste changer le statut.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


def payload_to_dict(payload: TicketUpdate) -> Dict[str, Any]:
    """
    POURQUOI exclude_unset=True ? 
    Si le front envoie seulement {status: "Closed"}, on ne veut pas que les autres 
    champs (title, desc) deviennent 'null' dans notre JSON. On garde uniquement ce qui a été touché.
    """
    if hasattr(payload, "model_dump"):  # Standard Pydantic v2
        return payload.model_dump(exclude_unset=True)
    return payload.dict(exclude_unset=True)  # Rétro-compatibilité Pydantic v1


# --- ROUTES DE L'API (Les portes d'entrée) ---

@app.get("/tickets")
def get_tickets():
    """Route de lecture : Renvoie simplement l'état actuel du JSON."""
    return load_tickets()


@app.post("/tickets", status_code=201)
def create_ticket(payload: TicketCreate):
    """
    Route de création. 
    STATUS 201 : Code HTTP standard pour signifier 'Created' (Succès et création).
    """
    tickets = load_tickets()

    # NETTOYAGE (strip) : Retire les espaces accidentels. 
    # Évite qu'un utilisateur crée un titre "   " (vide mais rempli d'espaces).
    title = payload.title.strip()
    desc = payload.description.strip()
    
    if not title or not desc:
        raise HTTPException(status_code=400, detail="Les champs texte ne peuvent pas être vides.")

    # SÉCURITÉ : On ne fait pas confiance au client. On vérifie que les valeurs 
    # sont bien dans notre liste autorisée (Enum métier).
    if payload.status not in {"Open", "In progress", "Closed"}:
        raise HTTPException(status_code=400, detail="Statut inconnu.")

    if payload.priority not in {"Low", "Medium", "High"}:
        raise HTTPException(status_code=400, detail="Priorité inconnue.")

    # Transformation du modèle Pydantic en dictionnaire Python pour le JSON.
    ticket = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    ticket["id"] = next_id(tickets)
    ticket["title"] = title
    ticket["description"] = desc

    tickets.append(ticket)
    save_tickets(tickets) # On écrit sur le disque immédiatement.
    return ticket


@app.patch("/tickets/{ticket_id}")
def patch_ticket(ticket_id: int, payload: TicketUpdate):
    """
    Route de modification partielle.
    POURQUOI PATCH et pas PUT ? 
    PUT remplace l'objet entier. PATCH ne modifie que les morceaux demandés.
    """
    tickets = load_tickets()

    # next() : Méthode hyper rapide pour trouver LE premier élément qui correspond à l'ID.
    ticket = next((t for t in tickets if int(t.get("id", -1)) == ticket_id), None)
    
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ce ticket n'existe pas.")

    data = payload_to_dict(payload)
    if not data:
        raise HTTPException(status_code=400, detail="Aucune donnée reçue.")

    # RE-VALIDATION : Même en mise à jour, on vérifie que les nouvelles valeurs sont correctes.
    if "status" in data and data["status"] not in {"Open", "In progress", "Closed"}:
        raise HTTPException(status_code=400, detail="Statut invalide.")

    # MISE À JOUR DYNAMIQUE : On boucle sur les clés envoyées (ex: 'status') 
    # et on met à jour la valeur correspondante dans notre dictionnaire ticket.
    for k, v in data.items():
        ticket[k] = v

    save_tickets(tickets)
    return ticket


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    """
    Route de suppression.
    STATUS 204 : 'No Content'. Le serveur confirme la suppression mais ne renvoie rien.
    """
    tickets = load_tickets()
    before = len(tickets)
    
    # LIST COMPREHENSION : On crée une nouvelle liste qui contient TOUT SAUF l'ID à supprimer.
    # C'est la manière la plus propre et rapide de "supprimer" en Python sans base SQL.
    tickets = [t for t in tickets if int(t.get("id", -1)) != ticket_id]

    if len(tickets) == before:
        # Si la taille n'a pas changé, c'est que l'ID n'existait pas.
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    save_tickets(tickets)
    return None # Avec 204, FastAPI ignore le retour et envoie une réponse vide.