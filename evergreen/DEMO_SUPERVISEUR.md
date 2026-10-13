# Présentation de demain — Evergreen

## Ce que tu peux dire

« J’ai préparé un premier prototype pour valider l’approche. Il couvre les deux objectifs : comparer les trajets entre les salles, puis proposer des déplacements pour regrouper les catégories de PC par bâtiment. Les trajets prennent en compte les couloirs, les étages, les ascenseurs et l’accessibilité avec un chariot.

Pour l’instant, les données sont fictives. Le prochain travail sera d’intégrer notre inventaire et les plans des bâtiments, puis de valider les temps sur le terrain. Le code est léger, en Python, et les données sont dans des CSV faciles à modifier. »

## Parcours à montrer

1. Ouvrir la page : identifier Morisset, Marion et SITE. Préciser que la carte est schématique.
2. Comparer **MOR-1140 → MRN-302**, avec le chariot accessible. Montrer les couloirs, les ascenseurs et le chemin extérieur dans le détail du trajet. La salle 1140 est explicitement au premier étage; aucun numéro n’est interprété automatiquement.
3. Décoche « Trajet accessible avec chariot » puis compare distance et temps : une route courte n’est pas toujours la plus rapide, et un escalier peut rendre le chemin impropre au chariot. Recocher pour le plan opérationnel de démonstration.
4. Cliquer **Générer le plan** : montrer les PC conservés et les transferts vers les catégories cibles. Le scénario contient 24 PC; 10 restent et 14 sont affectés à d’autres salles.
5. Cliquer **Voir** sur un transfert, puis **Exporter CSV**.
6. Expliquer : l’ordre des mouvements et le stockage temporaire seront validés ensuite. Un plan de destinations ne suffit pas pour déplacer des PC entre salles déjà pleines.

## Informations à demander au superviseur

- Définition exacte de « catégorie 5 » et fichier d’inventaire par salle.
- Catégories cibles souhaitées par bâtiment et contraintes matérielles des salles.
- Plans des bâtiments, numérotation/étages, entrées accessibles et ascenseurs.
- Capacité des chariots, disponibilité des équipes et zone de stockage temporaire.
- Critère prioritaire : temps, nombre de déplacements, distance ou effort physique.

## Résultat honnête à présenter

Un prototype fonctionnel avec des calculs et des données d’exemple, pas un plan réel de campus déjà validé. Les prochaines étapes sont la collecte de données et un trajet pilote. Tu peux annoncer ce progrès sans prétendre que les mesures ont déjà été faites.
