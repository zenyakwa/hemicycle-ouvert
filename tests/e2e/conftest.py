import os
import pytest

BASE = os.environ.get("BASE_URL", "http://localhost")


@pytest.fixture(scope="session")
def base_url():
    return BASE


def _page(browser, **kw):
    ctx = browser.new_context(**kw)
    page = ctx.new_page()
    page.set_default_timeout(5000)
    errors = []
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.errors = errors
    return ctx, page


@pytest.fixture
def page_desktop(browser):
    ctx, page = _page(browser, viewport={"width": 1280, "height": 800})
    yield page
    errs = list(page.errors)
    ctx.close()
    assert not errs, "Erreurs dans la console : %s" % errs


@pytest.fixture
def page_mobile(browser):
    ctx, page = _page(browser, viewport={"width": 375, "height": 812}, has_touch=True, is_mobile=True, device_scale_factor=2)
    yield page
    errs = list(page.errors)
    ctx.close()
    assert not errs, "Erreurs dans la console : %s" % errs


@pytest.fixture(params=["desktop", "mobile"])
def page_any(request):
    return request.getfixturevalue("page_" + request.param)


def capture(page, etape, nom):
    d = ".captures/etape-%s" % etape
    os.makedirs(d, exist_ok=True)
    page.screenshot(path="%s/%s-%d.png" % (d, nom, page.viewport_size["width"]), full_page=True)
