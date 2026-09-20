"""
Base de code fournie -- projet "Robot de reconfort".

Ce module fait DEUX choses, et rien d'autre :

  1. lire les quatre fichiers d'entree (carte, dictionnaire, armoire,
     scenario) ;
  2. construire et exporter le fichier de trace attendu a la sortie.

Tout le reste du projet -- perception, carte mentale, planification de
chemin, consultation du dictionnaire, fouille de l'armoire, boucle de
decision -- est a votre charge. Ne cherchez pas ces fonctions ici : elles
n'y sont pas, et c'est volontaire.

Vous avez le droit de modifier ce fichier. Vous avez surtout le devoir de
le comprendre : les verifications faites ici sont minimales (voir la
section "Ce qui n'est PAS verifie" plus bas), et les validations
manquantes font partie du travail demande.

Python 3.9+. Aucune dependance externe.
"""


from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from sys import stderr


__all__ = [
    "ErreurFichier",
    "charger_carte",
    "charger_dictionnaire",
    "charger_armoire",
    "charger_scenario",
    "normaliser",
    "Trace",
]

VERSION_ATTENDUE = 1


class ErreurFichier(Exception):
    """Fichier d'entree absent, illisible, ou d'un type inattendu."""

# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def _lire_json(chemin: str | Path, format_attendu: str) -> Dict[str, Any]:
    """Lit un fichier JSON UTF-8 et verifie son en-tete.

    Ce qui EST verifie ici :
      - le fichier existe et se lit en UTF-8 ;
      - son contenu est du JSON valide ;
      - la racine est un objet ;
      - les champs "format" et "version" sont presents et corrects.

    Ce qui n'est PAS verifie (a vous de le faire, enonce section 5.6) :
      - la presence et le type de chacun des autres champs ;
      - la coherence des donnees (grille rectangulaire, positions dans les
        bornes, resident pose sur un mur, casier hors de l'armoire,
        emotion inconnue, resident cite par un scenario mais absent de la
        carte...).
    """
    chemin = Path(chemin)
    try:
        texte = chemin.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErreurFichier(f"fichier introuvable : {chemin}") from None
    except UnicodeDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas encode en UTF-8 (octet {err.start})"
        ) from None
    except OSError as err:
        raise ErreurFichier(f"{chemin} illisible : {err}") from None

    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas un JSON valide : {err.msg} "
            f"(ligne {err.lineno}, colonne {err.colno})"
        ) from None

    if not isinstance(donnees, dict):
        raise ErreurFichier(
            f"{chemin} : la racine doit etre un objet JSON, "
            f"pas {type(donnees).__name__}"
        )

    format_trouve = donnees.get("format")
    if format_trouve != format_attendu:
        raise ErreurFichier(
            f"{chemin} : format attendu '{format_attendu}', "
            f"trouve {format_trouve!r}"
        )

    version = donnees.get("version")
    if version != VERSION_ATTENDUE:
        raise ErreurFichier(
            f"{chemin} : version {VERSION_ATTENDUE} attendue, trouve {version!r}"
        )

    return donnees


