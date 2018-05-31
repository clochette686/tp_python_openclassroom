import socket
from threading import Thread
from threading import RLock
import re

from EntreeSortie.Message import MessageServeur
from EntreeSortie.Message import Status
from EntreeSortie.SortieConsole import AffichageConsole

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
            print("message a envoyer " + message + "\n")
            self.message_a_envoyer.append(message.encode())
            print("longueur message a envoyer = " + str(len(self.message_a_envoyer)))
    
    def run(self):
        while self.connection_active:
            with self.verrou_msg_a_envoyer:
                if len(self.message_a_envoyer) > 0:
                    for message in self.message_a_envoyer:
                        print("envoie du message " + message.decode())
                        self.serveur.send(message)
                    self.message_a_envoyer = []    
            time.sleep(4)        
                    

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
            print("receptionner les messages\n")
            with self.verrou_msg_a_lire:
                message = self.serveur.recv(1024)
                if len(message) > 0:
                    self.messages_recus.append(message)
            time.sleep(4)        

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
                print("commande lue = ", commande, " **\n")
                return commande
            else:
                return ""

    def run(self):
        while self.connection_active:
            commande = input()
            if commande != "": 
                with self.verrou_cmd_utilisateur:
                    self.saisie_utilisateur.append(commande)
            time.sleep(4)    
       


def connexion_au_serveur():
    hote = "localhost"
    port = 12800    
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_avec_serveur.connect((hote, port))
    print("Connexion établie avec le serveur sur le port {}".format(port))
    return connexion_avec_serveur


def traitement_messages_serveur(thread_recep_serveur):
    partie_commencee = False
    #on recupere et affiche tous les messages du serveur
    messages = thread_recep_serveur.get_messages()
    if len(messages) > 0:
        for message in messages:
            #si le message correspond au message de début de partie, un autre joueur a demarré la partie
            if re.search(r"vient de démarrer la partie", message):
                partie_commencee = True
            print(message + "\n")
        #apres chaque nouveau message du serveur, on rappelle au joueur la commande pour lancer la partie
        if not partie_commencee:
            print("Appuyez sur C pour commencer la partie \n")
    return partie_commencee       

def traitement_input_client(thread_envoi_serveur, thread_input_clavier):
    partie_commencee = False
    #on regarde parmi les saisies clavier du joueur si il n'aurait pas demandé à démarrer la partie
    commande = thread_input_clavier.get_first_commande()

    if commande.rstrip().upper() == 'C':
        thread_envoi_serveur.set_message(commande)
        partie_commencee = True
    return partie_commencee    

def attente_demarrage_partie(thread_envoi_serveur, thread_recep_serveur, thread_input_clavier):
    partie_commencee = False

    #phase d'attente du debut de la partie
    while not partie_commencee:
        #print("traitement messages serveur")
        partie_commencee = partie_commencee or traitement_messages_serveur(thread_recep_serveur)
        #print("traitement input client")
        if not partie_commencee:
            partie_commencee = partie_commencee or traitement_input_client(thread_envoi_serveur, thread_input_clavier)
    print("partie_commencee = TRUE maintenant")

def attendre_son_tour(thread_recep_serveur, thread_envoi_serveur, thread_input_clavier, partie_terminee):
    mon_tour = False
    #en attendant son tour de jeu, on affiche toutes les infos recues par le serveur
    while not mon_tour and not partie_terminee:
        messages = thread_recep_serveur.get_messages()
        for message in messages:
            #verifie si le serveur nous signale que c'est notre tour
            if re.search(r"c'est ton tour", message):
                mon_tour = True
            #verifie si le serveur nous signale que la partie est terminée    
            if re.search(r"gagné", message):
                partie_terminee = True
                thread_input_clavier.connection_active = False #condition pour arreter les thread de communication
                thread_envoi_serveur.connection_active = False #condition pour arreter les thread de communication
                thread_recep_serveur.connection_active = False #condition pour arreter les thread de communication
            print(message + "\n")
    return (mon_tour, partie_terminee)        

def jouer_son_tour(thread_envoi_serveur, thread_input_clavier):
    commande_valide = ""
    print("Veuillez entrer votre prochain mouvement")
    while commande_valide == "":
        
        commande = thread_input_clavier.get_first_commande()
        #commande = input()
        if commande.rstrip().upper() in ["N","S","E","W"]:
            commande_valide = commande
            
    #le joueur a saisi une commande valide, on l'envoie au serveur
    thread_envoi_serveur.set_message(commande_valide)    

