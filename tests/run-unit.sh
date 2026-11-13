#!/bin/sh
# Tests unitaires (pytest) dans un conteneur jetable : rien n'est installé sur l'hôte.
cd "$(dirname "$0")/.." || exit 1
exec docker run --rm --name "ho-test-unit-$$" --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$PWD":/w -w /w python:3.12-slim \
  sh -c 'pip install -q --user --disable-pip-version-check pytest==8.3.3 2>/dev/null && python -m pytest -p no:cacheprovider tests/unit "$@"' -- "$@"
