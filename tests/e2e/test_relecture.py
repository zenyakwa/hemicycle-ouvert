"""Correctifs issus de la relecture finale de la branche."""
import re
import urllib.parse
from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"


def test_adresse_avec_accents(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    d = p.evaluate(DATA + ".deputes.find(d=>/[éèêëàâîïôöûüçÉÈ]/.test(d.p+d.n))")
    tape = (d["p"] + "-" + d["n"]).replace(" ", "-")
    p.goto(base_url + "/depute/" + urllib.parse.quote(tape))
    expect(p.locator("#sheet h3")).to_have_text(d["p"] + " " + d["n"])
    p.goto(base_url + "/votes/" + urllib.parse.quote("Santé"))
    expect(p.locator('#cats [aria-pressed="true"]')).to_contain_text("Santé")


def test_fermer_la_fiche_garde_l_etat_de_la_page(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/scrutin/9895")
    p.locator("#voteList summary").click()
    lien = p.locator("#voteList a").first
    href = lien.get_attribute("href")
    lien.focus()
    p.keyboard.press("Enter")
    expect(p.locator("#sheet")).to_be_visible()
    p.keyboard.press("Escape")
    p.wait_for_url(base_url + "/scrutin/9895")
    expect(p.locator("#voteList")).to_have_attribute("open", "")
    assert p.evaluate("document.activeElement.getAttribute('href')") == href


def test_theme_montre_tous_les_votes(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/votes/censure")
    n = p.evaluate(DATA + ".votes.filter(v=>v.cat==='censure').length")
    expect(p.locator("#vcount")).to_contain_text("%d vote" % n)
    expect(p.locator('#resSeg [aria-pressed="true"]')).to_have_text("Tous")


def test_seuil_de_la_censure(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    n = p.evaluate(DATA + ".votes.find(v=>v.k==='Motion de censure').n")
    p.goto(base_url + "/scrutin/%d" % n)
    box = p.locator("#view-scrutin .resbox")
    expect(box).to_contain_text("majorité absolue des membres composant l'Assemblée")
    assert "au moins 289" not in box.inner_text()


def test_credits_des_logos_avec_auteur(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    expect(p.locator("#logoCredits")).to_contain_text("Rassemblement National")


def test_codes_postaux_nouvel_essai(page_desktop, base_url):
    p = page_desktop
    etat = {"n": 0}
    def route(r):
        etat["n"] += 1
        if etat["n"] == 1:
            r.fulfill(status=503, body="x")
        else:
            r.continue_()
    p.route("**/cp.json", route)
    p.goto(base_url + "/")
    box = p.get_by_role("searchbox", name="Trouver mon député")
    box.fill("24200")  # le premier chargement (au focus) échoue, la saisie relance le téléchargement
    expect(p.locator("#qHome-results a")).to_have_count(1)
    assert etat["n"] >= 2
    p.errors[:] = [e for e in p.errors if "503" not in e]
