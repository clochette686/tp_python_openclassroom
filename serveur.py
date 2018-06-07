import socket
import select

from EntreeSortie.EntreeClavier import SaisieClavier
from Labyrinthe.Labyrinthe import Labyrinthe
from EntreeSortie.SortieConsole import AffichageConsole

import glob
from EntreeSortie.Message import MessageServeur
from EntreeSortie.Message import Status
from EntreeSortie.Message import MessageClient
from EntreeSortie.Message import Status_Client


def ouverture_connexion():
    hote = ''
    port = 12800
    affichage = AffichageConsole()

    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)

    affichage.afficheMessage("Le serveur écoute à présent sur le port {}".format(port))
    return connexion_principale


def choix_labyrinthe():
    # objets utiles
    saisie = SaisieClavier()
    affichage = AffichageConsole()

    # Les cartes doivent être au format .txt, seul ces fichiers sont
    # recherchés dans le répertoire cartes/
    listeCartesTxt = glob.glob("cartes/*.txt")

    # afficher la liste des labyrinthes existants
    affichage.afficheMessage("Labyrinthes existants :")
    for i, carte in enumerate(listeCartesTxt):
        # on affiche uniquement le nom du fichier
        # soit la partie après le dernier "\"
        nomCarte = carte.split('\\')[-1]
        affichage.afficheMessage("\t{0} - {1}".format(i + 1, nomCarte))

    # on récupère le choix du joueur
    choixNumLabyrinthe = saisie.choixLabyrinthe(len(listeCartesTxt))

    # récupère le nom correspondant
    nomLabyrintheChoisi = listeCartesTxt[choixNumLabyrinthe - 1]

    # on créé notre objet Labyrinthe à partir du fichier sélectionné
    labyrinthe = Labyrinthe(nomLabyrintheChoisi)
    return labyrinthe


def creer_message_a_envoyer(texte, status):
    message = MessageServeur()
    message.modifier_message(texte)
    message.modifier_status(status)
    return message.exporter_json_message()


def envoyer_message_au_client(texte, status, connexion_avec_client):
    message_a_envoyer = creer_message_a_envoyer(texte, status).encode()
    connexion_avec_client.send(message_a_envoyer)


def traitement_demandes_connexions(connexion_principale, labyrinthe, clients_connectes):
    # objets utiles
    affichage = AffichageConsole()

    # On va vérifier que de nouveaux clients ne demandent pas à se connecter
    # Pour cela, on écoute la connexion_principale en lecture
    # On attend maximum 50ms
    connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)

    for (i, connexion) in enumerate(connexions_demandees):
        connexion_avec_client, infos_connexion = connexion.accept()

        # accueil du nouveau joueur
        num_joueur = len(clients_connectes)

        envoyer_message_au_client("Bonjour Joueur {}!\n".format(num_joueur + 1),
                                  Status.ECOUTE_SERVEUR,
                                  connexion_avec_client)

        # ajouter ce nouveau joueur dans le labyrinthe (calcul position depart)
        retour = labyrinthe.ajouterPositionNouveauJoueur()

        # vérifie que le robot du joueur peut bien etre rajouté
        if retour != "OK":
            envoyer_message_au_client("Connexion à la partie impossible : {}".format(retour),
                                      Status.DECONNEXION,
                                      connexion_avec_client)

            connexion_avec_client.close()

        else:

            # On ajoute le joueur à la liste des clients connectes
            clients_connectes.append(connexion_avec_client)

            # affichage en local sur le serveur
            affichage.afficheMessage("Joueur {0} connecté : {1}".format(num_joueur + 1, infos_connexion))

            # informer le joueur de succes de la connexion
            envoyer_message_au_client("Vous etes maintenant connectés à la partie\n",
                                      Status.ECOUTE_SERVEUR,
                                      connexion_avec_client)

            # affichage du labyrinthe
            affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, num_joueur)

            if num_joueur == 0:
                envoyer_message_au_client(affichage_labyrinthe,
                                          Status.DEMANDE_DEMARRAGE_PARTIE,
                                          connexion_avec_client)

            else:
                envoyer_message_au_client(affichage_labyrinthe,
                                          Status.ECOUTE_SERVEUR,
                                          connexion_avec_client)

                envoyer_message_au_client("Attendez que Joueur 1 démarre la partie\n",
                                          Status.ECOUTE_SERVEUR,
                                          connexion_avec_client)
    return clients_connectes


