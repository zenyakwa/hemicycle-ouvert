import pytest

PAGES = ["/", "/votes", "/scrutin/9895", "/depute/antoine-golliot", "/groupes", "/groupes/rn", "/lexique", "/jouer/devine", "/comprendre"]

MESURE = r"""() => {
  const parse = s => {
    let m = s.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = s.match(/color\(srgb ([^)]+)\)/);
    if (m) { const p = m[1].split(/[ \/]+/).filter(Boolean).map(Number); return [p[0]*255, p[1]*255, p[2]*255, p.length > 3 ? p[3] : 1]; }
    return [0, 0, 0, 0];
  };
  const over = (top, bot) => { const a = top[3]; return [0,1,2].map(i => top[i]*a + bot[i]*(1-a)).concat([1]); };
  const fond = el => {
    const pile = [];
    for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c[3] > 0) { pile.push(c); if (c[3] >= 1) break; } }
    let c = [255, 255, 255, 1];
    for (let i = pile.length - 1; i >= 0; i--) c = over(pile[i], c);
    return c;
  };
  const L = c => { const v = c.slice(0,3).map(x => { x /= 255; return x <= 0.03928 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); }); return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2]; };
  const R = (a, b) => { const x = L(a), y = L(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); };
  const out = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const vus = new Set();
  while (w.nextNode()) {
    const t = w.currentNode; if (!t.textContent.trim()) continue;
    const el = t.parentElement; if (vus.has(el)) continue; vus.add(el);
    if (el.closest('svg, [hidden], .sr-only, .gbadge, script, style, .tip, .pop')) continue;
    const r = el.getBoundingClientRect(), st = getComputedStyle(el);
    if (r.width < 2 || r.height < 2 || st.visibility === 'hidden' || st.opacity === '0' || el.offsetParent === null && st.position !== 'fixed') continue;
    const bg = fond(el), fg = over(parse(st.color), bg);
    const size = parseFloat(st.fontSize), bold = parseInt(st.fontWeight) >= 700;
    const min = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
    const ratio = R(fg, bg);
    if (ratio < min) out.push(`${(el.className||el.tagName)} « ${t.textContent.trim().slice(0,25)} » ${ratio.toFixed(2)}`);
  }
  return out;
}"""


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("path", PAGES)
def test_contraste(browser, base_url, path, scheme):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, color_scheme=scheme)
    p = ctx.new_page()
    p.goto(base_url + path)
    p.wait_for_timeout(150)
    bad = p.evaluate(MESURE)
    ctx.close()
    assert not bad, bad[:12]
