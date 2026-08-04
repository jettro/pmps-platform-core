.PHONY: \
	git-status \
	sync dev-release dev-framework dev-status \
	test build publish check-lock assert-release

INDEX_ENV := ../local-pypi/.env

git-status:
	@./scripts/git-status.sh . platform-core
	@./scripts/select-sources.py status

sync: dev-release

dev-release:
	@set -a; test ! -f $(INDEX_ENV) || . $(INDEX_ENV); set +a; \
		./scripts/select-sources.py release

dev-framework:
	@set -a; test ! -f $(INDEX_ENV) || . $(INDEX_ENV); set +a; \
		./scripts/select-sources.py framework

dev-status:
	@./scripts/select-sources.py status

test:
	@test -x .venv/bin/python || (echo "No development environment. Run 'make dev-release' or 'make dev-framework' first." >&2; exit 1)
	.venv/bin/python -m pytest packages

build:
	uv build --no-sources --package core-domain --out-dir dist
	uv build --no-sources --package core-services --out-dir dist

publish:
	@test -f ../local-pypi/.env || (echo "Run 'make pypi-init-auth' in the coordination repo first." >&2; exit 1)
	@set -a; . ../local-pypi/.env; set +a; uv publish --publish-url http://localhost:8080 dist/*.whl

check-lock:
	uv lock --check

assert-release:
	@./scripts/select-sources.py check release
