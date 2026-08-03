.PHONY: \
	git-status \
	sync dev-release dev-framework dev-status \
	test build publish check-lock check-dev-locks

DEV_ENV := $(CURDIR)/.venv
INDEX_ENV := ../local-pypi/.env

git-status:
	@./scripts/git-status.sh . platform-core

sync: dev-release

dev-release:
	@test -f $(INDEX_ENV) || (echo "Released framework dependencies need local index credentials. Run 'make pypi-init-auth' in the coordination repo first." >&2; exit 1)
	@set -a; . $(INDEX_ENV); set +a; \
		UV_PROJECT_ENVIRONMENT=$(DEV_ENV) uv sync --locked --all-groups
	@printf '%s\n' release > .dev-profile
	@echo "Active core profile: release (framework packages come from the index)"

dev-framework:
	@test -d ../platform-framework/packages/framework-core || (echo "platform-framework is not checked out. Run 'make checkout-framework' in the coordination repo." >&2; exit 1)
	@UV_PROJECT_ENVIRONMENT=$(DEV_ENV) uv sync --project dev/profiles/framework --locked --all-groups
	@printf '%s\n' framework > .dev-profile
	@echo "Active core profile: framework (framework source)"

dev-status:
	@if test -f .dev-profile; then \
		printf 'Active core profile: '; cat .dev-profile; \
	else \
		echo "Active core profile: not synced (release is the default)"; \
	fi

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

check-dev-locks:
	uv lock --project dev/profiles/framework --check
