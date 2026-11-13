import pytest
from playwright.sync_api import expect

DATA = "JSON.parse(document.getElementById('data').textContent)"
VUES = ["/", "/depute", "/votes", "/scrutin/9895", "/comprendre", "/groupes", "/groupes/rn", "/lexique", "/jouer", "/jouer/devine", "/jouer/groupe", "/depute/inexistant"]


@pytest.mark.parametrize("path", VUES)
def test_reperes(page_desktop, base_url, path):
    p = page_desktop
    p.goto(base_url + path)
    expect(p.locator("h1:visible")).to_have_count(1)
    expect(p.locator("main")).to_have_count(1)
    expect(p.get_by_role("navigation", name="Navigation principale")).to_have_count(1)
    p.keyboard.press("Tab")
    assert p.evaluate("document.activeElement.textContent.trim()") == "Aller au contenu"
    p.keyboard.press("Enter")
    assert p.evaluate("document.activeElement.closest('main') !== null")


def test_hemicycle_en_liste_au_clavier(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/comprendre")
    n = p.evaluate(DATA + ".deputes.length")
    expect(p.get_by_role("button", name="Afficher en liste")).to_have_attribute("aria-expanded", "false")
    btn = p.locator("#hemiListBtn")
    btn.focus()
    p.keyboard.press("Enter")
    expect(btn).to_have_attribute("aria-expanded", "true")
    expect(btn).to_have_text("Masquer la liste")
    liste = p.locator("#hemiList")
    expect(liste).to_be_visible()
    expect(liste.locator("a[href^='/depute/']")).to_have_count(n)
    expect(liste.locator("h3").first).to_contain_text("sièges")
    p.keyboard.press("Tab")
    assert p.evaluate("document.activeElement.closest('#hemiList') !== null")
    href = p.evaluate("document.activeElement.getAttribute('href')")
    p.keyboard.press("Enter")
    p.wait_for_url(base_url + href)
    expect(p.locator("#sheet")).to_be_visible()


def test_nom_accessible_de_l_hemicycle(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/comprendre")
    label = p.locator("#hemi").get_attribute("aria-label")
    assert "LFI-NFP" in label and "sièges" in label


def test_vote_en_liste(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/scrutin/9895")
    det = p.locator("#voteList")
    det.locator("summary").click()
    v = p.evaluate(DATA + ".votes.find(v=>v.n===9895)")
    voted = sum(1 for c in v["v"] if c in "pca")
    expect(det.locator("li")).to_have_count(len(v["v"]))
    expect(det).to_contain_text("Pour (%d)" % sum(1 for c in v["v"] if c == "p"))


def test_fiche_piege_le_focus(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/depute")
    p.locator('#deplist a[href="/depute/antoine-golliot"]').focus()
    p.keyboard.press("Enter")
    expect(p.locator("#sheet")).to_be_visible()
    for _ in range(40):
        p.keyboard.press("Tab")
        assert p.evaluate("document.activeElement.closest('#sheet') !== null")
    for _ in range(5):
        p.keyboard.press("Shift+Tab")
        assert p.evaluate("document.activeElement.closest('#sheet') !== null")


def test_mouvement_reduit(browser, base_url):
    ctx = browser.new_context(reduced_motion="reduce")
    p = ctx.new_page()
    p.goto(base_url + "/jouer/groupe")
    longues = p.evaluate("""() => [...document.querySelectorAll('*')].filter(e => {
        const s = getComputedStyle(e);
        return s.transitionDuration.split(',').some(d => parseFloat(d) > 0.01) || s.animationDuration.split(',').some(d => parseFloat(d) > 0.01);
    }).map(e => e.className || e.tagName).slice(0, 5)""")
    ctx.close()
    assert not longues, longues
