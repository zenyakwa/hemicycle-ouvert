import re
from slug import slugify

IDS = ["scrutin-public", "scrutin-solennel", "motion-de-censure", "motion-de-rejet", "article-49-3", "article-50-1",
       "projet-de-loi", "proposition-de-loi", "proposition-de-resolution", "lecture", "nouvelle-lecture",
       "lecture-definitive", "commission-mixte-paritaire", "amendement", "groupe-politique", "non-inscrit",
       "majorite-absolue", "abstention", "non-votant", "promulgation", "expose-des-motifs", "circonscription",
       "deport", "hatvp", "vote-avec-son-groupe"]
INTERDITS = ["large", "écrasant", "serré", "victoire", "défaite", "surprise", "fidèle", "fidélité", "frondeur", "discipliné", "cohésion"]
EXCEPTIONS = {"article-50-1"}


def termes():
    import lexique
    return lexique.TERMES


def test_ids_attendus_et_uniques():
    ids = [t["id"] for t in termes()]
    assert len(ids) == len(set(ids))
    assert set(IDS) <= set(ids)
    for t in termes():
        if t["id"] not in EXCEPTIONS:
            assert t["id"] == slugify(t["terme"]), t["id"]


def test_definitions_courtes_et_neutres():
    for t in termes():
        d = t["definition"]
        phrases = [x for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÉÀ])", d.strip()) if x]
        assert 1 <= len(phrases) <= 2, t["id"]
        assert len(d) <= 320, (t["id"], len(d))
        mots = re.findall(r"[\wéèêàâîôûç-]+", d.lower())
        for m in INTERDITS:
            assert m not in mots, (t["id"], m)
        assert t["formes"] and all(f == f.lower() for f in t["formes"])


def test_lexique_dans_les_donnees(data):
    lex = data["lex"]
    assert [x[0] for x in lex] == [t["id"] for t in termes()]
    assert all(len(x) == 4 for x in lex)


def test_censure_seuil_exact():
    d = {t["id"]: t["definition"] for t in termes()}
    assert "majorité absolue des membres composant l'Assemblée" in d["motion-de-censure"]
    assert "au moins 289" not in d["motion-de-censure"]
    assert d["proposition-de-resolution"].startswith("Texte proposé")
