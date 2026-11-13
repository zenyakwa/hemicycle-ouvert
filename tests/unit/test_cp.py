import json, os
import pytest
import cp

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope="module")
def table():
    lp = cp.parse_laposte(open(os.path.join(FIX, "laposte-extrait.csv"), "rb").read())
    bv = cp.parse_bureaux(open(os.path.join(FIX, "bureaux-extrait.csv"), "rb").read())
    return cp.build_table(lp, bv)


def circos(table, code):
    return {c for _, cs in table[code] for c in cs}


def test_parse_laposte():
    lp = cp.parse_laposte(open(os.path.join(FIX, "laposte-extrait.csv"), "rb").read())
    assert ("24520", "SARLAT LA CANEDA", "24200") in lp


def test_24200(table):
    assert len(table["24200"]) == 8
    assert circos(table, "24200") == {"2404"}  # les 8 communes sont dans la 4e circonscription
    assert ["Sarlat-la-Canéda", ["2404"]] in table["24200"]


def test_paris_11(table):
    assert circos(table, "75011") == {"7506", "7507"}
    assert table["75011"][0][0] == "Paris 11e arrondissement"


def test_paris_16_deux_codes(table):
    assert circos(table, "75116") <= {"7504", "7514"} and circos(table, "75116")


def test_lyon_et_marseille_par_arrondissement(table):
    assert circos(table, "69003") == {"6903", "6904"}
    assert circos(table, "13001") == {"1304"}


def test_toulouse_plusieurs_choix(table):
    assert len(circos(table, "31000")) > 1


def test_corse_et_outre_mer(table):
    assert circos(table, "20000") <= {"2A01", "2A02"} and circos(table, "20000")
    assert all(c.startswith("ZA") for c in circos(table, "97100"))


def test_monaco_absent(table):
    assert "98000" not in table


def test_circo_key():
    assert cp.circo_key("2401") == ("24", 1)
    assert cp.circo_key("2A01") == ("2A", 1)
    assert cp.circo_key("ZA03") == ("971", 3)
    assert cp.circo_key("ZD07") == ("974", 7)
    assert cp.circo_key("ZX01") == ("977", 1)
    assert cp.circo_key("ZZ11") == ("099", 11)


@pytest.mark.reseau
def test_table_reelle(root):
    """Lancé à la main : tests/run-unit.sh -m reseau (télécharge les deux sources)."""
    import gzip
    lp = cp.parse_laposte(cp.download(cp.LAPOSTE_URL))
    bv = cp.parse_bureaux(cp.download(cp.bureaux_url()))
    t = cp.build_table(lp, bv)
    metro = {c for _, _, c in lp if c[:2] not in ("98",) and not c.startswith("97") or c[:3] in ("971", "972", "973", "974", "976")}
    couverts = sum(1 for c in metro if c in t)
    assert couverts / len(metro) >= 0.99, (couverts, len(metro))
    d = json.load(gzip.open(os.path.join(root, "data", "an-data.json.gz"), "rt", encoding="utf-8"))
    sieges = {(x["nd"], int(x["ci"])) for x in d["deputes"]}
    toutes = {cp.circo_key(c) for v in t.values() for _, cs in v for c in cs}
    vacants = toutes - sieges
    print("circonscriptions sans député en exercice :", sorted(vacants))
    assert len(vacants) <= 10
    assert len(toutes) >= 560


def test_update_cp_panne_reseau_garde_la_table(tmp_path, monkeypatch):
    import fetch
    out = tmp_path / "cp.json"
    out.write_text('{"24200": [["Sarlat-la-Canéda", ["2404"]]]}', encoding="utf-8")
    def panne(*a, **k):
        raise OSError("réseau indisponible")
    monkeypatch.setattr(cp, "download", panne)
    assert fetch.update_cp(str(out)) is False
    assert json.loads(out.read_text(encoding="utf-8"))["24200"]


def test_update_cp_ecrit_la_table(tmp_path, monkeypatch):
    import fetch
    lp = open(os.path.join(FIX, "laposte-extrait.csv"), "rb").read()
    bv = open(os.path.join(FIX, "bureaux-extrait.csv"), "rb").read()
    monkeypatch.setattr(cp, "download", lambda url, **k: lp if url == cp.LAPOSTE_URL else bv)
    monkeypatch.setattr(cp, "bureaux_url", lambda: "bureaux")
    out = tmp_path / "cp.json"
    assert fetch.update_cp(str(out), min_codes=1) is True
    assert json.loads(out.read_text(encoding="utf-8"))["75011"][0][1] == ["7506", "7507"]
