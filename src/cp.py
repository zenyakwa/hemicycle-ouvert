"""
Table code postal -> communes -> circonscriptions législatives (data/cp.json, servie en /cp.json).

Sources ouvertes (data.gouv.fr, Licence Ouverte) :
  - Base officielle des codes postaux (La Poste) : code commune INSEE <-> code postal ;
  - Liste des bureaux de vote associés à leur circonscription législative
    (Etalab, d'après les données du ministère de l'Intérieur) : commune <-> bureau <-> circonscription.

Format produit : {"24200": [["Sarlat-la-Canéda", ["2404"]], ...], ...}
Le code de circonscription (« 2404 », « 2A01 », « ZA03 »…) se relie à un député par circo_key().
"""
import csv, io, json, urllib.request

LAPOSTE_URL = "https://data.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw"
BUREAUX_DATASET = "liste-des-bureaux-de-vote-associes-a-leur-circonscription-legislative"
UA = {"User-Agent": "hemicycle-ouvert/1.0 (site civique open data)"}

# Paris, Lyon, Marseille : La Poste donne les arrondissements, le fichier des bureaux la commune entière.
PLM = {"751": "75056", "693": "69123", "132": "13055"}
# Codes du ministère de l'Intérieur pour l'outre-mer et les Français de l'étranger -> département AN.
OUTREMER = {"ZA": "971", "ZB": "972", "ZC": "973", "ZD": "974", "ZM": "976", "ZN": "988",
            "ZP": "987", "ZS": "975", "ZW": "986", "ZX": "977", "ZZ": "099"}


def download(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def bureaux_url():
    meta = json.loads(download("https://www.data.gouv.fr/api/1/datasets/%s/" % BUREAUX_DATASET))
    res = [r for r in meta["resources"] if r["format"].lower() == "csv"]
    return res[0]["url"]


def parse_laposte(raw):
    """[(insee, nom, code postal)] ; CSV « ; » en latin-1, première ligne = en-tête."""
    out = []
    for row in csv.reader(io.StringIO(raw.decode("latin-1")), delimiter=";"):
        if len(row) < 3 or not row[2].strip().isdigit():
            continue
        out.append((row[0].strip(), row[1].strip(), row[2].strip()))
    return out


def parse_bureaux(raw):
    """[(insee, numéro de bureau, code circonscription, nom de commune)]."""
    out = []
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        out.append((r["codeCommune"], r["numeroBureauVote"], r["codeCirconscription"], r["nomCommune"]))
    return out


def circo_key(code):
    """« 2404 » -> ("24", 4) ; « 2A01 » -> ("2A", 1) ; « ZA03 » -> ("971", 3)."""
    dep, num = code[:2], int(code[2:])
    return (OUTREMER.get(dep, dep), num)


def _arr_label(insee):
    n = int(insee[-1]) if insee.startswith("693") else int(insee[-2:])
    ville = {"751": "Paris", "693": "Lyon", "132": "Marseille"}[insee[:3]]
    return "%s %d%s arrondissement" % (ville, n, "er" if n == 1 else "e")


def build_table(laposte, bureaux):
    par_commune, par_arr, noms, par_dep = {}, {}, {}, {}
    for insee, num, circo, nom in bureaux:
        par_commune.setdefault(insee, set()).add(circo)
        noms.setdefault(insee, nom)
        par_dep.setdefault(insee[:2] if not insee.startswith("97") else insee[:3], set()).add(circo)
        if insee in PLM.values() and len(num) >= 3:
            par_arr.setdefault((insee, int(num[:2])), set()).add(circo)
    table = {}
    for insee, nom_lp, code in laposte:
        if insee.startswith("98") and insee[:3] not in ("986", "987", "988") or insee.startswith("99"):
            continue  # Monaco et hors territoire
        if insee[:3] in PLM and insee not in PLM.values():
            ville = PLM[insee[:3]]
            arr = int(insee[-1]) if ville == "69123" else int(insee[-2:])  # Lyon : 6938x ; Paris 751xx ; Marseille 132xx
            circos = par_arr.get((ville, arr)) or par_commune.get(ville, set())
            nom = _arr_label(insee)
        else:
            circos = par_commune.get(insee)
            nom = noms.get(insee) or nom_lp.title()
            if not circos:  # commune absente du fichier des bureaux : toutes les circonscriptions du département
                circos = par_dep.get(insee[:3] if insee.startswith("97") else insee[:2], set())
        if not circos:
            continue
        entry = [nom, sorted(circos)]
        if entry not in table.setdefault(code, []):
            table[code].append(entry)
    for code in table:
        table[code].sort(key=lambda e: e[0])
    return table
