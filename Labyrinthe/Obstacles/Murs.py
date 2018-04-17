class Murs:

    def __init__(self):
        self.listeMurs = []
        self.imageMur = 'O'

    def ajouterMur(self,y,x):
        self.listeMurs.append((y,x))

    def __contains__(self,objet):
        return objet in self.listeMurs

    def __iter__(self):
        return iter(self.listeMurs)

    def getImage(self):
        return self.imageMur
