import os, re
import prep


def test_regles():
    f = prep.resume_inutilisable
    assert f("ARTICLE 1er. Le code de la santé publique est ainsi modifié.", 80) == "commence par ARTICLE"
    assert f("Article premier : le code est modifié.", 60) == "commence par ARTICLE"
    assert f("Le texte modifie l'article 3 et crée un Article 4 bis ; Article 5 : abrogé.", 90) == "liste d'articles"
    assert f("Cette proposition de loi vise à simplifier les démarches.", 300) == "trop long"
    assert f("Cette proposition de loi vise à simplifier les démarches des communes rurales.", 150) is None
    assert f(None, 0) is None


def test_donnees_reelles(data, root, tmp_path):
    autos = {k: v for k, v in data["dos"].items() if v[3] in (2, 3)}
    assert autos
    for k, v in autos.items():
        if v[3] == 3:
            assert v[0] is None, k
        else:
            assert v[0] and not v[0].upper().startswith("ARTICLE") and not v[0].endswith("…"), k
    assert data["dos"]["17N55223"][3] == 3  # « ARTICLE liminaire : … »
    out = tmp_path / "resumes-a-ecrire.md"
    prep.write_rapport(data, str(out))
    txt = out.read_text(encoding="utf-8")
    marques = [k for k, v in data["dos"].items() if v[3] == 3]
    for k in marques:
        assert k in txt
    assert "https://www.assemblee-nationale.fr/dyn/17/dossiers/" in txt
