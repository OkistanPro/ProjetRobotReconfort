class Resident:
    id : str
    nom : str
    position : tuple[int, int]

    def __init__(self, id, nom, position):
        self.id = id
        self.nom = nom
        self.position = position