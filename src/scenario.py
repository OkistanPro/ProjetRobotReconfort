class Scenario:
    ind_demande : int
    demandes : list[dict[str, str]]

    def Scenario(self, dico : dict[str, str]):
        self.ind_demande = -1
        # On suppose que le dico est de la même forme que scenario.json
        for demande in dico["demandes"]:
            new_dico: dict[str, str] = {}

            new_dico["resident"] = demande["resident"]
            new_dico["message"] = demande["message"]

            self.demandes.append(new_dico)


    def Scenario(self, dico : list[dict[str, str]]):
        self.ind_demande = -1
        self.demandes = dico
    
    def nextDemande(self):
        self.ind_demande += 1
        return self.demandes[self.ind_demande]