class Resident:
    def __init__(self, id, nom, position):
        self.id : str = id
        self.nom : str = nom
        self.position : tuple[int, int] = position