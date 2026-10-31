from typing import Any
from src.e_mouvement import MOUVEMENT

class Armoire:
    def __init__(self, position_carte: tuple[int, int], curseur_depart: list[int, int], casiers: list[dict[str, Any]]):
        self.position: tuple[int, int] = position_carte
        self.curseur: list[int] = curseur_depart
        self.en_utilisation = False
        # On suppose casiers même forme que dans armoire_standard.json
        self.casiers: list[list[str]] = [[None]*8, [None]*8, [None]*8]
        for objet in casiers:
            self.casiers[objet["ligne"]][objet["colonne"]] = objet["objet"]
        
    def deplacer_curseur(self, mov: MOUVEMENT):
        if self.en_utilisation:
            match mov:
                case MOUVEMENT.N:
                    self.curseur[1] = max(0, self.curseur[1] - 1)
                case MOUVEMENT.S:
                    self.curseur[1] = min(2, self.curseur[1] + 1)
                case MOUVEMENT.O:
                    self.curseur[0] = (self.curseur[0] - 1) % 8
                case MOUVEMENT.E:
                    self.curseur[0] = (self.curseur[0] + 1) % 8

    def __repr__(self) -> str:
        return str(self.casiers)