"""
Télécharge les données ouvertes de l'Assemblée nationale et prépare :
  data/an-data.json.gz    députés en exercice, groupes, votes clés (+ participation)
  data/an-dossiers.json   pour chaque texte voté : auteur, promulgation, exposé des motifs

Usage :
  python src/fetch.py                 # télécharge depuis data.assemblee-nationale.fr
  python src/fetch.py --local DOSSIER # utilise des .zip déjà téléchargés (tests)

Les fiches des textes (assemblee-nationale.fr) sont mises en cache dans
data/an-dossiers.json : seules les nouvelles sont téléchargées à chaque passage.
"""
import gzip, html, io, json, os, re, sys, time, unicodedata, zipfile
import urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
LEG = "17"
OPEN = "https://data.assemblee-nationale.fr/static/openData/repository/%s" % LEG
URLS = {
    "amo": OPEN + "/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip",
    "scr": OPEN + "/loi/scrutins/Scrutins.json.zip",
    "dos": OPEN + "/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip",
}
SITE = "https://www.assemblee-nationale.fr"
UA = "Mozilla/5.0 (compatible; hemicycle-ouvert/1.0; +https://github.com)"
LOCAL = None
if "--local" in sys.argv:
    LOCAL = sys.argv[sys.argv.index("--local") + 1]


def log(*a):
    print(*a, flush=True)


def get(url, tries=3, timeout=120):
    if LOCAL and url.startswith(OPEN):
        with open(os.path.join(LOCAL, url.rsplit("/", 1)[1]), "rb") as f:
            return f.read()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = e
        except Exception as e:  # réseau, timeout…
            last = e
        time.sleep(3 * (i + 1))
    raise RuntimeError("Échec du téléchargement %s : %s" % (url, last))


def zip_json(data, keep=lambda name: True):
    z = zipfile.ZipFile(io.BytesIO(data))
    for name in z.namelist():
        if name.endswith(".json") and keep(name):
            yield name, json.loads(z.read(name).decode("utf-8"))


def arr(x):
    return [] if x is None else x if isinstance(x, list) else [x]


def txt_id(x):
    return x.get("#text") if isinstance(x, dict) else x


