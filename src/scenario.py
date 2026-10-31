from typing import Any
class Scenario:
    def __init__(self, residents : list[Resident], dico : dict[str, Any]=None):
        self.ind_demande : int = -1
        # On suppose que le dico est de la même forme que scenario.json
        self.demandes : list[dict[str, str]] = []
        for demande in dico["demandes"]:
            new_dico: dict[str, Any] = {}

            for resident in residents:
                if resident.id == demande["resident"] : new_dico["resident"] = resident
            new_dico["message"] = demande["message"]

            self.demandes.append(new_dico)

    def nextDemande(self) -> dict[str, str]:
        self.ind_demande += 1
        if self.ind_demande >= len(self.demandes): return None
        return self.demandes[self.ind_demande]