import gzip, json, os


def test_slugs_uniques(data):
    sl = [d["sl"] for d in data["deputes"]]
    assert len(sl) == len(set(sl)) >= 500


def test_build_data_identique_a_avant(data, root):
    old = json.load(gzip.open(os.path.join(root, "tests/unit/fixtures/data-avant.json.gz"), "rt", encoding="utf-8"))
    for k in ("votes", "groups", "dos", "quiz", "cats", "generated", "lastScrutin", "nScrutins"):
        assert data[k] == old[k], k
    for a, b in zip(data["deputes"], old["deputes"]):
        a = {k: v for k, v in a.items() if k != "sl"}
        assert a == b
