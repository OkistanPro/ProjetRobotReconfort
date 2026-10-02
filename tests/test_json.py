from io import TextIOWrapper
from random import randint
from copy import deepcopy
import json
import pytest
import subprocess
from tempfile import TemporaryFile
import os


class TestJSONChargerCarte:
    
    def saveData(self, data):
        # On l'enregistre
        with open("tests/tmpappart.json", "w", encoding="utf-8") as file_write:
            json.dump(data, file_write)
    
    def launchAndReturnCode(self):
        process = subprocess.run(["python", "./demo.py", "tests/tmpappart.json", "cartes/scenario_01.json", "donnees", "sortie.json"])
        os.remove("tests/tmpappart.json")
        return process.returncode
        

    def test_ok(self):
        # Charger JSON
        with open("cartes/appartement_test.json", "r") as file:
            data = json.load(file)
            # On enregistre un bon fichier
            self.saveData(data)
            # Code bon
            assert self.launchAndReturnCode() == 0

    def test_existence(self, subtests : pytest.Subtests):
        # Charger JSON
        with open("cartes/appartement_test.json", "r") as file:
            data = json.load(file)
            # Copie du JSON
            data_copy = deepcopy(data)

            # Pour chaque propriété
            for prop in data_copy.keys() :
                with subtests.test("Existence " + prop, prop=prop):
                    # On l'enlève de la copie
                    del data[prop]

                    self.saveData(data)
                    # Erreur
                    assert self.launchAndReturnCode() == 1

                    # On remet data
                    data = deepcopy(data_copy)
    
    def test_type(self, subtests : pytest.Subtests):
        # Charger JSON
        with open("cartes/appartement_test.json", "r") as file:
            data = json.load(file)
            # Copie du JSON
            data_copy = deepcopy(data)

            # On change les propriétés par des int
            prop_to_test = ["nom", "dimensions", "legende"]
            for prop in prop_to_test:
                with subtests.test("Type " + prop, prop=prop):
                    # On change le type
                    data[prop] = 45

                    # On l'enregistre
                    self.saveData(data)
                    # Erreur
                    assert self.launchAndReturnCode() == 1

                    # On remet data
                    data = deepcopy(data_copy)
    
    def test_coherence(self, subtests : pytest.Subtests):
        # Charger JSON
        with open("cartes/appartement_test.json", "r") as file:
            data = json.load(file)
            # Copie du JSON
            data_copy = deepcopy(data)

            # Vérification nom vide
            with subtests.test("Nom vide"):
                # On définit un nom vide
                data["nom"] = ""

                # On l'enregistre
                self.saveData(data)
                
                # Erreur
                assert self.launchAndReturnCode() == 1

                # On remet data
                data = deepcopy(data_copy)
            
            with subtests.test("Cohérence dimensions"):
                del data["dimensions"]["largeur"]
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                del data["dimensions"]["hauteur"]
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                data["dimensions"]["largeur"] = 1
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                data["dimensions"]["hauteur"] = 1
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)
            
            with subtests.test("Légende"):
                # Prendre un random
                key_to_remove = randint(0, len(data["legende"]) - 1)
                # L'enlever
                del data["legende"][list(data["legende"].keys())[key_to_remove]]

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)
                
            with subtests.test("Cohérence grille/dimensions"):
                # Modification largeur
                data["dimensions"]["largeur"] -= 2

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Modification hauteur
                data["dimensions"]["hauteur"] -= 2

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Données grilles"):
                x = randint(0, data["dimensions"]["largeur"] - 1)
                y = randint(0, data["dimensions"]["hauteur"] - 1)
                # Ajouter un R aléatoire
                while data["grille"][y][x] != 'R':
                    data["grille"][y] = data["grille"][y].replace(data["grille"][y][x], 'R', 1)

                    x = randint(0, data["dimensions"]["largeur"] - 1)
                    y = randint(0, data["dimensions"]["hauteur"] - 1)

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)
            
                # Ajouter un A aléatoire
                while data["grille"][y][x] != 'A':
                    data["grille"][y] = data["grille"][y].replace(data["grille"][y][x], 'A', 1)

                    x = randint(0, data["dimensions"]["largeur"] - 1)
                    y = randint(0, data["dimensions"]["hauteur"] - 1)

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Ajouter un D aléatoire
                while data["grille"][y][x] != 'D':
                    data["grille"][y] = data["grille"][y].replace(data["grille"][y][x], 'D', 1)

                    x = randint(0, data["dimensions"]["largeur"] - 1)
                    y = randint(0, data["dimensions"]["hauteur"] - 1)

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Ajouter caractère invalide
                x: int = randint(0, data["dimensions"]["largeur"] - 1)
                y = randint(0, data["dimensions"]["hauteur"] - 1)
                data["grille"][y] = data["grille"][y].replace(data["grille"][y][x], 'K', 1)

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Position départ robot"):
                # Test y
                data["depart_robot"][0] = data["dimensions"]["hauteur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Test x
                data["depart_robot"][1] = data["dimensions"]["largeur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Posiion armoire"):
                # Aucune position
                del data["armoire"]["position"]

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Test y
                data["armoire"]["position"][0] = data["dimensions"]["hauteur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Test x
                data["armoire"]["position"][1] = data["dimensions"]["largeur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Position dictionnaire"):
                # Aucune position
                del data["dictionnaire"]["position"]

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Test y
                data["dictionnaire"]["position"][0] = data["dimensions"]["hauteur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Test x
                data["dictionnaire"]["position"][1] = data["dimensions"]["largeur"] + 5

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Position grille"):
                # Décalage position robot
                data["depart_robot"][0] += 1

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Décalage position armoire
                data["armoire"]["position"][0] += 1

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Décalage position armoire
                data["dictionnaire"]["position"][0] += 1

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)
                
            with subtests.test("Nombre résidents"):
                # Créer un résident
                new_resident = {
                    "id": "R8",
                    "nom": "Gertrude",
                    "position": [
                        1,
                        1
                    ]
                }
                data["residents"].append(new_resident)
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

            with subtests.test("Résidents"):
                # Pas d'identifiant
                del data["residents"][0]["id"]

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Pas de nom
                del data["residents"][0]["nom"]
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Pas de position
                del data["residents"][0]["position"]
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Position invalide x
                data["residents"][0]["position"][0] = data["dimensions"]["hauteur"]
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)
            
                # Position invalide y
                data["residents"][0]["position"][1] = data["dimensions"]["largeur"]
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Changement position
                data["residents"][0]["position"][0] += 1
                data["residents"][0]["position"][1] -= 1
                
                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)

                # Unicité identifiant
                data["residents"][1]["id"] = data["residents"][0]["id"]

                self.saveData(data)
                assert self.launchAndReturnCode() == 1
                data = deepcopy(data_copy)


