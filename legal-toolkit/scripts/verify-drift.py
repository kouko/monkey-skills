#!/usr/bin/env python3
"""Verify each ROUTE destination is byte-identical to its canonical source.

Exit 0 -> every routed destination exists and matches canonical.
Exit 1 -> at least one drift (mismatch, missing file, or missing canonical).

No auto-skip — every entry in ROUTE is mandatory. Update ROUTE in the same
commit that creates (or removes) a consuming skill.

CI gate: runs after every PR / push that touches legal-toolkit/.
"""
from __future__ import annotations

import filecmp
import hashlib
import subprocess
import sys
from pathlib import Path

# Reuse routing from distribute.py for consistency.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    CANONICAL_DIR,
    ROOT,
    ROUTE,
)


def verify_drift(
    route: dict[str, list[str]] | None = None,
    root: Path | None = None,
) -> int:
    """Return 0 if every routed destination matches its canonical source; 1
    otherwise. Pure function — does not touch the real filesystem unless
    `root` defaults to ROOT.
    """
    if route is None:
        route = ROUTE
    if root is None:
        root = ROOT
    canonical_dir = root / "scripts" / "canonical"

    drifts: list[str] = []
    checked = 0
    for canonical_name, destinations in route.items():
        src = canonical_dir / canonical_name
        if not src.is_file():
            drifts.append(f"MISSING-CANONICAL  scripts/canonical/{canonical_name}")
            continue
        for rel_dst in destinations:
            dst = root / rel_dst
            if not dst.is_file():
                drifts.append(f"MISSING  {rel_dst}")
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}"
                )
            checked += 1
    if drifts:
        for d in drifts:
            print(d)
        return 1
    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0


def _md5(path: Path) -> str:
    # usedforsecurity=False keeps this working on FIPS-140 systems (md5 is
    # used here as a fingerprint for the drift report, not a security primitive).
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()


def _print_unified_diff(reference: Path, drift_path: Path, max_lines: int = 50) -> None:
    """Print up to max_lines of `diff -u` output so reviewers see WHAT differs,
    not just THAT it differs. Also print md5 for both files.
    """
    print(f"    md5(canonical) = {_md5(reference)}")
    print(f"    md5(copy)      = {_md5(drift_path)}")
    try:
        out = subprocess.run(
            ["diff", "-u", str(reference), str(drift_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        text = out.stdout or out.stderr or ""
        lines = text.splitlines()
        for line in lines[:max_lines]:
            print(f"    {line}")
        if len(lines) > max_lines:
            print(f"    ... ({len(lines) - max_lines} more lines truncated)")
    except FileNotFoundError:
        print("    (diff binary unavailable)")


def main() -> int:
    if not CANONICAL_DIR.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL_DIR}", file=sys.stderr)
        return 2

    drifts: list[tuple[str, Path | None, Path | None]] = []
    checked = 0
    for canonical_name, destinations in ROUTE.items():
        src = CANONICAL_DIR / canonical_name
        if not src.is_file():
            drifts.append(
                (f"MISSING-CANONICAL  scripts/canonical/{canonical_name}", None, None)
            )
            continue
        for rel_dst in destinations:
            dst = ROOT / rel_dst
            if not dst.is_file():
                drifts.append((f"MISSING  {rel_dst}", None, None))
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    (
                        f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}",
                        src,
                        dst,
                    )
                )
            checked += 1

    if drifts:
        for label, ref, drift_path in drifts:
            print(label)
            if ref is not None and drift_path is not None:
                _print_unified_diff(ref, drift_path)
        print(f"\nFAIL: {len(drifts)} drift(s) detected (checked {checked} pairs).")
        print("\nFix locally: python3 legal-toolkit/scripts/distribute.py")
        return 1

    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
