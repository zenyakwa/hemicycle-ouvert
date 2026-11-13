"""Adresses lisibles des députés : /depute/<prenom-nom>."""
import collections, re, unicodedata


def slugify(s):
    s = s.replace("œ", "oe").replace("Œ", "Oe").replace("æ", "ae").replace("Æ", "Ae")
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def assign_slugs(deputes):
    """Ajoute d['sl'] ; en cas d'homonymie, tous les homonymes reçoivent le n° de département."""
    base = [slugify(d["p"] + " " + d["n"]) for d in deputes]
    count = collections.Counter(base)
    for d, b in zip(deputes, base):
        d["sl"] = b if count[b] == 1 else b + "-" + d["nd"].lower()
