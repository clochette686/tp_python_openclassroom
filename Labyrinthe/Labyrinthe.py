from .Robots import Robots
from .Obstacles.Murs import Murs
from .Obstacles.Sorties import Sorties
from .Obstacles.Portes import Portes
import random

class Labyrinthe:
    
    def __init__(self,carte=None):
        self.largeur = 0
        self.hauteur = 0
        self.murs = Murs()
        self.sorties = Sorties()
        self.portes = Portes()
        self.robots = Robots()

        if carte != None :
            with open(carte,'r') as labyrinthe:
                lignes = labyrinthe.readlines()
                self.hauteur = len(lignes)
                for y,ligne in enumerate(lignes):
                    self.largeur = len(ligne)
                    for x,colonne in enumerate(ligne):
                        if colonne == 'O':
                            self.murs.ajouterMur(y,x)
                        elif colonne == ".":
                            self.portes.ajouterPorte(y,x)
                        elif colonne == "X":
                            pass #le robot n'est plus positionné de base
                        elif colonne == "U":
                            self.sorties.ajouterSortie(y,x)
                           
    def estUnMur(self,y,x):
        """ vérifie si l'élément à la position (y,x) est un mur """
        return (y,x) in self.murs

    def estUnePorte(self,y,x):
        """ vérifie si l'élément à la position (y,x) est une porte """
        return (y,x) in self.portes

    def estUneSortie(self,y,x):
        """ vérifie si l'élément à la position (y,x) est une sortie """
        return (y,x) in self.sorties

    def estUnRobot(self,y,x):
        """ vérifie si l'élément à la position (y,x) est un robot """
        return (y,x) in self.robots		
		
    def deplacementPossible(self,direction):
        """ détermine si un déplacement du robot dans la direction indiquée en parametre
            est possible : la prochaine case est comprise dans la grille et n'est pas un obstacle
            non franchissable """

        #créé une copie du robot pour obtenir sa prochaine position
        robotTemp = Robot(self.robot.y,self.robot.x)
        robotTemp.avancer(direction)

        #si le robot se retrouve à la même position qu'un mur
        if self.estUnMur(robotTemp.y,robotTemp.x):
            deplacementPossible = False

        #si le robot se retrouve en dehors de la grille
        elif robotTemp.y < 0 or\
                robotTemp.y >= self.hauteur or\
                robotTemp.x < 0  or\
                robotTemp.x >= self.largeur:
            deplacementPossible = False
        else:
            deplacementPossible = True
        return deplacementPossible

    def partieGagnee(self):
        """ vérifie que le robot est à la même position que l'une des sorties """
        partie_gagnee = False
        for (y,x) in self.Robots:
            partie_gagne = partie_gagnee or self.estUneSortie(y,x)
        return partie_gagnee
		    
    def ajouterPositionNouveauJoueur(self):
        liste_cases_vides = []
        for y in range(self.hauteur):
            for x in range(self.largeur):
                if not self.estUnMur(y,x) and not self.estUnePorte(y,x) and not self.estUneSortie(y,x) and not self.estUnRobot(y,x):
                    liste_cases_vides.append((y,x))
        if len(liste_cases_vides) == 0:
            return "Il n'y a plus de case vide pour placer votre robot"
        else:
            (y_nouveau_robot,x_nouveau_robot) =  random.choice(liste_cases_vides)
            self.robots.ajouterRobot(y_nouveau_robot, x_nouveau_robot)
            return ""