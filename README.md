# Hémicycle ouvert

Un site simple et ludique pour suivre l'Assemblée nationale (17ᵉ législature) :

- **Mon député** : recherche par nom, ville, code postal ou département ; fiche de chaque député (circonscription, commission, participation, vote avec son groupe, derniers votes clés, transparence).
- **Les décisions** : les votes clés par thème, et une page par vote (résultat, résumé, vote de chaque groupe, « et mon député ? »).
- **Comprendre** : l'hémicycle interactif (avec sa version en liste), les groupes et un lexique de la procédure parlementaire.
- **Transparence** : lien vers les déclarations HATVP, déports déclarés au registre de l'Assemblée, conditions d'arrivée au siège.
- **Les votes** : 314 votes clés classés par thème (santé, éducation, budget, armées, immigration…), avec un résumé « En bref » de chaque texte.
- **Jouer** : « Devine le vote » et « Trouve ton groupe ».

Site statique : une seule page `index.html` (données intégrées), servie par nginx, avec une vraie adresse par contenu :
`/depute/<prenom-nom>`, `/scrutin/<numéro>`, `/votes/<thème>`, `/groupes`, `/groupes/<sigle>`, `/comprendre`, `/lexique`, `/jouer/devine`, `/jouer/groupe`.
`nginx.conf` renvoie toute adresse vers `index.html` ; les anciennes adresses `#votes`, `#jeu`, `#questionnaire` sont redirigées.

## Voir le site

- En ligne : https://hemicycle.scriptek.eu (hébergé sur le serveur Scriptek, publié par Dokploy à chaque modification du dépôt).
- En local : `docker build -t hemicycle . && docker run --rm -p 8080:80 hemicycle`, puis http://localhost:8080 (ouvrir `index.html` directement ne gère pas les adresses).

## Données

Source : [open data de l'Assemblée nationale](https://data.assemblee-nationale.fr) (députés en exercice, scrutins publics), plus les exposés des motifs des textes sur assemblee-nationale.fr.
Codes postaux : [Base officielle des codes postaux](https://www.data.gouv.fr/datasets/base-officielle-des-codes-postaux) (La Poste) et [Liste des bureaux de vote associés à leur circonscription](https://www.data.gouv.fr/datasets/liste-des-bureaux-de-vote-associes-a-leur-circonscription-legislative) (data.gouv.fr), assemblées dans `data/cp.json`.
Logos des groupes : Wikimedia Commons, licences et auteurs dans `logos/SOURCES.md`.
Instantané du 28 septembre 2026 (dernier scrutin : 21 juillet 2026).

## Mise à jour automatique

Chaque nuit, n8n (sur le serveur Scriptek) appelle le service `updater/` :

1. `src/fetch.py` télécharge les députés, les scrutins et les dossiers législatifs sur data.assemblee-nationale.fr, puis les fiches des nouveaux textes, le registre des déports et la table des codes postaux (en cas d'échec de cette dernière, la table précédente est gardée).
2. `src/prep.py` classe les votes par thème, calcule les statistiques et reconstruit `index.html`.
3. Si quelque chose a changé, les nouvelles données sont poussées sur GitHub, et Dokploy republie le site.

Le service renvoie un compte rendu JSON à n8n (`POST /run`, dernier résultat sur `GET /status`).

En secours, la même mise à jour peut être lancée sur GitHub : onglet **Actions** → **Mise à jour (secours)** → **Run workflow**.

Pour les nouveaux textes, le résumé « En bref » est d'abord un extrait automatique de l'exposé des motifs. Quand cet extrait est inutilisable (il commence par « ARTICLE », ressemble à une liste d'articles ou est trop long), le site affiche « Résumé à venir » avec le lien vers le texte officiel. La liste des dossiers à compléter est régénérée chaque nuit dans `data/resumes-a-ecrire.md`. Pour écrire un résumé, ajoutez une ligne dans `src/resumes.py` (la clé est l'identifiant du dossier, ex. `"17N52746"`).

Les définitions du lexique sont dans `src/lexique.py`.

## Structure

```
index.html              le site (généré : ne pas modifier à la main)
src/fetch.py            téléchargement des données officielles
src/cp.py               table code postal → circonscription
src/template.html       squelette HTML (__CSS__, __JS__, __DATA__)
src/ui/*.css, *.js      styles et scripts, assemblés par prep.py (ordre : UI_CSS, UI_JS)
src/prep.py             classement par thème, statistiques, résumés, lexique, index.html
src/resumes.py          résumés « En bref » des textes
src/lexique.py          définitions du lexique
data/                   données brutes et préparées (dont cp.json, resumes-a-ecrire.md)
logos/                  logos des groupes et leurs sources
updater/                service de mise à jour appelé par n8n (Docker)
Dockerfile, nginx.conf  publication du site (nginx) par Dokploy
tests/                  tests (pytest et Playwright, en conteneurs)
```

Pour régénérer à la main :

```
python src/fetch.py   # nouvelles données (facultatif)
python src/prep.py    # reconstruit index.html
```

## Tests

Tout tourne dans des conteneurs jetables (rien à installer) :

```
tests/run-unit.sh           # pytest : prep.py, codes postaux, lexique, contrastes
tests/run-unit.sh -m reseau # + test sur les vraies sources de codes postaux
tests/run-e2e.sh            # construit l'image nginx et teste le site dans Chromium (1280 et 375 px)
ETAPE=n tests/run-e2e.sh    # + captures d'écran dans .captures/etape-n/
```
