class Robots:

    def __init__(self):
        self.listeRobots = []
        self.imageRobot = 'x'

    def ajouterRobot(self, y, x):
        self.listeRobots.append((y,x))

    def __contains__(self, objet):
        return objet in self.listeRobots

    def __iter__(self):
        return iter(self.listeRobots)

    def getImage(self):	
        return self.imageRobot	

    def getPositionRobot(self, num_joueur):
        return self.listeRobots[num_joueur]

    def get_prochaine_position(self, num_joueur, direction):
        """ permet d'avancer le robot d'une case dans la direction
            indiquée en parametre """
        (y, x) = self.getPositionRobot(num_joueur)
        proch_pos = (-1,-1)
        if direction == 'S':
            proch_pos = (y + 1, x)
        elif direction == 'N':
            proch_pos = (y - 1, x)
        elif direction == 'O':
            proch_pos = (y, x - 1)
        elif direction == 'E':
            proch_pos = (y, x + 1)
        return proch_pos

    #Nom des directions à sauvegarder dans un fichier pour pouvoir le modifier si besoin
    def avancer(self, num_joueur, direction):
        """ permet d'avancer le robot d'une case dans la direction
            indiquée en parametre """
        (y, x) = self.getPositionRobot(num_joueur)
        if direction == 'S':
            self.listeRobots[num_joueur] = (y + 1, x)
        elif direction == 'N':
            self.listeRobots[num_joueur] = (y - 1, x)
        elif direction == 'O':
            self.listeRobots[num_joueur] = (y, x - 1)
        elif direction == 'E':
            self.listeRobots[num_joueur] = (y, x + 1)

    def __repr__(self):
        affichage = ""
        for i, (y,x) in enumerate(self.listeRobots):
            affichage +=  "robot {2} : ({0},{1})".format(y,x,i)
        return affichage	
        
