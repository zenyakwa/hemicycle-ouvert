from playwright.sync_api import expect


def sheet(p):
    return p.locator("#sheet")


def test_nouvel_onglet(page_desktop, base_url):
    p = page_desktop.context.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(base_url + "/depute/antoine-golliot")
    expect(sheet(p)).to_be_visible()
    expect(sheet(p).locator("h3")).to_have_text("Antoine Golliot")
    assert p.title().startswith("Antoine Golliot, député du Pas-de-Calais")
    assert not errs


def test_adresse_mal_ecrite(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/depute/Antoine-Golliot/")
    expect(sheet(p).locator("h3")).to_have_text("Antoine Golliot")
    assert p.url == base_url + "/depute/antoine-golliot"


def test_fermer_apres_ouverture_directe_reste_sur_le_site(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/depute/antoine-golliot")
    p.get_by_role("button", name="Fermer").click()
    expect(sheet(p)).to_be_hidden()
    assert p.url == base_url + "/depute"


def test_siege_puis_retour_avancer(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/comprendre")
    i = p.evaluate("JSON.parse(document.getElementById('data').textContent).deputes.findIndex(d=>d.sl==='antoine-golliot')")
    p.locator('#hemi circle[data-i="%d"]' % i).click()
    p.wait_for_url(base_url + "/depute/antoine-golliot")
    expect(sheet(p)).to_be_visible()
    p.go_back()
    p.wait_for_url(base_url + "/comprendre")
    expect(sheet(p)).to_be_hidden()
    expect(p.locator("main h1:visible")).to_have_text("Comprendre l'Assemblée")
    p.go_forward()
    p.wait_for_url(base_url + "/depute/antoine-golliot")
    expect(sheet(p)).to_be_visible()


def test_fermer_revient_a_la_vue_d_origine(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/depute")
    p.locator('#deplist a[href="/depute/antoine-golliot"]').click()
    expect(sheet(p)).to_be_visible()
    p.get_by_role("button", name="Fermer").click()
    p.wait_for_url(base_url + "/depute")
    expect(sheet(p)).to_be_hidden()


def test_echap_ferme_et_rend_le_focus(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/depute")
    link = p.locator('#deplist a[href="/depute/antoine-golliot"]')
    link.focus()
    p.keyboard.press("Enter")
    expect(sheet(p)).to_be_visible()
    p.keyboard.press("Escape")
    expect(sheet(p)).to_be_hidden()
    p.wait_for_url(base_url + "/depute")
    assert p.evaluate("document.activeElement.getAttribute('href')") == "/depute/antoine-golliot"


def test_recherche_ouvre_la_fiche(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/")
    p.get_by_role("searchbox", name="Trouver mon député").fill("Golliot")
    p.locator("#qHome-results a").first.click()
    p.wait_for_url(base_url + "/depute/antoine-golliot")
    expect(sheet(p)).to_be_visible()
