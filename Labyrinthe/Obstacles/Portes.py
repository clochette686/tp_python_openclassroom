class Portes:

    def __init__(self):
        self.listePortes = []
        self.imagePorte = '.'

    def ajouterPorte(self,y,x):
        self.listePortes.append((y,x))

    def __contains__(self,objet):
        return objet in self.listePortes

    def __iter__(self):
        return iter(self.listePortes)

    def getImage(self):
        return self.imagePorte
