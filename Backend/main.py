from fastapi import FastAPI, HTTPException
import script # On importe ton fichier de logique

app = FastAPI()

# Route de base pour vérifier que l'API tourne
@app.get("/")
def read_root():
    return {"message": "L'API de gestion de tickets est en ligne"}

# 1. GET /tickets : Récupérer tous les tickets
@app.get("/tickets")
def get_all_tickets():
    data = script.open_read_JSON()
    return data