def charger_carte(chemin: str | Path) -> Dict[str, Any]:
    dict_carte = _lire_json(chemin, "robot-reconfort/carte")

    # ----------------------
    # Vérification existence
    # ----------------------
    
    # Vérifier nom
    if "nom" not in dict_carte:
        print("Erreur chargement carte : L'appartement n'a pas de nom.", file=stderr)
        exit(1)
    
    # Vérifier dimensions
    if "dimensions" not in dict_carte:
        print("Erreur chargement carte : L'appartement doit spécifier les dimensions", file=stderr)
        exit(1)
    
    # Vérifier légende
    if "legende" not in dict_carte:
        print("Erreur chargement carte : Aucune légende définie.", file=stderr)
        exit(1)
    
    # Vérifier existence grille
    if "grille" not in dict_carte :
        print("Erreur chargement carte : Aucune grille disponible.", file=stderr)
        exit(1)
    
    # Vérifier existence position depart robot
    if "depart_robot" not in dict_carte:
        print("Erreur chargement carte : Aucune position de départ robot.", file=stderr)
        exit(1)
    
    # Vérifier existence armoire
    if "armoire" not in dict_carte:
        print("Erreur chargement carte : Aucune armoire définie.", file=stderr)
        exit(1)
    
    # Vérifier existence dictionnaire
    if "dictionnaire" not in dict_carte:
        print("Erreur chargement carte : Aucun dictionnaire défini.", file=stderr)
        exit(1)
    
    # Vérifier existence résidents
    if "residents" not in dict_carte:
        print("Erreur chargement carte : Aucun résident défini.", file=stderr)
        exit(1)
    
    # -----------------------------
    # Vérification type des données
    # -----------------------------

    for key in dict_carte:
        match key:
            case "nom":
                if type(dict_carte[key]) is not str:
                    print(f"Erreur chargement carte : Type propriété {key} - str attendu.", file=stderr)
                    exit(1)
            case "dimensions":
                if type(dict_carte[key]) is not dict:
                    print(f"Erreur chargement carte : Type propriété {key} - Dict[String, int] attendu.", file=stderr)
                    exit(1)
            case "legende":
                if type(dict_carte[key]) is not dict:
                    print(f"Erreur chargement carte : Type propriété {key} - Dict[String, String] attendu.", file=stderr)
                    exit(1)

    # ------------------------------------------
    # Vérification cohérence des données
    # ------------------------------------------

    # Vérifier nom vide
    if dict_carte["nom"] == "":
        print("Erreur chargement carte : Nom invalide", file=stderr)
        exit(1)
    
    # Vérifier cohérence dimensions
    if "largeur" not in dict_carte["dimensions"] or \
    "hauteur" not in dict_carte["dimensions"] or \
    dict_carte["dimensions"]["largeur"] <= 3 or \
    dict_carte["dimensions"]["hauteur"] <= 3 :
        print("Carte : Dimensions invalides.", file=stderr)
        exit(1)
    
    signes = ["#", ".", "R", "A", "D", "P"]
    # Vérifier légende
    for signe in signes:
        if signe not in dict_carte["legende"]:
            print(f"Erreur chargement carte : Légende manquante - \"{signe}\"", file=stderr)
            exit(1)
    
    largeur = dict_carte["dimensions"]["largeur"]
    hauteur = dict_carte["dimensions"]["hauteur"]

    # Vérifier cohérence grille/dimensions
    if len(dict_carte["grille"]) != hauteur or \
    False in [len(x) == largeur for x in dict_carte["grille"]]:
        print("Erreur chargement carte : Dimensions grille invalide.", file=stderr)
        exit(1)

    # Vérifier données grille
    nb_depart_robot = 0
    nb_armoire = 0
    nb_dict = 0
    nb_residents = 0

    for ligne in dict_carte["grille"]:
        for c in ligne:
            match c:
                case "R":
                    nb_depart_robot += 1
                    if nb_depart_robot > 1:
                        print("Erreur chargement carte : Plusieurs départs sur la grille.", file=stderr)
                        exit(1)
                case "A":
                    nb_armoire += 1
                    if nb_armoire > 1:
                        print("Erreur chargement carte : Plusieurs armoires sur la grille.", file=stderr)
                        exit(1)
                case "D":
                    nb_dict += 1
                    if nb_dict > 1:
                        print("Erreur chargement carte : Plusieurs dictionnaires sur la grille.", file=stderr)
                        exit(1)
                case "P":
                    nb_residents += 1
                case "#" | ".":
                    pass
                case _:
                    print("Erreur chargement carte : Grille conient des caractères invalides.", file=stderr)
                    exit(1)
            
    
    # Vérifier position depart robot
    if not (0 <= dict_carte["depart_robot"][0] < hauteur) or \
    not (0 <= dict_carte["depart_robot"][1] < largeur):
        print("Erreur chargement carte : Position départ du robot dépasse la grille", file=stderr)
        exit(1)
    
    # Vérifier position armoire
    if "position" not in dict_carte["armoire"]:
        print("Erreur chargement carte : Pas de position d'armoire.", file=stderr)
        exit(1)
    if not (0 <= dict_carte["armoire"]["position"][0] < hauteur) or \
    not (0 <= dict_carte["armoire"]["position"][1] < largeur):
        print("Erreur chargement carte : Position armoire dépasse la grille", file=stderr)
        exit(1)
    
    # Vérifier position dictionnaire
    if "position" not in dict_carte["dictionnaire"]:
        print("Erreur chargement carte : Pas de position d'armoire.", file=stderr)
        exit(1)
    if not (0 <= dict_carte["dictionnaire"]["position"][0] < hauteur) or \
    not (0 <= dict_carte["dictionnaire"]["position"][1] < largeur):
        print("Erreur chargement carte : Position dictionnaire dépasse la grille", file=stderr)
        exit(1)
    

    # Vérifier chaque position dans la grille
    if dict_carte["grille"][dict_carte["depart_robot"][0]][dict_carte["depart_robot"][1]] != 'R':
        print("Erreur chargement carte : Position départ du robot invalide selon grille", file=stderr)
        exit(1)
    if dict_carte["grille"][dict_carte["armoire"]["position"][0]][dict_carte["armoire"]["position"][1]] != 'A':
        print("Erreur chargement carte : Position armoire invalide selon grille", file=stderr)
        exit(1)
    if dict_carte["grille"][dict_carte["dictionnaire"]["position"][0]][dict_carte["dictionnaire"]["position"][1]] != 'D':
        print("Erreur chargement carte : Position dictionnaire invalide selon grille", file=stderr)
        exit(1)

    # Vérifier nombre résidents
    if len(dict_carte["residents"]) != nb_residents:
        print("Erreur chargement carte : Incohérence nombre de résidents sur la grille.", file=stderr)
        exit(1)
    
    # Pour chaque résident
    id_residents = []
    for resident in dict_carte["residents"]:
        # Vérifier existence propriétés
        if "id" not in resident or "nom" not in resident or "position" not in resident:
            print("Erreur chargement carte : Données résidents invalides", file=stderr)
            exit(1)
        
        # Vérifier position résident selon dimensions
        if not (0 <= resident["position"][0] < hauteur) or \
        not (0 <= resident["position"][1] < largeur):
            print(f"Erreur chargement carte : Position résident {resident["id"]} dépasse la grille", file=stderr)
            exit(1)

        # Vérifier posiion résident dans la grille
        if dict_carte["grille"][resident["position"][0]][resident["position"][1]] != 'P':
            print(f"Erreur chargement carte : Position résident {resident["id"]} invalide selon grille", file=stderr)
            exit(1)
        
        # Unicité de l'identifiant
        if resident["id"] in id_residents:
            print(f"Erreur chargement carte : Résident {resident["id"]} non unique.", file=stderr)
            exit(1)
        
        id_residents.append(resident["id"])

    return dict_carte


