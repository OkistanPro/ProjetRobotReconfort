from src.carte import Carte, Fore, Style
from src.e_mouvement import MOUVEMENT

class CarteMonde (Carte):
    def __init__(self, dimensions, grille):
        super().__init__(dimensions, grille)
    
    def getCase(self, pos : tuple[int, int], adj : MOUVEMENT) -> str:
        match adj:
            case MOUVEMENT.N:
                if pos[0] > 0:
                    return self.grille[pos[0] - 1][pos[1]]
            case MOUVEMENT.S:
                if pos[0] < self.dimensions[0] - 1:
                    return self.grille[pos[0] + 1][pos[1]]
            case MOUVEMENT.E:
                if pos[1] < self.dimensions[1] - 1:
                    return self.grille[pos[0]][pos[1] + 1]
            case MOUVEMENT.O:
                if pos[1] > 0:
                    return self.grille[pos[0]][pos[1] - 1]
    """
    def afficher_carte(self):
        for rangee in self.grille:
            print(Fore.MAGENTA + rangee)
        print(Style.RESET_ALL)
    """

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
    
    def __repr__(self) -> str:
        to_print: str = ""
        for ligne in range(len(self.grille)):
            for colonne in range(len(self.grille[ligne])):
                match self.grille[ligne][colonne]:
                    case "#":
                        to_print += "█"
                    case ".":
                        to_print += "░"
                    case _:
                        to_print += self.grille[ligne][colonne]
            to_print += "\n"
        return to_print