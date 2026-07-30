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

### Deployment modes

The root manifest remains optimized for editable host development. Release, Git, and
non-editable local image sources are selected by independent manifests and locks under the
sales application's `docker/modes` directory.

## How sales-application consumes these packages

`sales-application` uses editable paths on the host. Its Docker-specific manifests select
released wheels, exact Git commits, or neighbouring non-editable source snapshots without
editing this repository's development configuration.

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
