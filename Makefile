.PHONY: sync test build publish check-lock

sync:
	uv sync

test:
	uv run pytest

build:
	uv build --package core-domain
	uv build --package core-services

publish:
	UV_PUBLISH_USERNAME=any UV_PUBLISH_PASSWORD=any uv publish --publish-url http://localhost:8080 dist/*.whl

check-lock:
	uv lock --check
