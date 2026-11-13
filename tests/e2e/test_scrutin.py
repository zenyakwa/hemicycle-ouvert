import re
from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"
ORDER = ['LFI-NFP', 'GDR', 'ECOS', 'SOC', 'LIOT', 'DEM', 'EPR', 'HOR', 'DR', 'UDR', 'RN', 'NI']


def load(p, base_url, which="votes[0]"):
    p.goto(base_url + "/")
    D = p.evaluate(DATA)
    v = eval(which, {}, {"votes": D["votes"], "D": D})
    p.goto(base_url + "/scrutin/%d" % v["n"])
    return D, v


def test_page_de_vote(page_any, base_url):
    p = page_any
    D, v = load(p, base_url)
    cats = dict(D["cats"])
    page = p.locator("#view-scrutin")
    crumb = page.get_by_role("navigation", name="Fil d'Ariane")
    expect(crumb.get_by_role("link", name="Les décisions")).to_have_attribute("href", "/votes")
    expect(crumb.get_by_role("link", name=cats[v["cat"]])).to_have_attribute("href", "/votes/" + v["cat"])
    box = page.locator(".resbox")
    expect(box.locator(".big")).to_have_text("ADOPTÉ" if v["so"] == "adopté" else "REJETÉ")
    for n in v["sy"]:
        expect(box).to_contain_text(str(n))
    expect(box).to_contain_text("Seuls les députés présents votent : %d ont pris part à ce vote." % sum(v["sy"]))
    expect(page.get_by_role("heading", name="De quoi s'agit-il ?")).to_be_visible()
    expect(page.get_by_role("heading", name="Comment chaque groupe a voté")).to_be_visible()
    rows = page.locator(".grow")
    expect(rows).to_have_count(len(v["gv"]))
    G = {g["id"]: g for g in D["groups"]}
    expected = [G[x[0]]["a"] for x in sorted(v["gv"], key=lambda x: ORDER.index(G[x[0]]["a"]) if G[x[0]]["a"] in ORDER else 99)]
    shown = rows.locator(".gsig").all_inner_texts()
    assert shown == expected
    first = sorted(v["gv"], key=lambda x: ORDER.index(G[x[0]]["a"]) if G[x[0]]["a"] in ORDER else 99)[0]
    r0 = rows.first
    expect(r0).to_contain_text(G[first[0]]["l"])
    expect(r0.locator(".gpos")).to_have_text(first[1].capitalize())
    for n in first[2:5]:
        expect(r0).to_contain_text(str(n))
    expect(page.get_by_role("link", name=re.compile("Scrutin n° %d" % v["n"]))).to_have_attribute("href", "https://www.assemblee-nationale.fr/dyn/17/scrutins/%d" % v["n"])
    if v.get("dr"):
        expect(page.get_by_role("link", name=re.compile("Texte officiel"))).to_be_visible()
    assert p.title().startswith("Scrutin n° %d" % v["n"])


def test_motion_de_censure(page_desktop, base_url):
    p = page_desktop
    D, v = load(p, base_url, "[x for x in votes if x['k']=='Motion de censure'][0]")
    expect(p.locator("#view-scrutin .resbox")).to_contain_text("289")


def test_mon_depute_a_vote(page_desktop, base_url):
    p = page_desktop
    D, v = load(p, base_url)
    i = next(k for k, d in enumerate(D["deputes"]) if d["sl"] == "antoine-golliot")
    d = D["deputes"][i]
    c = v["v"][i]
    attendu = "Pas encore député à cette date" if v["dt"] < d["d"] else {"p": "Pour", "c": "Contre", "a": "Abstention"}.get(c, "N'a pas pris part au vote")
    box = p.get_by_role("searchbox", name="Et mon député, qu'a-t-il voté ?")
    box.fill("Golliot")
    p.locator("#qVote-results button").first.click()
    expect(p.locator("#myVote")).to_contain_text("Antoine Golliot")
    expect(p.locator("#myVote")).to_contain_text(attendu)


def test_copier_le_lien(browser, base_url):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    # l'origine de test est en http : on remplace le presse-papiers (réservé au https) par un témoin
    ctx.add_init_script("Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__copie=t;return Promise.resolve();}}})")
    p = ctx.new_page()
    p.goto(base_url + "/")
    n = p.evaluate(DATA + ".votes[0].n")
    p.goto(base_url + "/scrutin/%d" % n)
    p.get_by_role("button", name="Copier le lien de ce vote").click()
    expect(p.locator("#copyMsg")).to_have_text("Lien copié")
    assert p.locator("#copyMsg").get_attribute("aria-live") == "polite"
    assert p.evaluate("window.__copie") == base_url + "/scrutin/%d" % n
    ctx.close()


def test_scrutin_non_cle(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/scrutin/2")
    expect(p.locator("main h1:visible")).to_have_text("Page introuvable")
    expect(p.locator("#nfMsg")).to_contain_text("Ce scrutin ne fait pas partie des votes clés suivis ici")
    expect(p.get_by_role("link", name=re.compile("assemblee-nationale.fr|site de l'Assemblée"))).to_have_attribute("href", "https://www.assemblee-nationale.fr/dyn/17/scrutins/2")


def test_cartes_de_la_liste(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/votes/sante")
    cards = p.locator("#vlist a.vcard")
    expect(cards.first).to_be_visible()
    href = cards.first.get_attribute("href")
    assert re.fullmatch(r"/scrutin/\d+", href)
    cards.first.click()
    p.wait_for_url(base_url + href)
    expect(p.locator("#view-scrutin")).to_be_visible()
    p.go_back()
    p.wait_for_url(base_url + "/votes/sante")
    expect(p.locator('#cats [aria-pressed="true"]')).to_contain_text("Santé")


def test_liens_vers_les_votes_ailleurs(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/groupes/rn")
    a = p.locator(".gv a").first
    assert re.fullmatch(r"/scrutin/\d+", a.get_attribute("href"))
    p.goto(base_url + "/depute/antoine-golliot")
    a = p.locator("#sheet .dvote a").first
    assert re.fullmatch(r"/scrutin/\d+", a.get_attribute("href"))
