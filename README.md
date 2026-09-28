# Hémicycle ouvert

Un site simple et ludique pour suivre l'Assemblée nationale (17ᵉ législature) :

- **L'hémicycle** : les 577 sièges colorés par groupe politique, cliquables.
- **Fiches députés** : circonscription, commission, participation, fidélité au groupe, derniers votes clés, liens vers le site officiel.
- **Les votes** : 314 votes clés classés par thème (santé, éducation, budget, armées, immigration…), avec un résumé « En bref » de chaque texte.
- **Devine le vote** : un jeu pour deviner comment chaque groupe a voté.

Site 100 % statique : tout tient dans `index.html` (aucun serveur nécessaire).

## Voir le site

- En ligne : via GitHub Pages (voir l'onglet *Settings → Pages* du dépôt).
- En local : ouvrir `index.html` dans un navigateur.

## Données

Source : [open data de l'Assemblée nationale](https://data.assemblee-nationale.fr) (députés en exercice, scrutins publics), plus les exposés des motifs des textes sur assemblee-nationale.fr.
Instantané du 28 septembre 2026 (dernier scrutin : 21 juillet 2026).

## Mise à jour automatique

Chaque nuit, GitHub lance `.github/workflows/mise-a-jour.yml` :

1. `src/fetch.py` télécharge les députés, les scrutins et les dossiers législatifs sur data.assemblee-nationale.fr, puis les fiches des nouveaux textes sur assemblee-nationale.fr.
2. `src/prep.py` classe les votes par thème, calcule les statistiques et reconstruit `index.html`.
3. Si quelque chose a changé, les nouvelles données sont enregistrées dans le dépôt et le site est republié.

Pour lancer une mise à jour tout de suite : onglet **Actions** → **Mise à jour du site** → **Run workflow**.

Pour les nouveaux textes, le résumé « En bref » est d'abord un extrait automatique de l'exposé des motifs. Pour le remplacer par un vrai résumé, ajoutez une ligne dans `src/resumes.py` (la clé est l'identifiant du dossier, ex. `"17N52746"`).

Réglage à faire une fois : **Settings → Pages → Source : GitHub Actions**.

## Structure

```
index.html              le site (données intégrées)
src/fetch.py            téléchargement des données officielles
src/template.html       gabarit HTML/CSS/JS (la balise __DATA__ reçoit les données)
src/prep.py             classement par thème, statistiques, fusion des résumés
src/resumes.py          résumés « En bref » des textes (à relire / corriger)
data/                   données brutes et préparées
```

Pour régénérer à la main :

```
python src/fetch.py   # nouvelles données (facultatif)
python src/prep.py    # reconstruit index.html
```
