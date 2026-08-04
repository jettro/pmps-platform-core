#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "pyproject.toml"
LOCK = ROOT / "uv.lock"
START = "# BEGIN GENERATED DEVELOPMENT SOURCES"
END = "# END GENERATED DEVELOPMENT SOURCES"

INTERNAL = ("framework-core", "framework-infra")
WORKSPACE = {
    "core-domain": {"workspace": True},
    "core-services": {"workspace": True},
}
INDEX = {"index": "local"}
SOURCES = {
    "release": {
        **WORKSPACE,
        "framework-core": INDEX,
        "framework-infra": INDEX,
    },
    "framework": {
        **WORKSPACE,
        "framework-core": {
            "path": "../platform-framework/packages/framework-core",
            "editable": True,
        },
        "framework-infra": {
            "path": "../platform-framework/packages/framework-infra",
            "editable": True,
        },
    },
}


def atomic_write(path: Path, content: bytes) -> None:
    permissions = path.stat().st_mode & 0o777 if path.exists() else 0o644
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    os.chmod(temporary, permissions)
    os.replace(temporary, path)


def load(path: Path) -> dict:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def toml_value(value: object) -> str:
    if value is True:
        return "true"
    if isinstance(value, str):
        return f'"{value}"'
    raise TypeError(f"unsupported TOML value: {value!r}")


def render(mode: str) -> str:
    lines = [START, "[tool.uv.sources]"]
    for name, source in SOURCES[mode].items():
        fields = ", ".join(f"{key} = {toml_value(value)}" for key, value in source.items())
        lines.append(f"{name} = {{ {fields} }}")
    lines.append(END)
    return "\n".join(lines)


def replace_sources(text: str, mode: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise RuntimeError("managed source markers are missing or duplicated")
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    candidate = before + render(mode) + after
    tomllib.loads(candidate)
    return candidate


def current_mode() -> str | None:
    actual = load(MANIFEST).get("tool", {}).get("uv", {}).get("sources", {})
    return next((mode for mode, expected in SOURCES.items() if actual == expected), None)


def validate_checkouts(mode: str) -> None:
    if mode == "framework":
        path = ROOT.parent / "platform-framework" / "packages" / "framework-core"
        if not path.is_dir():
            raise RuntimeError("platform-framework is not checked out; run 'make checkout-framework'")


def validate_lock(mode: str) -> list[str]:
    if not LOCK.is_file():
        return ["uv.lock is missing"]
    packages = {item["name"]: item for item in load(LOCK).get("package", [])}
    errors: list[str] = []
    for name in INTERNAL:
        expected = SOURCES[mode][name]
        actual = packages.get(name, {}).get("source", {})
        if "index" in expected:
            if actual.get("registry", "").rstrip("/") != "http://localhost:8080/simple":
                errors.append(f"{name} is not locked to the local index")
        elif actual.get("editable") != expected["path"]:
            errors.append(f"{name} is not locked to editable path {expected['path']}")
    return errors


def check(mode: str) -> int:
    actual = current_mode()
    errors = [] if actual == mode else [f"manifest mode is {actual or 'custom'}, expected {mode}"]
    errors.extend(validate_lock(mode))
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Core source mode is {mode}; manifest and lock are valid.")
    return 0


def select(mode: str) -> int:
    validate_checkouts(mode)
    original_manifest = MANIFEST.read_bytes()
    original_lock = LOCK.read_bytes() if LOCK.exists() else None
    candidate = replace_sources(original_manifest.decode(), mode).encode()

    try:
        atomic_write(MANIFEST, candidate)
        subprocess.run(["uv", "lock"], cwd=ROOT, check=True)
        subprocess.run(["uv", "sync", "--locked", "--all-groups"], cwd=ROOT, check=True)
    except BaseException as error:
        atomic_write(MANIFEST, original_manifest)
        if original_lock is None:
            LOCK.unlink(missing_ok=True)
        else:
            atomic_write(LOCK, original_lock)
        print("Source switch failed; restored the previous manifest and lock.", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            raise RuntimeError(f"{error.cmd[0]} failed with exit code {error.returncode}") from error
        if isinstance(error, OSError):
            raise RuntimeError(f"could not run source switch command: {error}") from error
        raise

    print(f"Active core source mode: {mode}")
    return 0


def usage() -> int:
    print("Usage: select-sources.py release|framework|status|check MODE", file=sys.stderr)
    return 2


def main() -> int:
    args = sys.argv[1:]
    if args == ["status"]:
        print(f"Active core source mode: {current_mode() or 'custom'}")
        return 0
    if len(args) == 2 and args[0] == "check" and args[1] in SOURCES:
        return check(args[1])
    if len(args) == 1 and args[0] in SOURCES:
        return select(args[0])
    return usage()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
