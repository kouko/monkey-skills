#!/usr/bin/env python3
"""Distribute sibling-neutral loom family policies into both plugins.

Each destination is byte-identical to ``header_for(source) + source bytes``.
Run without arguments to regenerate the copies, or with ``--check`` to fail
on a missing or divergent copy without changing the filesystem.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_CANONICAL = "scripts/canonical/loom-family"
_ARTIFACT_CANONICAL = "scripts/canonical/loom-artifacts"
_CODE_HOOKS = "loom-code/hooks"
_DESIGN_REFERENCES = "loom-design/skills/using-loom-design/references"
ROUTE: dict[str, tuple[str, ...]] = {
    f"{_CANONICAL}/{name}": (
        f"{_CODE_HOOKS}/{name}",
        f"{_DESIGN_REFERENCES}/{name}",
    )
    for name in ("family-reception.md", "family-relay.md", "plain-relay.md")
}
ROUTE[f"{_ARTIFACT_CANONICAL}/requirement-identifiers.md"] = (
    "loom-design/skills/spec-expansion/references/requirement-identifiers.md",
    "loom-code/skills/writing-plans/references/requirement-identifiers.md",
)

PLUGIN_INTERNAL_PATH = re.compile(
    rb"(?:loom-code|loom-design)/(?:hooks|skills|scripts)/"
)


def header_for(source_rel: str) -> str:
    """Return the managed-copy header for ``source_rel``."""
    return (
        "<!--\n"
        "FUNCTIONAL COPY — DO NOT EDIT IN PLACE\n"
        f"SSOT: {source_rel}\n"
        "Sync via: scripts/sync_loom_family_contracts.py\n"
        "-->\n\n"
    )


def expected_payload(source_rel: str) -> bytes:
    """Return the exact bytes required at the routed destination."""
    return header_for(source_rel).encode("utf-8") + (
        REPO_ROOT / source_rel
    ).read_bytes()


def sync() -> int:
    """Write every routed functional copy and return the number written."""
    written = 0
    for source_rel, destination_rels in ROUTE.items():
        source = REPO_ROOT / source_rel
        if not source.is_file():
            raise FileNotFoundError(f"SSOT missing: {source_rel}")
        source_bytes = source.read_bytes()
        if PLUGIN_INTERNAL_PATH.search(source_bytes):
            raise ValueError(f"plugin-internal path in SSOT: {source_rel}")
        payload = expected_payload(source_rel)
        for destination_rel in destination_rels:
            destination = REPO_ROOT / destination_rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            print(f"[sync] {source_rel} -> {destination_rel}")
            written += 1
    return written


def check() -> int:
    """Return 0 when every copy matches; report drift and return 1 otherwise."""
    failures: list[str] = []
    checked = 0
    for source_rel, destination_rels in ROUTE.items():
        source = REPO_ROOT / source_rel
        if not source.is_file():
            failures.append(f"MISSING-SSOT {source_rel}")
            continue
        source_bytes = source.read_bytes()
        if PLUGIN_INTERNAL_PATH.search(source_bytes):
            failures.append(f"PLUGIN-INTERNAL-PATH {source_rel}")
        expected = expected_payload(source_rel)
        for destination_rel in destination_rels:
            destination = REPO_ROOT / destination_rel
            if not destination.is_file():
                failures.append(f"MISSING {destination_rel}")
                continue
            destination_bytes = destination.read_bytes()
            checked += 1
            if PLUGIN_INTERNAL_PATH.search(destination_bytes):
                failures.append(f"PLUGIN-INTERNAL-PATH {destination_rel}")
            if destination_bytes != expected:
                failures.append(
                    f"DRIFT {destination_rel} (SSOT: {source_rel})"
                )

    if failures:
        for failure in failures:
            print(failure)
        print("Fix: python3 scripts/sync_loom_family_contracts.py")
        return 1

    print(
        f"OK: all {checked} loom family policy copies match "
        "their SSOT plus managed-copy header."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify copies without writing",
    )
    args = parser.parse_args()
    if args.check:
        return check()
    sync()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
