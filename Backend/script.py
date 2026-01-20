import json
from collections import defaultdict
from tkinter import filedialog, Tk
from datetime import datetime

#Lecture du fichier json qui esty dans c:\Users\Candillier Aurélien\OneDrive - yncréa\Documents\Prog\Python\Python_Traitement_Donnees\Backend\structure_ticket.json
def open_read_JSON():
    # 1. On crée une fenêtre invisible (Tkinter en a besoin pour afficher le sélecteur)
    root = Tk()
    root.withdraw() # Cache la fenêtre principale
    root.attributes('-topmost', True) # Force le sélecteur à passer devant les autres fenêtres

    # on va chercher le fichier json dans c:\Users\Candillier Aurélien\OneDrive - yncréa\Documents\Prog\Python\Python_Traitement_Donnees\Backend\structure_ticket.json
    chemin_fichier = 'structure_ticket.json'
    

    # # 2. On ouvre la boîte de dialogue Windows
    # chemin_fichier = filedialog.askopenfilename(
    #     title="Sélectionnez votre fichier de tickets",
    #     filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
    # )

    # 3. On vérifie si l'utilisateur a bien choisi un fichier ou s'il a annulé
    if not chemin_fichier:
        print("Aucun fichier sélectionné.")
        return []

    # 4. On réutilise ta logique de lecture habituelle
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
            return json.load(fichier)
    except Exception as e:
        print(f"Erreur lors de l'ouverture : {e}")
        return []

    
#Calcul du nombre de ticket par statut
def count_tic_stat(liste_tickets):
    resultats = {}
    for ticket in liste_tickets:
        # On extrait le statut. Si absent, on met 'Unknown'
        s = ticket.get('status', 'inconnu').lower()
        
        # Logique de comptage
        if s in resultats:
            resultats[s] += 1
        else:
            resultats[s] = 1
    return resultats
        
# récupère les tickets en entrée et renvoie la liste des tickets triés selon le critère
def trier(liste_tickets, critere='priority'):
    return sorted(liste_tickets, key=lambda x: x.get(critere, ''))

# récupère les tickets en entrée et renvoie la liste des tickets filtrés selon le critère
def filtre(liste_tickets, critere, valeur):
    return [ticket for ticket in liste_tickets if ticket.get(critere) == valeur]

# affiche les options si on veut filtrer, trier, etc
def afficher_options():
    print("Options disponibles :")
    print("1. Trier les tickets")
    print("2. Filtrer les tickets")
    print("3. Ajouter un ticket")
    print("4. Mettre à jour un ticket")
    while True:
        choix = input("Sélectionnez une option (1-4) ou 'q' pour quitter : ")
        if choix in ['1', '2', '3', '4', 'q']:
            return choix
        else:
            print("Option invalide. Veuillez réessayer.")
            
#Fonction pour choisir le critère de tri et afficher le résultat
def choix_trier():
    while True:
            Select_critere = input("saisissez un critère de tri (par défaut 'priority') : \n1- id \n2- status \n3- priority \n4- tags \n5- date créée\n").lower()
            if Select_critere == "":
                continue
            elif Select_critere == "1" or "id":
                print(trier(data, "id"))
                break
            elif Select_critere == "2" or "status":
                print(trier(data, "status"))
                break
            elif Select_critere == "3" or "priority":
                print(trier(data, "priority"))
                break
            elif Select_critere == "4" or "tags":
                print(trier(data, "tags"))
                break
            elif Select_critere == "5" or "date créée":
                print(trier(data, "createdAt"))
                break
            else:
                print("Critère invalide. Veuillez réessayer.")
                
