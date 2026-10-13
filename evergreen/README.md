# Evergreen — Campus transfer planner

Prototype Python léger pour préparer le regroupement des catégories/modèles de PC par bâtiment avant le remplacement estival. Interface et guide de démonstration en français. Python standard uniquement, aucun service externe, aucune clé API, aucune installation pip.

**Toutes les données sont fictives.** Les noms Morisset, Marion et SITE servent au scénario. Les positions, salles, capacités, catégories, distances et caractéristiques des ascenseurs ne sont pas des mesures réelles du campus. « CAT-5 » représente une catégorie d’inventaire et ne désigne pas une version de Windows.

## Ouvrir dans GitHub Codespaces

1. Décompresser l’archive.
2. Créer un dépôt GitHub vide, de préférence privé pour les futurs inventaires internes.
3. Ajouter le **contenu** du dossier `evergreen` à la racine du dépôt : `server.py`, `planner.py`, `static/`, `data/`, `tests/`, `.devcontainer/`, etc. Vérifier que `.devcontainer/devcontainer.json` est inclus; certains explorateurs masquent les dossiers commençant par un point.
4. GitHub : **Code → Codespaces → Create codespace on main**.
5. Le conteneur essaie de démarrer `python server.py` automatiquement. Si nécessaire, saisir dans le terminal :

```bash
python server.py
```

6. Dans l’onglet **Ports**, ouvrir le port **8000** dans le navigateur. Garder le port privé. Si un serveur fonctionne déjà, utiliser le port existant; ne pas démarrer une deuxième instance sur le même port.

Alternative locale : Python 3.11 ou supérieur, ouvrir un terminal dans le dossier et exécuter `python server.py`, puis ouvrir http://localhost:8000. Ctrl+C arrête le serveur. `python server.py --port 8001` permet de choisir un autre port.

## Démonstration de 3 minutes

Voir `DEMO_SUPERVISEUR.md` pour le texte et les étapes.

- Comparer MOR-1140 → MRN-302 avec un chariot accessible.
- Basculer entre distance et temps, et comparer sans contrainte d’accessibilité.
- Générer un plan pour regrouper CAT-3 à Morisset, CAT-5 à Marion et CAT-7 à SITE.
- Voir les trajets d’un transfert et exporter le tableau CSV.
- Modifier une liaison dans `data/links.csv`, puis « Recharger les CSV » pour simuler une panne d’ascenseur.

## Méthode

Chaque salle est reliée à un palier par un couloir. Les paliers sont reliés par ascenseurs ou escaliers. Les entrées sont reliées par des chemins extérieurs. Les liaisons sont bidirectionnelles dans cette version.

- **Objectif 1 :** Dijkstra trouve le trajet de distance minimale ou de temps estimé minimal entre deux salles. Avec un chariot, les liaisons non accessibles sont exclues.
- **Objectif 2 :** un flot de coût minimal affecte les stocks aux capacités des salles du modèle cible. Il maximise d’abord les quantités affectables, puis minimise leur coût total, selon les trajets disponibles. Les catégories cibles sont des choix humains, pas déduites par l’algorithme.
- Les PC déjà dans une bonne salle peuvent rester, à coût de trajet nul.
- La fonction objectif est la somme des mètres ou secondes **par PC**, pas le temps global d’une tournée. Une affectation par chariot, la mutualisation des trajets et la tournée de plusieurs équipes sont des extensions.
- Les quantités ne sont jamais inventées : manque de stock, surplus sans cible ou destinations inaccessibles produisent des alertes. Les PC non affectés restent à gérer; ils ne disparaissent pas de l’inventaire.

### Estimations

`temps liaison = mètres / vitesse + délai fixe`.

Pour un ascenseur, le facteur ascenseur multiplie le délai fixe qui combine attente et trajet. Il s’agit d’un scénario modifiable, pas d’une mesure de file d’attente. Les mètres verticaux sont approximatifs et ne remplacent pas une mesure de temps.

`voyages = plafond(quantité / capacité chariot)`

`effort transfert = 2 × voyages × temps aller + quantité × manutention`.

Cela suppose un retour après chaque voyage, avec le même trajet et temps au retour. La manutention correspond au temps total de prise en charge et dépôt **par PC**. Le temps affiché est une somme de durées, pas des heures-personnes ni une durée calendaire. Le trajet initial des équipes depuis Morisset, la déconnexion, l’installation, les tests, les horaires, les pauses et la coordination ne sont pas inclus.