def charger_dictionnaire(chemin: str | Path) -> Dict[str, Any]:
    dict_d = _lire_json(chemin, "robot-reconfort/dictionnaire")
    # ----------------------
    # Vérification existence
    # ----------------------
    if "nom" not in dict_d:
        print("Erreur chargement dictionnaire : Dictionnaire sans nom.", file=stderr)
        exit(1)
    
    if "emotions" not in dict_d:
        print("Erreur chargement dictionnaire : Emotions manquantes.", file=stderr)
        exit(1)
    
    if "intensites" not in dict_d:
        print("Erreur chargement dictionnaire : Intensités manquantes.", file=stderr)
        exit(1)

    if "entrees" not in dict_d:
        print("Erreur chargement dictionnaire : Aucune entrée dans dictionnaire.", file=stderr)
        exit(1)

    # ------------------------------------------
    # Vérification type et cohérence des données
    # ------------------------------------------

    # Type des émotions
    if type(dict_d["emotions"]) is not list:
        print("Erreur chargement dictionnaire : Emotions doit être list[str]", file=stderr)
        exit(1)

    # Type des intensités
    if type(dict_d["intensites"]) is not list:
        print("Erreur chargement dictionnaire : Intensités doit être list[str]", file=stderr)
        exit(1)
    
    # Type des entrées
    if type(dict_d["entrees"]) is not list:
        print("Erreur chargement dictionnaire : Entrées doit être liste d'objets", file=stderr)
        exit(1)

    list_formes: list[str] = []

    # Vérifier propriétés de chaque entrée
    for i in range(len(dict_d["entrees"])):
        if "formes" not in dict_d["entrees"][i] or type(dict_d["entrees"][i]["formes"]) is not list:
            print(f"Erreur chargement dictionnaire : Entrée {i} - Formes - type invalide ou propriété non défini.", file=stderr)
            exit(1)
        
        if "emotion" not in dict_d["entrees"][i] or type(dict_d["entrees"][i]["emotion"]) is not str:
            print(f"Erreur chargement dictionnaire : Entrée {i} - émotion - type invalide ou propriété non défini.", file=stderr)
            exit(1)
        
        if "intensite" not in dict_d["entrees"][i] or type(dict_d["entrees"][i]["intensite"]) is not str:
            print(f"Erreur chargement dictionnaire : Entrée {i} - intensité - type invalide ou propriété non défini.", file=stderr)
            exit(1)
        
        # Vérifier présence émotion et intensité
        if dict_d["entrees"][i]["emotion"] not in dict_d["emotions"]:
            print(f"Erreur chargement dictionnaire : Entrée {i} - émotion invalide.", file=stderr)
            exit(1)
        
        if dict_d["entrees"][i]["intensite"] not in dict_d["intensites"]:
            print(f"Erreur chargement dictionnaire : Entrée {i} - intensité invalide.", file=stderr)
            exit(1)
        
        # Vérifier unicité formes
        for forme in dict_d["entrees"][i]["formes"]:
            if forme in list_formes:
                print(f"Erreur chargement dictionnaire : Entrée {i} - forme \"{forme}\" existe dans une autre entrée.", file=stderr)
                exit(1)
            list_formes.append(forme)

    return dict_d


