# Hémicycle ouvert : refonte de l'accès (conception)

Date : 13 novembre 2026 · Branche : `refonte-acces` · Statut : à valider

## 1. Intention

Rendre hemicycle.scriptek.eu simple d'accès : un visiteur trouve **son député** ou **une décision** en quelques secondes, sur ordinateur comme sur mobile, et peut **partager l'adresse** exacte de ce qu'il regarde. L'identité visuelle (Big Shoulders Display, Public Sans, IBM Plex Mono, thèmes sombre et clair, palette actuelle) est conservée.

## 2. Objectifs, non-objectifs, anti-objectifs

**Objectifs**
- Une vraie adresse par contenu (History API), compatible avec le bouton Retour et ouvrable directement dans un nouvel onglet.
- Accueil orienté tâches : recherche « Trouver mon député » (nom, ville, code postal), dernières décisions, Assemblée en un coup d'œil, jeux à part.
- Navigation en 4 entrées : Mon député · Les décisions · Comprendre · Jouer ; barre fixe en bas sur mobile.
- Page complète pour chaque scrutin clé.
- Recherche par code postal fiable, avec choix quand plusieurs circonscriptions sont possibles.
- Lexique d'une vingtaine de termes et vocabulaire clair (« Vote avec son groupe » au lieu de « cohésion » / « fidélité »).
- Plus d'extraits bruts illisibles dans « En bref ».
- Accessibilité : alternative en liste de l'hémicycle, contraste ≥ 4,5:1, cibles tactiles ≥ 44 px, plus de « Survolez » sur écran tactile.
- Logos des groupes visibles.

