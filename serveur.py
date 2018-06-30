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
from Joueur.joueur import Joueur
from Joueur.joueur import Joueurs


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

def envoyer_message_tous_les_joueurs(texte, status, liste_connexions):
    for connexion in liste_connexions:
        envoyer_message_au_client(texte, status, connexion)

def envoyer_affichage_labyrinthe_tous_les_joueurs(labyrinthe, status, liste_connexions):
    affichage = AffichageConsole()

    for joueur in liste_connexions:
        print("DEBUG joueur = ", joueur)
        affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, joueur.get_index_joueur())
        envoyer_message_au_client(affichage_labyrinthe,
                                  status,
                                  joueur.get_connexion())

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
        num_joueur = clients_connectes.get_nombre_joueurs()
        joueur = Joueur(num_joueur, connexion_avec_client)

        envoyer_message_au_client("Bonjour Joueur {}!\n".format(joueur.get_num_joueur()),
                                  Status.ECOUTE_SERVEUR,
                                  joueur.get_connexion())

        # ajouter ce nouveau joueur dans le labyrinthe (calcul position depart)
        retour = labyrinthe.ajouterPositionNouveauJoueur()

        # vérifie que le robot du joueur peut bien etre rajouté
        if retour != "OK":
            envoyer_message_au_client("Connexion à la partie impossible : {}".format(retour),
                                      Status.DECONNEXION,
                                      joueur.get_connexion())

            joueur.get_connexion().close()

        else:

            # On ajoute le joueur à la liste des clients connectes
            clients_connectes.ajouter_joueur(joueur)

            # affichage en local sur le serveur
            affichage.afficheMessage("Joueur {0} connecté : {1}".format(joueur.get_num_joueur(), infos_connexion))

            # informer le joueur de succes de la connexion
            envoyer_message_au_client("Vous etes maintenant connectés à la partie\n",
                                      Status.ECOUTE_SERVEUR,
                                      joueur.get_connexion())

            # affichage du labyrinthe
            affichage_labyrinthe = affichage.afficheLabyrinthe(labyrinthe, joueur.get_index_joueur())

            if num_joueur == 0:
                envoyer_message_au_client(affichage_labyrinthe,
                                          Status.DEMANDE_DEMARRAGE_PARTIE,
                                          joueur.get_connexion())

            else:
                envoyer_message_au_client(affichage_labyrinthe,
                                          Status.ECOUTE_SERVEUR,
                                          joueur.get_connexion())

                envoyer_message_au_client("Attendez que Joueur 1 démarre la partie\n",
                                          Status.ECOUTE_SERVEUR,
                                          joueur.get_connexion())
    return clients_connectes


def compare_status(nom_status, status_a_comparer):
    return nom_status == status_a_comparer.name

def traitement_messages_clients(clients_connectes, labyrinthe):
    affichage = AffichageConsole()
    partie_demarree = False
    try:
        liste_connexion = clients_connectes.get_liste_connexions()
        clients_a_lire, wlist, xlist = select.select(liste_connexion, [], [], 0.05)
    except select.error:
        clients_a_lire = []
    else:
        # On parcourt la liste des clients à lire
        for client in clients_a_lire:
            # Client est de type socket
            msg_recu = client.recv(1024)
            msg_recu = msg_recu.decode()

            message_client = MessageClient()
            message_client.importer_json_message(msg_recu)

            if compare_status(message_client.lire_status(), Status_Client.DEMARRAGE_PARTIE):
                # demarrage de la partie, on sort de la boucle et on passe à la boucle suivante
                partie_demarree = True

                joueur_expediteur = clients_connectes.get_joueur_avec_connexion(client)
                # envoi le message de demarrage à tous les joueurs
                envoyer_message_tous_les_joueurs("Joueur {} vient de démarrer la partie\n"
                                                 .format(joueur_expediteur.get_num_joueur()),
                                                 Status.ECOUTE_SERVEUR,
                                                 clients_connectes.get_liste_connexions())

                # envoi le message de demarrage à tous les joueurs
                envoyer_affichage_labyrinthe_tous_les_joueurs(labyrinthe, Status.ECOUTE_SERVEUR, clients_connectes)

                envoyer_message_tous_les_joueurs("Veuillez attendre votre tour\n",
                                                 Status.ECOUTE_SERVEUR,
                                                 clients_connectes.get_liste_connexions())

    return partie_demarree


def attente_connexion_clients_et_demarrage_partie(connexion_principale, labyrinthe):
    clients_connectes = Joueurs()
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

def quitter_la_partie(joueur, clients_connectes):
    affichage = AffichageConsole()
    envoyer_message_tous_les_joueurs("Joueur {0} quitte la partie"
                                     .format(joueur.get_num_joueur()),
                                     Status.ECOUTE_SERVEUR,
                                     clients_connectes.get_liste_connexions())

    affichage.afficheMessage("Joueur {0} quitte la partie"
                             .format(joueur.get_num_joueur()))

    envoyer_message_au_client("Merci d'avoir joué. Au revoir.",
                              Status.DECONNEXION,
                              joueur.get_connexion())

    joueur.get_connexion().close()
    clients_connectes.supprimmer_joueur(joueur)



