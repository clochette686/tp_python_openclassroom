class Sorties:

    def __init__(self):
        self.listeSorties = []
        self.imageSortie = 'U'

    def ajouterSortie(self,y,x):
        self.listeSorties.append((y,x))

    def __contains__(self,objet):
        return objet in self.listeSorties

    def __iter__(self):
        return iter(self.listeSorties)

    def getImage(self):
        return self.imageSortie
