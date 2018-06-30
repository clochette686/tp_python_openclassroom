
class Joueur:

    def __init__(self, num, connexion):
        self.numero_joueur = num + 1
        self.index_joueur = num
        self.connexion = connexion

    def get_num_joueur(self):
        return self.numero_joueur

    def get_index_joueur(self):
        return self.index_joueur

    def get_connexion(self):
        return self.connexion

class Joueurs:

    def __init__(self):
        self.liste_joueurs = []

    def __iter__(self):
        return iter(self.liste_joueurs)

    def ajouter_joueur(self, joueur):
        self.liste_joueurs.append(joueur)

    def get_liste_connexions(self):
        liste_connexion = []
        for joueur in self.liste_joueurs:
            liste_connexion.append(joueur.get_connexion())
        return liste_connexion

    def get_joueur_avec_connexion(self, connexion):
        for joueur in self.liste_joueurs:
            if joueur.get_connexion() == connexion:
                return joueur
        return None

    def get_joueur_avec_index(self, index):
        return self.liste_joueurs[index]

    def get_nombre_joueurs(self):
        return len(self.liste_joueurs)

    def supprimmer_joueur(self, joueur):
        self.liste_joueurs.remove(joueur)