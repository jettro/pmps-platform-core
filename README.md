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

### Development mode (default)

While you are actively working on `platform-framework` at the same time, keep the
editable path sources active (already the default):

```toml
# root pyproject.toml
[tool.uv.sources]
framework-core  = { path = "../platform-framework/packages/framework-core",  editable = true }
framework-infra = { path = "../platform-framework/packages/framework-infra", editable = true }
```

Any change you make in `platform-framework` is instantly visible here because uv
mounts the source directory directly — no reinstall needed.

### Released mode

Once you have published framework wheels to the local private PyPI index, switch by
**commenting out** the path sources and **uncommenting** the index sources:

```toml
# root pyproject.toml
[tool.uv.sources]
# framework-core  = { path = "../platform-framework/packages/framework-core",  editable = true }
# framework-infra = { path = "../platform-framework/packages/framework-infra", editable = true }
framework-core  = { index = "local" }
framework-infra = { index = "local" }
```

Then run `uv sync` to pull the pinned wheels from `http://localhost:8080`.

## How sales-application consumes these packages

`sales-application` adds `core-domain` and `core-services` as dependencies. In its
workspace root `pyproject.toml` it declares:

```toml
# DEVELOPMENT MODE (parallel local development)
[tool.uv.sources]
core-domain   = { path = "../platform-core/packages/core-domain",   editable = true }
core-services = { path = "../platform-core/packages/core-services",  editable = true }

# RELEASED MODE (after `make publish` here)
# core-domain   = { index = "local" }
# core-services = { index = "local" }
```

Same two-mode pattern — switch by commenting/uncommenting a single block.

## Build and publish

```bash
# Build wheel archives for both packages
make build

# Upload to the local private PyPI server (must be running on :8080)
make publish
```

After publishing, downstream repos switch to released mode and run `uv sync` to pull
the pinned wheels.

## Common tasks

```bash
make sync        # Install / refresh the virtual environment
make test        # Run the full test suite with pytest
make check-lock  # Verify uv.lock is up to date (useful in CI)
```
