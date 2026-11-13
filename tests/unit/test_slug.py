from slug import slugify, assign_slugs


def test_slugify():
    assert slugify("Antoine Golliot") == "antoine-golliot"
    assert slugify("Marie-Noëlle Battistel") == "marie-noelle-battistel"
    assert slugify("Jean-Philippe  d'Artagnan") == "jean-philippe-d-artagnan"
    assert slugify("Éric Œuvrard") == "eric-oeuvrard"


def test_collision_suffixe_departement():
    deps = [{"p": "Jean", "n": "Martin", "nd": "01"}, {"p": "Jean", "n": "Martin", "nd": "2A"}, {"p": "Léa", "n": "Petit", "nd": "75"}]
    assign_slugs(deps)
    assert [d["sl"] for d in deps] == ["jean-martin-01", "jean-martin-2a", "lea-petit"]