def deroulement_tours_de_jeu(thread_recep_serveur, thread_envoi_serveur, thread_input_clavier):
    #demarrage de la partie            
    partie_terminee = False

    #on boucle tant que personne n'a gagné la partie
    while not partie_terminee:

        (mon_tour, partie_terminee) = attendre_son_tour(thread_recep_serveur, thread_envoi_serveur, thread_input_clavier, partie_terminee)

        #c'est mon tour
        if mon_tour and not partie_terminee:
            jouer_son_tour(thread_envoi_serveur, thread_input_clavier)

def fermeture_connexion_serveur(connexion_avec_serveur):
    print("Fermeture de la connexion")
    connexion_avec_serveur.close()    

def reception_message_serveur(thread_recep_serveur):

    message = None
    while message == None:
        thread_recep_serveur.get_message()
    message_json = MessageServeur()
    message_json.importer_json_message(message)
    return message_json

def client_main():
    status = Status.INIT
    affichage = AffichageConsole()
    mon_numero_joueur = -1

    connexion_avec_serveur = connexion_au_serveur()

    #demarrer les thread de communication
    thread_input_clavier = Partie_lecture_entree_clavier()
    thread_envoi_serveur = Partie_envoie_messages_serveur(connexion_avec_serveur)
    thread_recep_serveur = Partie_reception_messages_serveur(connexion_avec_serveur)

    thread_input_clavier.start()
    thread_envoi_serveur.start()
    thread_recep_serveur.start()

    while status != Status.DECONNECTE:

        if status == Status.INIT
            message_serveur = reception_message_serveur(thread_recep_serveur)
            status = message_serveur.lire_status()
            message_recu = message_serveur.lire_message()
            mon_numero_joueur = message_serveur.lire_numero_joueur()
            affichage.afficheMessage(message_recu)
            #suite : CONNEXION_REFUSEE ou CONNECION_ACCEPTEE

        elif status == Status.CONNEXION_REFUSEE:
            thread_envoi_serveur.connection_active = False
            thread_input_clavier.connection_active = False
            thread_recep_serveur.connection_active = False
            status = Status.DECONNECTE

        elif status == Status.CONNEXION_ACCEPTEE:
            if mon_numero_joueur == 1:
                #c'est à moi de demarrer la partie avec un input bloquant
                #une fois qu'une commande correcte est saisie
                status = Status.PARTIE_DEMARREE
            else:
                message_serveur = reception_message_serveur(thread_recep_serveur)
                status = message_serveur.lire_status()
                message_recu = message_serveur.lire_message()
                mon_numero_joueur = message_serveur.lire_numero_joueur()
                affichage.afficheMessage(message_recu)
                #suite PARTIE_DEMARREE

        elif status == Status.PARTIE_DEMARREE:
            message_serveur = reception_message_serveur(thread_recep_serveur)
            status = message_serveur.lire_status()
            message_recu = message_serveur.lire_message()
            mon_numero_joueur = message_serveur.lire_numero_joueur()
            affichage.afficheMessage(message_recu)
            #suite ATTENTE_TOUR_DE_JEU

        elif status == Status.ATTENTE_TOUR_DE_JEU:
            message_serveur = reception_message_serveur(thread_recep_serveur)
            status = message_serveur.lire_status()
            message_recu = message_serveur.lire_message()
            mon_numero_joueur = message_serveur.lire_numero_joueur()
            affichage.afficheMessage(message_recu)
            #suite : MON_TOUR ou PARTIE_FINIE

        elif status == Status.MON_TOUR:
            #demander saisie commande valide
            #envoi au serveur
            status = Status.ATTENTE_TOUR_DE_JEU

        elif status == Status.PARTIE_TERMINEE:
            message_serveur = reception_message_serveur(thread_recep_serveur)
            status = message_serveur.lire_status()
            message_recu = message_serveur.lire_message()
            mon_numero_joueur = message_serveur.lire_numero_joueur()
            affichage.afficheMessage(message_recu)
            #suite : DECONNEXION

        elif status == Status.DECONNEXION:
            #gérer la deconnexion
            status = Status.DECONNECTE



    print("attente demarrage partie ")
    attente_demarrage_partie(thread_envoi_serveur, thread_recep_serveur, thread_input_clavier)

    print("la partie est demarree ")
    deroulement_tours_de_jeu(thread_recep_serveur, thread_envoi_serveur, thread_input_clavier)

    print("fin de partie")
    fermeture_connexion_serveur(connexion_avec_serveur)

client_main()    




