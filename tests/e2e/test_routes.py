import re
import pytest
from playwright.sync_api import expect

SUFFIXE = " · Hémicycle ouvert"
ROUTES = [
    ("/", "Ce que fait votre Assemblée, en clair."),
    ("/depute", "Mon député"),
    ("/votes", "Les décisions"),
    ("/votes/sante", "Les décisions"),
    ("/comprendre", "Comprendre l'Assemblée"),
    ("/groupes", "Les groupes politiques"),
    ("/groupes/rn", "RN"),
    ("/groupes/lfi-nfp", "LFI-NFP"),
    ("/lexique", "Lexique"),
    ("/jouer", "Jouer"),
    ("/jouer/devine", "Devine le vote"),
    ("/jouer/groupe", "Trouve ton groupe"),
]


def h1(page):
    return page.locator("main h1:visible")


def meta(page, sel):
    return page.locator(sel).get_attribute("content")


@pytest.mark.parametrize("path,titre", ROUTES)
def test_adresse_directe(page_desktop, base_url, path, titre):
    p = page_desktop
    p.goto(base_url + path)
    expect(h1(p)).to_have_count(1)
    expect(h1(p)).to_have_text(titre)
    t = p.title()
    assert t.endswith(SUFFIXE)
    assert meta(p, 'meta[property="og:title"]') == t[: -len(SUFFIXE)]
    assert meta(p, 'meta[property="og:description"]')
    assert meta(p, 'meta[property="og:url"]') == base_url + path
    assert p.locator('link[rel="canonical"]').get_attribute("href") == base_url + path


def test_filtre_theme_dans_adresse(page_desktop, base_url):
    p = page_desktop
    for path in ("/votes/sante", "/votes/sante/", "/votes/sante?utm_source=x", "/Votes/Sante"):
        p.goto(base_url + path)
        expect(p.locator('#cats [aria-pressed="true"]')).to_contain_text("Santé")
    p.locator("#cats button", has_text="Tout").click()
    assert p.url == base_url + "/votes"


@pytest.mark.parametrize("path", ["/depute/inexistant", "/votes/inconnu", "/groupes/xyz", "/n/importe/quoi", "/scrutin/2"])
def test_introuvable(page_desktop, base_url, path):
    p = page_desktop
    p.goto(base_url + path)
    expect(h1(p)).to_have_text("Page introuvable")
    expect(p.get_by_role("searchbox", name="Trouver mon député")).to_be_visible()
    assert "introuvable" in p.title().lower()


@pytest.mark.parametrize("ancre,cible", [("#votes", "/votes"), ("#jeu", "/jouer/devine"), ("#questionnaire", "/jouer/groupe"), ("#autre", "/")])
def test_anciennes_ancres(page_desktop, base_url, ancre, cible):
    p = page_desktop
    p.goto(base_url + "/" + ancre)
    p.wait_for_url(base_url + cible)
    expect(h1(p)).to_have_count(1)


def test_retour_avancer(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    p.get_by_role("navigation", name="Navigation principale").get_by_role("link", name="Les décisions").click()
    p.wait_for_url(base_url + "/votes")
    expect(h1(p)).to_have_text("Les décisions")
    p.go_back()
    p.wait_for_url(base_url + "/")
    expect(h1(p)).to_have_text("Ce que fait votre Assemblée, en clair.")
    p.go_forward()
    p.wait_for_url(base_url + "/votes")
    expect(h1(p)).to_have_text("Les décisions")


def test_navigation_principale(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/jouer/devine")
    nav = p.get_by_role("navigation", name="Navigation principale")
    hrefs = [nav.get_by_role("link", name=n).get_attribute("href") for n in ("Mon député", "Les décisions", "Comprendre", "Jouer")]
    assert hrefs == ["/depute", "/votes", "/comprendre", "/jouer"]
    expect(nav.get_by_role("link", name="Jouer")).to_have_attribute("aria-current", "page")


def test_scrutin_provisoire(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    n = p.evaluate("JSON.parse(document.getElementById('data').textContent).votes[0].n")
    p.goto(base_url + "/scrutin/%d" % n)
    assert re.search(r"Scrutin n° %d" % n, p.title())
