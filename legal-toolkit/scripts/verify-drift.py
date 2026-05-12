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


if __name__ == "__main__":
    sys.exit(verify_drift())
