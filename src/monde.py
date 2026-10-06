from typing import Any
import sys
from src.scenario import Scenario
from src.resident import Resident
from src.dictionnaire import Dictionnaire
from src.armoire import Armoire
from src.carte_monde import CarteMonde
import reconfort_io as rio

class Monde:
    carte : CarteMonde
    armoire : Armoire
    dico : Dictionnaire
    residents : list[Resident] = []
    scenario : Scenario

    emotions : list[str]
    intensites : list[str]

    def __init__(self, path_carte : str, path_dico : str, path_armoire : str, path_scenario : str, nb_robots : int = 1):
        carte_dict: dict[str, Any]
        scenario_dict: dict[str, Any]
        dictionnaire_dict: dict[str, Any] 
        armoire_dict: dict[str, Any]

        try:
            carte_dict = rio.charger_carte(path_carte)
            scenario_dict = rio.charger_scenario(path_scenario)
            dictionnaire_dict = rio.charger_dictionnaire(path_dico)
            armoire_dict = rio.charger_armoire(path_armoire)
        except rio.ErreurFichier as err:
            print(f"erreur de chargement : {err}", file=sys.stderr)
            return 1
        
        # A partir des dicts, créer les objets
        self.carte = CarteMonde(carte_dict["dimensions"], carte_dict["grille"])
        self.armoire = Armoire(carte_dict["armoire"]["position"], armoire_dict["casier_depart"], armoire_dict["casiers"])
        self.dico = Dictionnaire(carte_dict["dictionnaire"]["position"], dictionnaire_dict)

        # Pour chaque résident
        for resident in carte_dict["residents"]:
            self.residents.append(Resident(resident["id"], resident["nom"], resident["position"]))
        
        self.scenario = Scenario(scenario_dict)

        self.emotions = armoire_dict["emotions"]
        self.intensites = armoire_dict["intensites"]