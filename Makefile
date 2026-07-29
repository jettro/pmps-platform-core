.PHONY: sync test build publish check-lock

sync:
	uv sync

test:
	uv run pytest

build:
	uv build --package core-domain
	uv build --package core-services

publish:
	uv publish --publish-url http://localhost:8080 packages/core-domain/dist/*.whl
	uv publish --publish-url http://localhost:8080 packages/core-services/dist/*.whl

check-lock:
	uv lock --check
