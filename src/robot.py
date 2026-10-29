from copy import deepcopy
from src.carte_mentale import CarteMentale
from src.resident import Resident
from src.monde import Monde
from src.e_actions import ACTIONS
from src.e_mouvement import MOUVEMENT
from src.e_etats import ETATS

class Robot():
    position : tuple[int,int]
    armoire_mentale : list[list[str | None]]
    carte_mentale : CarteMentale
    etat : ETATS
    resident_cible : Resident | None
    inventaire : str | None
    liste_casier_recherche : list[tuple[int,int]]
    perception : dict[str,str]
    contenu_casier : str | None
    actions : list[ACTIONS]
    curseur_courant : tuple[int,int] | None
    chemin_courant : list[tuple[int, int]] | None
    
    def __init__(self,
                position : tuple[int,int],
                carte_mentale_base : CarteMentale,
                resident_cible : Resident):
        self.position = position
        self.armoire_mentale = [
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None]
        ]       
        self.carte_mentale = deepcopy(carte_mentale_base)
        self.etat = ETATS.IDLE
        self.resident_cible = resident_cible
        self.inventaire = None
        self.liste_casier_recherche = []
        self.perception = {}
        self.contenu_casier = None
        self.actions = []
        self.curseur_courant = None
        self.chemin_courant = None
        
    def AVANCER(self, mov: MOUVEMENT):
        pass
    
    def CONSULTER(self):
        pass
    
    def CHERCHER(self, mov: MOUVEMENT):
        pass
    
    def PRENDRE(self):
        pass
    
    def DONNER(self):
        pass
    
    def PERCEVOIR(self, monde: Monde):
        # On demande à la carte de Monde de récupérer les positions adjacentes pour les placer dans le dico perception
        self.perception["N"] = Monde.carte.getCase(self.position, MOUVEMENT.N)
        self.perception["S"] = Monde.carte.getCase(self.position, MOUVEMENT.S)
        self.perception["E"] = Monde.carte.getCase(self.position, MOUVEMENT.E)
        self.perception["O"] = Monde.carte.getCase(self.position, MOUVEMENT.O)
        
        # Si une des cases est l'armoire, on enregistre le contenu_casier sur lequel le curseur d'armoire est placé
        if "A" in self.perception.values():
            ligne_casier_courant = Monde.armoire.curseur[0]
            colonne_casier_courant = Monde.armoire.curseur[1]
            
            self.contenu_casier = Monde.armoire.casiers[ligne_casier_courant][colonne_casier_courant]
            self.curseur_courant = (ligne_casier_courant,colonne_casier_courant)
            
    
    def MEMORISER(self):
        self.carte_mentale.saveCases(self.position, self.perception)
        self.armoire_mentale[self.curseur_courant[0]][self.curseur_courant[1]] = self.contenu_casier
    
    def DECISION(self):
        while not self.actions:
            match self.etat:
                # ---- IDLE ---- #
                case ETATS.IDLE:
                    if self.resident_cible == None:
                        self.actions.append(ACTIONS.ATTENDRE)
                    else:
                        self.etat = ETATS.MOVING_DICO
                        
                # ---- MOVING_DICO ---- #        
                case ETATS.MOVING_DICO:
                    if "D" not in self.perception.values():
                        #il faut calculer le chemin courant
                        #pour cela j'ai besoin de calculer d'abord les cases d'arrivée du chemin, càd les cases adjacentes à la case qui contient "D"
                        nblignes = self.carte_mentale.dimensions[0]
                        nbcolonnes = self.carte_mentale.dimensions[1]
                        arrivees = []
                        for ligne in range(nblignes):
                            for colonne in range(nbcolonnes):
                                if self.carte_mentale.grille[ligne][colonne] == "D":
                                    if ligne > 0:
                                        case = [ligne - 1, colonne]
                                        arrivees.append(case)
                                    if ligne < nblignes - 1:
                                        case = [ligne + 1, colonne]
                                        arrivees.append(case)
                                    if colonne > 0:
                                        case = [ligne, colonne - 1]
                                        arrivees.append(case)
                                    if colonne < nbcolonnes - 1:
                                        case = [ligne, colonne + 1]
                                        arrivees.append(case)
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(self.position, arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.actions.append(ACTIONS.AVANCER)
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_DICO
                    else:
                        self.actions.append(ACTIONS.CONSULTER)
                
                # ---- MOVING_ARMOIRE ---- #  
                case ETATS.MOVING_ARMOIRE:
                    if "A" not in self.perception.values():
                        #il faut calculer le chemin courant
                        nblignes = self.carte_mentale.dimensions[0]
                        nbcolonnes = self.carte_mentale.dimensions[1]
                        arrivees = []
                        for ligne in range(nblignes):
                            for colonne in range(nbcolonnes):
                                if self.carte_mentale.grille[ligne][colonne] == "A":
                                    if ligne > 0:
                                        case = [ligne - 1, colonne]
                                        arrivees.append(case)
                                    if ligne < nblignes - 1:
                                        case = [ligne + 1, colonne]
                                        arrivees.append(case)
                                    if colonne > 0:
                                        case = [ligne, colonne - 1]
                                        arrivees.append(case)
                                    if colonne < nbcolonnes - 1:
                                        case = [ligne, colonne + 1]
                                        arrivees.append(case)
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(self.position, arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.actions.append(ACTIONS.AVANCER)
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_ARMOIRE
                    else:
                        self.etat = ETATS.FINDING_OBJECT
                
                # ---- MOVING_RESIDENT ---- #
                case ETATS.MOVING_RESIDENT:
                    if "R" not in self.perception.values():
                        #il faut calculer le chemin courant
                        nblignes = self.carte_mentale.dimensions[0]
                        nbcolonnes = self.carte_mentale.dimensions[1]
                        arrivees = []
                        for ligne in range(nblignes):
                            for colonne in range(nbcolonnes):
                                if self.carte_mentale.grille[ligne][colonne] == "R":
                                    if ligne > 0:
                                        case = [ligne - 1, colonne]
                                        arrivees.append(case)
                                    if ligne < nblignes - 1:
                                        case = [ligne + 1, colonne]
                                        arrivees.append(case)
                                    if colonne > 0:
                                        case = [ligne, colonne - 1]
                                        arrivees.append(case)
                                    if colonne < nbcolonnes - 1:
                                        case = [ligne, colonne + 1]
                                        arrivees.append(case)
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(self.position, arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.actions.append(ACTIONS.AVANCER)
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_RESIDENT
                    else:
                        self.actions.append(ACTIONS.DONNER)
                
                # ---- FINDING_OBJECT ---- #
                case ETATS.FINDING_OBJECT:
                    pass
    
    def ACTION(self):
        pass
    
    def deplacer_vers(self, pos: tuple[int,int]):
        pass
    
    