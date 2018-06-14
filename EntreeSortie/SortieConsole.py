from Labyrinthe import Labyrinthe

class AffichageConsole:

    
    def afficheLabyrinthe(self, labyrinthe, joueur_actif):
        """ Reconstruit l'image du Labyrinthe à partir de l'objet Labyrinthe """
        #créé une grille (matrice) remplie de caractères vides de la taille du labyrinthe
        imageLabyrinthe = list()
        for i in range(labyrinthe.hauteur):
            imageLabyrinthe.append([" "] * labyrinthe.largeur)

        #ajouter les murs
        for (y,x) in labyrinthe.murs:
            imageLabyrinthe[y][x] = labyrinthe.murs.getImage()

        #ajouter les sorties
        for (y,x) in labyrinthe.sorties:
            imageLabyrinthe[y][x] = labyrinthe.sorties.getImage()

        #ajouter les portes
        for (y,x) in labyrinthe.portes:
            imageLabyrinthe[y][x] = labyrinthe.portes.getImage()

        #ajouter robot
        for i,(y,x) in enumerate(labyrinthe.robots):
            image = labyrinthe.robots.getImage()
            if i == joueur_actif:
                    image = image.upper()
            imageLabyrinthe[y][x] = image

        #transforme la matrice en une chaine de caractère à afficher
        affichage = ""
        for ligne in imageLabyrinthe:
            affichage += str.join("",ligne) + "\n"
        return affichage

    def afficheMessage(self,message):
        """ gere l'affichage des messages à l'utilisateur """
        print(message)

    def affichage_numero_joueur(self,num_joueur):
        return str(num_joueur + 1)