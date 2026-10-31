from abc import ABC, abstractmethod
from colorama import Fore, Style
class Carte(ABC):
    def __init__(self, dimensions, grille):
        self.dimensions = dimensions
        self.grille = grille

    @abstractmethod
    def afficher_carte():
        pass