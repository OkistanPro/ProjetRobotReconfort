from abc import ABC, abstractmethod
from colorama import Fore, Style
class Carte(ABC):
    dimensions : tuple[int,int]
    grille : list[str]

    @abstractmethod
    def afficher_carte():
        pass