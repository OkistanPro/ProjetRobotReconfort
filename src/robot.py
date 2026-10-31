from typing import Any
import reconfort_io
from src.dictionnaire import Dictionnaire
from src.armoire import Armoire
from src.carte_monde import CarteMonde
from copy import deepcopy
from src.carte_mentale import CarteMentale
from src.resident import Resident
from src.e_actions import ACTIONS
from src.e_mouvement import MOUVEMENT
from src.e_etats import ETATS

class Robot():
    def __init__(self,
                position : tuple[int,int],
                carte_mentale : CarteMentale,
                demande_courante : dict[str, str],
                trace : reconfort_io.Trace):
        self.position : list[int,int] = list(position)
        self.armoire_mentale : list[list[str | None]] = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]       
        self.carte_mentale : CarteMentale = carte_mentale
        self.etat : ETATS = ETATS.IDLE
        self.id_demande : int = -1
        self.demande_courante : dict[str, Any] | None = demande_courante
        self.inventaire : str | None = None
        self.liste_casier_recherche : list[tuple[int,int]] = []
        self.perception : dict[str,Any] = {}
        self.contenu_casier : str | None = None
        self.actions : list[ACTIONS] = []
        self.curseur_courant : tuple[int,int] | None = None
        self.chemin_courant : list[tuple[int, int]] | None = None
        self.chemin_armoire_courant : list[tuple[int, int]] | None = None
        self.trace = trace
        self.emotions: list[str] = [
            "joie",
            "confiance",
            "peur",
            "surprise",
            "tristesse",
            "degout",
            "colere",
            "anticipation"
        ]
        self.intensites: list[str] = [
            "faible",
            "moyenne",
            "forte"
        ]
        self.repli : str = "aucun"
        self.succes : bool = True
        self.motif_echec : str = ""

    def AVANCER(self, to: tuple[int, int]):
        if self.carte_mentale.grille[to[0]][to[1]] != "#":
            self.old_pos: list[int] = self.position
            self.position = to
    
    def CONSULTER(self, dico : Dictionnaire):
        # Normaliser la phrase
        liste_mots: list[str] = reconfort_io.normaliser(self.demande_courante["message"])
        for mot in liste_mots:
            emotion_intensite: tuple[int, int] = dico.getEmotionIntensite(mot)
            if emotion_intensite != None:
                self.perception["dico"] = emotion_intensite
        if "dico" not in self.perception: 
            self.etat = ETATS.ERREUR_EMOTION_INDETERMINEE
        else:
            self.etat = ETATS.MOVING_ARMOIRE
    
    def CHERCHER(self, to: tuple[int, int], armoire : Armoire):
        if to[1] < self.curseur_courant[1]:
            armoire.deplacer_curseur(MOUVEMENT.N)
        elif to[1] > self.curseur_courant[1]:
            armoire.deplacer_curseur(MOUVEMENT.S)
        else:
            if to[0] < self.curseur_courant[0]:
                armoire.deplacer_curseur(MOUVEMENT.O)
            elif to[0] > self.curseur_courant[0]:
                armoire.deplacer_curseur(MOUVEMENT.E)
        self.curseur_courant = armoire.curseur
    
    def PRENDRE(self, armoire : Armoire):
        if "A" in self.perception.values() and self.contenu_casier != None and self.inventaire == None:
            self.inventaire = self.contenu_casier
            armoire.casiers[self.curseur_courant[1]][self.curseur_courant[0]] = None
            self.etat = ETATS.MOVING_RESIDENT
            self.liste_casier_recherche = []
            self.chemin_armoire_courant = []
    
    def DONNER(self):
        if "P" in self.perception.values() and self.inventaire != None:
            self.inventaire = None
            self.demande_courante = None
            self.etat = ETATS.IDLE
    
    def PERCEVOIR(self, carte : CarteMonde, armoire : Armoire):
        # On demande à la carte de Monde de récupérer les positions adjacentes pour les placer dans le dico perception
        self.perception["N"] = carte.getCase(self.position, MOUVEMENT.N)
        self.perception["S"] = carte.getCase(self.position, MOUVEMENT.S)
        self.perception["E"] = carte.getCase(self.position, MOUVEMENT.E)
        self.perception["O"] = carte.getCase(self.position, MOUVEMENT.O)
        
        # Si une des cases est l'armoire, on enregistre le contenu_casier sur lequel le curseur d'armoire est placé
        if "A" in self.perception.values():
            ligne_casier_courant = armoire.curseur[1]
            colonne_casier_courant = armoire.curseur[0]
            
            self.contenu_casier = armoire.casiers[ligne_casier_courant][colonne_casier_courant]
            self.curseur_courant = (colonne_casier_courant,ligne_casier_courant)
        else:
            self.contenu_casier = None
            self.curseur_courant = None
            
    
    def MEMORISER(self):
        self.carte_mentale.saveCases(self.position, self.perception)
        if self.curseur_courant != None:
            if self.contenu_casier == None:
                self.armoire_mentale[self.curseur_courant[1]][self.curseur_courant[0]] = "VIDE"
            else:
                self.armoire_mentale[self.curseur_courant[1]][self.curseur_courant[0]] = self.contenu_casier
    
    def DECISION(self):
        while not self.actions and self.etat != ETATS.ARRET:
            match self.etat:
                # ---- IDLE ---- #
                case ETATS.IDLE:
                    if self.demande_courante == None:
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
                                        case = (ligne - 1, colonne)
                                        arrivees.append(case)
                                    if ligne < nblignes - 1:
                                        case = (ligne + 1, colonne)
                                        arrivees.append(case)
                                    if colonne > 0:
                                        case = (ligne, colonne - 1)
                                        arrivees.append(case)
                                    if colonne < nbcolonnes - 1:
                                        case = (ligne, colonne + 1)
                                        arrivees.append(case)
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(tuple(self.position), arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.chemin_courant = self.chemin_courant[1:]
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
                                        case = (ligne - 1, colonne)
                                        arrivees.append(case)
                                    if ligne < nblignes - 1:
                                        case = (ligne + 1, colonne)
                                        arrivees.append(case)
                                    if colonne > 0:
                                        case = (ligne, colonne - 1)
                                        arrivees.append(case)
                                    if colonne < nbcolonnes - 1:
                                        case = (ligne, colonne + 1)
                                        arrivees.append(case)
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(tuple(self.position), arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.chemin_courant = self.chemin_courant[1:]
                            self.actions.append(ACTIONS.AVANCER)
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_ARMOIRE
                    else:
                        self.etat = ETATS.FINDING_OBJECT
                
                # ---- MOVING_RESIDENT ---- #
                case ETATS.MOVING_RESIDENT:
                    no_resident: bool = "P" not in self.perception.values()
                    good_resident: bool = False
                    if not no_resident:
                        where_is_resident = list(self.perception.keys())[list(self.perception.values()).index("P")]

                        match where_is_resident:
                            case "N":
                                good_resident = \
                                    [self.position[0] - 1, self.position[1]] == self.demande_courante["resident"].position
                            case "S":
                                good_resident = \
                                    [self.position[0] + 1, self.position[1]] == self.demande_courante["resident"].position
                            case "O":
                                good_resident = \
                                    [self.position[0], self.position[1] - 1] == self.demande_courante["resident"].position
                            case "E":
                                good_resident = \
                                    [self.position[0], self.position[1] + 1] == self.demande_courante["resident"].position
                        
                    if no_resident or not no_resident and not good_resident:
                        #il faut calculer le chemin courant
                        nblignes = self.carte_mentale.dimensions[0]
                        nbcolonnes = self.carte_mentale.dimensions[1]
                        arrivees = []

                        ligne : int = self.demande_courante["resident"].position[0]
                        colonne : int= self.demande_courante["resident"].position[1]

                        if ligne > 0:
                            case = (ligne - 1, colonne)
                            arrivees.append(case)
                        if ligne < nblignes - 1:
                            case = (ligne + 1, colonne)
                            arrivees.append(case)
                        if colonne > 0:
                            case = (ligne, colonne - 1)
                            arrivees.append(case)
                        if colonne < nbcolonnes - 1:
                            case = (ligne, colonne + 1)
                            arrivees.append(case)
                        
                        #je calcule enfin mon chemin courant
                        self.chemin_courant = self.carte_mentale.calcul_chemin(tuple(self.position), arrivees)
                        #si j'ai bien un chemin j'avance, sinon etat erreur (chemin n'existe pas)
                        if self.chemin_courant != None:
                            self.chemin_courant = self.chemin_courant[1:]
                            self.actions.append(ACTIONS.AVANCER)
                        else:
                            self.etat = ETATS.ERREUR_CHEMIN_RESIDENT
                    else:
                        self.actions.append(ACTIONS.DONNER)
                
                # ---- FINDING_OBJECT ---- #
                case ETATS.FINDING_OBJECT:
                    # Si aucune liste de casier à rechercher, la créer
                    if not self.liste_casier_recherche:
                        self.liste_casier_recherche = self.calcul_casier_recherche(self.perception["dico"])
                        self.repli = "aucun"
                    
                    # Si le curseur courant n'a pas atteint le casier à rechercher
                    if self.curseur_courant != self.liste_casier_recherche[0]:
                        # Si aucun chemin est calculé
                        if not self.chemin_armoire_courant:
                            # Regarder dans l'armoire mentale si un objet est présent
                            a_regarder: str | None = self.armoire_mentale[self.liste_casier_recherche[0][1]][self.liste_casier_recherche[0][0]]
                            # Si l'objet regardé est vide, enlever de la liste de casier et regarder la suite
                            while a_regarder == "VIDE" and self.liste_casier_recherche:
                                self.liste_casier_recherche.pop(0)
                                if len(self.liste_casier_recherche) < 15 and len(self.liste_casier_recherche) > 11:
                                    self.repli = "intensite"
                                if len(self.liste_casier_recherche) <= 11 and len(self.liste_casier_recherche) > 5:
                                    self.repli = "voisine_1"
                                if len(self.liste_casier_recherche) <= 5:
                                    self.repli = "voisine_2"
                                if self.liste_casier_recherche:
                                    a_regarder = self.armoire_mentale[self.liste_casier_recherche[0][1]][self.liste_casier_recherche[0][0]]
                            
                            # Si la liste est vide, objet n'est pas là
                            if not self.liste_casier_recherche:
                                self.etat = ETATS.ERREUR_ARMOIRE_VIDE
                                continue
                            # Construire le chemin sur l'armoire
                            self.chemin_armoire_courant = self.deplacer_vers(self.liste_casier_recherche[0])
                        # Action CHERCHER
                        self.actions.append(ACTIONS.CHERCHER)
                    # Si le curseur courant a atteint le casier à rechercher
                    else:
                        # Si est un objet, le prendre
                        if self.contenu_casier != None:
                            self.actions.append(ACTIONS.PRENDRE)
                        # Sinon, enlever de la liste
                        else:
                            self.liste_casier_recherche.pop(0)
                            if len(self.liste_casier_recherche) < 15 and len(self.liste_casier_recherche) > 11:
                                self.repli = "intensite"
                            if len(self.liste_casier_recherche) <= 11 and len(self.liste_casier_recherche) > 5:
                                self.repli = "voisine_1"
                            if len(self.liste_casier_recherche) <= 5:
                                self.repli = "voisine_2"
                            # Si liste vide, objet n'est pas là
                            if not self.liste_casier_recherche:
                                self.etat = ETATS.ERREUR_ARMOIRE_VIDE
                
                case ETATS.ERREUR_ARMOIRE_VIDE:
                    self.trace.ajouter_livraison(
                        self.id_demande,
                        self.demande_courante["resident"].id,
                        self.emotions[self.perception["dico"][0]],
                        self.intensites[self.perception["dico"][1]],
                        None,
                        self.repli,
                        None,
                        False,
                        "armoire vide"
                    )
                    self.etat = ETATS.IDLE
                    self.demande_courante = None

                case ETATS.ERREUR_CHEMIN_ARMOIRE:
                    self.trace.ajouter_livraison(
                        self.id_demande,
                        self.demande_courante["resident"].id,
                        self.emotions[self.perception["dico"][0]],
                        self.intensites[self.perception["dico"][1]],
                        None,
                        self.repli,
                        None,
                        False,
                        "armoire inaccessible"
                    )
                    self.etat = ETATS.ARRET
                case ETATS.ERREUR_CHEMIN_RESIDENT:
                    self.trace.ajouter_livraison(
                        self.id_demande,
                        self.demande_courante["resident"].id,
                        self.emotions[self.perception["dico"][0]],
                        self.intensites[self.perception["dico"][1]],
                        self.casier_choisi,
                        self.repli,
                        None,
                        False,
                        "resident inaccessible"
                    )
                    self.etat = ETATS.ARRET
                case ETATS.ERREUR_CHEMIN_DICO:
                    self.trace.ajouter_livraison(
                        self.id_demande,
                        self.demande_courante["resident"].id,
                        None,
                        None,
                        None,
                        self.repli,
                        None,
                        False,
                        "dictionnaire inaccessible"
                    )
                    self.etat = ETATS.ARRET
                case ETATS.ERREUR_EMOTION_INDETERMINEE:
                    self.trace.ajouter_livraison(
                        self.id_demande,
                        self.demande_courante["resident"].id,
                        None,
                        None,
                        None,
                        self.repli,
                        None,
                        False,
                        "emotion indeterminee"
                    )
                    self.etat = ETATS.IDLE
                    self.demande_courante = None

    
    def ACTION(self, dico : Dictionnaire, armoire : Armoire):
        action_a_faire = self.actions.pop()
        match action_a_faire:
            case ACTIONS.AVANCER:
                old_pos = self.position
                perception_no_dico: dict[str, Any] = deepcopy(self.perception)
                argument = ""
                if self.position[0] != self.chemin_courant[0][0]:
                    if self.position[0] < self.chemin_courant[0][0]:
                        argument = "S"
                    if self.position[0] > self.chemin_courant[0][0]:
                        argument = "N"
                else:
                    if self.position[1] < self.chemin_courant[0][1]:
                        argument = "E"
                    if self.position[1] > self.chemin_courant[0][1]:
                        argument = "O"
                if "dico" in perception_no_dico : del perception_no_dico["dico"]

                if self.chemin_courant: self.AVANCER(self.chemin_courant.pop(0))
                
                self.trace.ajouter_pas(
                    self.id_demande,
                    old_pos,
                    armoire.curseur,
                    "AVANCER",
                    argument,
                    perception_no_dico,
                    self.contenu_casier,
                    ""
                )
            case ACTIONS.CONSULTER:
                perception_no_dico: dict[str, Any] = deepcopy(self.perception)
                if "dico" in perception_no_dico : del perception_no_dico["dico"]
                self.CONSULTER(dico)
                self.trace.ajouter_pas(
                    self.id_demande,
                    self.position,
                    armoire.curseur,
                    "CONSULTER",
                    None,
                    perception_no_dico,
                    self.contenu_casier,
                    ""
                )
            case ACTIONS.CHERCHER:
                armoire.en_utilisation = True
                perception_no_dico: dict[str, Any] = deepcopy(self.perception)
                if "dico" in perception_no_dico : del perception_no_dico["dico"]

                argument = ""
                if self.curseur_courant[0] != self.chemin_armoire_courant[0][0]:
                    if self.curseur_courant[0] < self.chemin_armoire_courant[0][0]:
                        argument = "S"
                    if self.curseur_courant[0] > self.chemin_armoire_courant[0][0]:
                        argument = "N"
                else:
                    if self.curseur_courant[1] < self.chemin_armoire_courant[0][1]:
                        argument = "E"
                    if self.curseur_courant[1] > self.chemin_armoire_courant[0][1]:
                        argument = "O"
                
                self.CHERCHER(self.chemin_armoire_courant.pop(0), armoire)
                self.trace.ajouter_pas(
                    self.id_demande,
                    self.position,
                    armoire.curseur,
                    "CHERCHER",
                    argument,
                    perception_no_dico,
                    self.contenu_casier,
                    ""
                )
            case ACTIONS.PRENDRE:
                perception_no_dico: dict[str, Any] = deepcopy(self.perception)
                if "dico" in perception_no_dico : del perception_no_dico["dico"]
                self.PRENDRE(armoire)
                self.trace.ajouter_pas(
                    self.id_demande,
                    self.position,
                    armoire.curseur,
                    "PRENDRE",
                    None,
                    perception_no_dico,
                    self.contenu_casier,
                    ""
                )
                self.casier_choisi: list[int] = armoire.curseur
            case ACTIONS.DONNER:
                perception_no_dico: dict[str, Any] = deepcopy(self.perception)
                if "dico" in perception_no_dico : del perception_no_dico["dico"]
                self.objet_donné: str | None = self.inventaire
                self.resident_courant = self.demande_courante["resident"]
                self.DONNER()
                self.trace.ajouter_pas(
                    self.id_demande,
                    self.position,
                    armoire.curseur,
                    "DONNER",
                    None,
                    perception_no_dico,
                    self.contenu_casier,
                    ""
                )
                
                self.trace.ajouter_livraison(
                    self.id_demande,
                    self.resident_courant.id,
                    self.emotions[self.perception["dico"][0]],
                    self.intensites[self.perception["dico"][1]],
                    self.casier_choisi,
                    self.repli,
                    self.objet_donné,
                    True
                )
                
    
    def deplacer_vers(self, to: tuple[int, int]):
        chemin: list[tuple[int, int]] = []
        distance: int = abs(to[0] - self.curseur_courant[0])
        courant = list(self.curseur_courant)
        if distance > 4:
            # Un moyen plus simple est envisageable
            d_min = min(to[0], self.curseur_courant[0])
            d_max = max(to[0], self.curseur_courant[0])

            distance = abs((d_min+8) - d_max)
            
            if to[0] < self.curseur_courant[0]:
                for i in range(distance):
                    courant[0] += 1
                    chemin.append(courant.copy())
            else:
                for i in range(distance):
                    courant[0] -= 1
                    chemin.append(courant.copy())
        else:
            if to[0] < self.curseur_courant[0]:
                for i in range(distance):
                    courant[0] -= 1
                    chemin.append(courant.copy())
            else:
                for i in range(distance):
                    courant[0] += 1
                    chemin.append(courant.copy())

        if to[1] < self.curseur_courant[1]:
            for i in range(self.curseur_courant[1] - to[1]):
                courant[1] -= 1
                chemin.append(courant.copy())
        else:
            for i in range(to[1] - self.curseur_courant[1]):
                courant[1] += 1
                chemin.append(courant.copy())
        
        return chemin
    
    def calcul_casier_recherche(self, casier : tuple[int, int]):
        # On considère toutes les cases (e', i') dont la distance sur la roue d(e, e') est inférieure ou égale à 2
        liste_casiers: list[tuple[int, int]] = []
        for i in range(-2, 3):
            liste_casiers.append((casier[0] + i, 0))
            liste_casiers.append((casier[0] + i, 1))
            liste_casiers.append((casier[0] + i, 2))
        
        # Tri
        liste_casiers.sort(key=lambda x: \
            (
                abs(casier[0] - x[0]), # d(e, e') croissante
                abs(casier[1] - x[1]), # écart d'intensité |rang(i) − rang(i')| croissant
                x[1], # l'intensité la plus faible d'abord
                -x[0] # le sens horaire avant le sens antihoraire
            )
        )

        # Application modulo
        liste_casiers = list(map(lambda x: (x[0] % 8, x[1]), liste_casiers))

        return liste_casiers