class TestJSONChargerDict:
    original_dict : dict
    
    def save_original_dict(self):
        file = open("donnees/dictionnaire.json", "r", encoding="utf-8")
        self.original_dict = json.load(file)
    
    def restore_original_dict(self):
        with open("donnees/dictionnaire.json", "w", encoding="utf-8") as file_write:
            json.dump(self.original_dict, file_write, indent=2)
        
    def save_data(self, data):
        with open("donnees/dictionnaire.json", "w", encoding="utf-8") as file_write:
            json.dump(data, file_write)
        
    def launchAndReturnCode(self):
        process = subprocess.run(["python", "./demo.py", "cartes/appartement_test.json", "cartes/scenario_01.json", "donnees", "sortie.json"])
        return process.returncode
    
    def errortest(self, data):
        self.save_data(data)
        # Erreur
        assert self.launchAndReturnCode() == 1
        # Remettre le fichier original
        self.restore_original_dict()
        # Données recopiées
        data = deepcopy(self.original_dict)

    def test_ok(self):
        assert self.launchAndReturnCode() == 0
    
    def test_existence(self, subtests : pytest.Subtests):
        # Capture du dictionnaire original
        self.save_original_dict()

        # Données à travailler
        data: dict = deepcopy(self.original_dict)

        # Pour chaque propriété
        for prop in self.original_dict.keys():
            with subtests.test("Existence " + prop, prop=prop):
                # Supprimer la propriété
                del data[prop]
                # Sauvegarder sur le fichier dictionnaire
                self.save_data(data)
                # Erreur
                assert self.launchAndReturnCode() == 1
                # Remettre le fichier original
                self.restore_original_dict()
                # Données recopiées
                data = deepcopy(self.original_dict)
    
    def test_type(self, subtests : pytest.Subtests):
        # Capture du dictionnaire original
        self.save_original_dict()

        # Données à travailler
        data: dict = deepcopy(self.original_dict)

        prop_to_test = ["emotions", "intensites", "entrees"]

        # On remplace par des entiers
        for prop in prop_to_test:
            with subtests.test("Remplacement propriété", prop=prop):
                data[prop] = 45
                # Sauvegarder sur le fichier dictionnaire
                self.save_data(data)
                # Erreur
                assert self.launchAndReturnCode() == 1
                # Remettre le fichier original
                self.restore_original_dict()
                # Données recopiées
                data = deepcopy(self.original_dict)
        
        # Vérifier type propriétés
        with subtests.test("Remplacement entrée - formes"):
            # Prendre une entrée au hasard
            i = randint(0, len(data["entrees"]) - 1)
            # Modifier valeur
            data["entrees"][i]["formes"] = 45

            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)

        with subtests.test("Remplacement entrée - emotion"):
            i = randint(0, len(data["entrees"]) - 1)
            data["entrees"][i]["emotion"] = 45

            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)
        
        with subtests.test("Remplacement entrée - intensite"):
            i = randint(0, len(data["entrees"]) - 1)
            data["entrees"][i]["intensite"] = 45
            
            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)
    
    @pytest.mark.parametrize(["i1", "i2"], [(0, 1) for i in range(10)])
    def test_coherence(self, subtests : pytest.Subtests, i1, i2):
        # Capture du dictionnaire original
        self.save_original_dict()

        # Données à travailler
        data: dict = deepcopy(self.original_dict)
        
        # Test invalidités
        with subtests.test("Test émotion invalide"):
            i1 = randint(0, len(data["entrees"]) - 1)
            data["entrees"][i1]["emotion"] = "bigleur"

            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)
        
        with subtests.test("Test intensité invalide"):
            i1 = randint(0, len(data["entrees"]) - 1)
            data["entrees"][i1]["intensite"] = "spritante"

            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)
        
        # Test unicité
        with subtests.test("Test unicité"):
            i1 = randint(0, len(data["entrees"]) - 1)
            i2: int = randint(0, len(data["entrees"]) - 1)
            while (i2 == i1):
                i2 = randint(0, len(data["entrees"]) - 1)

            data["entrees"][i1]["formes"] = data["entrees"][i2]["formes"]

            self.save_data(data)
            assert self.launchAndReturnCode() == 1
            self.restore_original_dict()
            data = deepcopy(self.original_dict)
