import socket
import select

from EntreeSortie.EntreeClavier import SaisieClavier
from Labyrinthe.Labyrinthe import Labyrinthe
from EntreeSortie.SortieConsole import AffichageConsole

import glob
from EntreeSortie.Message import MessageServeur
from EntreeSortie.Message import Status


def ouverture_connexion():
    hote = ''
    port = 12800

    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)

    print("Le serveur écoute à présent sur le port {}".format(port))
    return connexion_principale


def choix_labyrinthe():
    # objets utiles
    saisie = SaisieClavier()
    affichage = AffichageConsole()

    # Les cartes doivent être au format .txt, seul ces fichiers sont
    # recherchés dans le répertoire cartes/
    listeCartesTxt = glob.glob("cartes/*.txt")

    # afficher la liste des labyrinthes existants
    print("Labyrinthes existants :")
    for i, carte in enumerate(listeCartesTxt):
        # on affiche uniquement le nom du fichier
        # soit la partie après le dernier "\"
        nomCarte = carte.split('\\')[-1]
        print("\t{0} - {1}".format(i + 1, nomCarte))

    # on récupère le choix du joueur
    choixNumLabyrinthe = saisie.choixLabyrinthe(len(listeCartesTxt))

    # récupère le nom correspondant
    nomLabyrintheChoisi = listeCartesTxt[choixNumLabyrinthe - 1]

    # on créé notre objet Labyrinthe à partir du fichier sélectionné
    labyrinthe = Labyrinthe(nomLabyrintheChoisi)
    return labyrinthe

def creer_message_a_envoyer(texte, num_joueur, status):
    message = MessageServeur()
    message.modifier_message(texte)
    message.modifier_numero_joueur(num_joueur)
    message.modifier_status(status)
    return message.exporter_json_message()

def envoyer_message_au_client(message, connexion_client):
    message_a_envoyer = message.encode()
    connexion_avec_client.send(message_a_envoyer)
    

def traitement_demandes_connexions(connexion_principale, labyrinthe, clients_connectes):
    # objets utiles
    saisie = SaisieClavier()
    affichage = AffichageConsole()

    # On va vérifier que de nouveaux clients ne demandent pas à se connecter
    # Pour cela, on écoute la connexion_principale en lecture
    # On attend maximum 50ms
    connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)

    for (i, connexion) in enumerate(connexions_demandees):
        connexion_avec_client, infos_connexion = connexion.accept()

        # accueil du nouveau joueur
        num_joueur = len(clients_connectes)

        message_a_envoyer = creer_message_a_envoyer( "Bonjour Joueur {}!\n".format(num_joueur + 1), \
                                                     num_joueur + 1,\
                                                     Status.INIT)
        envoyer_message_au_client(message_a_envoyer, connexion_avec_client)


        # ajouter ce nouveau joueur dans le labyrinthe (calcul position depart)
        retour = labyrinthe.ajouterPositionNouveauJoueur()

        # vérifie que le robot du joueur peut bien etre rajouté
        if retour != "":
            message_a_envoyer = creer_message_a_envoyer( "Connexion à la partie impossible : {}".format(retour), \
                                                         num_joueur + 1,\
                                                         Status.CONNEXION_REFUSEE)
            envoyer_message_au_client(message_a_envoyer, connexion_avec_client)

            connexion_avec_client.close()

        else:

            # On ajoute le joueur à la liste des clients connectes
            clients_connectes.append(connexion_avec_client)

            # affichage en local sur le serveur
            print("Joueur {0} connecté : {1}".format(num_joueur + 1, infos_connexion))

            # informer le joueur de succes de la connexion
            message_a_envoyer = creer_message_a_envoyer( "Vous etes maintenant connectés à la partie\n", \
                                                         num_joueur + 1,\
                                                         Status.CONNEXION_ACCEPTEE)
            envoyer_message_au_client(message_a_envoyer, connexion_avec_client)

            # affichage du labyrinthe
            affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, num_joueur)

            message_a_envoyer = creer_message_a_envoyer( affichage_labyrinthe, \
                                                         num_joueur + 1,\
                                                         Status.ATTENTE_DEMARRAGE)
            envoyer_message_au_client(message_a_envoyer, connexion_avec_client)

    return clients_connectes


