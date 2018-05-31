import json
from enum import Enum

class Status(Enum):
    INIT                    = 0
    CONNEXION_ACCEPTEE      = 1
    CONNEXION_REFUSEE       = 2
    ATTENTE_DEMARRAGE       = 3
    PARTIE_DEMARREE         = 4
    ATTENTE_TOUR_DE_JEU     = 5
    MON_TOUR                = 6
    PARTIE_TERMINEE         = 7
    DECONNEXION             = 8
    DECONNECTE              = 9




class MessageServeur:

    def __init__(self):
        self.json_data = dict()
        self.json_data['message'] = ""
        self.json_data['status'] = Status.INIT.name
        self.json_data['numero_joueur'] = -1



    def modifier_message(self, message):
        self.json_data['message'] = message


    def modifier_numero_joueur(self, valeur):
        self.json_data['numero_joueur'] = valeur

    def modifier_status(self, valeur):
        if valeur in Status:
            self.json_data['status'] = valeur

    def exporter_json_message(self):
        return json.dumps(self.json_data)

    def importer_json_message(self, message):
        json_message = json.loads(message)
        for key in self.json_data.keys():
            if key in json_message.keys():
                self.json_data[key] = json_message[key]

    def lire_status(self):
        return self.json_data['status']

    def lire_message(self):
        return self.json_data['message']

    def lire_numero_joueur(self):
        return self.json_data['numero_joueur']
    
json_test = MessageServeur()

json_test.modifier_message("plop")
json_test.modifier_status(Status.CONNEXION_ACCEPTEE.name)

json_test_str = json_test.exporter_json_message()
print(json_test_str)

json_test_2 = MessageServeur()
json_test_2.importer_json_message('{"message": "booooooouhhh", "status": "ATTENTE_TOUR_DE_JEU",\
                                     "numero_joueur": true, "inutile": "plop"}')
print(json_test_2.json_data)
    
