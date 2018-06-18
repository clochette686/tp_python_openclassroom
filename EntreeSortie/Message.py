import json
from enum import Enum

class Status(Enum):
    ECOUTE_SERVEUR                      = 0
    DEMANDE_DEMARRAGE_PARTIE            = 1
    MON_TOUR                            = 2
    DECONNEXION             = 3
    DECONNECTE              = 4

    def get_nom_status(self, status_enum):
        return status_enum.name


class Status_Client(Enum):
    DEMARRAGE_PARTIE        = 0
    DEPLACEMENT             = 1
    QUITTER                 = 2
    INIT                    = 3
    MURER                   = 4
    PERCER                  = 5


class MessageServeur:

    def __init__(self):
        self.json_data = dict()
        self.json_data['message'] = ""
        self.json_data['status'] = Status.ECOUTE_SERVEUR.name

    def modifier_message(self, message):
        self.json_data['message'] = message

    def modifier_status(self, valeur):
        if valeur in Status:
            self.json_data['status'] = valeur.name

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

class MessageClient:

    def __init__(self):
        self.json_data = dict()
        self.json_data['status'] = Status_Client.INIT.name
        self.json_data['message'] = ""

    def modifier_message(self, message):
        self.json_data['message'] = message

    def modifier_status(self, valeur):
        if valeur in Status_Client:
            self.json_data['status'] = valeur.name

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


if __name__ == '__main__':
    json_test = MessageServeur()

    json_test.modifier_message("plop")
    json_test.modifier_status(Status.DEMANDE_DEMARRAGE_PARTIE.name)

    json_test_str = json_test.exporter_json_message()
    print(json_test_str)

    json_test_2 = MessageServeur()
    json_test_2.importer_json_message('{"message": "booooooouhhh", "status": "ECOUTE_SERVEUR",\
                                         "numero_joueur": true, "inutile": "plop"}')
    print(json_test_2.json_data)

    message_double = '{"message": "booooooouhhh", "status": "ECOUTE_SERVEUR",\
    "numero_joueur": true, "inutile": "plop"}{"message": "booooooouhhh", "status": "ECOUTE_SERVEUR",\
    "numero_joueur": true, "inutile": "plop"}'

    print("nb json = ", message_double.count("{"))
    new_message = message_double.split("{")[1:]
    print(new_message)
    new_message = ["{" + message for message in new_message]
    print(new_message)
    