## Données CSV

Modifier dans Codespaces puis cliquer sur « Recharger les CSV ». Encodage UTF-8. Utiliser des identifiants sans espaces, par exemple `MOR-1140`. Les étages sont explicites : on ne déduit jamais l’étage des chiffres de la salle.

| Fichier | Colonnes / rôle |
|---|---|
| `buildings.csv` | `id,name,x,y,target_model`. x/y sont uniquement des positions sur le schéma SVG, sans unité géographique. |
| `rooms.csv` | `id,building,floor,capacity,corridor_m`. floor est l’étage déclaré; 0 représente le niveau d’entrée du scénario. capacity est le nombre de postes cibles. |
| `inventory.csv` | `room,model,quantity`. Une ligne unique par salle et catégorie. Le total d’une salle ne doit pas dépasser sa capacité. |
| `links.csv` | `id,source,target,meters,fixed_seconds,kind,accessible,enabled,label`. kind : walk/elevator/stairs; drapeaux 0/1. |

Les paliers portent l’identifiant `BATIMENT:FETAGE`, par exemple `MOR:F1`. Une liaison doit référencer une salle ou un palier correspondant à un étage déclaré dans rooms.csv, ou le niveau F0 d’un bâtiment. Pour un palier sans salle, ajouter un point de capacité 0 dans rooms.csv. Une salle bureau ou un dépôt peut avoir une capacité positive pour gérer du stock; le bureau fictif actuel a une capacité 0 et sert seulement de point de départ.

### Ajouter un bâtiment

1. Ajouter sa ligne et son modèle cible dans buildings.csv.
2. Ajouter ses salles et leurs étages vérifiés dans rooms.csv.
3. Ajouter une liaison extérieure entre son palier F0 et un bâtiment existant.
4. Ajouter les liaisons verticales jusqu’aux étages concernés, avec leurs disponibilités/accessibilités.
5. Ajouter l’inventaire réel et vérifier les capacités.

## Prochaines étapes avant utilisation opérationnelle

1. Confirmer la définition des catégories et les règles de regroupement avec le superviseur.
2. Récupérer l’inventaire et les plans, puis mesurer les trajets réellement praticables avec un chariot.
3. Cartographier les entrées, couloirs, rampes, portes, ascenseurs, capacités/largeurs, temps d’attente, heures et restrictions d’accès. Ajouter les liaisons intérieures entre bâtiments s’il y en a.
4. Choisir les cibles compatibles avec le stock, les besoins et les capacités des bâtiments.
5. Valider un transfert pilote avec les deux techniciens.
6. Définir une zone tampon et l’ordre des échanges : **ne pas livrer dans une salle pleine**. Le prototype propose des destinations, pas une séquence exécutable. Les cycles d’échange exigent du stockage ou une coordination.
7. Ajouter ensuite le géoréférencement (latitude/longitude des entrées), les plans d’étage, le départ du bureau, la tournée des équipes et les créneaux d’accès. La distance à vol d’oiseau ne suffit pas pour calculer un chemin accessible.

## Répartition pour deux personnes

| Personne | Travail proposé |
|---|---|
| A | Inventaire, catégories, capacities, modèles cibles; échanges avec le superviseur; collecte des plans. |
| B | Relevé chemins/ascenseurs, mise à jour du graphe, interface, vérification des trajets et exports. |
| Ensemble | Parcours pilote avec chariot, validation des temps et du stockage temporaire. |

## Vérification

```bash
python -m unittest discover -s tests -v
```

Tests : étages explicites, trajets accessibles, panne d’ascenseur, distance/temps, conservation du stock et capacités, déficit, réaffectation optimale et paramètres invalides.

## Structure

- `server.py` : serveur HTTP et API JSON, en lecture seule.
- `planner.py` : lecture/validation, graphe, trajets, affectation.
- `static/` : interface sans dépendances ni tuiles de carte externes.
- `data/` : scénarios d’exemple modifiables.
- `.devcontainer/` : environnement Codespaces.
- `tests/` : tests des calculs.

Le serveur est destiné au développement et à la démonstration via port privé. Il ne fournit pas d’authentification pour un déploiement public. Aucune modification de PC ni action de déplacement n’est exécutée.
