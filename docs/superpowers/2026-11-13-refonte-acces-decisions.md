# Refonte de l'accès : décisions prises pendant l'exécution

Extrait du journal d'exécution du plan `docs/superpowers/plans/2026-11-13-refonte-acces.md`. Chaque décision indique ce qu'elle coûte si elle se révèle mauvaise.

## Décisions

- - T7→T9/T11 : searchBox/bindSearch dans composants.js ; T11 dit « recherche.js ou composants.js ». Ruling: searchBox vit dans composants.js (T7 le définit là) — un seul composant (spec §5.5) — coût si faux : nul.
- Task 1: Ruling: le test de fumée échoue sur le site actuel (12+ erreurs console 404 : logos/<sigle>.png absents) alors que le plan attendait « 2 passés » — on garde la fixture stricte (c'est l'exigence « zéro erreur console ») ; le défaut est corrigé en tâche 4 (logos connus au build, pas de requête pour les absents) — coût si faux : nul, e2e rouge jusqu'à T4.
- Task 4: Ruling: 7 logos sur 11 (RN, DR, GDR, LIOT, UDR, EPR, ECOS) — SOC et LFI-NFP n'ont qu'un fichier non libre (fr.wikipedia), DEM et HOR aucun ; ils gardent le sigle — coût si faux : logos manquants, rien de cassé.
- Task 4: Ruling: data["logos"] = {sigle: [chemin, page Commons, licence]} (au lieu de {sigle: chemin}) pour afficher les crédits exigés par CC BY/BY-SA dans le pied de page — coût si faux : nul.
- Task 4: Ruling: logo ECOS en .webp (seul format fourni par Commons) — nginx le sert en image/webp.
- Task 5: Ruling: searchDeps/bindSearch/depLink/renderDepList créés dès T5 dans composants.js (besoin de la recherche sur /depute et la page introuvable) ; T7 les réutilise — coût si faux : nul.
- Task 5: Ruling: resultSentence(v) défini dans votes.js (utilisé par la description de /scrutin) ; T7 le réutilise au lieu de le recréer dans composants.js — coût : nul.
- Task 5: Ruling: accueil provisoire = h1 « Ce que fait votre Assemblée, en clair. » + date + grande recherche ; le reste de l'accueil en T7 — coût : nul.
- Task 5: Ruling: l'adresse non canonique (/Votes/Sante/, ?utm) est remplacée par sa forme canonique (replaceState) au chargement — URL propre à partager — coût : les paramètres utm disparaissent de la barre d'adresse.
- Task 5: Ruling: titres de fiche « Prénom Nom, député du/de la/des <département> » via deDep() (table d'articles) — coût si faux : un article erroné dans un titre.
- Task 6: Ruling: une fiche ouverte depuis le site garde la vue en cours en fond (pushState sans re-rendu) ; ouverte directement, fond = /depute — coût : nul.
- Task 7: Ruling: la barre des groupes n'est pas focalisable (segments aria-hidden) ; la légende porte les liens accessibles (sigle + sièges + nom complet) — évite 12 arrêts de tabulation en double — coût : nul.
- Task 8: Ruling: sur mobile (< 760 px), le slogan et le bloc de dates de l'en-tête sont masqués (la date des données reste sur l'accueil) — gagne un demi-écran — coût : la date n'est plus visible sur les autres pages mobiles.
- Task 8: Ruling: test des 44 px : liens dans du texte courant exclus (paragraphes, notes, pied de page, listes par département) comme prévu par le plan ; les boutons ⓘ gardent un rond de 22 px visuel dans une zone tactile de 44 px.
- Task 9: Ruling: bug existant corrigé — ORDER attendait le sigle « UDDPLR » alors que les données disent « UDR » : UDR était placé après les non-inscrits (tout à droite). Ajout de « UDR » entre DR et RN — coût si faux : ordre des sièges différent de l'intention d'origine.
- Task 9: Ruling: dans les listes de votes, plus de bouton ⓘ dans les cartes (bouton dans un lien = HTML invalide) ; le résumé est sur la page du vote et sur les cartes de l'accueil — coût : une info-bulle de moins dans la liste.
- Task 9: Ruling: copie du lien avec repli (textarea + execCommand) si l'API presse-papiers est indisponible ; dernier recours : afficher le lien à copier.
- Task 10: Ruling: 24200 → une seule circonscription (4e de la Dordogne) d'après la source officielle ; la spec et le plan disaient « 1re et 4e » (erreur de ma part au brainstorming) — spec corrigée ; T11 testera 24200 → député direct, et le choix multiple sur 75011 et 31000 — coût : nul.
- Task 10: Ruling: codes ZA…ZZ du ministère (outre-mer, Français de l'étranger) convertis vers 971…099 de l'AN ; Lyon : arrondissement = dernier chiffre du code INSEE 6938x et 2 premiers chiffres du n° de bureau (vérifié sur les données).
- Task 10: Ruling: garde-fou : table < 5 000 codes postaux = on garde l'ancienne (évite d'écrire une table tronquée).
- Task 11: Ruling: résultats d'un code postal regroupés par circonscription (« Code postal 24200 (8 communes) · 4e circonscription de la Dordogne → député ») — §5.5 « une seule circonscription : on propose directement le député » — coût : la liste des communes n'est pas détaillée au-delà de 2.
- Task 11: Ruling: la recherche « Et mon député » de la page de vote utilise le même composant (nom, ville, code postal).
- Task 12: Ruling: les info-bulles existantes (KIND_NOTE, lecNote, aide Transparence) lisent désormais leurs définitions dans le lexique (une seule source) — leur texte change légèrement — coût : nul.
- Task 12: Ruling: termes liés au lexique : type de texte et lecture (page de vote), abstention, motion de censure, majorité absolue (accueil, vote), vote avec son groupe (groupes). Pas de liens dans les cartes de vote (lien dans un lien interdit).
- Task 13: Ruling: drapeau 3 = « résumé à venir », raison en 5e position de l'entrée dos (lue par le rapport) ; un dossier sans extrait mais avec auteur/promulgation passe aussi en 3 (« pas d'extrait ») — coût : nul.
- Task 13: Ruling: le rapport a 3 sections : « Résumé à venir » (6), extraits automatiques gardés à relire (7), votes sans aucune donnée de dossier (1) — utile pour compléter resumes.py.
- Task 14: Ruling: liste « Voir le vote de chaque député en liste » (details) sur la page de vote, comptée sur les députés en exercice (v.v), d'où des effectifs qui peuvent différer de v.sy (députés partis depuis) — coût : un écart de quelques unités possible entre la liste et le résultat officiel ; le résultat officiel reste affiché en tête.
- Task 14: Ruling: le lien d'évitement est géré en JS (focus sur le h1 de la vue) pour ne pas déclencher de navigation par ancre.
- Task 15: Ruling: nouveaux jetons de texte --pour-ink, --contre-ink, --abst-ink (clair : #1F6941, #AB241D, #835707 ; sombre : #4CC283, #F37A75, #E9AE3C) pour les pastilles teintées ; barres et sièges gardent --pour/--contre/--abst. Accent sombre #E2566C → #E35F74 — coût : teintes de texte légèrement plus foncées en thème clair.
- Task 15: Ruling: textColorOn choisit désormais la couleur (blanc ou #111) au meilleur contraste (ECOS et NI passaient à 2,7 et 3,1 avec du blanc).
- Final: Ruling: M1 « Seuls les députés présents votent » (inexact : délégation de vote) — texte imposé par le propriétaire, conservé ; signalé dans le compte rendu — coût : phrase inexacte affichée.

## Corrections après la relecture finale

- I1 adresses accentuées — test_adresse_avec_accents RED→GREEN, suite 143/143 e2e + 29/29 unit
- I2 fermeture de fiche sans reconstruire la vue — test_fermer_la_fiche_garde_l_etat_de_la_page RED→GREEN
- I3 thèmes : tous les votes (filtre « Tous » par défaut) — test_theme_montre_tous_les_votes RED→GREEN
- I4 seuil de censure exact (rq par scrutin, formulation lexique) — test_seuil_de_la_censure + test_censure_seuil_exact RED→GREEN
- M3 (regradé important : licences CC BY) auteurs des logos dans les crédits — test_credits_des_logos_avec_auteur RED→GREEN
- M2 (regradé important : exactitude du lexique) proposition de résolution — test_censure_seuil_exact RED→GREEN
- M7 (regradé important : recherche CP cassée jusqu'au rechargement) — test_codes_postaux_nouvel_essai RED→GREEN
- (trouvé en corrigeant) test de non-régression qui aurait échoué après la 1re mise à jour nocturne — skip hors instantané.

## Points mineurs reportés

- M4 /index.html → page introuvable
- M5 /logos sans barre finale → 403 nginx
- M6 message dédié pour thème disparu / député remplacé
- M8 homonyme arrivant la nuit change l'adresse du député en place ; pas d'assertion d'unicité à la construction
- M9 délai total de téléchargement des codes postaux non borné
- M10 choix de la 1re ressource CSV du jeu data.gouv
- M11 « les 12 groupes » écrit en dur dans template.html
- M12 champ « formes » du lexique inutilisé
- M13 aria-label statique de la fiche