**Non-objectifs**
- Aperçus de partage personnalisés par député ou scrutin (les robots de prévisualisation n'exécutent pas le JavaScript) : l'aperçu générique du site suffit (décision du 13/11).
- Pages pour les scrutins non « clés » (votes d'amendements).
- Toute modification du service updater, de n8n, de Dokploy ou d'un autre service.

**Anti-objectifs** (échec même si « ça marche »)
- Un texte ajouté qui qualifie un groupe, un député ou un vote (« fidèle », « frondeur », « large victoire »…) : seulement des faits et des définitions.
- Une régression de l'existant : fiche député (panneau latéral), recherche nom/département qui allume les sièges, les deux jeux, mise à jour nocturne.
- Une page blanche sur une adresse, quelle qu'elle soit.
- Une modification faite directement dans `index.html` (tout passe par `src/` et `prep.py`).

## 3. Contraintes

- `index.html` est reconstruit chaque nuit par `prep.py` ; le service updater exécute `src/fetch.py` puis `src/prep.py`, puis commite **uniquement `data/` et `index.html`** sur `main` (même chose pour le workflow GitHub de secours). Tout fichier régénéré chaque nuit doit donc être dans `data/` ou dans `index.html`.
- `main` déclenche la publication Dokploy : rien n'est fusionné dans `main` sans l'accord du propriétaire. Seule l'image Docker change (nouveau `nginx.conf`, nouveaux fichiers copiés).
- Sur la branche, `index.html` diverge de `main` chaque nuit : il est **régénéré** par `prep.py` (jamais fusionné à la main) au moment de la fusion.
- La machine de développement est le serveur de production : aucun outil installé sur l'hôte. Tests dans des conteneurs jetables (noms préfixés `ho-test-`, ports liés à `127.0.0.1`), supprimés après usage.
- 574 députés en exercice dans les données (sièges vacants possibles) : afficher le nombre réel, pas « 577 » en dur (sauf « 577 sièges »).
- Python standard seulement dans `fetch.py`/`prep.py` (l'updater n'installe aucune dépendance) ; `pytest` uniquement pour les tests, dans un conteneur.

## 4. Approches envisagées

| | Approche | Avantages | Inconvénients |
|---|---|---|---|
| **A (retenue)** | Un seul `index.html` avec données intégrées, routage History API côté navigateur, repli nginx `try_files … /index.html`. Sources du gabarit découpées en fichiers que `prep.py` assemble. | Chaîne nocturne, updater, secours GitHub et Dokploy inchangés ; une seule requête ; simple. | Page de ~800 Ko (≈150 Ko gzip) retéléchargée quand les données changent. |
| B | `index.html` léger + `/data.json` séparé. | Interface mise en cache séparément. | Gain faible (données quotidiennes) ; l'image doit copier depuis `data/` ; état « chargement » à gérer. |
| C | Une page HTML générée par député et par scrutin. | Aperçus de partage personnalisés. | Inutile depuis le choix de l'aperçu générique ; ~900 fichiers. |

Choix du propriétaire : **A** (13/11).

## 5. Ce qui a été décidé

### 5.1 Adresses (routes)

Toutes en chemins absolus. Le routeur lit `location.pathname` au chargement et sur `popstate` ; les liens internes sont de vrais `<a href="/…">` interceptés (clic gauche sans modificateur) pour `history.pushState`, de sorte que « ouvrir dans un nouvel onglet » fonctionne.

| Adresse | Vue |
|---|---|
| `/` | Accueil |
| `/depute` | Mon député : recherche + par département + liste des députés *(décision de conception, voir § 6)* |
| `/depute/<prenom-nom>` | Accueil ou vue d'origine + panneau latéral de la fiche ouvert |
| `/votes` | Les décisions (liste filtrable) |
| `/votes/<thème>` | Les décisions filtrées par thème (clés de `cats` : `sante`, `finances`…) |
| `/scrutin/<numéro>` | Page d'un vote |
| `/comprendre` | Comprendre : hémicycle interactif, liste alternative, liens groupes et lexique *(décision de conception)* |
| `/groupes` | Les 12 groupes |
| `/groupes/<sigle>` | Un groupe (sigle en minuscules : `lfi-nfp`, `udr`…) *(décision de conception)* |
| `/lexique` (+ ancre `#<terme>`) | Lexique ; l'ancre ne sert qu'à faire défiler jusqu'au terme |
| `/jouer` | Les deux jeux |
| `/jouer/devine` | Devine le vote |
| `/jouer/groupe` | Trouve ton groupe |
| autre | Page « introuvable » avec la recherche de député et des liens vers les 4 entrées |

- **Identifiant de député** : `prenom-nom` en minuscules, sans accents, caractères non alphanumériques remplacés par `-` (ex. `/depute/antoine-golliot`). Aucun doublon aujourd'hui (16 noms de famille en double, 0 couple prénom-nom). `prep.py` calcule le slug ; en cas de collision future, suffixe `-<numéro de département>` ; un test pytest garantit l'unicité. Un ancien slug d'un député qui n'est plus en exercice mène à la page introuvable.
- **Fiche député** : on garde le panneau latéral. À l'ouverture : `pushState('/depute/x')` ; à la fermeture : retour à l'adresse précédente (`history.back()` si on est arrivé par l'application, sinon `replaceState` vers `/depute`). Ouverte directement, l'adresse affiche la vue « Mon député » en fond avec le panneau ouvert.
- **Anciennes adresses** : au chargement, `#votes` → `/votes`, `#jeu` → `/jouer/devine`, `#questionnaire` → `/jouer/groupe`, autre `#…` → `/`, via `replaceState`. L'ancien onglet mémorisé dans `localStorage` (`ho-tab`) n'est plus utilisé pour choisir la vue de départ (c'est l'adresse qui décide).
- **Titre et balises** : à chaque changement de vue, mise à jour de `document.title` (« Antoine Golliot, député du Pas-de-Calais · Hémicycle ouvert », « Scrutin n° 9895 : … · Hémicycle ouvert »…), `meta[name=description]`, `og:title`, `og:description`, `og:url` et `link[rel=canonical]`. Les valeurs statiques de `head.html` restent l'aperçu générique.
- **Focus et défilement** : à chaque navigation, défilement en haut et focus sur le `<h1>` de la vue (accessibilité) ; sur Retour, le défilement précédent est restauré quand le navigateur le permet.
- **Tous les chemins internes en absolu** : logos `/logos/…`, `/cp.json`, liens.

### 5.2 nginx et Docker

- Nouveau `nginx.conf` à la racine du dépôt, copié par le `Dockerfile` (`/etc/nginx/conf.d/default.conf`).
  - `location / { try_files $uri $uri/ /index.html; }`
  - Les adresses avec extension (`/logos/x.png`, `/cp.json`, `/favicon.ico`…) qui n'existent pas renvoient un vrai **404**, pas `index.html`.
  - `gzip on` pour `text/html`, `application/json`, `image/svg+xml`, `text/css`, `application/javascript`.
  - `index.html` (donc toutes les routes) : `Cache-Control: no-cache` (revalidation à chaque visite, ETag) ; `/cp.json` : `max-age=3600` ; `/logos/` : `max-age=604800`.
- `Dockerfile` : copie `index.html`, `nginx.conf`, `logos/` et `data/cp.json` (servi en `/cp.json`). `.dockerignore` est ajusté pour laisser passer `data/cp.json` (le reste de `data/` reste exclu).
- Port, image de base et comportement Dokploy inchangés.

### 5.3 Structure du gabarit

- `src/template.html` garde le squelette HTML ; CSS et JS sont découpés en `src/ui/*.css` et `src/ui/*.js` (par ex. `base.css`, `mobile.css`, `router.js`, `home.js`, `depute.js`, `votes.js`, `scrutin.js`, `comprendre.js`, `lexique.js`, `jeux.js`), que `prep.py` insère dans l'ordre à des marqueurs (`__CSS__`, `__JS__`). Résultat : toujours **un seul `index.html`**.
- `prep.py` est restructuré en fonctions importables (`build_data()`, `build_index()`, …) avec un `if __name__ == "__main__":` qui garde exactement le comportement en ligne de commande actuel (l'updater appelle `python src/prep.py`).

### 5.4 Accueil (`/`)

Dans l'ordre :
1. Titre « Ce que fait votre Assemblée, en clair. » et date des données (« Données du … · dernier scrutin : … »).
2. Grand champ « Trouver mon député » (nom, ville ou code postal), puis en dessous : « Ou parcourir **par département** · **la liste des N députés** » (liens vers `/depute`).
3. Trois cartes : Mon député (`/depute`) · Ce que l'Assemblée a décidé (`/votes`) · Comprendre l'Assemblée (`/comprendre`).
4. « Les dernières décisions » : 3 cartes cliquables vers `/scrutin/<n>`. Chaque carte affiche le badge ADOPTÉ/REJETÉ, la date, le thème, le type de texte, le titre, le résumé « En bref » (ou « Résumé à venir »), la barre pour/contre/abstention et la phrase de résultat (« Rejeté : 49 pour, 63 contre, 76 abstentions. »). En dessous, des puces de thèmes vers `/votes/<thème>`.
5. « L'Assemblée en un coup d'œil » : barre horizontale des 12 groupes proportionnelle aux sièges (ordre gauche → droite de l'hémicycle), légende (sigle + sièges, chaque entrée liée à `/groupes/<sigle>`), la phrase « Majorité absolue : 289 sièges. Aucun groupe ne l'atteint seul. » (calculée à partir des données, pas en dur), et les liens « Explorer l'hémicycle interactif » (`/comprendre`), « Les 12 groupes » (`/groupes`), « Lexique » (`/lexique`).
6. « Jouer » : deux cartes séparées visuellement de l'information (Devine le vote, Trouve ton groupe).

**Mobile** (< 760 px) : même ordre ; l'hémicycle interactif n'est pas sur l'accueil ; sous la barre des groupes, un bouton « Voir les N députés en liste » (`/depute`).

### 5.5 Recherche « Trouver mon député »

Un seul composant, réutilisé (accueil, `/depute`, page introuvable, page de vote en version « qu'a voté mon député ? »).
- **Nom** : comportement actuel (normalisation sans accents, tous les termes doivent correspondre).
- **Numéro de département** (1 à 3 caractères, `2A`/`2B`) : comportement actuel.
- **Code postal** (5 chiffres) : chargement paresseux de `/cp.json` (une fois), puis les communes de ce code postal et leurs circonscriptions. Si une seule circonscription : on propose directement le député. Si plusieurs : on liste les choix « Commune · 4e circonscription de la Dordogne → Député » et l'utilisateur choisit. Siège vacant : « Siège vacant actuellement ».
- **Ville** (texte qui correspond à un nom de commune de `/cp.json`) : mêmes résultats que pour le code postal, en plus des noms de députés correspondants. `/cp.json` est donc chargé dès que l'utilisateur tape 3 caractères ou plus qui ne correspondent à aucun député (ou dès le focus du champ, au choix du constructeur).
- Le résultat ouvre la fiche (`/depute/<slug>`). Dans la vue Comprendre, la recherche continue d'allumer les sièges de l'hémicycle comme aujourd'hui.
- Liste de résultats accessible : `role="listbox"`/`option` (ou liste de liens), navigation aux flèches, annonce du nombre de résultats dans une zone `aria-live`.

### 5.6 Table code postal → circonscription (`fetch.py` → `data/cp.json`)

- Sources (data.gouv.fr, Licence Ouverte) :
  - *Base officielle des codes postaux* (La Poste) : `https://data.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw` (CSV `;`, latin-1) : code commune INSEE ↔ code postal ↔ nom.
  - *Liste des bureaux de vote associés à leur circonscription législative* (Etalab, d'après le ministère de l'Intérieur) : `bureaux-de-vote-circonscriptions.csv` (URL récupérée par l'API data.gouv du jeu `liste-des-bureaux-de-vote-associes-a-leur-circonscription-legislative`) : commune ↔ numéro de bureau ↔ circonscription.
- Règles :
  - commune → ensemble des circonscriptions de ses bureaux ;
  - **Paris, Lyon, Marseille** : La Poste utilise les codes d'arrondissement (75111, 69383, 13201…), le fichier des bureaux le code de la commune entière (75056, 69123, 13055). Les deux premiers chiffres du numéro de bureau donnent l'arrondissement pour Paris et Marseille (vérifié : 75011 → 6e et 7e circ. de Paris). Pour Lyon, la règle de numérotation est à vérifier par le constructeur ; si elle n'est pas fiable, repli sur toutes les circonscriptions de la commune ;
  - commune absente du fichier des bureaux (commune nouvelle créée depuis 2022) : on utilise les anciennes communes si La Poste les liste encore, sinon on propose toutes les circonscriptions du département.
- Format compact (`data/cp.json`, servi en `/cp.json`) : `{ "<cp>": [["Nom commune", ["2401","2404"]], …], … }`. Le code circonscription `DDNN` (`2A01`, `9741`…) est relié au député par `nd` + `ci` dans les données AN ; le constructeur vérifie la correspondance pour la Corse, l'outre-mer (971–976, 986–988) et les Français de l'étranger (99, sans code postal).
- Rafraîchissement : téléchargé par `fetch.py` à chaque passage. En cas d'échec réseau, on garde le fichier existant et la mise à jour nocturne **ne doit pas échouer** pour autant (journal d'avertissement seulement).
- Tests : 24200 → 8 communes, toutes dans la 4e circonscription de la Dordogne (correction du 13/11 : pas de 1re circonscription) ; 75011 → 6e et 7e de Paris ; une grande ville hors PLM (31000 Toulouse) → plusieurs choix ; couverture ≥ 99 % des codes postaux de métropole et des DROM ; chaque circonscription de la table correspond à un siège connu (député ou vacant).

### 5.7 Les décisions (`/votes`, `/votes/<thème>`)

- Liste actuelle conservée (filtres thème, résultat, type, recherche), mais chaque carte est un **lien** vers `/scrutin/<n>` (plus de dépliage sur place). Le filtre par thème change l'adresse (`/votes/<thème>`) ; les autres filtres restent locaux.
- Le dépliage existant (tableau par groupe + hémicycle du vote) est déplacé dans la page de vote.

### 5.8 Page d'un vote (`/scrutin/<numéro>`)

Pour chacun des scrutins clés (330 aujourd'hui) :
- Fil d'Ariane : Les décisions › Thème (lien `/votes/<thème>`).
- Date · type de texte · lecture (le type et la lecture renvoient au lexique).
- Titre.
- Encadré résultat : ADOPTÉ / REJETÉ en grand, chiffres pour/contre/abstention, barre, phrase « N députés ont pris part à ce vote (pour, contre ou abstention). » (formulation modifiée le 13/11 : un député absent peut voter par délégation) (N = pour + contre + abstentions ; « ont pris part » = votants exprimés et abstentionnistes, définition dans le lexique). Pour les motions de censure : rappel factuel que seules les voix « pour » sont comptées et que 289 sont nécessaires.
- « De quoi s'agit-il ? » : résumé « En bref » (ou « Résumé à venir » + lien vers le texte officiel), auteur, promulgation éventuelle, puis la définition d'un mot-clé du vote (type de texte ou lecture) avec un lien « Voir le lexique ».
- « Comment chaque groupe a voté » : une ligne par groupe dans l'ordre de l'hémicycle : pastille de couleur, sigle, nom complet, position majoritaire en couleur (Pour/Contre/Abstention), mini-barre, chiffres pour/contre/abst.
- L'hémicycle du vote (existant), avec en dessous une **liste équivalente** accessible (repliable).
- Colonne latérale (sous le contenu sur mobile) : recherche « Et mon député, qu'a-t-il voté ? » (même composant que § 5.5 : renvoie « Pour / Contre / Abstention / N'a pas pris part au vote / Pas encore député à cette date »), lien « Texte officiel » (dossier législatif) et « Scrutin sur assemblee-nationale.fr », bouton « Copier le lien de ce vote » (`navigator.clipboard`, avec un retour visuel et annoncé « Lien copié »).
- Partout ailleurs (fiche député, groupe, jeux), les titres de votes mènent à `/scrutin/<n>`.
- `/scrutin/<n>` d'un scrutin non clé : page introuvable adaptée (« Ce scrutin ne fait pas partie des votes clés suivis ici ») avec le lien vers sa page officielle.

### 5.9 Comprendre (`/comprendre`, `/groupes`, `/groupes/<sigle>`)

- `/comprendre` : l'hémicycle interactif actuel (légende cliquable, recherche qui allume les sièges), la barre des groupes, liens vers `/groupes` et `/lexique`.
- **Alternative en liste de l'hémicycle** : bouton « Afficher en liste » qui présente les députés groupés par groupe (ordre de l'hémicycle), en vrais boutons/liens focalisables, chacun ouvrant la fiche. Le SVG garde `role="img"` et une description textuelle (répartition des sièges).
- `/groupes` : les cartes de groupes actuelles ; `/groupes/<sigle>` : le panneau d'un groupe actuel.
- Sur écran tactile (`(hover: none)`), le texte « Survolez un siège… » est remplacé par « Touchez un siège pour ouvrir la fiche du député. » ; plus aucun « Survolez » sur tactile.

### 5.10 Mobile

- Barre de navigation fixe en bas (< 760 px), 4 entrées avec icônes SVG intégrées et libellés : Mon député · Les décisions · Comprendre · Jouer ; entrée active indiquée (`aria-current="page"`) ; respect de `env(safe-area-inset-bottom)` ; le contenu a une marge basse pour ne pas être masqué.
- Sur ordinateur : les 4 entrées en haut (remplacent les onglets actuels).
- Cibles tactiles ≥ 44 × 44 px partout (puces, boutons ⓘ, liens de liste, boutons de jeux).
- Pas de défilement horizontal de la page à 375 px.

### 5.11 Vocabulaire et lexique

- « cohésion » et « Fidélité » deviennent **« Vote avec son groupe »** partout (cartes de groupes, panneau de groupe, tri des membres, fiche, notes explicatives).
- `src/lexique.py` (même logique que `resumes.py`) : une vingtaine de termes avec une définition factuelle et neutre d'une ou deux phrases, et des variantes de forme pour la détection. Au moins : scrutin public, scrutin solennel, motion de censure, motion de rejet, article 49.3, article 50-1 (déclaration du Gouvernement), projet de loi, proposition de loi, proposition de résolution, lecture (première, nouvelle, définitive), commission mixte paritaire, amendement, groupe politique, non-inscrit, majorité absolue, abstention, non-votant, promulgation, exposé des motifs, circonscription, déport, HATVP.
- `prep.py` intègre le lexique aux données ; `/lexique` les liste par ordre alphabétique, chaque terme ayant une ancre.
- Chaque terme technique affiché (type de texte, lecture, « majorité absolue », « non-inscrit », etc.) est un lien discret vers `/lexique#<terme>`. Les info-bulles existantes (`KIND_NOTE`, `lecNote`, aide Transparence) reprennent les définitions du lexique au lieu d'avoir leur propre texte.
- Les définitions sont relues par le propriétaire avant fusion (liste fournie dans le compte rendu de l'étape).

### 5.12 Résumés « En bref »

- `prep.py` marque l'extrait automatique (drapeau 2) comme **inutilisable** s'il commence par « ARTICLE » / « Article premier » ou équivalent, s'il ressemble à une liste d'articles (plusieurs « Article n » ou numérotation), ou s'il a été tronqué (longueur d'origine > 280 caractères). Le seuil et les motifs sont testés par pytest sur les cas réels.
- Dans ce cas, l'interface affiche « Résumé à venir » avec le lien vers le texte officiel, au lieu de l'extrait.
- Rapport : `prep.py` écrit `data/resumes-a-ecrire.md` (clé du dossier, titre, n° de scrutin, lien officiel, raison), reconstruit à chaque passage, donc commité chaque nuit par l'updater. Il sert à compléter `src/resumes.py`.

### 5.13 Logos des groupes

- Fichiers récupérés une fois sur Wikimedia Commons, **seulement** sous licence libre ou domaine public (dont « PD-textlogo »), placés dans `logos/<SIGLE>.svg` (ou `.png`), avec `logos/SOURCES.md` (URL Commons, auteur, licence, date). Les groupes sans logo réutilisable gardent le sigle sur fond de couleur actuel.
- Le code cherche `/logos/<SIGLE>.<ext>` à partir d'une liste connue au moment du build (pas de requête 404 pour les logos absents).
- Les logos ne sont pas rafraîchis la nuit ; un nouveau groupe s'affiche avec son sigle jusqu'à l'ajout manuel du logo.

### 5.14 Accessibilité

- Contraste ≥ 4,5:1 pour tout le texte, dans les deux thèmes. Mesures actuelles : `--abst` clair `#C07F0A` = 2,95:1 sur le fond → ajouter un jeton de texte plus foncé pour l'abstention (la couleur des barres peut rester) ; `--accent` sombre sur `--surface-2` = 4,32:1 → à foncer/éclaircir. Le texte sur les couleurs de groupe utilise `textColorOn` (à vérifier sur les 12 couleurs). Un test automatisé mesure les contrastes des jetons.
- Repères : `<header>`, `<nav aria-label>`, `<main>`, un seul `<h1>` par vue, lien d'évitement « Aller au contenu ».
- Panneau de fiche : focus piégé dans le dialogue, Échap pour fermer, retour du focus.
- Barres pour/contre/abstention : toujours accompagnées des chiffres en texte.
- `prefers-reduced-motion` respecté.

### 5.15 Neutralité

Aucun texte ajouté ne qualifie un groupe, un député ou un vote. Les phrases de résultat sont générées à partir des chiffres (« Adopté : 312 pour, 210 contre, 40 abstentions. »), sans adjectif (« large », « serré », « surprise »…). Les définitions du lexique décrivent les procédures sans jugement. Revue explicite de ces textes à chaque étape.

## 6. Décisions de conception prises (à vérifier en relisant)

1. Slug député `prenom-nom` (le nom seul provoque 16 collisions).
2. Routes ajoutées en plus de la liste demandée : `/depute` (page « Mon député »), `/comprendre`, `/groupes/<sigle>`, `/jouer`.
3. La fiche reste un panneau latéral superposé à la vue d'origine ; ouverte directement, elle se superpose à `/depute`.
4. Seul le filtre par thème est dans l'adresse ; résultat, type et recherche restent locaux.
5. `/cp.json` séparé, chargé à la demande ; repli « toutes les circonscriptions de la commune » pour les grandes villes hors Paris et Marseille (et Lyon si sa numérotation n'est pas fiable).
6. `index.html` en `no-cache` (revalidation) plutôt qu'une durée fixe, pour que les données de la nuit soient vues tout de suite.
7. Rapport des résumés dans `data/resumes-a-ecrire.md` (commité automatiquement chaque nuit).
8. Le lexique est une source Python (`src/lexique.py`), comme `resumes.py`, pour être modifiable de la même façon.

## 7. Découpage en étapes livrables

Chaque étape : commits courts en français sur `refonte-acces`, tests verts, vérification dans Chromium sans affichage (conteneur Playwright) à 1280 px et 375 px, **zéro erreur console**, captures d'écran, compte rendu. Les adresses sont testées sur le conteneur nginx construit depuis le `Dockerfile`, pas en ouvrant `index.html`.

1. **Adresses partageables** : découpage du gabarit, restructuration testable de `prep.py`, slugs, routeur, nouvelle navigation à 4 entrées (contenu des vues existantes réutilisé), page introuvable, anciennes ancres, titres et balises `og:`, `nginx.conf` + `Dockerfile`, chemins absolus, logos (§ 5.13). Test clé : `/depute/<slug>` ouvert directement dans un nouvel onglet affiche la fiche ; Retour et Avancer fonctionnent ; `/depute/inexistant` affiche la page introuvable.
2. **Mobile et accueil** : nouvel accueil (§ 5.4), barre fixe en bas, cibles de 44 px, « Survolez » remplacé, hémicycle hors de l'accueil mobile.
3. **Pages de vote** : § 5.7 et § 5.8, cartes cliquables partout.
4. **Recherche par code postal** : § 5.5 et § 5.6 (`fetch.py`, `data/cp.json`, Docker).
5. **Lexique et vocabulaire** : § 5.11 et § 5.12 (rapport des résumés).
6. **Accessibilité** : § 5.14, liste alternative de l'hémicycle, contrastes, audit clavier et lecteur d'écran (arbre d'accessibilité Chromium).

## 7 bis. Retour arrière

- Avant la fusion, une étiquette `avant-refonte` est posée sur le dernier commit de `main`.
- La fusion se fait en un seul commit de fusion (`--no-ff`). En cas de problème : `git revert -m 1 <commit de fusion>` puis `git push` ; Dokploy republie l'ancienne version comme pour toute modification de `main`. Rien n'est à faire côté Dokploy, n8n ou updater.
- Après un retour arrière, la mise à jour nocturne continue : elle reconstruit `index.html` avec l'ancien gabarit, revenu par le revert. Les fichiers ajoutés dans `data/` (`cp.json`, `resumes-a-ecrire.md`) n'ont aucun effet sur l'ancienne version.
- Chaque étape peut être fusionnée séparément si le propriétaire le souhaite, ce qui limite l'ampleur d'un éventuel retour arrière.
- Avant toute fusion, l'image est construite et vérifiée en local depuis le `Dockerfile`, ce qui réduit le risque au départ.

## 8. Laissé au constructeur

- Mise en page fine, icônes, transitions, dans le respect des jetons et polices existants.
- Seuils exacts de détection des extraits inutilisables (testés sur les données réelles).
- Forme exacte du JSON intégré (clés courtes, comme aujourd'hui).
- Règle de numérotation des bureaux de Lyon (vérifier, sinon repli).
- Outils de test : image Playwright officielle (Python), conteneur `python:3.12` pour pytest.
