import json
import os
from typing import List, Dict, Any
from fastapi import HTTPException

# On définit le nom du fichier ici
""" Ce fichier gère exclusivement les interactions avec le disque ("Base de données" JSON). 
Il contient tes fonctions utilitaires."""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "structure_ticket.json")

def load_tickets() -> List[Dict[str, Any]]:
    """Charge les tickets depuis le fichier JSON."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail="Structure JSON invalide.")
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Fichier JSON corrompu.")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Erreur système de fichier: {e}")


def save_tickets(tickets: List[Dict[str, Any]]) -> None:
    """Sauvegarde la liste sur le disque."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tickets, f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Échec de l'écriture disque: {e}")


def next_id(tickets: List[Dict[str, Any]]) -> int:
    """Calcule le prochain ID disponible."""
    if not tickets:
        return 1
    return max(int(t.get("id", 0)) for t in tickets) + 1