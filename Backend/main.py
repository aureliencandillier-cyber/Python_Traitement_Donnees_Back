from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# On importe le routeur que nous venons de créer
from routers import tickets

""" Son seul rôle est de configurer l'app et d'importer les routeurs."""

# --- INITIALISATION ---
app = FastAPI(title="Ticketing API System")

# --- CONFIGURATION CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DES ROUTES ---
# C'est ici qu'on "branche" le fichier tickets.py sur l'application principale
app.include_router(tickets.router)

# Note : Plus besoin de définir les fonctions load_tickets ou les classes ici !