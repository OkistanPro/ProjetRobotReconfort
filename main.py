"""
Demonstration de la base fournie -- projet "Robot de reconfort".

Ce script ne resout rien. Il montre seulement :
  - le contrat d'appel attendu (quatre arguments) ;
  - comment charger les quatre fichiers d'entree ;
  - comment gerer proprement un fichier absent ou mal forme ;
  - comment produire un fichier de trace conforme.

Le robot de cette demo n'avance pas, ne consulte rien, et echoue sur
toutes les demandes. C'est a vous d'ecrire celui qui reussit.

    python3 demo.py cartes/appartement_01.json cartes/scenario_01.json \
        donnees sorties/trace_01.json
"""

from src.e_etats import ETATS
from time import sleep
from typing import Any
from src.armoire import Armoire
import sys
from pathlib import Path
import reconfort_io as rio

from src.monde import Monde
from src.e_mouvement import MOUVEMENT

import os, platform
def clear():
   if platform.system() == 'Windows':
      os.system('cls')
   else:
      os.system('clear')

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(__doc__.strip())
        exit(2)
    
    chemin_carte, chemin_scenario = Path(sys.argv[1]), Path(sys.argv[2])
    dossier_donnees, chemin_sortie = Path(sys.argv[3]), Path(sys.argv[4])

    delai = float(sys.argv[5])

    scenario = rio.charger_scenario(chemin_scenario)

    chemin_dictionnaire: Path = dossier_donnees / "dictionnaire.json"
    chemin_armoire = dossier_donnees / f"{scenario['armoire']}.json"

    monde = Monde(
        chemin_carte,
        chemin_dictionnaire,
        chemin_armoire,
        chemin_scenario,
        1
    )

    trace = rio.Trace(
        nom_carte=monde.nom_carte,
        nom_scenario=monde.nom_scenario,
        equipe=["Jonathan Merlet", "Emmanuel Sanchez"],
    )

    # Envoyer le premier scénario
    for robot in monde.agents:
        robot.trace = trace
        if robot.etat == ETATS.IDLE:
            robot.demande_courante = monde.scenario.nextDemande()
            robot.id_demande = monde.scenario.ind_demande

    while monde.agents[0].demande_courante != None:
        for robot in monde.agents:
            robot.PERCEVOIR(monde.carte, monde.armoire)
        for robot in monde.agents:
            robot.MEMORISER()
        for robot in monde.agents:
            robot.DECISION()
            if robot.etat == ETATS.ARRET:
                # On s'arrête
                print("!!! Erreur bloquant : Robot en arrêt !!!")
                trace.ecrire(Path(sys.argv[4]))
                exit(1)
        for robot in monde.agents:
            ancienne_position = robot.position
            robot.ACTION(monde.dico, monde.armoire)
            if robot.position != ancienne_position:
                if ancienne_position[0] != robot.position[0]:
                    ligne1: list[str] = list(monde.carte.grille[ancienne_position[0]])
                    ligne2: list[str] = list(monde.carte.grille[robot.position[0]])
                    ligne1[ancienne_position[1]] = "."
                    ligne2[robot.position[1]] = "R"
                    monde.carte.grille[ancienne_position[0]] = "".join(ligne1)
                    monde.carte.grille[robot.position[0]] = "".join(ligne2)
                else:
                    ligne: list[str] = list(monde.carte.grille[ancienne_position[0]])
                    ligne[ancienne_position[1]] = "."
                    ligne[robot.position[1]] = "R"
                    monde.carte.grille[ancienne_position[0]] = "".join(ligne)
        clear()
        print("-- Carte du monde --")
        print(monde)
        for robot in monde.agents:
            print("-- Carte mentale --")
            robot.carte_mentale.afficher_carte(robot.chemin_courant)
            print("-- Armoire mentale --")
            print(robot.armoire_mentale[0])
            print(robot.armoire_mentale[1])
            print(robot.armoire_mentale[2])
            print("-- Demande courante :", monde.scenario.demandes[monde.scenario.ind_demande]["resident"].nom, ":", monde.scenario.demandes[monde.scenario.ind_demande]["message"])
            print("-- Objet à la main :", robot.inventaire)
            print("-- ETAT :", robot.etat.name)
            print("-- CURSEUR ARMOIRE:", monde.armoire.curseur)
        sleep(delai)
        for robot in monde.agents:
            if robot.etat == ETATS.IDLE:
                robot.demande_courante = monde.scenario.nextDemande()
                robot.id_demande = monde.scenario.ind_demande
        
    trace.ecrire(Path(sys.argv[4]))
    print("FIN")