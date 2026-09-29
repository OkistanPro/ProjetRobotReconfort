class Resident:
    id : str
    nom : str
    position : tuple[int, int]

    def Resident(self, id, nom, position):
        self.id = id
        self.nom = nom
        self.position = position