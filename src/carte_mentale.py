from colorama import Style
from colorama import Fore
from e_mouvement import MOUVEMENT
from carte import Carte
from collections import deque

class CarteMentale(Carte):
    def __init__(
        self, 
        dimensions : tuple[int, int], 
        positions_robots : list[list[int, int]], 
        positions_residents : list[tuple[int, int]], 
        position_armoire : tuple[int, int],
        position_dictionnaire : tuple[int, int]
    ):
        self.dimensions = dimensions
        self.grille = ["."*self.dimensions[1]]*self.dimensions[0]

        # Placement des positions
        for pos_robot in positions_robots:
            ligne = list(self.grille[pos_robot[0]])
            ligne[pos_robot[1]] = "R"
            self.grille[pos_robot[0]] = "".join(ligne)

        for pos_resident in positions_residents:
            ligne = list(self.grille[pos_resident[0]])
            ligne[pos_resident[1]] = "P"
            self.grille[pos_resident[0]] = "".join(ligne)

        ligne_armoire = list(self.grille[position_armoire[0]])
        ligne_armoire[position_armoire[1]] = "A"
        self.grille[position_armoire[0]] = "".join(ligne_armoire)

        ligne_dico = list(self.grille[position_dictionnaire[0]])
        ligne_dico[position_dictionnaire[1]] = "D"
        self.grille[position_dictionnaire[0]] = "".join(ligne_dico)
    
    def saveCases(self, position_robot : tuple[int, int], cases : dict[str, str]):
        # De la forme {"N": case, "O" : case, "E" : case, "S" : case}
        for direction in cases:
            match direction:
                case "N":
                    if position_robot[0] > 0:
                        ligne: list[str] = list(self.grille[position_robot[0] - 1])
                        ligne[position_robot[1]] = cases[direction]
                        self.grille[position_robot[0] - 1] = "".join(ligne)
                case "S":
                    if position_robot[0] < self.dimensions[0] - 1:
                        ligne: list[str] = list(self.grille[position_robot[0] + 1])
                        ligne[position_robot[1]] = cases[direction]
                        self.grille[position_robot[0] + 1] = "".join(ligne)
                case "O":
                    if position_robot[1] > 0:
                        ligne: list[str] = list(self.grille[position_robot[0]])
                        ligne[position_robot[1] - 1] = cases[direction]
                        self.grille[position_robot[0]] = "".join(ligne)
                case "E":
                    if position_robot[1] < self.dimensions[1] - 1:
                        ligne: list[str] = list(self.grille[position_robot[0]])
                        ligne[position_robot[1] + 1] = cases[direction]
                        self.grille[position_robot[0]] = "".join(ligne)
                    
    
    def reconstruire(self, predecesseur : dict[tuple[int, int], tuple[int, int]], case : tuple[int, int]):
        chemin: list[tuple[int, int]] = [case]
        while predecesseur[chemin[-1]] != None:
            chemin.append(predecesseur[chemin[-1]])
        chemin.reverse()
        return chemin
    
    def calcul_chemin(self, depart : tuple[int, int], arrivees : list[tuple[int, int]]):
        if depart in arrivees:
            return [depart]
        
        predecesseur : dict[tuple[int, int], tuple[int, int]] = {}
        predecesseur[depart] = None
        file: deque[tuple[int, int]] = deque([depart])

        while len(file) > 0:
            courant: tuple[int, int] = file.popleft()
            voisins = []
            if courant[0] > 0 : voisins.append((courant[0] - 1, courant[1]))
            if courant[0] < self.dimensions[0] - 1 : voisins.append((courant[0] + 1, courant[1]))
            if courant[1] > 0 : voisins.append((courant[0], courant[1] - 1))
            if courant[1] < self.dimensions[1] - 1 : voisins.append((courant[0], courant[1] + 1))

            for voisin in voisins:
                if voisin in predecesseur : continue
                if self.grille[voisin[0]][voisin[1]] != ".": continue
                predecesseur[voisin] = courant
                if voisin in arrivees:
                    return self.reconstruire(predecesseur, voisin)
                file.append(voisin)
        
        return None
    
    def afficher_carte(self, chemin=None):
        for ligne in range(len(self.grille)):
            for colonne in range(len(self.grille[ligne])):
                if chemin and (ligne, colonne) in chemin:
                    match self.grille[ligne][colonne]:
                        case "#":
                            print(Fore.CYAN + "█" + Style.RESET_ALL, end="")
                        case ".":
                            print(Fore.CYAN + "░" + Style.RESET_ALL, end="")
                        case _:
                            print(Fore.CYAN + self.grille[ligne][colonne] + Style.RESET_ALL, end="")
                    
                else:
                    match self.grille[ligne][colonne]:
                        case "#":
                            print("█", end="")
                        case ".":
                            print("░", end="")
                        case _:
                            print(self.grille[ligne][colonne], end="")
            print("")