def murer_une_porte(joueur, direction, labyrinthe, clients_connectes):
    affichage = AffichageConsole()
    affichage.afficheMessage("Joueur {0} veut murer la porte dans la direction {1}"
                             .format(joueur.get_num_joueur(), direction))

    labyrinthe.murer_porte(joueur.get_index_joueur(), direction)

    # signaler aux autres joueurs que le joueur X a joué
    envoyer_message_tous_les_joueurs("Joueur {0} a muré la porte dans la direction {1}"
                                     .format(joueur.get_num_joueur(), direction),
                                     Status.ECOUTE_SERVEUR,
                                     clients_connectes.get_liste_connexions())

    # renvoyer le labyrinthe mis à jour à tous les joueurs
    envoyer_affichage_labyrinthe_tous_les_joueurs(labyrinthe,
                                                  Status.ECOUTE_SERVEUR,
                                                  clients_connectes)

def percer_un_mur(joueur, direction, labyrinthe, clients_connectes):
    affichage = AffichageConsole()
    affichage.afficheMessage("Joueur {0} veut percer un mur dans la direction {1}"
                             .format(joueur.get_num_joueur(), direction))

    labyrinthe.percer_mur(joueur.get_index_joueur(), direction)

    # signaler aux autres joueurs que le joueur X a joué
    envoyer_message_tous_les_joueurs("Joueur {0} a percé le mur dans la direction {1}"
                                     .format(joueur.get_num_joueur(), direction),
                                     Status.ECOUTE_SERVEUR,
                                     clients_connectes.get_liste_connexions())

    # renvoyer le labyrinthe mis à jour à tous les joueurs
    envoyer_affichage_labyrinthe_tous_les_joueurs(labyrinthe,
                                                  Status.ECOUTE_SERVEUR,
                                                  clients_connectes)

def deplacer_robot(joueur, direction, labyrinthe, clients_connectes):
    affichage = AffichageConsole()


    affichage.afficheMessage("Joueur {0} a entré la commande {1}"
                             .format(joueur.get_num_joueur(), direction))

    if labyrinthe.deplacementPossible(joueur.get_index_joueur(), direction):
        labyrinthe.robots.avancer(joueur.get_index_joueur(), direction)

    # signaler aux autres joueurs que le joueur X a joué
    envoyer_message_tous_les_joueurs("Joueur {0} a déplacé son robot vers le {1}"
                                     .format(joueur.get_num_joueur(), direction),
                                     Status.ECOUTE_SERVEUR,
                                     clients_connectes.get_liste_connexions())

    # renvoyer le labyrinthe mis à jour à tous les joueurs
    envoyer_affichage_labyrinthe_tous_les_joueurs(labyrinthe,
                                                  Status.ECOUTE_SERVEUR,
                                                  clients_connectes)




def passer_au_joueur_suivant(joueur_courant, nb_joueurs):
    return (joueur_courant + 1) % nb_joueurs

def gestion_partie(labyrinthe, clients_connectes):
    affichage = AffichageConsole()
    partie_demarree = True
    joueur_gagnant = -1
    index_joueur = 0
    while partie_demarree:

        joueur = clients_connectes.get_joueur_avec_index(index_joueur)
        affichage.afficheMessage("Tour de joueur {}"
                                 .format(joueur.get_num_joueur()))

        # demarrer le tour de jeu du joueur index_joueur+1
        envoyer_message_au_client("Joueur {0}, c'est ton tour"
                                  .format(joueur.get_num_joueur()),
                                  Status.MON_TOUR,
                                  joueur.get_connexion())

        message_recu_client = recuperer_message_client(joueur.get_connexion())

        status_client = message_recu_client.lire_status()
        message_client = message_recu_client.lire_message()

        if compare_status(status_client, Status_Client.QUITTER):
            # gérer le cas où le joueur veut quitter la partie
            #passer en parametre le joueur directement
            quitter_la_partie(joueur, clients_connectes)
            if clients_connectes.get_nombre_joueurs() == 0:
                partie_demarree = False
            else:
                index_joueur = index_joueur - 1

        elif compare_status(status_client, Status_Client.MURER):
            murer_une_porte(joueur, message_client, labyrinthe, clients_connectes)

        elif compare_status(status_client, Status_Client.PERCER):
            percer_un_mur(joueur, message_client, labyrinthe, clients_connectes)

        elif compare_status(status_client, Status_Client.DEPLACEMENT):
            deplacer_robot(joueur, message_client, labyrinthe, clients_connectes)

        # verifier si le joueur a gagné
        if labyrinthe.partieGagnee(joueur.get_index_joueur()):
            partie_demarree = False
            joueur_gagnant = joueur.get_num_joueur()
        elif clients_connectes.get_nombre_joueurs() > 0:
            index_joueur = passer_au_joueur_suivant(index_joueur, clients_connectes.get_nombre_joueurs())



    if clients_connectes.get_nombre_joueurs() > 0:
        envoyer_message_tous_les_joueurs("Joueur {0} a gagné"
                                        .format(joueur_gagnant),
                                        Status.ECOUTE_SERVEUR,
                                        clients_connectes.get_liste_connexions())


def fermeture_connexion(clients_connectes, connexion_principale):
    affichage = AffichageConsole()

    affichage.afficheMessage("Fermeture de la connexion")
    for joueur in clients_connectes:
        affichage.afficheMessage("fermeture connection Joueur {0}"
                                 .format(joueur.get_num_joueur()))

        envoyer_message_au_client("Merci d'avoir joué. Au revoir.",
                                  Status.DECONNEXION,
                                  joueur.get_connexion())

        joueur.get_connexion().close()
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
