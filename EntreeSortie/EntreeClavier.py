class SaisieClavier:

    def reponseOuiNon(self):
        """ Demande au joueur d'entrer la réponse 'O' ou 'N'
            tant que la réponse saisie n'est pas valide """
        
        choixValide = False
        choix = ""
        while not choixValide:
            choix = input()
            try:
                assert len(choix) == 1
                assert choix.upper() in ['O','N']
                choixValide = True
            except AssertionError:
                print("Veuillez entrer O ou N")
        return choix.upper()        

    def choixLabyrinthe(self,limite):
        """ Demande au joueur d'entrer le numéro d'un des labyrinthes de la liste
            tant que la réponse saisie n'est pas un entier compris entre 1 et
            le nombre de labyrinthes disponibles """
        choixValide = False
        choix = ""
        while not choixValide:
            print("Entrez un numéro de labyrinthe pour commencer à jouer :")
            choix = input()
            try:
                choix = int(choix)
                assert choix > 0
                assert choix <= limite
                choixValide = True
            except ValueError:
                print("Votre choix doit être un entier")
            except AssertionError:
                print("Votre choix doit être compris entre 1 et {0}".format(limite))
        return choix
                
    def choixDeplacement(self):
        """ Demande au joueur d'entrer une commande de déplacement ou la commande pour quitter la partie
            tant que la réponse saisie n'est pas au bon format"""
        choixValide = False
        choix = ""
        while not choixValide:
            print("Mouvement robot (E,S,N,O suivi ou non du nombre de déplacement) ou Quitter (Q):")
            choix = input()
            lettre = choix[0]
            chiffre = "1"
            quitter = False
            if len(choix) > 1:
                chiffre = str.join("",choix[1:])
            try:
                chiffre = int(chiffre)
                assert lettre.upper() in ['S','N','E','O','Q']
                quitter = (lettre.upper() == 'Q')
                if lettre.upper() == 'Q':
                    assert len(choix) == 1
                choixValide = True
            except ValueError:
                print("Le format d'une commande doit être une lettre (S,N,E,O) suivi ou non d'un chiffre ou Q pour quitter")
            except AssertionError:
                print("Le format d'une commande doit être une lettre (S,N,E,O) suivi ou non d'un chiffre ou Q pour quitter")
        return (lettre.upper(), chiffre, quitter)     
                
                