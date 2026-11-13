from playwright.sync_api import expect


def test_accueil_sans_erreur(page_any, base_url):
    page_any.goto(base_url + "/")
    expect(page_any.locator("h1").first).to_be_visible()