def charger_armoire(chemin: str | Path) -> Dict[str, Any]:
    """Charge un fichier armoire. Voir l'enonce, section 5.3."""
    return _lire_json(chemin, "robot-reconfort/armoire")


def charger_scenario(chemin: str | Path) -> Dict[str, Any]:
    """Charge un fichier scenario. Voir l'enonce, section 5.4."""
    return _lire_json(chemin, "robot-reconfort/scenario")


# ---------------------------------------------------------------------------
# Normalisation des messages
# ---------------------------------------------------------------------------

def normaliser(texte: str) -> List[str]:
    """Decoupe un message en mots comparables au dictionnaire.

    Minuscules, accents retires, decoupage sur tout ce qui n'est pas une
    lettre. C'est exactement la regle de l'enonce, section 6.1 ;
    reimplementez-la vous-meme si vous travaillez dans un autre langage.

        >>> normaliser("Je suis TERRIFIEE, vraiment !")
        ['je', 'suis', 'terrifiee', 'vraiment']
    """
    decompose = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(
        c for c in decompose if unicodedata.category(c) != "Mn"
    )
    mots: List[str] = []
    courant: List[str] = []
    for caractere in sans_accents:
        if caractere.isalpha():
            courant.append(caractere)
        elif courant:
            mots.append("".join(courant))
            courant = []
    if courant:
        mots.append("".join(courant))
    return mots


# ---------------------------------------------------------------------------
# Ecriture de la trace
# ---------------------------------------------------------------------------

ACTIONS = ("AVANCER", "CONSULTER", "CHERCHER", "PRENDRE", "DONNER", "ATTENDRE")
DIRECTIONS = ("N", "S", "E", "O")
REPLIS = ("aucun", "intensite", "voisine_1", "voisine_2")


