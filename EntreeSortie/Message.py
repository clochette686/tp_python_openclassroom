import re

class MessageClientServeur:

    def __init__(self, message_client_serveur = None):
        if message_client_serveur is None:
            self.message = ""
            self.partie_commencee = False
            self.mon_tour = False
            self.partie_terminee = False
        else:
            valeurs = self.analyse_message_client_serveur(message_client_serveur)
            self.message = valeurs[1]
            self.partie_commencee = valeurs[2]
            self.mon_tour = valeurs[3]
            self.partie_terminee = valeurs[4]            
            
    def analyse_message_client_serveur(self, message):
        recherche = r'^{ *message: (.*), *partie_commencee: (.*), *mon_tour: (.*), *partie_terminee: (.*)}$'
        valeurs = re.split( recherche, message)
        print(valeurs)

    def set_message(self, message):
        self.message = message

    def set_partie_commencee(self, booleen):
        self.partie_commencee = booleen

    def set_mon_tour(self, booleen):
        self.mon_tour = booleen

    def set_partie_terminee(self, booleen):
        self.partie_terminee = booleen
        
    def creer_message_depuis_valeurs(self):
        message = "{ "
        message += "message: '" + self.message + "', "
        message += "partie_commencee: " + str(self.partie_commencee) + ", "
        message += "mon_tour: " + str(self.mon_tour) + ", "
        message += "partie_terminee: " + str(self.partie_terminee)
        message += "}"
        print(message)
        return message
    
m = MessageClientServeur()
m.set_message("plop salut")
message = m.creer_message_depuis_valeurs()
#message = "{message: 'bonjour', partie_commencee: False, mon_tour: False, partie_terminee: False}"
m.analyse_message_client_serveur(message)
