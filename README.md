# platform-core

Shared domain primitives for the product catalog — consumed by `sales-application`
and any other application in this project that needs to work with products, prices,
and addresses.

## What's inside

| Package | Description |
|---|---|
| `core-domain` | Value objects (`Money`, `Address`) and the `Product` entity |
| `core-services` | Application services (`ProductService`, `CatalogQuery`) over those entities |

`core-domain` is pure domain logic with zero infrastructure dependencies.
`core-services` depends on the `Repository` protocol from `platform-framework` so it
can be wired to any store (in-memory, file, database) without coupling to one.

## Dependencies

Both packages consume `platform-framework` (framework-core / framework-infra).
How those cross-repo packages are resolved is controlled by the workspace root
`pyproject.toml` — **not** by individual package configs.

### Released mode (default)

The root manifest resolves framework packages from the authenticated named index:

```toml
[tool.uv.sources]
framework-core = { index = "local" }
framework-infra = { index = "local" }
```

Select editable framework source only when changing framework itself:

```bash
make dev-release    # released framework
make dev-framework  # editable sibling framework
make dev-status
```

Both commands update the same root manifest and lock and synchronize into
`platform-core/.venv`, so the IDE sees one project and interpreter. The presence of a
framework checkout never changes dependencies by itself. Return to `dev-release` before
committing or pulling.

## How sales-application consumes these packages

`sales-application` consumes released core wheels by default and exposes an explicit
`dev-core` mode for editable core source. Its image inputs select released wheels, exact
Git commits, or neighbouring non-editable source snapshots.

## Build and publish

```bash
# Build wheel archives for both packages
make build

# Upload to the local private PyPI server (must be running on :8080)
make publish
```

After publishing, downstream repos run `make dev-release` to pull their pinned wheels.

## Common tasks

```bash
make sync        # Alias for the released profile
make test        # Run the full test suite with pytest
make check-lock  # Verify uv.lock is up to date (useful in CI)
```
