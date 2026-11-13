from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"


def phrase(v):
    p, c, a = v["sy"]
    return "%s : %d pour, %d contre, %d abstention%s." % ("Adopté" if v["so"] == "adopté" else "Rejeté", p, c, a, "s" if a > 1 else "")


def test_accueil(page_any, base_url):
    p = page_any
    p.goto(base_url + "/")
    home = p.locator("#view-home")
    expect(home.locator("h1")).to_have_text("Ce que fait votre Assemblée, en clair.")
    expect(home.get_by_role("searchbox", name="Trouver mon député")).to_be_visible()
    # trois cartes d'entrée
    for name, href in (("Mon député", "/depute"), ("Ce que l'Assemblée a décidé", "/votes"), ("Comprendre l'Assemblée", "/comprendre")):
        expect(home.locator(".entry[href='%s']" % href)).to_contain_text(name)
    # dernières décisions
    expect(home.get_by_role("heading", name="Les dernières décisions")).to_be_visible()
    cards = home.locator(".vcard")
    expect(cards).to_have_count(3)
    v0 = p.evaluate(DATA + ".votes[0]")
    assert cards.first.get_attribute("href") == "/scrutin/%d" % v0["n"]
    expect(cards.first).to_contain_text(phrase(v0))
    expect(cards.first.locator(".res")).to_have_text("Adopté" if v0["so"] == "adopté" else "Rejeté")
    expect(home.locator(".themechips a").first).to_have_attribute("href", "/votes/" + p.evaluate(DATA + ".cats[0][0]"))
    # l'Assemblée en un coup d'œil
    expect(home.get_by_role("heading", name="L'Assemblée en un coup d'œil")).to_be_visible()
    expect(home.locator(".gbar .seg")).to_have_count(12)
    expect(home.locator(".gbar-legend a").first).to_have_attribute("href", "/groupes/lfi-nfp")
    expect(home).to_contain_text("Majorité absolue : 289 sièges. Aucun groupe ne l'atteint seul.")
    for name, href in (("Explorer l'hémicycle interactif", "/comprendre"), ("Les 12 groupes", "/groupes"), ("Lexique", "/lexique")):
        expect(home.get_by_role("link", name=name, exact=True)).to_have_attribute("href", href)
    # jouer
    expect(home.get_by_role("heading", name="Jouer")).to_be_visible()
    expect(home.locator(".playcard[href='/jouer/devine']")).to_be_visible()
    expect(home.locator(".playcard[href='/jouer/groupe']")).to_be_visible()


def test_carte_vers_scrutin(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    n = p.evaluate(DATA + ".votes[0].n")
    p.locator("#view-home .vcard").first.click()
    p.wait_for_url(base_url + "/scrutin/%d" % n)


def test_accueil_mobile_sans_hemicycle(page_mobile, base_url):
    p = page_mobile
    p.goto(base_url + "/")
    assert p.locator("svg.hemi:visible").count() == 0
    n = p.evaluate(DATA + ".deputes.length")
    link = p.get_by_role("link", name="Voir les %d députés en liste" % n)
    expect(link).to_be_visible()
    expect(link).to_have_attribute("href", "/depute")


def test_comprendre_a_la_barre_des_groupes(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/comprendre")
    expect(p.locator("#view-hemi .gbar .seg")).to_have_count(12)
