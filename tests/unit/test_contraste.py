import json, os, re
import pytest

TEXTE = ["--ink", "--muted", "--accent", "--pour", "--contre", "--pour-ink", "--contre-ink", "--abst-ink"]
FONDS = ["--bg", "--surface", "--surface-2"]


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + 0.05) / (y + 0.05)


def blocs(root):
    css = open(os.path.join(root, "src", "ui", "base.css"), encoding="utf-8").read()
    out = []
    for m in re.finditer(r"(:root(?:\[data-theme=\"dark\"\]|:not\(\[data-theme=\"light\"\]\))?)\{([^}]*)\}", css):
        out.append((m.group(1), dict(re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})", m.group(2)))))
    return out


def test_trois_themes(root):
    b = blocs(root)
    assert len(b) == 3, [x[0] for x in b]


@pytest.mark.parametrize("i", [0, 1, 2])
def test_jetons(root, i):
    nom, t = blocs(root)[i]
    bad = [(f, g, round(ratio(t[f], t[g]), 2)) for f in TEXTE for g in FONDS if ratio(t[f], t[g]) < 4.5]
    assert not bad, (nom, bad)


def test_couleurs_de_groupe(data):
    def text_on(h):  # même règle que textColorOn() dans core.js : la couleur la plus contrastée
        return "#ffffff" if ratio(h, "#ffffff") >= ratio(h, "#111111") else "#111111"
    bad = [(g["a"], round(ratio(g["col"], text_on(g["col"])), 2)) for g in data["groups"] if ratio(g["col"], text_on(g["col"])) < 4.5]
    assert not bad, bad
