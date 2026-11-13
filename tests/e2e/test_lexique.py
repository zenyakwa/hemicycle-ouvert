import re
from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"


def test_page_lexique(page_any, base_url):
    p = page_any
    p.goto(base_url + "/lexique")
    termes = p.locator("#lexique dt").all_inner_texts()
    assert len(termes) >= 25
    assert termes == p.evaluate("t=>t.slice().sort((a,b)=>a.localeCompare(b,'fr'))", termes)


def test_ancre(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/lexique#motion-de-censure")
    expect(p.locator("#motion-de-censure")).to_be_in_viewport()


def test_type_de_texte_lie_au_lexique(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    n = p.evaluate(DATA + ".votes.find(v=>v.k==='Projet de loi').n")
    p.goto(base_url + "/scrutin/%d" % n)
    link = p.locator("#view-scrutin .smeta a", has_text="Projet de loi")
    expect(link).to_have_attribute("href", "/lexique#projet-de-loi")
    link.click()
    p.wait_for_url(base_url + "/lexique#projet-de-loi")
    expect(p.locator("#projet-de-loi")).to_be_in_viewport()


def test_vote_avec_son_groupe(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/groupes")
    expect(p.locator("#groupsArea")).to_contain_text("Vote avec son groupe")
    p.goto(base_url + "/groupes/rn")
    expect(p.locator("#groupsArea")).to_contain_text("Vote avec son groupe")
    p.goto(base_url + "/depute/antoine-golliot")
    expect(p.locator("#sheet")).to_contain_text("Vote avec son groupe")


def test_plus_de_cohesion(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    html = p.evaluate("document.documentElement.outerHTML.replace(document.getElementById('data').outerHTML,'')")
    for mot in ("cohésion", "Cohésion", "Fidélité", "fidélité"):
        assert mot not in html, mot
