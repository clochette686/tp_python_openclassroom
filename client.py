import socket
from threading import Thread
from threading import RLock


from EntreeSortie.Message import MessageServeur
from EntreeSortie.Message import Status
from EntreeSortie.Message import MessageClient
from EntreeSortie.Message import Status_Client
from EntreeSortie.SortieConsole import AffichageConsole
from EntreeSortie.EntreeClavier import SaisieClavier

import time


class Partie_envoie_messages_serveur(Thread):

    def __init__(self, connexion_serveur):
        Thread.__init__(self)
        self.serveur = connexion_serveur
        self.message_a_envoyer = []
        self.verrou_msg_a_envoyer = RLock()
        self.connection_active = True

    def set_message(self, message):
        with self.verrou_msg_a_envoyer:
            self.message_a_envoyer.append(message.encode())
    
    def run(self):
        while self.connection_active:
            with self.verrou_msg_a_envoyer:
                if len(self.message_a_envoyer) > 0:
                    for message in self.message_a_envoyer:
                        self.serveur.send(message)
                    self.message_a_envoyer = []    
            time.sleep(1)
                    

class Partie_reception_messages_serveur(Thread):

    def __init__(self, connexion_serveur):
        Thread.__init__(self)
        self.serveur = connexion_serveur
        self.messages_recus = []
        self.verrou_msg_a_lire = RLock()
        self.connection_active = True

    def get_messages(self):
        with self.verrou_msg_a_lire:
            messages = []
            while len(self.messages_recus) > 0:
                message = self.messages_recus.pop(0)
                messages.append(message.decode())
            return messages

    def get_message(self):
        with self.verrou_msg_a_lire:
            if len(self.messages_recus) > 0:
                message = self.messages_recus.pop(0)
            else:
                message = None
            return message

    def run(self):
        while self.connection_active:
            with self.verrou_msg_a_lire:
                message = self.serveur.recv(1024)
                message = message.decode()
                if len(message) > 0:
                    #cas particulier de plusieurs json recu dans un seul message
                    if message.count("{") > 1:
                        messages_json = ["{" + message for message in message.split("{")[1:]]
                        for message_json in messages_json:
                            self.messages_recus.append(message_json)
                    else:
                        self.messages_recus.append(message)
            time.sleep(1)

class Partie_lecture_entree_clavier(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.saisie_utilisateur = []
        self.verrou_cmd_utilisateur = RLock()
        self.connection_active = True

    def get_commandes(self):
        with self.verrou_cmd_utilisateur:
            liste_commandes = list(self.saisie_utilisateur)
            self.saisie_utilisateur = []
            return liste_commandes

    def get_first_commande(self):
        with self.verrou_cmd_utilisateur:
            if len(self.saisie_utilisateur) > 0:
                commande = self.saisie_utilisateur.pop(0)
                return commande
            else:
                return ""

    def run(self):
        while self.connection_active:
            commande = input()
            if commande != "": 
                with self.verrou_cmd_utilisateur:
                    self.saisie_utilisateur.append(commande)
            time.sleep(1)
       


def connexion_au_serveur():
    hote = "localhost"
    port = 12800    
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_avec_serveur.connect((hote, port))
    print("Connexion établie avec le serveur sur le port {}".format(port))
    return connexion_avec_serveur

def creer_message_a_envoyer(texte, status):
    message = MessageClient()
    message.modifier_message(texte)
    message.modifier_status(status)
    return message.exporter_json_message()

def jouer_son_tour(thread_envoi_serveur):
    saisie_clavier = SaisieClavier()
    (lettre, chiffre, quitter) = saisie_clavier.choixDeplacement()

    if lettre == 'Q':
        status = Status_Client.QUITTER
    else:
        status = Status_Client.DEPLACEMENT
    message_a_envoyer = creer_message_a_envoyer(lettre, status)

    thread_envoi_serveur.set_message(message_a_envoyer)

def fermeture_connexion_serveur(connexion_avec_serveur):
    print("Fermeture de la connexion")
    connexion_avec_serveur.close()    

def reception_message_serveur(thread_recep_serveur):

    message = thread_recep_serveur.get_message()

    if message is not None:
        message_json = MessageServeur()
        message_json.importer_json_message(message)
        return message_json
    else:
        return None

def saisie_demarrage_partie(thread_envoi_serveur):
    saisie_clavier = SaisieClavier()
    commande = saisie_clavier.demarragePartie()

    message_a_envoyer = creer_message_a_envoyer(commande, Status_Client.DEMARRAGE_PARTIE)

    thread_envoi_serveur.set_message(message_a_envoyer)

def compare_status(nom_status, status_a_comparer):
    return nom_status == status_a_comparer.name

def client_main():
    status = Status.ECOUTE_SERVEUR.name
    affichage = AffichageConsole()

    connexion_avec_serveur = connexion_au_serveur()

    #demarrer les thread de communication
    thread_envoi_serveur = Partie_envoie_messages_serveur(connexion_avec_serveur)
    thread_recep_serveur = Partie_reception_messages_serveur(connexion_avec_serveur)

    thread_envoi_serveur.start()
    thread_recep_serveur.start()

    while not compare_status(status, Status.DECONNECTE):

        if compare_status(status, Status.ECOUTE_SERVEUR):
            message_serveur = reception_message_serveur(thread_recep_serveur)
            if message_serveur is not None:
                status = message_serveur.lire_status()
                message_recu = message_serveur.lire_message()
                affichage.afficheMessage(message_recu)

        elif compare_status(status, Status.DEMANDE_DEMARRAGE_PARTIE):
            saisie_demarrage_partie(thread_envoi_serveur)
            status = Status.ECOUTE_SERVEUR.name

        elif compare_status(status, Status.MON_TOUR):
            jouer_son_tour(thread_envoi_serveur)
            status = Status.ECOUTE_SERVEUR.name

        elif compare_status(status, Status.DECONNEXION):
            #gérer la deconnexion
            thread_envoi_serveur.connection_active = False
            thread_recep_serveur.connection_active = False
            fermeture_connexion_serveur(connexion_avec_serveur)
            status = Status.DECONNECTE.name

if __name__ == "__main__":
    client_main()