class Trace:
    """Accumule les pas et les livraisons, puis ecrit le fichier de sortie.

    Utilisation typique :

        trace = Trace(nom_carte="appartement_01",
                      nom_scenario="scenario_01",
                      equipe=["Dupont", "Martin"])
        ...
        trace.ajouter_pas(demande=1, position=(6, 1), casier=(1, 0),
                          action="AVANCER", argument="E",
                          perception={"N": "libre", "S": "mur",
                                      "E": "libre", "O": "mur"})
        ...
        trace.ajouter_livraison(demande=1, resident="R1",
                                emotion="tristesse", intensite="moyenne",
                                casier_choisi=(1, 4), repli="aucun",
                                objet="couverture", succes=True)
        trace.ecrire("sorties/trace_01.json")
    """

    def __init__(
        self,
        nom_carte: str,
        nom_scenario: str,
        equipe: Optional[Sequence[str]] = None,
    ) -> None:
        self.nom_carte = nom_carte
        self.nom_scenario = nom_scenario
        self.equipe: List[str] = list(equipe or [])
        self.pas: List[Dict[str, Any]] = []
        self.livraisons: List[Dict[str, Any]] = []

    # -- pas ---------------------------------------------------------------

    def ajouter_pas(
        self,
        demande: Optional[int],
        position: Sequence[int],
        casier: Sequence[int],
        action: str,
        argument: Optional[str] = None,
        perception: Optional[Dict[str, str]] = None,
        contenu_casier: Optional[str] = None,
        commentaire: Optional[str] = None,
    ) -> None:
        """Enregistre un pas de simulation.

        `position`  : couple (ligne, colonne) du robot AVANT l'action.
        `casier`    : couple (ligne, colonne) du selecteur dans l'armoire,
                      AVANT l'action.
        `perception`: ce que le robot voit depuis sa position, sous la forme
                      d'un dictionnaire des quatre directions vers "mur",
                      "libre", "armoire", "dictionnaire" ou "resident".
        `contenu_casier` : l'objet du casier courant, quand le robot est
                      devant l'armoire et peut donc le voir ; None sinon.
        """
        if action not in ACTIONS:
            raise ValueError(
                f"action inconnue {action!r} (attendu : {', '.join(ACTIONS)})"
            )
        if action in ("AVANCER", "CHERCHER") and argument not in DIRECTIONS:
            raise ValueError(
                f"{action} attend une direction parmi {DIRECTIONS}, "
                f"pas {argument!r}"
            )
        self.pas.append({
            "t": len(self.pas),
            "demande": demande,
            "position": [int(position[0]), int(position[1])],
            "casier": [int(casier[0]), int(casier[1])],
            "action": action,
            "argument": argument,
            "perception": dict(perception) if perception else None,
            "contenu_casier": contenu_casier,
            "commentaire": commentaire,
        })

    # -- livraisons --------------------------------------------------------

    def ajouter_livraison(
        self,
        demande: int,
        resident: str,
        emotion: Optional[str],
        intensite: Optional[str],
        casier_choisi: Optional[Sequence[int]],
        repli: str,
        objet: Optional[str],
        succes: bool,
        motif_echec: Optional[str] = None,
    ) -> None:
        """Enregistre l'issue d'une demande, reussie ou non.

        En cas d'echec, `succes` vaut False et `motif_echec` explique
        pourquoi en une chaine courte (par exemple "resident inaccessible",
        "armoire vide", "emotion indeterminee").
        """
        if repli not in REPLIS:
            raise ValueError(
                f"repli inconnu {repli!r} (attendu : {', '.join(REPLIS)})"
            )
        if not succes and not motif_echec:
            raise ValueError("un echec doit etre accompagne d'un motif_echec")
        self.livraisons.append({
            "demande": int(demande),
            "resident": resident,
            "emotion": emotion,
            "intensite": intensite,
            "casier_choisi": ([int(casier_choisi[0]), int(casier_choisi[1])]
                              if casier_choisi is not None else None),
            "repli": repli,
            "objet": objet,
            "pas_utilises": sum(1 for p in self.pas if p["demande"] == demande),
            "succes": bool(succes),
            "motif_echec": motif_echec,
        })

    # -- export ------------------------------------------------------------

    def en_dictionnaire(self) -> Dict[str, Any]:
        reussies = sum(1 for l in self.livraisons if l["succes"])
        return {
            "format": "robot-reconfort/trace",
            "version": VERSION_ATTENDUE,
            "carte": self.nom_carte,
            "scenario": self.nom_scenario,
            "equipe": self.equipe,
            "pas": self.pas,
            "livraisons": self.livraisons,
            "resume": {
                "demandes": len(self.livraisons),
                "reussies": reussies,
                "echecs": len(self.livraisons) - reussies,
                "pas_total": len(self.pas),
            },
        }

    def ecrire(self, chemin: str | Path) -> Path:
        """Ecrit la trace en JSON UTF-8 indente. Cree le dossier au besoin."""
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(
            json.dumps(self.en_dictionnaire(), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        return chemin
