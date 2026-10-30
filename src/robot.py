from copy import deepcopy
import reconfort_io as rio
from src.carte_mentale import CarteMentale
from src.e_actions import ACTIONS
from src.e_mouvement import MOUVEMENT
from src.e_etats import ETATS

class Robot():
    position : tuple[int,int]
    armoire_mentale : list[list[str | None]]
    carte_mentale : CarteMentale
    etat : ETATS
    resident_cible : str | None
    demande_cible : str | None
    inventaire : str | None
    liste_casier_recherche : list[tuple[int,int]]
    perception : dict[str,str]
    contenu_casier : str | None
    actions : list[ACTIONS]
    curseur_courant : tuple[int,int] | None
    chemin_courant : list[tuple[int, int]] | None
    emotion_intensite : tuple[int, int] | None
    chemin_armoire_courant : list[tuple[int, int]] | None
    
    def __init__(self,
                position : tuple[int,int],
                carte_mentale_base : CarteMentale,
                scenario : Scenario):
        self.position = position
        self.armoire_mentale = [
            ["inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu"],
            ["inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu"],
            ["inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu", "inconnu"]
        ]       
        self.carte_mentale = deepcopy(carte_mentale_base)
        self.etat = ETATS.IDLE
        demande = scenario.nextDemande()
        self.resident_cible = demande["resident"]
        self.demande_cible = demande["message"]
        self.inventaire = None
        self.liste_casier_recherche = []
        self.perception = {}
        self.contenu_casier = None
        self.actions = []
        self.curseur_courant = None
        self.chemin_courant = None
        self.emotion_intensite = None
        self.chemin_armoire_courant = None
        
    def AVANCER(self, mov: MOUVEMENT):
        match mov:
            case MOUVEMENT.N:
                self.position = (self.position[0] - 1,self.position[1])
            case MOUVEMENT.S:
                self.position = (self.position[0] + 1,self.position[1])
            case MOUVEMENT.E:
                self.position = (self.position[0] - 1,self.position[1])
            case MOUVEMENT.O:
                self.position = (self.position[0] - 1,self.position[1])
    
    def CONSULTER(self, dico: Dictionnaire):
        liste_mots = self.demande_cible.normaliser()
        for mot in liste_mots:
            self.emotion_intensite = dico.getEmotionIntensite(mot)
            if self.emotion_intensite != None:
                return None
    
    def CHERCHER(self, mov: MOUVEMENT, armoire: Armoire):
        armoire.deplacer_curseur(mov)
        self.curseur_courant = armoire.curseur
    
    def PRENDRE(self, nom_obj: str, armoire: Armoire):
        self.inventaire.append(nom_obj)
        for lignes in Armoire.casiers:
            if nom_obj in lignes:
                ligne.remove(nom_obj)
    
    def DONNER(self, nom_obj: str):
        self.inventaire.remove(nom_obj)
        demande = scenario.nextDemande()
        self.resident_cible = demande["resident"]
        self.demande_cible = demande["message"]
    
    def ATTENDRE(self):
        pass
    
    def PERCEVOIR(self, carte: CarteMonde, armoire: Armoire):
        # On demande à la carte de récupérer les positions adjacentes pour les placer dans le dico perception
        self.perception["N"] = carte.getCase(self.position, MOUVEMENT.N)
        self.perception["S"] = carte.getCase(self.position, MOUVEMENT.S)
        self.perception["E"] = carte.getCase(self.position, MOUVEMENT.E)
        self.perception["O"] = carte.getCase(self.position, MOUVEMENT.O)
        
        # Si une des cases est l'armoire, on enregistre le contenu_casier sur lequel le curseur d'armoire est placé
        if "A" in self.perception.values():
            ligne_casier_courant = armoire.curseur[0]
            colonne_casier_courant = armoire.curseur[1]
            
            self.contenu_casier = armoire.casiers[ligne_casier_courant][colonne_casier_courant]
            self.curseur_courant = (ligne_casier_courant,colonne_casier_courant)
            
    
    def MEMORISER(self):
        self.carte_mentale.saveCases(self.position, self.perception)
        self.armoire_mentale[self.curseur_courant[0]][self.curseur_courant[1]] = self.contenu_casier
    
    def distance(self, e : int, e2 : int):
        d1 = (e-e2)%8
        d2 = (e2-e)%8
        return(min(d1,d2))
    
    def sens(self, emotion_donnee: int, emotion_ref : int):
        
        # distance = arrivée - départ
        # on est dans une roue de taille 8 : un déplacement bien fait n'est jamais supérieur à 4 de distance
        # autrement dit : on calcule la distance (modulo 8). Si elle est inférieure ou égale à 4, le sens est bien horaire, sinon il vaut mieux changer de sens
        
        # ici on a de toute façon une distance de 2 max entre la ref et l'arrivée 
        # donc en réalité, on va trouver soit d = 0, 1, 2 ou d = 6, 7
        # PS: on va renvoyer 0 pour sens horaire, 1 sinon. Comme le sorted est croissant (en tous cas ici), 0 passera avant 1
        
        distance = (emotion_donnee - emotion_ref) % 8
        if distance <= 4:
            return 0
        else:
            return 1
        
    def generer_liste_casiers(self):
        e = self.emotion_intensite[0]
        i = self.emotion_intensite[1]
        
        # liste des cases non triées et sans tenir compte d'armoire mentale
        liste = [
            (0,(e-2)%8), (0,(e-1)%8), (0,e) ,(0,(e+1)%8), (0,(e+2)%8),
            (1,(e-2)%8), (1,(e-1)%8), (1,e) ,(1,(e+1)%8), (1,(e+2)%8),
            (2,(e-2)%8), (2,(e-1)%8), (2,e) ,(2,(e+1)%8), (2,(e+2)%8),
        ]
        
        # création d'une nouvelle liste qui supprime les éléments dont on sait que les cases sont vides dans l'armoire mentale
        liste2 = deepcopy(liste)
        for pos in liste:
            if self.armoire_mentale[pos[0]][pos[1]] == None:
                liste2.remove(pos)
        
        # tri de liste 2
        self.liste_casier_recherche = sorted(liste2, key = lambda position: (distance(e, position[1]), abs(i - position[0]), position[0], sens(position[1],e)))
        
    def deplacer_vers(self, arrivee: tuple[int,int]):
        chemin = [] # vaut en réalité la liste d'actions CHERCHER avec leur orientation pour atteindre l'arrivée
        depart = self.curseur_courant
        mov_verticaux = arrivee[0] - depart [0]        
        match mov_verticaux:
            case 1:
                chemin.append[ACTIONS.CHERCHER(S)]
            case 2:
                chemin.append[ACTIONS.CHERCHER(S)]
                chemin.append[ACTIONS.CHERCHER(S)]
            case -1:
                chemin.append[ACTIONS.CHERCHER(N)]
            case -2:
                chemin.append[ACTIONS.CHERCHER(N)]
                chemin.append[ACTIONS.CHERCHER(N)]
        a = (arrivee[1] - depart[1]) % 8
        mov_horizontaux = min(a, 8-a) #d'après l'énoncé
        
        if a == mov_horizontaux:
            for i in range(a):
                chemin.append[ACTIONS.CHERCHER(E)]
        else:
            for i in range(mov_horizontaux):
                chemin.append[ACTIONS.CHERCHER(O)]
        self.chemin_armoire_courant = chemin
                
    
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
                            if self.chemin_courant[1][0] < self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.N))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.S))
                            if self.chemin_courant[1][1] < self.position[1]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.O))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.E)) 
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
                            if self.chemin_courant[1][0] < self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.N))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.S))
                            if self.chemin_courant[1][1] < self.position[1]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.O))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.E)) 
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
                            if self.chemin_courant[1][0] < self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.N))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.S))
                            if self.chemin_courant[1][1] < self.position[1]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.O))
                            if self.chemin_courant[1][0] > self.position[0]:
                                self.actions.append(ACTIONS.AVANCER(MOUVEMENT.E))    
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_RESIDENT
                    else:
                        self.actions.append(ACTIONS.DONNER(self.inventaire))
                
                # ---- FINDING_OBJECT ---- #
                case ETATS.FINDING_OBJECT:
                    if not self.liste_casier_recherche:
                        generer_liste_casiers()
                                                
                    #la liste est créée
                    #si je ne suis pas à destination
                    casier_cible = self.liste_casier_recherche[0]
                    if self.curseur_courant != casier_cible:
                        #si je n'ai pas encore de chemin, j'en crée un
                        if self.chemin_armoire_courant == None:
                            #génère la liste des actions CHERCHER à effectuer jusqu'à la cible
                            deplacer_vers(casier_cible)
                        #j'ajoute la prochaine action à faire au robot
                        actions.append(self.chemin_armoire_courant.pop(0))
                        
                    #ici je suis donc à destination
                    else:
                        contenu_casier_courant = self.armoire_mentale[curseur_courant[0]][curseur_courant[1]]
                        if contenu_casier_courant != None and contenu_casier_courant != "inconnu":
                            self.actions.append(ACTIONS.PRENDRE(contenu_casier_courant))
                            self.etat = ETATS.MOVING_RESIDENT
                        else:
                            pass
                            self.liste_casier_recherche.pop(0)
                            if self.liste_casier_recherche == []:
                                self.etat = ETATS.ERREUR_ARMOIRE_VIDE
                    
                # ---- ERREURS ---- #
                case ETATS.ERREUR_CHEMIN_DICO:
                    pass
                case ETATS.ERREUR_CHEMIN_ARMOIRE:
                    pass
                case ETATS.ERREUR_CHEMIN_RESIDENT:
                    pass
                case ETATS.ERREUR_ARMOIRE_VIDE:
                    pass
    
    def ACTION(self):
        pass