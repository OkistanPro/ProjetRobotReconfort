from carte import Carte, Fore, Style
from e_mouvement import MOUVEMENT

class CarteMonde (Carte):
    def __init__(self, dimensions, grille):
        self.dimensions = dimensions
        self.grille = grille
    
    def getCase(self, pos : tuple[int, int], adj : MOUVEMENT) -> str:
        match adj:
            case MOUVEMENT.N:
                if pos[0] > 0:
                    return (pos[0] - 1, pos[1])
            case MOUVEMENT.S:
                if pos[0] < self.dimensions[0] - 1:
                    return (pos[0] + 1, pos[1])
            case MOUVEMENT.E:
                if pos[1] < self.dimensions[1] - 1:
                    return (pos[0], pos[1] + 1)
            case MOUVEMENT.O:
                if pos[1] > 0:
                    return (pos[0], pos[1] - 1)

    def afficher_carte(self):
        for rangee in self.grille:
            print(Fore.MAGENTA + rangee)
        print(Style.RESET_ALL)