# on ajoute un ticket (en étant limité sur les champs id, status, priority et tags)
def ajouter_ticket():
    new_ticket = {}
    
    #on renseigne l'id du dernier ticket valide + 1 et que le format reste sans les guillemets
    new_ticket['id'] = int(data[-1]['id']) + 1
    
    # on renseigne le titre du ticket et on vérifie qu'il n'est pas vide
    while True:
        new_ticket['title'] = input("Entrez le titre du ticket : ")
        if new_ticket['title']:
            break
        else:
            print("Le titre ne peut pas être vide.")
    
    # on renseigne la description du ticket et on vérifie qu'elle n'est pas vide
    while True:
        new_ticket['description'] = input("Entrez la description du ticket : ")
        if new_ticket['description']:
            break
        else:
            print("La description ne peut pas être vide.")
    
    # on s'assure que la priorité renseignée est valide
    while True:  
        new_ticket['priority'] = input("Entrez la priorité du ticket (choix possibles : low, medium, high) : ").capitalize()
        if new_ticket['priority'] in ['Low', 'Medium', 'High']:
            break
        else:
            print("Priorité invalide. Veuillez réessayer. Choix possibles : low, medium, high")
        
   # on s'assure que le status renseigné est valide
    while True:
        new_ticket['status'] = input("Entrez le statut du ticket  (choix possibles : Open, Closed, In progress): ").capitalize()
        if new_ticket['status'] in ['Open', 'Closed', 'In progress']:
            break
        else:
            print("Statut invalide. Veuillez réessayer. Choix possibles : Open, Closed, In progress")
        
    new_ticket['tags'] = input("Entrez les tags du ticket (séparés par des virgules) : ").split(',')
    
    # on rajoute la date de création année-mois-jour
    new_ticket['createdAt'] = datetime.now().strftime("%Y-%m-%d")
        
    data.append(new_ticket)
    
    # on va écrire dans le fichier JSON qu'on a ouvert au début et on rajoute le ticket créé à la fin puis on sauvegarde
    with open('structure_ticket.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    print("Ticket ajouté avec succès.")
    
# mise à jour des tickets
def mettre_a_jour_ticket():
    while True:
        ticket_id = input(f"Entrez l'ID du ticket à mettre à jour (choix possibles : {[ticket['id'] for ticket in data]}    ) ")
        try:
            ticket_id = int(ticket_id)
        except:
            continue
        
        print(ticket_id)
        if ticket_id in [ticket['id'] for ticket in data]:
            for ticket in data:
                if ticket['id'] == ticket_id:
                    print(f"Ticket trouvé : {ticket}")
                    
                    #on met à jour le titre
                    new_titre = input("Entrez le nouveau titre (laisser vide pour ne pas changer) : ")
                    if new_titre:
                        ticket['title'] = new_titre
                        
                    #on met à jour la description
                    new_description = input("Entrez la nouvelle description (laisser vide pour ne pas changer) : ")
                    if new_description:
                        ticket['description'] = new_description
                    
                    # on peut mettre à jour le status et la priority
                    new_status = input("Entrez le nouveau statut (laisser vide pour ne pas changer) : ").capitalize()
                    if new_status in ['Open', 'Closed', 'In progress']:
                        ticket['status'] = new_status
                    elif new_status != "":
                        print("Statut invalide. Le statut n'a pas été modifié.")
                    
                    new_priority = input("Entrez la nouvelle priorité (laisser vide pour ne pas changer) : ").capitalize()
                    if new_priority in ['Low', 'Medium', 'High']:
                        ticket['priority'] = new_priority
                    elif new_priority != "":
                        print("Priorité invalide. La priorité n'a pas été modifiée.")
                    
                    # on sauvegarde les modifications dans le fichier JSON
                    with open('structure_ticket.json', 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    
                    print("Ticket mis à jour avec succès.")
                    return
        else:
            print("ID introuvable. Veuillez réessayer.")
    


#vérifie les valeurs possibles pour un critère donné et on return la liste des valeurs possibles
def check_crit(liste_tickets, critere):
    valeurs_possibles = set()
    for ticket in liste_tickets:
        if critere in ticket:
            valeurs_possibles.add(ticket[critere])
    return valeurs_possibles

    
if __name__ == "__main__":
    # Ce code ne s'exécute QUE si tu lances "python script.py"
    # Il ne se lancera PAS quand FastAPI importera ce fichier.
    data = open_read_JSON()
    if data:
        stats = count_tic_stat(data)
        print(f"Statistiques des tickets : {stats}")
        while True:
            option = afficher_options()
            if option == '1':
                choix_trier()
                break
            elif option == '2':
                while True:
                    critere = input("Entrez le critère de filtrage (status, priority, etc.) : ")
                    # on vérifie que le critère est valide
                    if critere not in ['status', 'priority', 'tags']:
                        print("Critère invalide. Veuillez réessayer.")
                        continue
                    break
                
                while True:
                    Liste_possible = check_crit(data, critere)
                    print(f"Valeurs possibles pour {critere} : {Liste_possible}")
                    valeur = input(f"Entrez la valeur pour {critere} : ").capitalize()
                    if valeur in Liste_possible:
                        break
                    else:
                        print("Valeur invalide. Veuillez réessayer.")
                        continue
                
                tickets_filtres = filtre(data, critere, valeur)
                print(f"Tickets filtrés : {tickets_filtres}")
                break
            elif option == '3':
                ajouter_ticket()
                break
            elif option == '4':
                mettre_a_jour_ticket()
                break
            elif option == 'q':
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez réessayer.")
                
    print("Fin du programme.")