# ------------------------------------------------------------------ députés + votes
def build_core(amo_zip, scr_zip):
    org, acteurs = {}, []
    for name, o in zip_json(amo_zip):
        if "/organe/" in name:
            org[o["organe"]["uid"]] = o["organe"]
        elif "/acteur/" in name:
            acteurs.append(o["acteur"])

    deps = []
    for a in acteurs:
        ms = arr(a["mandats"]["mandat"])
        an = next((m for m in ms if m.get("typeOrgane") == "ASSEMBLEE" and not m.get("dateFin") and m.get("legislature") == LEG), None)
        if not an:
            continue
        cur = lambda t: next((m for m in ms if m.get("typeOrgane") == t and not m.get("dateFin")), None)
        gpm, com, pp = cur("GP"), cur("COMPER"), cur("PARPOL")
        lieu = an["election"]["lieu"]
        ec = a["etatCivil"]
        prof = ((a.get("profession") or {}).get("libelleCourant") or "")
        c_org = org.get(com["organes"]["organeRef"]) if com else None
        p_org = org.get(pp["organes"]["organeRef"]) if pp else None
        deps.append({
            "id": txt_id(a["uid"]), "c": ec["ident"]["civ"], "p": ec["ident"]["prenom"], "n": ec["ident"]["nom"],
            "g": gpm["organes"]["organeRef"] if gpm else None,
            "gq": ((gpm or {}).get("infosQualite") or {}).get("codeQualite"),
            "dep": lieu["departement"], "nd": lieu["numDepartement"], "ci": lieu["numCirco"], "r": lieu["region"],
            "s": (an.get("mandature") or {}).get("placeHemicycle"),
            "b": (ec.get("infoNaissance") or {}).get("dateNais"),
            "pr": re.sub(r"^\(\d+\)\s*-\s*", "", prof),
            "com": (c_org.get("libelleAbrege") or c_org.get("libelle")) if c_org else None,
            "comq": ((com or {}).get("infosQualite") or {}).get("codeQualite"),
            "pp": p_org.get("libelle") if p_org else None,
            "d": an["dateDebut"], "pe": (an.get("mandature") or {}).get("premiereElection"),
            "hatvp": a.get("uri_hatvp"),
            "cm": None if (an.get("election") or {}).get("causeMandat") in (None, "élections générales") else an["election"]["causeMandat"],
        })
    idx = {d["id"]: i for i, d in enumerate(deps)}

    scr = [o["scrutin"] for _, o in zip_json(scr_zip)]
    scr.sort(key=lambda s: -int(s["numero"]))
    key_re = re.compile(r"^l'ensemble|^la motion de censure|^la motion de rejet|déclaration du Gouvernement|^la proposition de résolution", re.I)
    part = [0] * len(deps); elig = [0] * len(deps); votes = []
    for s in scr:
        codes = ["-"] * len(deps)
        gv = []
        groupes = arr((((s.get("ventilationVotes") or {}).get("organe") or {}).get("groupes") or {}).get("groupe"))
        for g in groupes:
            dn = g["vote"].get("decompteNominatif") or {}
            for k, c in (("pours", "p"), ("contres", "c"), ("abstentions", "a"), ("nonVotants", "n")):
                for v in arr((dn.get(k) or {}).get("votant")):
                    i = idx.get(v.get("acteurRef"))
                    if i is not None:
                        codes[i] = c
            dv = g["vote"]["decompteVoix"]
            gv.append([g["organeRef"], g["vote"].get("positionMajoritaire"), int(dv["pour"]), int(dv["contre"]), int(dv["abstentions"])])
        for i, d in enumerate(deps):
            if s["dateScrutin"] >= d["d"]:
                elig[i] += 1
                if codes[i] in ("p", "c", "a"):
                    part[i] += 1
        if key_re.search(s["titre"]) or s["typeVote"]["codeTypeVote"] == "SPS":
            dl = ((s.get("objet") or {}).get("dossierLegislatif") or {})
            dec = s["syntheseVote"]["decompte"]
            votes.append({
                "n": int(s["numero"]), "dt": s["dateScrutin"], "t": s["titre"],
                "dos": dl.get("libelle"), "dr": dl.get("dossierRef"),
                "so": s["sort"]["code"], "ty": s["typeVote"]["codeTypeVote"],
                "sy": [int(dec["pour"]), int(dec["contre"]), int(dec["abstentions"])],
                "gv": gv, "v": "".join(codes),
            })
    for i, d in enumerate(deps):
        d["part"] = part[i]; d["elig"] = elig[i]
    groups = [{"id": o["uid"], "l": o["libelle"], "a": o["libelleAbrev"], "col": o.get("couleurAssociee")}
              for o in org.values() if o.get("codeType") == "GP" and not (o.get("viMoDe") or {}).get("dateFin")]
    return {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "lastScrutin": scr[0]["dateScrutin"], "nScrutins": len(scr),
            "groups": groups, "deputes": deps, "votes": votes}, scr


# ------------------------------------------------------------------ votes -> dossiers
def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def map_votes_to_dossiers(dos_zip, core, scr):
    vmap, dossiers = {}, []
    z = zipfile.ZipFile(io.BytesIO(dos_zip))
    for name in z.namelist():
        if "dossierParlementaire" not in name or not name.endswith(".json"):
            continue
        raw = z.read(name).decode("utf-8")
        o = json.loads(raw).get("dossierParlementaire") or {}
        for m in re.finditer(r"VTANR5L%sV(\d+)" % LEG, raw):
            vmap[int(m.group(1))] = o.get("uid")
        titre = ((o.get("titreDossier") or {}).get("titre")) or ""
        dossiers.append((o.get("uid"), norm(titre)))
    by_num = {int(s["numero"]): s for s in scr}
    out = {}
    for v in core["votes"]:
        uid = v.get("dr") or vmap.get(v["n"])
        if not uid:
            nt = norm(by_num[v["n"]]["titre"])
            best = None
            for u, dt in dossiers:
                if len(dt) > 15 and dt in nt and (best is None or len(dt) > len(best[1])):
                    best = (u, dt)
            uid = best[0] if best else None
        if uid:
            out[v["n"]] = uid
    return out


