"""Captures d'écran de fin d'étape : ETAPE=<n> tests/run-e2e.sh tests/e2e/test_captures.py"""
import os
import pytest
from conftest import capture

ETAPE = os.environ.get("ETAPE")
VUES = [("accueil", "/"), ("fiche", "/depute/antoine-golliot"), ("decisions-sante", "/votes/sante"),
        ("scrutin", "/scrutin/9895"), ("introuvable", "/depute/inexistant"), ("devine", "/jouer/devine"),
        ("groupes", "/groupes"), ("comprendre", "/comprendre"), ("mon-depute", "/depute")]


@pytest.mark.skipif(not ETAPE, reason="captures seulement en fin d'étape (ETAPE=n)")
@pytest.mark.parametrize("nom,path", VUES)
def test_captures_etape(page_any, base_url, nom, path):
    page_any.goto(base_url + path)
    page_any.wait_for_load_state("networkidle")
    page_any.wait_for_timeout(300)
    capture(page_any, ETAPE, nom, full=nom not in ("fiche", "mon-depute"))
