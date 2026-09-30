from typing import Any
class Scenario:
    ind_demande : int
    demandes : list[dict[str, str]] = []

    def __init__(self, *, dico : dict[str, Any]=None):
        self.ind_demande = -1
        # On suppose que le dico est de la même forme que scenario.json
        for demande in dico["demandes"]:
            new_dico: dict[str, str] = {}

            new_dico["resident"] = demande["resident"]
            new_dico["message"] = demande["message"]

            self.demandes.append(new_dico)

    def nextDemande(self):
        self.ind_demande += 1
        if self.ind_demande >= len(self.demandes): return None
        return self.demandes[self.ind_demande]