def traitement_messages_clients(clients_connectes, labyrinthe):
    affichage = AffichageConsole()
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
            print("msg_recu = ", msg_recu)

            message_client = MessageClient()
            message_client.importer_json_message(msg_recu)

            if message_client.lire_status() == Status_Client.DEMARRAGE_PARTIE.name:
                # demarrage de la partie, on sort de la boucle et on passe à la boucle suivante
                partie_demarree = True

                # calcul numero joueur ayant demarré la partie
                num_joueur = clients_connectes.index(client) + 1

                # envoi le message de demarrage à tous les joueurs
                for (i, client_connecte) in enumerate(clients_connectes):
                    envoyer_message_au_client("Joueur {} vient de démarrer la partie\n".format(num_joueur),
                                              Status.ECOUTE_SERVEUR,
                                              client_connecte)

                # envoi le message de demarrage à tous les joueurs
                for (i, client_connecte) in enumerate(clients_connectes):
                    affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, i)
                    envoyer_message_au_client(affichage_labyrinthe,
                                              Status.ECOUTE_SERVEUR,
                                              client_connecte)

                    envoyer_message_au_client("Veuillez attendre votre tour\n",
                                              Status.ECOUTE_SERVEUR,
                                              client_connecte)

    return partie_demarree


def attente_connexion_clients_et_demarrage_partie(connexion_principale, labyrinthe):
    clients_connectes = []
    partie_demarree = False

    while not partie_demarree:
        clients_connectes = traitement_demandes_connexions(connexion_principale, labyrinthe, clients_connectes)
        partie_demarree = traitement_messages_clients(clients_connectes, labyrinthe)
    return clients_connectes


def recuperer_message_client(client):
    # attendre sa commande pour deplacer son robot
    commande_recue = client.recv(1024)
    commande_recue = commande_recue.decode()

    message_client = MessageClient()
    message_client.importer_json_message(commande_recue)
    return message_client

def gestion_partie(labyrinthe, clients_connectes):
    affichage = AffichageConsole()
    partie_demarree = True
    joueur_gagnant = -1
    index_joueur = 0
    while partie_demarree:

        client = clients_connectes[index_joueur]
        affichage.afficheMessage("Tour de joueur {}".format(index_joueur + 1))

        # demarrer le tour de jeu du joueur index_joueur+1
        envoyer_message_au_client("Joueur {0}, c'est ton tour".format(index_joueur + 1),
                                  Status.MON_TOUR,
                                  client)

        message_recu_client = recuperer_message_client(client)

        status_client = message_recu_client.lire_status()
        message_client = message_recu_client.lire_message()

        if status_client == Status_Client.QUITTER.name:
            # gérer le cas où le joueur veut quitter la partie
            affichage.afficheMessage("Joueur {0} veut quitter la partie".format(index_joueur + 1))
        elif status_client == Status_Client.DEPLACEMENT.name:
            affichage.afficheMessage("Joueur {0} a entré la commande {1}".format(index_joueur + 1, message_client))
            if labyrinthe.deplacementPossible(index_joueur, message_client):
                labyrinthe.robots.avancer(index_joueur, message_client)

            # signaler aux autres joueurs que le joueur X a joué
            for client in clients_connectes:
                envoyer_message_au_client("Joueur {0} a déplacé son robot vers le {1}".format(index_joueur + 1, message_client),
                                          Status.ECOUTE_SERVEUR,
                                          client)

            # renvoyer le labyrinthe mis à jour à tous les joueurs
            for (num_client, client_connecte) in enumerate(clients_connectes):
                affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, num_client)
                envoyer_message_au_client(affichage_labyrinthe,
                                          Status.ECOUTE_SERVEUR,
                                          client_connecte)

            # verifier si le joueur a gagné
            if labyrinthe.partieGagnee(index_joueur):
                partie_demarree = False
                joueur_gagnant = index_joueur + 1
            else:
                index_joueur = (index_joueur + 1) % len(clients_connectes)

    for (num_client, client) in enumerate(clients_connectes):
        envoyer_message_au_client("Joueur {0} a gagné".format(joueur_gagnant),
                                  Status.ECOUTE_SERVEUR,
                                  client)


def fermeture_connexion(clients_connectes, connexion_principale):
    affichage = AffichageConsole()

    affichage.afficheMessage("Fermeture de la connexion")
    for (index_client, client) in enumerate(clients_connectes):
        affichage.afficheMessage("fermeture connection Joueur {0}".format(index_client + 1))

        envoyer_message_au_client("Merci d'avoir joué. Au revoir.",
                                  Status.DECONNEXION,
                                  client)

        client.close()
    connexion_principale.close()


def serveur_main():
    # objet utile
    affichage = AffichageConsole()

    # deroulement code serveur
    connexion_principale = ouverture_connexion()
    labyrinthe = choix_labyrinthe()

    affichage.afficheMessage("attente connexion des clients")
    clients_connectes = attente_connexion_clients_et_demarrage_partie(connexion_principale, labyrinthe)

    affichage.afficheMessage("la partie commence")
    gestion_partie(labyrinthe, clients_connectes)

    affichage.afficheMessage("la partie est terminee")
    fermeture_connexion(clients_connectes, connexion_principale)


if __name__ == "__main__":
    serveur_main()
