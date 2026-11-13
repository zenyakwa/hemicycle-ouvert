#!/bin/sh
# Tests d'interface : construit l'image du site depuis le Dockerfile, la lance sur un
# réseau Docker privé (aucun port publié) et pilote Chromium sans affichage (Playwright).
set -e
cd "$(dirname "$0")/.."
python3 src/prep.py >/dev/null
NET=ho-test-net-$$; SITE=ho-test-site-$$
cleanup(){ docker stop "$SITE" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM
docker build -q -t ho-test-site . >/dev/null
docker network create "$NET" >/dev/null
docker run -d --rm --name "$SITE" --network "$NET" ho-test-site >/dev/null
docker run --rm --name "ho-test-e2e-$$" --network "$NET" --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -e BASE_URL="http://$SITE" -e ETAPE="${ETAPE:-}" -v "$PWD":/w -w /w \
  mcr.microsoft.com/playwright/python:v1.48.0-jammy \
  sh -c 'pip install -q --user --disable-pip-version-check pytest==8.3.3 pytest-playwright==0.5.2 playwright==1.48.0 2>/dev/null && python -m pytest -p no:cacheprovider tests/e2e "$@"' -- "$@"
