class Dictionnaire:
    position_carte : tuple[int, int]
    contenu : dict[str, tuple[int, int]]

    def Dictionnaire(self, position_carte : tuple[int, int], dico : dict):
        self.position_carte = position_carte
        # On suppose que le dico est de la même forme que dictionnaire.json
        for entree in dico["entrees"]:
            emotion : int = dico["emotions"].find(entree["emotion"])
            intensite : int = dico["intensites"].find(entree["intensite"])

            for forme in entree["formes"]:
                self.contenu[forme] = (emotion, intensite)
    
    def Dictionnaire(self, position_carte : tuple[int, int], dico : dict[str, tuple[int, int]]):
        self.position_carte = position_carte
        self.contenu = dico

    def getEmotionIntensite(self, key : str) -> tuple[int, int]: 
        return self.contenu[key]