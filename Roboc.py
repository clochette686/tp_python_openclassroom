
from EntreeSortie.EntreeClavier import SaisieClavier
from Labyrinthe.Labyrinthe import Labyrinthe
from EntreeSortie.SortieConsole import AffichageConsole
import os
import glob


#objets utiles
saisie = SaisieClavier()
affichage = AffichageConsole()

#Les cartes doivent être au format .txt, seul ces fichiers sont
#recherchés dans le répertoire cartes/
listeCartesTxt = glob.glob("cartes/*.txt")

#afficher la liste des labyrinthes existants
print ("Labyrinthes existants :")
for i,carte in enumerate(listeCartesTxt):
	#on affiche uniquement le nom du fichier
	#soit la partie après le dernier "\"
	nomCarte = carte.split('\\')[-1]
	print("\t{0} - {1}".format(i+1,nomCarte))

#on récupère le choix du joueur
choixNumLabyrinthe = saisie.choixLabyrinthe(len(listeCartesTxt))

#récupère le nom correspondant
nomLabyrintheChoisi = listeCartesTxt[choixNumLabyrinthe - 1]

#on créé notre objet Labyrinthe à partir du fichier sélectionné
labyrinthe = Labyrinthe(nomLabyrintheChoisi)

#affiche le labyrinthe choisi 
affichage.afficheLabyrinthe(labyrinthe)

#demarrage de la partie
quitter = False
while not labyrinthe.partieGagnee() and not quitter:
    #lecture et vérification synthaxique du déplacement choisi par le joueur
    (direction,nbCase,quitter) = saisie.choixDeplacement()

    #l'utilisateur demande à quitter la partie
    if quitter:
        affichage.afficheMessage("Merci d'avoir joué avec nous. Au revoir")
        #on sauvegarde la partie en cours
        labyrinthe.sauverPartieEnCours()

    #l'utilisateur a saisi une commande pour déplacer le robot
    else:        
        i = 0
        sortieTrouvee = False
        #on avance le robot en pas à pas
        while i < nbCase and not sortieTrouvee:
            #si le déplacement est possible
            if labyrinthe.deplacementPossible(direction):
                labyrinthe.robot.avancer(direction)
                affichage.afficheLabyrinthe(labyrinthe)
            #si le robot a trouvé une sortie, on arrete le déplacement
            elif labyrinthe.partieGagnee():
                sortieTrouvee = True
            #si le déplacement n'est pas possible
            else:
                affichage.afficheMessage("Aïe !!! Je me suis cogné")
            i += 1            
#fin de partie
#affichage si le jeu se termine par une victoire
if not quitter:
    affichage.afficheMessage("Bravo!! Vous êtes sorti du labyrinthe")

