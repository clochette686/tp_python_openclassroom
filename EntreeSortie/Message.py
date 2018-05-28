import json

class MessageClientServeur:

    def __init__(self, message_client_serveur = None):
        if message_client_serveur is None:
             self.json_data = dict()
             self.json_data['message'] = ""
             self.json_data['connexion_acceptee'] = False
             self.json_data['premier_joueur'] = False
             self.json_data['partie_demarree'] = False
             self.json_data['mon_tour'] = False
             self.json_data['partie_terminee'] = False
        else:
            self.json_data = json.loads(message_client_serveur)

    def modifier_message(self, message):
        self.json_data['message'] = message

    def modifier_connexion_acceptee(self, valeur):
        self.json_data['connexion_acceptee'] = valeur

    def modifier_premier_joueur(self, valeur):
        self.json_data['premier_joueur'] = valeur

    def modifier_partie_demarree(self, valeur):
        self.json_data['partie_demarree'] = valeur

    def modifier_mon_tour(self, valeur):
        self.json_data['mon_tour'] = valeur        

    def modifier_partie_terminee(self, valeur):
        self.json_data['partie_terminee'] = valeur

    def exporter_json_message(self):
        return json.dumps(self.json_data)

    
json_test = MessageClientServeur()

json_test.modifier_message("plop")
json_test.modifier_connexion_acceptee(True)

json_test_str = json_test.exporter_json_message()
print(json_test_str)

json_test_2 = MessageClientServeur('{"connexion_acceptee": false, "partie_demarree": false,\
                                     "mon_tour": true, "partie_terminee": true, "message": "bouhhh",\
                                     "premier_joueur": true}')        
print(json_test_2.json_data['message'])
    
