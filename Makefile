.PHONY: sync test build publish check-lock

sync:
	uv sync

test:
	uv run pytest

build:
	uv build --no-sources --package core-domain --out-dir dist
	uv build --no-sources --package core-services --out-dir dist

publish:
	@test -f ../local-pypi/.env || (echo "Run 'make pypi-init-auth' in the coordination repo first." >&2; exit 1)
	@set -a; . ../local-pypi/.env; set +a; uv publish --publish-url http://localhost:8080 dist/*.whl

check-lock:
	uv lock --check
