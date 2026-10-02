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
        self.grille = [["."]*self.dimensions[1]]*self.dimensions[0]
        # Placement des positions
        for pos_robot in positions_robots:
            self.grille[pos_robot[0]][pos_robot[1]] = "R"
        for pos_resident in positions_residents:
            self.grille[pos_resident[0]][pos_resident[1]] = "P"
        self.grille[position_armoire[0]][position_armoire[1]] = "A"
        self.grille[position_dictionnaire[0]][position_dictionnaire[1]] = "D"
    
    def saveCases(self, position_robot : tuple[int, int], cases : dict[str, str]):
        # De la forme {"N": case, "O" : case, "E" : case, "S" : case}
        for direction in cases:
            match direction:
                case "N":
                    if position_robot[0] > 0:
                        self.grille[position_robot[0] - 1][position_robot[1]] = cases[direction]
                case "S":
                    if position_robot[0] < self.dimensions[0] - 1:
                        self.grille[position_robot[0] + 1][position_robot[1]] = cases[direction]
                case "O":
                    if position_robot[1] > 0:
                        self.grille[position_robot[0]][position_robot[1] - 1] = cases[direction]
                case "E":
                    if position_robot[1] < self.dimensions[1] - 1:
                        self.grille[position_robot[0]][position_robot[1] + 1] = cases[direction]
                    
    
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
                if voisin in predecesseur : next
                if self.grille[voisin[0]][voisin[1]] != ".": next
                predecesseur[voisin] = courant
                if voisin in arrivees:
                    return self.reconstruire(predecesseur, voisin)
                file.append(voisin)
        
        return None
    
    def afficher_carte(self):
        print(self.grille)

test_carte = CarteMentale((9, 13), [[6, 1]], [[6, 11], [3, 3]], (6, 4), (7, 6))
test_carte.grille = [
    "#############",
    "#......#....#",
    "#...........#",
    "#..P...#....#",
    "#.#########.#",
    "#......#....#",
    "#R..A..#...P#",
    "#.....D#....#",
    "#############"
  ]

print(test_carte.calcul_chemin((6, 1), [(3, 4)]))