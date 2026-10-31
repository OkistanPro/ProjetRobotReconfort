# Robot de réconfort — Jonathan Merlet & Emmanuel Sanchez

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : Python
Testé sur la version 3.14

## Lancer

```
<votre commande> <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json> <delai-par-pas>
```

Exemple :

```
python main.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json 0.3
```

Dépendances : 
- colorama 0.4.6
- jsonschema 4.26.0
- pytest 9.2.0

Pour les installer :

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install colorama==0.4.6
python -m pip install jsonschema==4.26.0
python -m pip install pytest==9.2.0
```

## Tester

```
pytest -v
```

Il est possible que les tests ne fonctionnent pas et qu'il faille effectuer la commande
```
git reset --hard origin/test
```
pour pouvoir exécuter le code normalement par la suite (c'est possiblement un problème unique à Windows).

Les tests couvrent la vérification des fichiers JSON qui doivent correspondre aux schémas définies dans les fichiers `src/schema_<nom-fichier>.json`

## Organisation du code

| Fichier | Rôle |
|---|---|
| `main.py` | point d'entrée, boucle de décision |
| `src/monde.py` | Objet monde, définissant tous les objets pour un appartement et un scénario |
| `src/robot.py` | Objet robot, définissant son comportement et ses actions |
| `src/carte.py` | Objet abstrait carte |
| `src/carte_monde.py` | Objet carte monde, définissant les positions réelles des murs et entités |
| `src/carte_mentale.py` | Objet carte mentale, présent dans le robot |
| `src/dictionnaire.py` | Objet dictionnaire |
| `src/resident.py` | Objet résident |
| `src/scenario.py` | Objet scénario, qui stocke les demandes |
| `src/e_<>.py` | Objet stockant les états |
| `src/schema_<>.json` | Schéma des JSON à respecter |
| `cartes` | Fichiers JSON des appartements et scénarios |
| `donnees` | Fichiers JSON de l'armoire et du dictionnaire |
| `tests` | Fichiers de tests détectés par `pytest` |


## État

**Ce qui marche.**
- Vérification des fichiers JSON
- Initialisation des objets (CarteMonde, Robots, Scénario, Dictionnaire, Armoire)
- Robot :
    - Réalisation d'un scénario complet
    - Gestion des erreurs
        - ERREUR_CHEMIN_DICO
        - ERREUR_CHEMIN_ARMOIRE
        - ERREUR_CHEMIN_RESIDENT
        - ERREUR_ARMOIRE_VIDE
        - ERREUR_EMOTION_INDETERMINEE
    - Ecriture de la trace
    

**Ce qui ne marche pas.** 
- Erreurs bloquants :
    - ERREUR_CHEMIN_DICO
    - ERREUR_CHEMIN_ARMOIRE
    - ERREUR_CHEMIN_RESIDENT
- Tests pour le robot non réalisé
- Commentaires de codes

## Vidéo

`demo.mp4`, également déclarée dans `rendu.json`.
