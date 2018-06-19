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
		
    def deplacementPossible(self, num_joueur, direction):
        """ détermine si un déplacement du robot dans la direction indiquée en parametre
            est possible : la prochaine case est comprise dans la grille et n'est pas un obstacle
            non franchissable """

        #créé une copie du robot pour obtenir sa prochaine position
        (proch_pos_robot_y, proch_pos_robot_x) = self.robots.get_prochaine_position(num_joueur, direction)

        #si le robot se retrouve à la même position qu'un mur
        if self.estUnMur(proch_pos_robot_y, proch_pos_robot_x):
            deplacementPossible = False

        #si le robot se retrouve en dehors de la grille
        elif proch_pos_robot_y < 0 or \
                proch_pos_robot_y >= self.hauteur or \
                proch_pos_robot_x < 0  or \
                proch_pos_robot_x >= self.largeur:
            deplacementPossible = False
        else:
            deplacementPossible = True
        return deplacementPossible

    def partieGagnee(self, num_joueur):
        """ vérifie que le robot est à la même position que l'une des sorties """
        (y,x) = self.robots.getPositionRobot(num_joueur)
        return self.estUneSortie(y,x)

		    
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
            return "OK"

    def murer_porte(self, num_joueur, direction):
        #recuperer la position de la porte ciblee
        (pos_porte_y, pos_porte_x) = self.robots.get_prochaine_position(num_joueur, direction)
        if self.estUnePorte(pos_porte_y,pos_porte_x):
            self.portes.suppr_porte(pos_porte_y, pos_porte_x)
            self.murs.ajouterMur(pos_porte_y,pos_porte_x)

    def percer_mur(self, num_joueur, direction):
        #recuperer la position de la porte ciblee
        (pos_mur_y, pos_mur_x) = self.robots.get_prochaine_position(num_joueur, direction)

        if self.estUnMur(pos_mur_y,pos_mur_x):
            self.murs.suppr_mur(pos_mur_y, pos_mur_x)
            self.portes.ajouterPorte(pos_mur_y,pos_mur_x)