# ------------------------------------------------------------------ fiches des textes
BLOCK = re.compile(r"(?i)</?(p|div|br|li|ul|ol|h\d|td|tr|table|section|article|header|footer|nav|main|dt|dd)\b[^>]*>")


def strip_html(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = BLOCK.sub(" ", h)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def page_text(h):
    m = re.search(r"(?is)<main[^>]*>(.*)</main>", h)
    return strip_html(m.group(1) if m else h)


def fetch_dossier(uid):
    k = uid.replace("DLR5L", "")
    r, url = None, None
    for leg in dict.fromkeys([LEG, k[:2]]):
        url = "%s/dyn/%s/dossiers/%s" % (SITE, leg, uid)
        r = get(url)
        if r:
            break
    if not r:
        return None
    h = r.decode("utf-8", "replace")
    txt = page_text(h)
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", h)
    titre = strip_html(h1.group(1)) if h1 else None
    texts = list(dict.fromkeys(re.findall(r'href="((?:https://www\.assemblee-nationale\.fr)?/dyn/1\d/textes/l1\db\d+_(?:proposition|projet)[^"#?]*)"', h)))
    promu = re.search(r"Promulgation de la loi\s*(\w+ \d{1,2} \w+ \d{4})", txt)
    cc = re.search(r"Conseil constitutionnel\s*(\w+ \d{1,2} \w+ \d{4})\s?(Conforme|Partiellement conforme|Non conforme)?", txt)
    aut = re.search(r"(?:proposition de loi|proposition de résolution)(?: organique| constitutionnelle)? de (M\.|Mme|MM\.|Mmes)\s(.{3,140}?)(?= visant| relati| portant| pour | sur | tendant| créant| instaurant| fixant| (?:et|,) )", txt, re.I)
    expo = None
    for t in texts[:5]:
        th = get(t if t.startswith("http") else SITE + t)
        if not th:
            continue
        m = re.search(r'data-id="([A-Z0-9]+)"', th.decode("utf-8", "replace"))
        if not m:
            continue
        od = get("%s/dyn/opendata/%s.html" % (SITE, m.group(1)))
        if not od:
            continue
        ot = strip_html(od.decode("utf-8", "replace"))
        i = re.search(r"EXPOS[ÉE] DES MOTIFS", ot, re.I)
        if i:
            expo = ot[i.start() + 17: i.start() + 2200]
            break
        time.sleep(0.3)
    return {"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "titre": titre, "url": url, "auteur": " ".join(aut.groups()) if aut else None,
            "promu": promu.group(1) if promu else None,
            "cc": (cc.group(1) + " " + (cc.group(2) or "")).strip() if cc else None,
            "expo": expo, "senat": bool(re.search(r"Dépôt au Sénat|déposée? au Sénat", txt[:3000], re.I))}


# ------------------------------------------------------------------ registre des déports
DEPORT_RE = re.compile(r"Date\s*:\s*(?P<date>.+?)\s+Cible\s*:\s*(?P<cible>.+?)\s+Portée\s*:\s*(?P<portee>.+?)\s+Lecture\s*:\s*(?P<lecture>.+?)\s+Instance\s*:\s*(?P<instance>Séance publique et Commission|Séance publique|Commission)\s*(?P<motif>.*)$", re.S)


def parse_deport(h):
    t = page_text(h)
    m = DEPORT_RE.search(t)
    if not m:
        return None
    motif = re.split(r"\s(?:Partager|Retour|Imprimer)\b", m.group("motif"))[0].strip()
    return {"date": m.group("date").strip(), "cible": m.group("cible").strip(), "portee": m.group("portee").strip(),
            "lecture": m.group("lecture").strip(), "instance": m.group("instance"), "motif": motif[:400]}


def update_deports(core):
    """Registre public des déports (www.assemblee-nationale.fr/dyn/17/deports).
    Chaque jour : la page d'accueil du registre (derniers déports).
    Une fois par semaine : un passage député par député pour ne rien manquer."""
    path = P("data", "an-transparence.json")
    cache = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"swept": "", "deports": {}}
    if LOCAL:
        return cache
    ids = set()
    h = get(SITE + "/dyn/%s/deports" % LEG)
    if h:
        ids |= set(re.findall(r"DPTR5L%sPA\d+D\d+" % LEG, h.decode("utf-8", "replace")))
    week_ago = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400))
    if cache.get("swept", "") < week_ago:
        log("  passage complet du registre des déports (%d députés)…" % len(core["deputes"]))
        for d in core["deputes"]:
            try:
                r = get(SITE + "/dyn/%s/deports?depute=%s" % (LEG, d["id"]))
                if r:
                    ids |= set(x for x in re.findall(r"DPTR5L%sPA\d+D\d+" % LEG, r.decode("utf-8", "replace")) if (d["id"] + "D") in x)
            except Exception as e:
                log("    %s ignoré (%s)" % (d["id"], e))
            time.sleep(0.2)
        cache["swept"] = time.strftime("%Y-%m-%d", time.gmtime())
    new = sorted(i for i in ids if i not in cache["deports"])
    for i in new:
        try:
            r = get(SITE + "/dyn/deports/" + i)
            info = parse_deport(r.decode("utf-8", "replace")) if r else None
            if info:
                info["pa"] = re.search(r"PA\d+", i).group(0)
                cache["deports"][i] = info
                log("  nouveau déport : %s — %s" % (i, info["cible"][:60]))
        except Exception as e:
            log("  déport %s ignoré (%s)" % (i, e))
        time.sleep(0.3)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0)
    return cache


