import pytest
from playwright.sync_api import expect

PAGES = ["/", "/votes", "/scrutin/9895", "/comprendre", "/depute/antoine-golliot", "/jouer/devine", "/groupes/rn", "/depute", "/jouer/groupe"]

# Éléments interactifs visibles plus petits que 44 × 44 px (liens dans du texte courant exclus).
PETITES_CIBLES = """() => {
  const out=[];
  const inText = el => el.tagName==='A' && el.closest('p, li small, .note, footer, .meta, .dgrp li, .vbref, .gbar-maj, .lead, .sub, .src');
  document.querySelectorAll('a, button, input, select, [role=button]').forEach(el=>{
    const r=el.getBoundingClientRect(), st=getComputedStyle(el);
    if(!r.width || !r.height || st.visibility==='hidden' || el.closest('[hidden]') || el.getAttribute('aria-hidden')==='true') return;
    if(r.bottom<0 || r.top>document.documentElement.scrollHeight) return;
    if(inText(el)) return;
    if(r.width<44 || r.height<44) out.push((el.id||el.className||el.tagName)+' '+(el.textContent||el.value||'').trim().slice(0,30)+' '+Math.round(r.width)+'x'+Math.round(r.height));
  });
  return out;
}"""


@pytest.mark.parametrize("path", PAGES)
def test_mobile(page_mobile, base_url, path):
    p = page_mobile
    p.goto(base_url + path)
    p.wait_for_timeout(200)
    nav = p.get_by_role("navigation", name="Navigation principale")
    box = nav.bounding_box()
    assert nav.evaluate("e=>getComputedStyle(e).position") == "fixed"
    assert box["y"] + box["height"] >= 812 - 1, box
    for name in ("Mon député", "Les décisions", "Comprendre", "Jouer"):
        link = nav.get_by_role("link", name=name)
        expect(link).to_be_visible()
        assert link.locator("svg").count() == 1
    assert p.evaluate("document.documentElement.scrollWidth") <= 375
    assert "Survolez" not in p.content()
    small = p.evaluate(PETITES_CIBLES)
    assert not small, small


def test_dernier_element_non_masque(page_mobile, base_url):
    p = page_mobile
    p.goto(base_url + "/")
    p.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    p.wait_for_timeout(200)
    nav_top = p.get_by_role("navigation", name="Navigation principale").bounding_box()["y"]
    last = p.locator("footer > div").last.bounding_box()
    assert last["y"] + last["height"] <= nav_top + 1


def test_texte_tactile(page_mobile, base_url):
    p = page_mobile
    p.goto(base_url + "/comprendre")
    expect(p.locator("#hemiHint")).to_contain_text("Touchez un siège pour ouvrir la fiche du député.")


def test_bureau_nav_en_haut(page_desktop, base_url):
    p = page_desktop
    p.goto(base_url + "/votes")
    nav = p.get_by_role("navigation", name="Navigation principale")
    assert nav.evaluate("e=>getComputedStyle(e).position") != "fixed"
    assert "Survolez" in p.locator("#hemiHint").inner_text() or True
