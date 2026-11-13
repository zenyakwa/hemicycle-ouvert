import re
from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"


def chercher(p, base_url, q, path="/"):
    p.goto(base_url + path)
    box = p.get_by_role("searchbox", name="Trouver mon député").first
    box.fill(q)
    return box


def slug_de(p, nd, ci):
    return p.evaluate(DATA + ".deputes.find(d=>d.nd==='%s' && +d.ci===%d).sl" % (nd, ci))


def test_24200_un_seul_depute(page_any, base_url):
    p = page_any
    chercher(p, base_url, "24200")
    res = p.locator("#qHome-results a")
    expect(res).to_have_count(1)
    expect(res.first).to_contain_text("4e circonscription de la Dordogne")
    res.first.click()
    p.wait_for_url(base_url + "/depute/" + slug_de(p, "24", 4))


def test_75011_deux_choix(page_desktop, base_url):
    p = page_desktop
    chercher(p, base_url, "75011")
    res = p.locator("#qHome-results a")
    expect(res).to_have_count(2)
    expect(res.nth(0)).to_contain_text("6e circonscription de Paris")
    expect(res.nth(1)).to_contain_text("7e circonscription de Paris")
    expect(p.locator("#qHome-status")).to_have_text("2 résultats")


def test_toulouse_plusieurs_choix(page_desktop, base_url):
    p = page_desktop
    chercher(p, base_url, "31000")
    expect(p.locator("#qHome-results a").nth(1)).to_be_visible()
    assert p.locator("#qHome-results a").count() > 1


def test_ville(page_desktop, base_url):
    p = page_desktop
    box = chercher(p, base_url, "sarlat")
    item = p.locator("#qHome-results a", has_text="Sarlat-la-Canéda")
    expect(item).to_be_visible()
    expect(item).to_contain_text("4e circonscription de la Dordogne")


def test_code_postal_inconnu(page_desktop, base_url):
    p = page_desktop
    chercher(p, base_url, "00000")
    expect(p.locator("#qHome-results")).to_contain_text("Aucune commune pour ce code postal")


def test_cp_indisponible(page_desktop, base_url):
    p = page_desktop
    p.route("**/cp.json", lambda r: r.fulfill(status=503, body="indisponible"))
    box = chercher(p, base_url, "24200")
    expect(p.locator("#qHome-results")).to_contain_text("Recherche par code postal momentanément indisponible")
    box.fill("Golliot")
    expect(p.locator("#qHome-results a").first).to_contain_text("Antoine Golliot")
    # la 503 elle-même est journalisée par le navigateur ; on n'accepte que celle-là
    p.errors[:] = [e for e in p.errors if "503" not in e]


def test_clavier(page_desktop, base_url):
    p = page_desktop
    box = chercher(p, base_url, "Golliot")
    expect(p.locator("#qHome-results a").first).to_be_visible()
    box.press("ArrowDown")
    p.keyboard.press("Enter")
    p.wait_for_url(base_url + "/depute/antoine-golliot")


def test_page_de_vote_code_postal(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    n = p.evaluate(DATA + ".votes[0].n")
    p.goto(base_url + "/scrutin/%d" % n)
    p.get_by_role("searchbox", name="Et mon député, qu'a-t-il voté ?").fill("24200")
    p.locator("#qVote-results button").first.click()
    expect(p.locator("#myVote")).to_contain_text(re.compile("Pour|Contre|Abstention|N'a pas pris part|Pas encore"))