def traitement_messages_clients(clients_connectes):
    partie_demarree = False
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
    except select.error:
        clients_a_lire = []
    else:
        # On parcourt la liste des clients à lire
        for client in clients_a_lire:
            # Client est de type socket
            msg_recu = client.recv(1024)
            msg_recu = msg_recu.decode()
            print("Reçu {}".format(msg_recu))
            if msg_recu.rstrip().upper() == 'C':
                # demarrage de la partie, on sort de la boucle et on passe à la boucle suivante
                partie_demarree = True

                # calcul numero joueur ayant demarré la partie
                num_joueur = clients_connectes.index(client) + 1

                # envoi le message de demarrage à tous les joueurs
                for (i, client_connecte) in enumerate(clients_connectes):
                    message_a_envoyer = creer_message_a_envoyer( "Joueur {} vient de démarrer la partie\n".format(num_joueur), \
                                                                 i + 1,\
                                                                 Status.PARTIE_DEMARREE)
                    envoyer_message_au_client(message_a_envoyer, client_connecte)

                # envoi le message de demarrage à tous les joueurs
                for (i, client_connecte) in enumerate(clients_connectes):
                    message_a_envoyer = creer_message_a_envoyer( "Veuillez attendre votre tour\n", \
                                                                 i + 1,\
                                                                 Status.ATTENTE_TOUR_DE_JEU)
                    envoyer_message_au_client(message_a_envoyer, client_connecte)

    return partie_demarree


def attente_connexion_clients_et_demarrage_partie(connexion_principale, labyrinthe):
    clients_connectes = []
    partie_demarree = False

    while not partie_demarree:
        clients_connectes = traitement_demandes_connexions(connexion_principale, labyrinthe, clients_connectes)
        partie_demarree = traitement_messages_clients(clients_connectes)
    return clients_connectes


def gestion_partie(labyrinthe, clients_connectes, connexion_principale):
    partie_demarree = True
    while partie_demarree:
        for i, client in enumerate(clients_connectes):
            # demarrer le tour de jeu du joueur i+1
            message_a_envoyer = creer_message_a_envoyer( "Joueur {0}, c'est ton tour".format(i + 1), \
                                                         i + 1,\
                                                         Status.MON_TOUR)
            envoyer_message_au_client(message_a_envoyer, client)

            #attendre sa commande pour deplacer son robot
            commande_recue = client.recv(1024)
            commande_recue = commande_recue.decode()
            print("Joueur {0} a entré la commande {1}".format(i + 1, commande_recue))

            # faire bouger le robot de ce joueur

            # signaler aux autres joueurs que le joueur X a joué

            # renvoyer le labyrinthe mis à jour à tous les joueurs
            for (num_client, client_connecte) in enumerate(clients_connectes):
                affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, num_client)
                message_a_envoyer = creer_message_a_envoyer( affichage_labyrinthe, \
                                                             num_client + 1,\
                                                             Status.ATTENTE_TOUR_DE_JEU)
                envoyer_message_au_client(message_a_envoyer, client_connecte)

            # verifier si le joueur a gagné
            # si oui, partie_demarree = False, serveur_lance = False
            # et on envoie un message à tous les joeurs "Joueur X a gagné"

        partie_demarree = False
    for (num_client, client) in enumerate(clients_connectes):
        message_a_envoyer = creer_message_a_envoyer( "Joueur X a gagné", \
                                                     num_client + 1,\
                                                     Status.PARTIE_TERMINEE)
        envoyer_message_au_client(message_a_envoyer, client)        



def fermeture_connexion(clients_connectes, connexion_principale):
    print("Fermeture de la connexion")
    for (i, client) in enumerate(clients_connectes):
        print("fermeture connection Joueur {0}".format(i + 1))
        client.close()
    connexion_principale.close()


def serveur_main():
    connexion_principale = ouverture_connexion()
    labyrinthe = choix_labyrinthe()
    print("attente connexion des clients")
    clients_connectes = attente_connexion_clients_et_demarrage_partie(connexion_principale, labyrinthe)
    print("la partie commence")
    gestion_partie(labyrinthe, clients_connectes, connexion_principale)
    print("la partie est terminee")
    fermeture_connexion(clients_connectes, connexion_principale)


serveur_main()
