import json
import os
from datetime import datetime

# Constante pour le nom du fichier
FICHIER_DONNEES = 'structure_ticket.json'

# --- GESTION DES FICHIERS ---

def open_read_JSON():
    """Lit le fichier JSON et retourne la liste des tickets."""
    if not os.path.exists(FICHIER_DONNEES):
        return []
    try:
        with open(FICHIER_DONNEES, 'r', encoding='utf-8') as fichier:
            return json.load(fichier)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_JSON(data):
    """Sauvegarde la liste des données dans le fichier JSON."""
    with open(FICHIER_DONNEES, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# --- FONCTIONS LOGIQUES (MÉTIER) ---
# Ces fonctions ne contiennent aucun print() ni input()

def count_tic_stat(liste_tickets):
    """Compte le nombre de tickets par statut."""
    resultats = {}
    for ticket in liste_tickets:
        s = ticket.get('status', 'inconnu').lower()
        if s in resultats:
            resultats[s] += 1
        else:
            resultats[s] = 1
    return resultats

def trier(liste_tickets, critere='priority'):
    """Trie la liste selon une clé donnée."""
    # On utilise str() pour éviter les crashs si la valeur n'est pas une string
    return sorted(liste_tickets, key=lambda x: str(x.get(critere, '')).lower())

def filtre(liste_tickets, critere, valeur):
    """Filtre la liste pour ne garder que les tickets correspondant à la valeur."""
    return [ticket for ticket in liste_tickets if str(ticket.get(critere, '')).lower() == valeur.lower()]

def ajouter_ticket(data, title, description, priority, status, tags):
    """Crée un ticket, l'ajoute à la liste et sauvegarde."""
    if data:
        # On s'assure que l'ID est bien un entier pour l'incrémentation
        last_id = int(data[-1]['id'])
        new_id = last_id + 1
    else:
        new_id = 1
    
    new_ticket = {
        "id": new_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "tags": tags,
        "createdAt": datetime.now().strftime("%Y-%m-%d")
    }
    
    data.append(new_ticket)
    save_JSON(data)
    return new_ticket

def mettre_a_jour_ticket_logique(data, ticket_id, modifications):
    """
    Met à jour un ticket spécifique.
    modifications est un dictionnaire contenant les champs à changer.
    """
    ticket_trouve = None
    for ticket in data:
        if ticket['id'] == ticket_id:
            ticket_trouve = ticket
            break
    
    if ticket_trouve:
        # On applique les modifications seulement si elles ne sont pas vides
        for cle, valeur in modifications.items():
            if valeur: # Si la valeur n'est pas vide
                ticket_trouve[cle] = valeur
        
        save_JSON(data)
        return ticket_trouve
    return None

# --- FONCTIONS UTILITAIRES ---

def check_crit(liste_tickets, critere):
    """Renvoie les valeurs uniques existantes pour un critère donné."""
    valeurs_possibles = set()
    for ticket in liste_tickets:
        if critere in ticket:
            valeurs_possibles.add(ticket[critere])
    return valeurs_possibles

# --- INTERFACE UTILISATEUR (CLI) ---
# Tout ce qui concerne l'interaction humaine est ici

if __name__ == "__main__":
    print("--- Démarrage du script en mode CLI ---")
    data = open_read_JSON()
    
    if not data:
        print("Attention : Aucune donnée chargée ou fichier vide.")

    while True:
        print("\nOptions disponibles :")
        print("1. Trier les tickets")
        print("2. Filtrer les tickets")
        print("3. Ajouter un ticket")
        print("4. Mettre à jour un ticket")
        print("5. Voir les stats")
        print("q. Quitter")
        
        choix = input("Votre choix : ")

        if choix == '1':
            critere = input("Critère de tri (id, status, priority, tags, createdAt) : ")
            # Correction du bug logique 'or' que tu avais
            if critere in ['id', 'status', 'priority', 'tags', 'createdAt']:
                res = trier(data, critere)
                print(json.dumps(res, indent=2, ensure_ascii=False))
            else:
                print("Critère inconnu, tri par défaut (priority).")
                print(json.dumps(trier(data), indent=2, ensure_ascii=False))

        elif choix == '2':
            critere = input("Critère (status, priority) : ")
            possibles = check_crit(data, critere)
            print(f"Valeurs existantes : {possibles}")
            valeur = input("Valeur recherchée : ")
            res = filtre(data, critere, valeur)
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif choix == '3':
            # On pose les questions ICI, pas dans la fonction
            t = input("Titre : ")
            d = input("Description : ")
            
            p = ""
            while p not in ['Low', 'Medium', 'High']:
                p = input("Priorité (Low, Medium, High) : ").capitalize()
            
            s = ""
            while s not in ['Open', 'In progress', 'Closed']:
                s = input("Statut (Open, In progress, Closed) : ").capitalize()
                
            tags_input = input("Tags (séparés par des virgules) : ")
            tags_list = [tag.strip() for tag in tags_input.split(',')]
            
            # Appel de la fonction pure
            ticket = ajouter_ticket(data, t, d, p, s, tags_list)
            print(f"✅ Ticket ajouté : ID {ticket['id']}")

        elif choix == '4':
            try:
                tid = int(input("ID du ticket à modifier : "))
                
                # On prépare les changements
                print("Laissez vide si pas de changement.")
                new_title = input("Nouveau titre : ")
                new_desc = input("Nouvelle description : ")
                new_p = input("Nouvelle priorité : ").capitalize()
                new_s = input("Nouveau statut : ").capitalize()
                
                # On vérifie la validité des champs restreints si l'utilisateur a tapé quelque chose
                if new_p and new_p not in ['Low', 'Medium', 'High']:
                    print("Priorité invalide, ignorée.")
                    new_p = None
                
                if new_s and new_s not in ['Open', 'In progress', 'Closed']:
                    print("Statut invalide, ignoré.")
                    new_s = None

                # On construit le dictionnaire de modifications
                updates = {
                    "title": new_title,
                    "description": new_desc,
                    "priority": new_p,
                    "status": new_s
                }
                
                resultat = mettre_a_jour_ticket_logique(data, tid, updates)
                if resultat:
                    print(f"✅ Ticket {tid} mis à jour.")
                else:
                    print("❌ ID introuvable.")
            except ValueError:
                print("Erreur : L'ID doit être un nombre.")

        elif choix == '5':
            print(count_tic_stat(data))

        elif choix == 'q':
            break