def main():
    log("Téléchargement des députés et des scrutins…")
    core, scr = build_core(get(URLS["amo"]), get(URLS["scr"]))
    log("  %d députés, %d scrutins, %d votes clés, dernier scrutin le %s" % (len(core["deputes"]), core["nScrutins"], len(core["votes"]), core["lastScrutin"]))
    if len(core["deputes"]) < 500 or len(core["votes"]) < 10:
        raise SystemExit("Données incomplètes : arrêt sans rien modifier.")

    log("Rattachement des votes aux dossiers législatifs…")
    num2uid = map_votes_to_dossiers(get(URLS["dos"]), core, scr)

    cache_path = P("data", "an-dossiers.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {"map": {}, "dos": {}}
    # le cache garde les fiches déjà téléchargées ; on reconstruit la table votes -> dossier
    new_map = {}
    for n, uid in num2uid.items():
        new_map.setdefault(uid.replace("DLR5L", ""), []).append(n)
    missing = [k for k in new_map if k not in cache["dos"]]
    # textes pas encore promulgués : on revérifie leur fiche au plus une fois par semaine
    week_ago = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400))
    stale = [k for k in new_map if k in cache["dos"] and not cache["dos"][k].get("promu")
             and cache["dos"][k].get("fetched", "") < week_ago]
    stale.sort(key=lambda k: cache["dos"][k].get("fetched", ""))
    log("  %d textes : %d nouveaux, %d à revérifier" % (len(new_map), len(missing), len(stale)))
    missing += stale[:40]
    if LOCAL:
        missing = []  # pas de réseau en mode test
    for i, k in enumerate(missing, 1):
        try:
            info = fetch_dossier("DLR5L" + k)
            if info:
                old = cache["dos"].get(k) or {}
                if not info.get("expo") and old.get("expo"):
                    info["expo"] = old["expo"]
                cache["dos"][k] = info
                log("  [%d/%d] %s — %s" % (i, len(missing), k, (info.get("titre") or "")[:70]))
        except Exception as e:
            log("  [%d/%d] %s — ignoré (%s)" % (i, len(missing), k, e))
        time.sleep(0.5)
    cache["map"] = new_map

    log("Registre des déports…")
    try:
        dep = update_deports(core)
        log("  %d déports enregistrés" % len(dep["deports"]))
    except Exception as e:
        log("  registre des déports indisponible (%s) — on garde les données précédentes" % e)

    with gzip.open(P("data", "an-data.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(core, f, ensure_ascii=False, separators=(",", ":"))
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
    log("Données enregistrées dans data/.")


if __name__ == "__main__":
    main()
