# Refonte de l'accès : plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Objectif :** rendre hemicycle.scriptek.eu navigable par adresses partageables, utilisable sur mobile, avec pages de vote, recherche par code postal, lexique et accessibilité, sans toucher à la chaîne nocturne.

**Architecture :** toujours un seul `index.html` (données intégrées) produit par `prep.py`, désormais assemblé à partir de `src/template.html` + `src/ui/*.css` + `src/ui/*.js` (concaténés dans une seule IIFE, comme aujourd'hui). Routage History API côté navigateur ; nginx renvoie toute adresse sans extension vers `index.html`. `/cp.json` et `/logos/` sont servis à côté.

**Pile :** Python 3.12 (bibliothèque standard seulement dans `src/`), JavaScript sans dépendance ni outil de build, nginx 1.27-alpine, tests pytest (conteneur `python:3.12-slim`) et Playwright Python (conteneur `mcr.microsoft.com/playwright/python:v1.48.0-jammy`).

**Spécification :** `docs/superpowers/specs/2026-11-13-refonte-acces-design.md` (abrégée « spec » ; § = section de la spec).

## Contraintes globales

- Ne jamais modifier `index.html` à la main : il est produit par `python src/prep.py`. Le régénérer et le commiter à chaque tâche qui change `src/`.
- `python src/fetch.py` puis `python src/prep.py` doivent continuer à marcher tels quels (appel de l'updater). Aucune dépendance hors bibliothèque standard dans `src/`.
- Tout fichier régénéré chaque nuit va dans `data/` (l'updater ne commite que `data/` et `index.html`).
- Ne toucher ni à `updater/`, ni à `.github/`, ni à n8n, ni à Dokploy, ni à aucun conteneur existant. Les conteneurs de test s'appellent `ho-test-*` et sont supprimés après usage ; aucun port publié sur l'hôte.
- Branche `refonte-acces`, commits courts en français, identité `Scriptek <contact@scriptek.eu>`, terminés par `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Pas de fusion dans `main` sans accord explicite.
- Chemins internes absolus (`/…`) partout.
- Polices et jetons de couleur existants conservés ; nouvelles couleurs = nouveaux jetons dans `:root` et dans les deux blocs sombres.
- Neutralité : aucun adjectif ni jugement sur un groupe, un député ou un vote dans les textes ajoutés. Mots interdits dans les textes générés (testés) : `large`, `écrasant`, `serré`, `victoire`, `défaite`, `surprise`, `fidèle`, `fidélité`, `frondeur`, `discipliné`, `cohésion`.
- Vérification de chaque interface : Chromium sans affichage via `tests/run-e2e.sh`, à 1280 px et 375 px, **aucune erreur console ni exception de page**.
- Libellés fixés par la spec, à reprendre mot pour mot : « Ce que fait votre Assemblée, en clair. », « Trouver mon député », « Ou parcourir par département · la liste des N députés », « Les dernières décisions », « L'Assemblée en un coup d'œil », « Explorer l'hémicycle interactif », « Les 12 groupes », « Lexique », « Jouer », « Mon député », « Les décisions », « Comprendre », « De quoi s'agit-il ? », « Comment chaque groupe a voté », « Et mon député, qu'a-t-il voté ? », « Copier le lien de ce vote », « Seuls les députés présents votent : N ont pris part à ce vote. », « Résumé à venir », « Vote avec son groupe », « Voir les N députés en liste ».

## Points de vigilance (Review Focus)

1. Adresse de député saisie à la main ou venue d'ailleurs : majuscules, accents encodés (`/depute/Antoine-Golliot`, `/depute/fran%C3%A7ois-…`), barre finale → doit ouvrir la bonne fiche (normalisation avant recherche). Test en tâche 6.
2. Barre oblique finale et paramètres (`/votes/`, `/votes/sante?utm_source=x`) → même vue que sans. Test en tâche 5.
3. Lien profond ouvert dans un nouvel onglet puis fermeture de la fiche ou « Retour » dans le fil d'Ariane → on reste sur le site (pas de `history.back()` qui quitte le site). Test en tâche 6.
4. `/cp.json` indisponible (réseau, 404) → message « Recherche par code postal momentanément indisponible », la recherche par nom continue de marcher, aucune erreur console non gérée. Test en tâche 11.
5. Données de la nuit qui changent : député remplacé (ancien slug), thème disparu (`/votes/<clé inconnue>`), scrutin non clé (`/scrutin/1`) → page introuvable adaptée, jamais de page blanche. Tests en tâches 5 et 9.

---

## Structure des fichiers

| Fichier | Rôle |
|---|---|
| `src/prep.py` | Restructuré en fonctions ; `main()` garde le comportement actuel |
| `src/slug.py` | `slugify()` et `assign_slugs()` |
| `src/cp.py` | Construction de la table code postal → circonscription (fonctions pures) |
| `src/lexique.py` | Termes et définitions |
| `src/fetch.py` | + téléchargement des deux sources CP (non bloquant) |
| `src/template.html` | Squelette HTML avec marqueurs `__CSS__`, `__JS__`, `__DATA__` |
| `src/ui/*.css` | `base.css`, `layout.css`, `home.css`, `votes.css`, `scrutin.css`, `mobile.css` |
| `src/ui/*.js` | Ordre de concaténation fixé dans `prep.UI_JS` (tâche 3) |
| `nginx.conf`, `Dockerfile`, `.dockerignore` | Publication |
| `logos/*.svg|png`, `logos/SOURCES.md` | Logos sous licence libre |
| `tests/unit/` | pytest sur `prep`, `slug`, `cp`, `lexique`, contrastes |
| `tests/e2e/` | Playwright contre le conteneur nginx |
| `tests/run-unit.sh`, `tests/run-e2e.sh` | Lanceurs en conteneur |
| `data/cp.json`, `data/resumes-a-ecrire.md` | Générés |

---

# Étape 1 : adresses partageables

### Tâche 1 : lanceurs de tests en conteneur

**Fichiers :**
- Créer : `tests/run-unit.sh`, `tests/run-e2e.sh`, `tests/e2e/conftest.py`, `tests/e2e/test_smoke.py`, `tests/unit/test_placeholder.py` (supprimé en tâche 2)
- Modifier : `.dockerignore` (+ `tests`, `docs`, `.captures`), `.gitignore` (+ `.captures/`)

**Interfaces :**
- Produit : `tests/run-unit.sh [args pytest]`, `tests/run-e2e.sh [args pytest]` ; fixtures pytest `base_url` (str), `page_desktop`, `page_mobile` (pages Playwright à 1280×800 et 375×812, `has_touch=True` et `is_mobile=True` pour mobile) qui **échouent le test** sur tout message console de type `error` ou `pageerror` ; fonction `capture(page, etape: int, nom: str)` qui écrit `.captures/etape-<n>/<nom>-<largeur>.png` (page entière).

- [ ] **Étape 1 : écrire `run-unit.sh`** : `docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/w -w /w python:3.12-slim sh -c 'pip install -q --user pytest==8.3.3 && python -m pytest tests/unit "$@"' -- "$@"`.
- [ ] **Étape 2 : écrire `run-e2e.sh`** : `set -e` ; `python3 src/prep.py >/dev/null` ; `docker build -q -t ho-test-site .` ; `docker network create ho-test-net` ; `docker run -d --rm --name ho-test-site --network ho-test-net ho-test-site` ; `docker run --rm --network ho-test-net --user "$(id -u):$(id -g)" -e HOME=/tmp -e BASE_URL=http://ho-test-site -v "$PWD":/w -w /w mcr.microsoft.com/playwright/python:v1.48.0-jammy sh -c 'pip install -q --user pytest==8.3.3 pytest-playwright==0.5.2 && python -m pytest tests/e2e "$@"' -- "$@"` ; nettoyage (`docker stop ho-test-site`, `docker network rm ho-test-net`) dans un `trap … EXIT`.
- [ ] **Étape 3 : test de fumée** `test_accueil_sans_erreur(page_desktop, page_mobile)` : `goto(base_url + "/")` puis `expect(page.locator("h1")).to_be_visible()`.
- [ ] **Étape 4 : lancer** `tests/run-e2e.sh -q` → 2 passés (le site actuel sert `/` sans erreur). Lancer `tests/run-unit.sh -q` → 1 passé. `docker ps -a --filter name=ho-test` → vide.
- [ ] **Étape 5 : commit** « Tests : lanceurs pytest et Playwright en conteneur ».

### Tâche 2 : `prep.py` en fonctions + slugs des députés

**Fichiers :**
- Créer : `src/slug.py`, `tests/unit/test_slug.py`, `tests/unit/test_prep.py`, `tests/unit/conftest.py`
- Modifier : `src/prep.py`

**Interfaces :**
- Produit : `slug.slugify(s: str) -> str` ; `slug.assign_slugs(deputes: list[dict]) -> None` (ajoute `d["sl"]`) ; `prep.build_data(root: str) -> dict` (aucune écriture disque, renvoie le dict complet, aujourd'hui écrit dans `data/data.json`) ; `prep.render_index(data: dict, root: str) -> str` ; `prep.main()` (écrit `data/data.json` et `index.html` comme aujourd'hui). Fixture pytest `data` (scope session) = `prep.build_data(ROOT)`.

- [ ] **Étape 1 : tests**
```python
def test_slugify():
    assert slugify("Antoine Golliot") == "antoine-golliot"
    assert slugify("Marie-Noëlle Battistel") == "marie-noelle-battistel"
    assert slugify("Jean-Philippe  d'Artagnan") == "jean-philippe-d-artagnan"
def test_collision_suffixe_departement():
    deps=[{"p":"Jean","n":"Martin","nd":"01"},{"p":"Jean","n":"Martin","nd":"2A"}]
    assign_slugs(deps); assert [d["sl"] for d in deps]==["jean-martin-01","jean-martin-2a"]
def test_slugs_uniques(data):
    sl=[d["sl"] for d in data["deputes"]]; assert len(sl)==len(set(sl))>=500
def test_build_data_identique_a_avant(data):  # non-régression
    old=json.load(gzip.open("tests/unit/fixtures/data-avant.json.gz"))  # sortie de l'ancien prep.py
    for k in ("votes","groups","dos","quiz"): assert data[k]==old[k]
```
Pour le dernier test : avant de modifier `prep.py`, exécuter l'ancien `prep.py` et compresser `data/data.json` dans `tests/unit/fixtures/data-avant.json.gz` (la comparaison lit ce fichier).
- [ ] **Étape 2 : lancer** `tests/run-unit.sh -q` → échecs (import).
- [ ] **Étape 3 : implémenter** `slug.py` (NFD, suppression des diacritiques, minuscules, `[^a-z0-9]+` → `-`, `strip('-')` ; en cas de collision, **tous** les homonymes reçoivent le suffixe département en minuscules) ; découper `prep.py` sans changer sa logique, appeler `assign_slugs` dans `build_data`.
- [ ] **Étape 4 : lancer** les tests → tous passent ; `python3 src/prep.py` → `index.html regénéré` ; `git diff --stat index.html` ne montre que l'ajout des `sl`.
- [ ] **Étape 5 : commit** « prep.py : fonctions testables et adresses des députés ».

### Tâche 3 : découpage du gabarit

**Fichiers :**
- Créer : `src/ui/*.css`, `src/ui/*.js` (contenu actuel de `template.html` déplacé, sans changement de comportement)
- Modifier : `src/template.html`, `src/prep.py`, `tests/unit/test_prep.py`

**Interfaces :**
- Produit : `prep.UI_CSS: list[str]` et `prep.UI_JS: list[str]` (noms de fichiers dans `src/ui/`, ordre d'insertion). Ordre initial JS : `core.js` (constantes, `D`, `G`, `deps`, `votes`, helpers `esc`, `fdate`, `vTitle`, `norm`…), `popups.js`, `hemicycle.js`, `groupes.js`, `recherche.js`, `fiche.js`, `votes.js`, `jeux.js`, `start.js`. `render_index` insère les CSS concaténés à `__CSS__` et les JS concaténés dans `(function(){\n…\n})();` à `__JS__`.

- [ ] **Étape 1 : test** `test_index_complet(data)` : `html = render_index(data, ROOT)` → aucun de `__CSS__`, `__JS__`, `__DATA__` dans `html` ; `html.count("<script>") == 1` ; `"function openDep" in html`.
- [ ] **Étape 2 : lancer** → échec.
- [ ] **Étape 3 : déplacer** le CSS et le JS, ajouter les marqueurs.
- [ ] **Étape 4 : lancer** unit + `tests/run-e2e.sh -q` → tout passe (le site se comporte comme avant).
- [ ] **Étape 5 : commit** « Gabarit découpé en fichiers src/ui, assemblés par prep.py ».

### Tâche 4 : nginx, Dockerfile, logos

**Fichiers :**
- Créer : `nginx.conf`, `logos/SOURCES.md`, `logos/<SIGLE>.svg|png`, `tests/e2e/test_serveur.py`
- Modifier : `Dockerfile`, `.dockerignore`, `src/prep.py` (liste des logos), `src/ui/core.js` (`groupBadge`)

**Interfaces :**
- Produit : `data["logos"]: dict[str, str]` = sigle court → chemin absolu (`{"RN": "/logos/RN.svg"}`), construit par `prep` à partir des fichiers présents dans `logos/`. `groupBadge` n'ajoute `<img>` que si le sigle est dans `D.logos`.

- [ ] **Étape 1 : tests** (`test_serveur.py`, via `urllib`/`page.request`) :
  - `/depute/antoine-golliot`, `/votes/sante`, `/nimporte/quoi` → 200, `content-type` `text/html`, même corps que `/` ;
  - `/logos/absent.png`, `/absent.js` → 404 ;
  - `/` avec `Accept-Encoding: gzip` → `content-encoding: gzip` ; `cache-control` contient `no-cache` ;
  - `/logos/<un logo présent>` → 200, `cache-control` contient `max-age=604800`.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : écrire `nginx.conf`** : `location ~ \.[a-zA-Z0-9]+$ { try_files $uri =404; }`, `location / { try_files $uri $uri/ /index.html; add_header Cache-Control "no-cache"; }`, `location /logos/ { add_header Cache-Control "public, max-age=604800"; }`, `location = /cp.json { add_header Cache-Control "public, max-age=3600"; }`, `gzip on; gzip_types text/css application/javascript application/json image/svg+xml;` (text/html est compressé par défaut), `gzip_min_length 1024`. Dockerfile : copie `nginx.conf` en `/etc/nginx/conf.d/default.conf`, `index.html`, `logos/`.
- [ ] **Étape 4 : logos** : pour chaque groupe (hors NI), chercher sur Wikimedia Commons (API `https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata`) le logo du **groupe parlementaire** (à défaut, ne rien prendre). Ne garder que les licences `Public domain`, `PD-textlogo`, `CC0`, `CC BY`, `CC BY-SA` ; noter dans `SOURCES.md` : sigle, page Commons, auteur, licence, date. Télécharger avec un `User-Agent` générique (`hemicycle-ouvert/1.0`), pas d'adresse personnelle.
- [ ] **Étape 5 : lancer** unit + e2e → tout passe ; capture de l'accueil montrant les logos.
- [ ] **Étape 6 : commit** « nginx : repli vers index.html, gzip, cache court ; logos des groupes ».

### Tâche 5 : routeur, navigation à 4 entrées, page introuvable, anciennes ancres, titres

**Fichiers :**
- Créer : `src/ui/router.js`, `src/ui/introuvable.js`, `tests/e2e/test_routes.py`
- Modifier : `src/template.html` (nav), `src/ui/start.js`, `src/ui/votes.js`, `src/ui/groupes.js`, `src/ui/jeux.js`, `src/ui/layout.css`

**Interfaces :**
- Produit (dans `router.js`) :
  - `route(path: string) -> {view: string, params: object}` avec `view` ∈ `home|depute-liste|depute|votes|scrutin|comprendre|groupes|groupe|lexique|jouer|devine|quiz|introuvable` ; normalise (décodage, minuscules, suppression de la barre finale, de `?…`) ;
  - `navigate(path: string, {replace?: bool}) -> void` (pushState/replaceState puis rendu) ;
  - `registerView(name: string, render: (params) => {title: string, description: string} | null)` : un rendu qui renvoie `null` déclenche la vue introuvable ;
  - `setMeta({title, description})` : met à jour `document.title` (`<titre> · Hémicycle ouvert`), `meta[name=description]`, `og:title`, `og:description`, `og:url`, `link[rel=canonical]` (créés s'ils manquent) ;
  - interception des clics sur `a[href^="/"]` sans modificateur ni `target`.
- Vues de l'étape 1 : `home` = vue hémicycle actuelle (remplacée en tâche 7) ; `votes` et `votes/<thème>` = liste actuelle avec `fCat` ; `scrutin/<n>` = provisoire : liste des votes avec ce vote déplié (`gotoVote`) ; `comprendre` = hémicycle ; `groupes` et `groupes/<sigle>` = vues groupes actuelles ; `jouer` = les deux cartes de jeux ; `devine`, `quiz` = jeux actuels ; `lexique` = page « Lexique » vide avec un `<h1>` (remplie en tâche 12) ; `depute-liste` = recherche + liste des députés par département (`<h1>Mon député</h1>`).
- Navigation : `<nav aria-label="Navigation principale">` avec 4 liens : `/depute` « Mon député », `/votes` « Les décisions », `/comprendre` « Comprendre », `/jouer` « Jouer » ; `aria-current="page"` sur l'entrée active ; le titre « Hémicycle ouvert » renvoie à `/`.

- [ ] **Étape 1 : tests** (`test_routes.py`, desktop) :
  - chaque adresse du tableau § 5.1 ouverte directement → `h1` attendu visible, `document.title` se termine par `· Hémicycle ouvert`, `og:title` égal au titre sans le suffixe ;
  - `/votes/sante` → filtre « Santé » actif ; `/votes/` et `/votes/sante?utm_source=x` → même vue que sans (vigilance 2) ;
  - `/depute/inexistant`, `/votes/inconnu`, `/groupes/xyz`, `/n/importe/quoi` → `h1` « Page introuvable », champ « Trouver mon député » présent (vigilance 5) ;
  - `/#votes` → URL finale `/votes` ; `/#jeu` → `/jouer/devine` ; `/#questionnaire` → `/jouer/groupe` ;
  - clic sur « Les décisions » puis `go_back()` → URL `/`, puis `go_forward()` → `/votes` ;
  - clic droit / `ctrl+clic` non intercepté : l'attribut `href` des 4 entrées est l'adresse absolue.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter.** Au chargement : si `location.hash` correspond à une ancienne ancre, `navigate(nouvelle, {replace:true})` ; sinon rendu de `location.pathname`. Après rendu : `scrollTo(0,0)` sauf sur `popstate`, focus sur le `h1` de la vue (`tabindex="-1"`). Ne plus lire `ho-tab` au démarrage.
- [ ] **Étape 4 : lancer** e2e + unit → tout passe.
- [ ] **Étape 5 : commit** « Adresses partageables : routeur, navigation, page introuvable, anciennes ancres ».

### Tâche 6 : fiche député liée à son adresse

**Fichiers :**
- Modifier : `src/ui/fiche.js`, `src/ui/router.js`
- Créer : `tests/e2e/test_fiche.py`

**Interfaces :**
- Consomme : `navigate`, `registerView` (tâche 5), `d.sl` (tâche 2).
- Produit : `openDep(i: number, {fromRoute?: bool})` ouvre le panneau et, sauf `fromRoute`, fait `navigate('/depute/'+sl)` ; `closeDep()` : si l'entrée d'historique précédente est sur le site (drapeau `history.state.inApp`), `history.back()`, sinon `navigate('/depute', {replace:true})`. Titre : « Prénom Nom, député(e) de <département> » (« députée » si `c==='Mme'`).

- [ ] **Étape 1 : tests**
  - nouvel onglet (`context.new_page()`) sur `/depute/antoine-golliot` → `#sheet` visible, `h3` « Antoine Golliot », titre de page commençant par « Antoine Golliot » ;
  - même chose avec `/depute/Antoine-Golliot/` (vigilance 1) ;
  - ouverture directe puis clic sur « Fermer » → URL `/depute`, toujours sur le site (vigilance 3) ;
  - depuis `/comprendre`, clic sur un siège → URL `/depute/<slug>` ; `go_back()` → `/comprendre`, panneau fermé ; `go_forward()` → panneau rouvert ;
  - Échap ferme le panneau et restaure le focus.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** (vue `depute` = vue `depute-liste` en fond + `openDep(i,{fromRoute:true})` ; slug inconnu → `null` → introuvable).
- [ ] **Étape 4 : lancer** → tout passe.
- [ ] **Étape 5 : commit** « Fiche député : adresse /depute/<nom>, Retour et nouvel onglet ».

### Tâche 6 bis : compte rendu de l'étape 1

- [ ] Script `tests/e2e/test_captures.py::test_captures_etape` paramétré par `ETAPE` (variable d'environnement) : captures à 1280 et 375 px des vues `/`, `/depute/antoine-golliot`, `/votes/sante`, `/scrutin/<dernier>`, `/depute/inexistant`, `/jouer/devine`.
- [ ] `ETAPE=1 tests/run-e2e.sh -q` → tout passe ; copier `.captures/etape-1/` dans le dossier de travail temporaire ; compte rendu au propriétaire (tests passés, captures, ce qui reste provisoire). **Attendre son retour avant l'étape 2.**

---

# Étape 2 : accueil et mobile

### Tâche 7 : nouvel accueil

**Fichiers :**
- Créer : `src/ui/home.js`, `src/ui/home.css`, `src/ui/composants.js`, `tests/e2e/test_accueil.py`
- Modifier : `src/template.html`, `src/ui/start.js`

**Interfaces :**
- Produit (`composants.js`, réutilisés en étape 3) :
  - `resultSentence(v) -> string` : `"Adopté : 312 pour, 210 contre, 40 abstentions."` / `"Rejeté : …"` (singulier « 1 abstention ») ;
  - `voteCard(v, {compact?: bool}) -> string` : `<a class="vcard" href="/scrutin/<n>">` avec badge ADOPTÉ/REJETÉ, date, thème, type, titre, « En bref » (via `summaryOf`), `barHTML`, `resultSentence` ;
  - `groupsBar() -> string` : barre horizontale des groupes (ordre `groupsOrdered`, largeur ∝ sièges), légende en liens `/groupes/<sigle>`, phrase « Majorité absolue : M sièges. Aucun groupe ne l'atteint seul. » avec `M = Math.floor(577/2)+1` et la seconde phrase seulement si vraie ;
  - `searchBox(id: string, {mode: 'depute'|'vote', vote?: v}) -> string` + `bindSearch(id)` (recherche par nom/département actuelle ; étendue en tâche 11).
- Accueil (§ 5.4) dans l'ordre exact de la spec ; `N` = nombre réel de députés.
- `/comprendre` reçoit aussi `groupsBar()` au-dessus de l'hémicycle, et les liens « Les 12 groupes » et « Lexique » (§ 5.9).

- [ ] **Étape 1 : tests** : sur `/` (desktop et mobile), `h1` = « Ce que fait votre Assemblée, en clair. » ; 3 cartes `.vcard` dont le `href` commence par `/scrutin/` ; la première contient la phrase de résultat exacte du vote le plus récent (calculée dans le test à partir de `D` lu via `page.evaluate("JSON.parse(document.getElementById('data').textContent).votes[0]")`) ; 12 segments dans la barre des groupes ; liens « Explorer l'hémicycle interactif » → `/comprendre`, « Les 12 groupes » → `/groupes`, « Lexique » → `/lexique` ; section « Jouer » avec 2 cartes `/jouer/devine` et `/jouer/groupe` ; à 375 px aucun `svg.hemi` visible et un lien « Voir les N députés en liste » → `/depute`.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter.**
- [ ] **Étape 4 : lancer** → tout passe.
- [ ] **Étape 5 : commit** « Accueil : recherche, dernières décisions, Assemblée en un coup d'œil, jeux ».

### Tâche 8 : mobile (barre basse, cibles tactiles, textes tactiles)

**Fichiers :**
- Créer : `src/ui/mobile.css`, `tests/e2e/test_mobile.py`
- Modifier : `src/template.html` (icônes SVG intégrées dans la nav), `src/ui/hemicycle.js`, `src/ui/layout.css`

**Interfaces :** aucune nouvelle ; la même `<nav>` devient barre fixe en bas sous 760 px.

- [ ] **Étape 1 : tests** (375×812, tactile) sur `/`, `/votes`, `/comprendre`, `/depute/antoine-golliot`, `/jouer/devine` :
  - nav fixe visible en bas (`position: fixed`, `bottom` ≤ 0 + safe-area), 4 liens avec icône et libellé ;
  - `document.documentElement.scrollWidth <= 375` ;
  - tout élément visible `a, button, input, select, [role=button]` a une boîte ≥ 44×44 px (exceptions : liens dans un paragraphe de texte courant, listés explicitement dans le test) ;
  - `page.content()` ne contient pas « Survolez » ; `/comprendre` affiche « Touchez un siège pour ouvrir la fiche du député. » ;
  - le dernier élément de `main` n'est pas masqué par la barre (son bas ≤ haut de la nav après défilement complet).
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** (textes d'aide choisis par `matchMedia('(hover: none)')` au rendu).
- [ ] **Étape 4 : lancer** → tout passe, aussi à 1280 px.
- [ ] **Étape 5 : commit** « Mobile : barre de navigation en bas, cibles de 44 px, textes tactiles ».
- [ ] **Étape 6 : compte rendu de l'étape 2** (`ETAPE=2`), **attendre le retour.**

---

# Étape 3 : pages de vote

### Tâche 9 : page `/scrutin/<numéro>`

**Fichiers :**
- Créer : `src/ui/scrutin.js`, `src/ui/scrutin.css`, `tests/e2e/test_scrutin.py`
- Modifier : `src/ui/votes.js` (cartes en liens, suppression du dépliage), `src/ui/fiche.js`, `src/ui/groupes.js`, `src/ui/jeux.js` (titres de votes → `/scrutin/<n>`, `gotoVote` supprimé)

**Interfaces :**
- Consomme : `voteCard`, `resultSentence`, `searchBox(…, {mode:'vote', vote})`, `barHTML`, `drawHemi`, `summaryOf`.
- Produit : vue `scrutin` ; `depVoteText(v, d) -> string` ∈ « Pour », « Contre », « Abstention », « N'a pas pris part au vote », « Pas encore député à cette date » (`v.dt < d.d`) ; « députée » au féminin.

- [ ] **Étape 1 : tests** sur le vote le plus récent et sur une motion de censure :
  - fil d'Ariane « Les décisions › <Thème> » avec lien `/votes/<clé>` ;
  - encadré : texte ADOPTÉ ou REJETÉ, chiffres = `v.sy`, phrase exacte « Seuls les députés présents votent : N ont pris part à ce vote. » avec `N = sum(v.sy)` ;
  - « De quoi s'agit-il ? » présent ; « Comment chaque groupe a voté » : une ligne par groupe de `v.gv`, dans l'ordre de l'hémicycle, avec le sigle, le nom complet, la position et les 3 nombres ;
  - motion de censure : la phrase sur les 289 voix est présente ;
  - recherche « Et mon député, qu'a-t-il voté ? » : saisir « Golliot », choisir → texte attendu = `depVoteText` calculé dans le test depuis `v.v[i]` ;
  - bouton « Copier le lien de ce vote » (contexte avec permission `clipboard-write`) → presse-papiers = `BASE_URL/scrutin/<n>` et message « Lien copié » dans une zone `aria-live` ;
  - liens externes : scrutin sur assemblee-nationale.fr, dossier législatif si `v.dr` ;
  - `/scrutin/1` (non clé) → « Ce scrutin ne fait pas partie des votes clés suivis ici » + lien officiel (vigilance 5) ;
  - `/votes` : chaque carte est un `<a href="/scrutin/…">` ; clic → page du vote ; `go_back()` → `/votes` avec le même filtre de thème.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** (mise en page deux colonnes ≥ 960 px, une colonne en dessous ; titre de page « Scrutin n° <n> : <titre court> »).
- [ ] **Étape 4 : lancer** → tout passe.
- [ ] **Étape 5 : commit** « Page complète pour chaque vote clé ; cartes de vote cliquables ».
- [ ] **Étape 6 : compte rendu de l'étape 3** (`ETAPE=3`), **attendre le retour.**

---

# Étape 4 : recherche par code postal

### Tâche 10 : table code postal → circonscription

**Fichiers :**
- Créer : `src/cp.py`, `tests/unit/test_cp.py`, `tests/unit/fixtures/laposte-extrait.csv`, `tests/unit/fixtures/bureaux-extrait.csv`
- Modifier : `src/fetch.py` (`main()` : étape « Codes postaux » non bloquante), `Dockerfile` (copie `data/cp.json` en `/usr/share/nginx/html/cp.json`), `.dockerignore` (`data` exclu sauf `!data/cp.json`)

**Interfaces :**
- Produit :
  - `cp.LAPOSTE_URL = "https://data.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw"` ; `cp.BUREAUX_DATASET = "liste-des-bureaux-de-vote-associes-a-leur-circonscription-legislative"` (URL de la ressource lue via `https://www.data.gouv.fr/api/1/datasets/<id>/`) ;
  - `cp.parse_laposte(raw: bytes) -> list[tuple[insee, nom, cp]]` (latin-1, séparateur `;`, en-tête ignorée) ;
  - `cp.parse_bureaux(raw: bytes) -> list[tuple[insee, numero_bureau, code_circo]]` (UTF-8, colonnes `codeCommune`, `numeroBureauVote`, `codeCirconscription`) ;
  - `cp.build_table(laposte, bureaux) -> dict[str, list[list]]` au format `{cp: [[nom_commune, [code_circo, …]], …]}`, noms de commune en casse normale si disponibles (sinon libellé La Poste) ;
  - `cp.circo_key(code_circo: str) -> tuple[str, int]` : `"2401"` → `("24", 1)`, `"2A01"` → `("2A", 1)`, `"9741"` → `("974", 1)` (DROM et COM : 3 caractères de département), à vérifier contre les `nd`/`ci` des députés.
- Règles (§ 5.6) : PLM (Paris 751xx → 75056, Marseille 132xx → 13055, Lyon 6938x → 69123) : arrondissement = 2 premiers chiffres du numéro de bureau pour Paris et Marseille ; pour Lyon, vérifier sur les données, sinon toutes les circonscriptions de la commune ; commune absente → toutes les circonscriptions du département.

- [ ] **Étape 1 : tests** (fixtures réduites tirées des vrais fichiers, + un test « réel » marqué `@pytest.mark.reseau`, lancé une fois avec `-m reseau`, qui télécharge les deux sources) :
  - `build_table` : `"24200"` → 8 communes, union des circonscriptions == `{"2401","2404"}` ;
  - `"75011"` → `[["Paris 11e arrondissement" ou libellé, ["7506","7507"]]]` ;
  - `"31000"` → Toulouse avec plus d'une circonscription ;
  - `circo_key` sur les 3 formes ;
  - (réseau) ≥ 99 % des codes postaux de départements `01`–`95`, `2A`, `2B`, `971`–`976` ont au moins une circonscription ; chaque `circo_key` de la table correspond à un `(nd, ci)` présent dans `an-data.json.gz` ou à un siège vacant connu (liste imprimée).
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** `cp.py` ; dans `fetch.py`, `update_cp()` appelée dans un `try/except` qui journalise « codes postaux indisponibles (…) — on garde la table précédente » ; écriture atomique (`.tmp` puis `os.replace`) de `data/cp.json` (JSON compact).
- [ ] **Étape 4 : lancer** unit (+ `-m reseau` une fois) → passe ; `python3 src/fetch.py` (réseau réel) se termine sans erreur ; `data/cp.json` < 1,5 Mo.
- [ ] **Étape 5 : commit** « fetch.py : table code postal → circonscription (La Poste, data.gouv) ».

### Tâche 11 : recherche par code postal et par ville

**Fichiers :**
- Modifier : `src/ui/recherche.js` (ou `composants.js` si `searchBox` y est), `src/ui/composants.js`
- Créer : `tests/e2e/test_cp.py`

**Interfaces :**
- Consomme : `/cp.json` (format tâche 10), `circo_key` re-codée en JS (`circoKey(code) -> [nd, ci]`).
- Produit : `loadCP() -> Promise<object|null>` (une seule requête, mémorisée ; `null` si échec) ; résultats affichés « Commune · 4e circonscription de la Dordogne → Prénom Nom (sigle) » ou « … → Siège vacant actuellement ».

- [ ] **Étape 1 : tests**
  - `/` : saisir `24200` → au moins 2 choix (1re et 4e circonscription de la Dordogne), clic sur l'un → `/depute/<slug>` du député de `nd=24`, `ci` correspondant ;
  - `75011` → exactement 2 choix (6e et 7e de Paris) ;
  - `31000` → plusieurs choix ;
  - `sarlat` → la commune « Sarlat-la-Canéda » apparaît avec son député ;
  - code postal inconnu `00000` → « Aucune commune pour ce code postal » ;
  - route `/cp.json` interceptée (`page.route` → 503) puis saisie `24200` → message « Recherche par code postal momentanément indisponible », recherche « Golliot » toujours fonctionnelle, aucune erreur console (vigilance 4 ; le `console.error` ne doit pas être émis : utiliser `console.warn` au plus) ;
  - navigation clavier : flèche bas puis Entrée ouvre le premier résultat ; une zone `aria-live` annonce « N résultats ».
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** (chargement de `/cp.json` au premier focus du champ).
- [ ] **Étape 4 : lancer** → tout passe.
- [ ] **Étape 5 : commit** « Recherche du député par code postal et par ville ».
- [ ] **Étape 6 : compte rendu de l'étape 4** (`ETAPE=4`, captures de `24200` et `75011` à 375 et 1280 px), **attendre le retour.**

---

# Étape 5 : lexique, vocabulaire, résumés

### Tâche 12 : lexique et vocabulaire

**Fichiers :**
- Créer : `src/lexique.py`, `src/ui/lexique.js`, `tests/unit/test_lexique.py`, `tests/e2e/test_lexique.py`
- Modifier : `src/prep.py` (`data["lex"]`), `src/ui/popups.js` (`KIND_NOTE`, `lecNote`, aide Transparence lisent le lexique), `src/ui/groupes.js`, `src/ui/fiche.js`, `src/ui/scrutin.js`, `src/ui/composants.js`

**Interfaces :**
- Produit : `lexique.TERMES: list[dict]` avec `id` (ancre, slug), `terme`, `definition` (1 ou 2 phrases), `formes` (variantes détectées, minuscules) ; `data["lex"] = [[id, terme, definition, formes], …]` ; JS `lex(id) -> {terme, definition}` et `termLink(texte, id) -> string` (`<a class="lex" href="/lexique#<id>">`).
- Termes (au moins, ids fixés) : `scrutin-public`, `scrutin-solennel`, `motion-de-censure`, `motion-de-rejet`, `article-49-3`, `article-50-1`, `projet-de-loi`, `proposition-de-loi`, `proposition-de-resolution`, `lecture`, `nouvelle-lecture`, `lecture-definitive`, `commission-mixte-paritaire`, `amendement`, `groupe-politique`, `non-inscrit`, `majorite-absolue`, `abstention`, `non-votant`, `promulgation`, `expose-des-motifs`, `circonscription`, `deport`, `hatvp`, `vote-avec-son-groupe`.

- [ ] **Étape 1 : tests unitaires** : ids uniques et égaux à `slugify(terme)` sauf exceptions listées ; chaque définition fait 1 ou 2 phrases et ≤ 320 caractères ; aucune définition ne contient un mot interdit (contraintes globales) ; tous les ids ci-dessus présents.
- [ ] **Étape 2 : tests e2e** : `/lexique` liste les termes par ordre alphabétique (`localeCompare('fr')`) ; `/lexique#motion-de-censure` fait défiler jusqu'au terme ; page de vote d'un projet de loi : le type « Projet de loi » est un lien vers `/lexique#projet-de-loi` ; `/groupes` et la fiche : le texte « Vote avec son groupe » est présent ; dans `index.html` (sans les données), aucune occurrence de « cohésion », « Fidélité », « fidélité ».
- [ ] **Étape 3 : lancer** → échecs.
- [ ] **Étape 4 : implémenter.** Rédiger les définitions de façon factuelle (procédure, effet juridique, seuils) ; s'appuyer sur la Constitution et le règlement de l'Assemblée ; pas d'exemple tiré d'un groupe ou d'un vote réel.
- [ ] **Étape 5 : lancer** → tout passe.
- [ ] **Étape 6 : commit** « Lexique de 25 termes ; « Vote avec son groupe » remplace cohésion et fidélité ».

### Tâche 13 : résumés inutilisables et rapport

**Fichiers :**
- Modifier : `src/prep.py`, `src/ui/popups.js`, `src/ui/composants.js`, `src/ui/scrutin.js`
- Créer : `tests/unit/test_resumes.py`

**Interfaces :**
- Produit : `prep.resume_inutilisable(expo_extrait: str|None, longueur_origine: int) -> str|None` (renvoie la raison : `"commence par ARTICLE"`, `"liste d'articles"`, `"trop long"`, ou `None`) ; drapeau source `3` dans `data["dos"][k][3]` = « résumé à venir » (texte vidé) ; `prep.write_rapport(data, path)` → `data/resumes-a-ecrire.md` (tableau : clé dossier, titre, scrutins, lien officiel `https://www.assemblee-nationale.fr/dyn/17/dossiers/<dr>`, raison), trié par date du dernier scrutin décroissante.
- Interface : drapeau 3 ou pas de texte → « Résumé à venir » + lien « Lire le texte officiel » (dossier législatif).

- [ ] **Étape 1 : tests** : `resume_inutilisable("ARTICLE 1er. Le code…", 80) == "commence par ARTICLE"` ; `"Article premier …"` idem ; un extrait contenant au moins deux occurrences de `\bArticle \d+|\bArticle premier` → `"liste d'articles"` ; longueur d'origine > 280 → `"trop long"` ; une phrase normale de 150 caractères → `None` ; sur les données réelles, chaque dossier en drapeau 2 est soit gardé soit marqué 3, et `data/resumes-a-ecrire.md` liste exactement les dossiers marqués 3.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter** (`auto_resume` renvoie aussi la longueur d'origine de la phrase choisie).
- [ ] **Étape 4 : lancer** unit + e2e (page de vote d'un dossier marqué 3 → « Résumé à venir » et le lien) → tout passe.
- [ ] **Étape 5 : commit** « Résumés : « Résumé à venir » au lieu des extraits inutilisables, rapport data/resumes-a-ecrire.md ».
- [ ] **Étape 6 : compte rendu de l'étape 5** avec la liste complète des définitions du lexique et le rapport des résumés, **attendre la relecture.**

---

# Étape 6 : accessibilité

### Tâche 14 : liste alternative de l'hémicycle, repères, clavier

**Fichiers :**
- Modifier : `src/template.html` (lien d'évitement, repères), `src/ui/hemicycle.js`, `src/ui/fiche.js` (piège à focus), `src/ui/composants.js`
- Créer : `tests/e2e/test_a11y.py`

**Interfaces :** `renderHemiList() -> string` : députés groupés par groupe (ordre de l'hémicycle), `<h3>` par groupe (« <Nom complet> · N sièges »), `<ul>` de liens `/depute/<slug>`.

- [ ] **Étape 1 : tests**
  - `/comprendre` : bouton « Afficher en liste » (`aria-expanded`) ; au clavier seul (Tab, Entrée) on ouvre la liste puis la fiche d'un député ;
  - `page.accessibility.snapshot()` : la liste contient autant de liens que de députés ; le SVG a un nom accessible décrivant la répartition ;
  - chaque vue : un seul `h1`, un `main`, une `nav` nommée ; premier Tab → lien « Aller au contenu » ;
  - fiche ouverte : Tab répété ne sort jamais du dialogue ; Échap ferme et rend le focus ;
  - `prefers-reduced-motion: reduce` (émulé) : aucune transition > 0 s sur les éléments animés.
- [ ] **Étape 2 : lancer** → échecs.
- [ ] **Étape 3 : implémenter.**
- [ ] **Étape 4 : lancer** → tout passe.
- [ ] **Étape 5 : commit** « Accessibilité : liste de l'hémicycle, lien d'évitement, focus dans la fiche ».

### Tâche 15 : contrastes

**Fichiers :**
- Modifier : `src/ui/base.css` (jetons), feuilles qui utilisent `--abst` pour du texte
- Créer : `tests/unit/test_contraste.py`, `tests/e2e/test_contraste.py`

**Interfaces :** nouveau jeton `--abst-ink` (texte « abstention ») dans les trois blocs de thème ; `--abst` reste pour les barres et pastilles.

- [ ] **Étape 1 : tests**
  - unitaire : lit les jetons des trois blocs de `base.css` et vérifie un ratio ≥ 4,5 pour `--ink`, `--muted`, `--accent`, `--pour`, `--contre`, `--abst-ink` sur `--bg`, `--surface`, `--surface-2`, dans chaque thème (aujourd'hui en échec : `--abst` clair 2,95, `--accent` sombre sur `--surface-2` 4,32) ; `textColorOn` donne ≥ 4,5 sur les 12 couleurs de groupe (sinon on ajuste la fonction pour choisir la couleur au meilleur contraste) ;
  - e2e : sur `/`, `/scrutin/<n>`, `/depute/antoine-golliot` en `color_scheme` clair et sombre, pour chaque nœud de texte visible, ratio calculé entre `color` et le premier fond opaque des ancêtres ≥ 4,5 (texte ≥ 24 px ou ≥ 18,66 px gras : ≥ 3) ; la liste des échecs est affichée dans le message d'erreur.
- [ ] **Étape 2 : lancer** → échecs attendus.
- [ ] **Étape 3 : ajuster** les jetons au plus près des teintes actuelles (même teinte, luminosité modifiée).
- [ ] **Étape 4 : lancer** tous les tests (unit + e2e) → tout passe.
- [ ] **Étape 5 : commit** « Contrastes : au moins 4,5:1 dans les deux thèmes ».

### Tâche 16 : vérification finale et préparation de la fusion

- [ ] Test de neutralité e2e : texte visible de `/`, `/votes`, une page de vote, `/groupes`, `/lexique`, une fiche → aucun mot interdit (contraintes globales), hors titres officiels des textes (exclus via l'attribut `data-officiel` sur les titres).
- [ ] `python3 src/fetch.py && python3 src/prep.py` sur la branche → succès ; `git status` ne montre que `data/` et `index.html` modifiés (comme l'updater).
- [ ] Suite complète : `tests/run-unit.sh` et `ETAPE=6 tests/run-e2e.sh` → tout passe, zéro erreur console ; `docker ps -a --filter name=ho-test` vide.
- [ ] Mise à jour du `README.md` (adresses, `cp.json`, lexique, rapport des résumés, tests).
- [ ] Commit « README : adresses, recherche par code postal, lexique, tests ».
- [ ] Compte rendu final avec captures et procédure de fusion (§ 7 bis de la spec : étiquette `avant-refonte`, `git merge --no-ff`, `index.html` régénéré par `prep.py` après la fusion). **Aucune fusion ni push sur `main` sans accord.**
