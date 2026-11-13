import json, os, urllib.error, urllib.request
import pytest


def get(base, path, gzip=False):
    req = urllib.request.Request(base + path, headers={"Accept-Encoding": "gzip"} if gzip else {})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, dict((k.lower(), v) for k, v in r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict((k.lower(), v) for k, v in e.headers.items()), b""


@pytest.mark.parametrize("path", ["/depute/antoine-golliot", "/votes/sante", "/nimporte/quoi", "/scrutin/9895"])
def test_toute_adresse_sert_index(base_url, path):
    s0, _, home = get(base_url, "/")
    s, h, body = get(base_url, path)
    assert s == 200 and h["content-type"].startswith("text/html") and body == home


@pytest.mark.parametrize("path", ["/logos/absent.png", "/absent.js", "/depute/x.json"])
def test_fichier_absent_404(base_url, path):
    assert get(base_url, path)[0] == 404


def test_gzip_et_cache_court(base_url):
    s, h, _ = get(base_url, "/", gzip=True)
    assert h.get("content-encoding") == "gzip"
    assert "no-cache" in h.get("cache-control", "")
    s, h, _ = get(base_url, "/votes", gzip=True)
    assert "no-cache" in h.get("cache-control", "")


def test_logos_presents_et_caches(base_url):
    logos = sorted(f for f in os.listdir("logos") if f.rsplit(".", 1)[-1] in ("svg", "png", "webp"))
    assert logos, "aucun logo dans logos/"
    for f in logos:
        s, h, _ = get(base_url, "/logos/" + f)
        assert s == 200, f
        assert "max-age=604800" in h.get("cache-control", ""), f


def test_cp_json(base_url):
    s, h, body = get(base_url, "/cp.json", gzip=True)
    assert s == 200 and h["content-type"].startswith("application/json")
    assert "max-age=3600" in h.get("cache-control", "")
    assert h.get("content-encoding") == "gzip"
