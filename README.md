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

## Structure

```
index.html              le site (données intégrées)
src/template.html       gabarit HTML/CSS/JS (la balise __DATA__ reçoit les données)
src/prep.py             classement par thème, statistiques, fusion des résumés
src/resumes.py          résumés « En bref » des textes (à relire / corriger)
data/                   données brutes et préparées
```

Pour régénérer après modification : lancer `src/prep.py` pour produire `data.json`, puis injecter `data.json` dans `src/template.html` à la place de `__DATA__`.
