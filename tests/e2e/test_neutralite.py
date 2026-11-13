import re
import pytest

INTERDITS = ["large", "écrasant", "écrasante", "serré", "serrée", "victoire", "défaite", "surprise", "fidèle", "fidélité", "frondeur", "frondeuse", "discipliné", "cohésion"]
PAGES = ["/", "/votes", "/scrutin/9895", "/groupes", "/groupes/rn", "/lexique", "/depute/antoine-golliot", "/comprendre", "/jouer"]


@pytest.mark.parametrize("path", PAGES)
def test_neutralite(page_desktop, base_url, path):
    p = page_desktop
    p.goto(base_url + path)
    p.wait_for_timeout(100)
    # les titres et textes officiels (intitulés, résumés des textes) sont exclus : seuls les textes du site sont contrôlés
    texte = p.evaluate("""() => { const c = document.body.cloneNode(true);
        c.querySelectorAll('[data-officiel], script, style, [hidden]').forEach(e => e.remove());
        return c.innerText || c.textContent; }""")
    mots = set(re.findall(r"[a-zàâçéèêëîïôûùüÿœ-]+", texte.lower()))
    trouves = [m for m in INTERDITS if m in mots]
    assert not trouves, trouves


@pytest.mark.parametrize("path,sel", [("/votes", "#vlist .vtitle"), ("/", "#homeVotes .vtitle"), ("/", "#homeVotes .vbref"),
                                      ("/scrutin/9895", ".stitle"), ("/groupes/rn", ".gv a"), ("/depute/antoine-golliot", "#sheet .dvote a")])
def test_textes_officiels_marques(page_desktop, base_url, path, sel):
    p = page_desktop
    p.goto(base_url + path)
    els = p.locator(sel)
    assert els.count() > 0
    assert all(els.nth(i).evaluate("e => e.closest('[data-officiel]') !== null") for i in range(min(els.count(), 5)))
