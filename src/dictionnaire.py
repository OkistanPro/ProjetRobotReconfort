class Dictionnaire:
    def __init__(self, position_carte : tuple[int, int], dico : dict):
        self.position: tuple[int, int] = position_carte
        self.contenu : dict[str, tuple[int, int]] = {}
        # On suppose que le dico est de la même forme que dictionnaire.json
        for entree in dico["entrees"]:
            emotion : int = dico["emotions"].index(entree["emotion"])
            intensite : int = dico["intensites"].index(entree["intensite"])

            for forme in entree["formes"]:
                self.contenu[forme] = (emotion, intensite)
    

    def getEmotionIntensite(self, key : str) -> tuple[int, int]:
        if key not in self.contenu : return None
        return self.contenu[key]