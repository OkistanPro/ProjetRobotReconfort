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

import sys
from pathlib import Path
import reconfort_io as rio

from src.monde import Monde

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__.strip())
        exit(2)
    
    chemin_carte, chemin_scenario = Path(sys.argv[1]), Path(sys.argv[2])
    dossier_donnees, chemin_sortie = Path(sys.argv[3]), Path(sys.argv[4])

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

    print(monde)