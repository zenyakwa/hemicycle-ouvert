import gzip, json, os


def test_slugs_uniques(data):
    sl = [d["sl"] for d in data["deputes"]]
    assert len(sl) == len(set(sl)) >= 500


def test_build_data_identique_a_avant(data, root):
    old = json.load(gzip.open(os.path.join(root, "tests/unit/fixtures/data-avant.json.gz"), "rt", encoding="utf-8"))
    for k in ("votes", "groups", "quiz", "cats", "generated", "lastScrutin", "nScrutins"):
        assert data[k] == old[k], k
    # résumés : seuls changent les extraits automatiques devenus « résumé à venir » (drapeau 3)
    assert data["dos"].keys() == old["dos"].keys()
    for k, v in data["dos"].items():
        if v[3] == 3:
            assert old["dos"][k][3] == 2 and v[1:3] == old["dos"][k][1:3]
        else:
            assert v == old["dos"][k], k
    for a, b in zip(data["deputes"], old["deputes"]):
        a = {k: v for k, v in a.items() if k != "sl"}
        assert a == b


def test_index_complet(data, root):
    import prep
    html = prep.render_index(data, root)
    for m in ("__CSS__", "__JS__", "__DATA__"):
        assert m not in html
    assert html.count("<script>") == 1
    assert "function openDep" in html
    assert prep.UI_JS[0] == "core.js" and prep.UI_JS[-1] == "start.js"
    for f in prep.UI_CSS + prep.UI_JS:
        assert os.path.exists(os.path.join(root, "src", "ui", f)), f


def test_logos_connus_au_build(data, root):
    logos = data["logos"]
    assert logos["RN"][0] == "/logos/RN.png" and logos["ECOS"][0] == "/logos/ECOS.webp"
    assert logos["RN"][1].startswith("https://commons.wikimedia.org/") and logos["RN"][2] == "CC BY-SA 4.0"
    assert "SOC" not in logos
    for path, page, lic in logos.values():
        assert os.path.exists(os.path.join(root, path.lstrip("/")))
