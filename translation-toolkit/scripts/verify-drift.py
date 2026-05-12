#!/usr/bin/env python3
"""Verify each canonical/* file is byte-identical to all functional copies.

Exit 0 -> all good (or no copies expected yet).
Exit 1 -> at least one drift detected (canonical and functional copy differ,
          or canonical exists but functional copy is missing for an active skill
          that already has the routed subfolder).

CI gate: runs after every PR / push to enforce SSOT discipline (spec Decision #14).
"""
from __future__ import annotations

import filecmp
import sys
from pathlib import Path

# Reuse routing from distribute.py for consistency.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    ACTIVE_SKILLS,
    CANONICAL,
    ROOT,
    iter_canonical_files,
    route,
)


def main() -> int:
    if not CANONICAL.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL}", file=sys.stderr)
        return 2

    drifts: list[str] = []
    checked = 0

    for rel, src in iter_canonical_files():
        target = route(rel)
        if target is None or target == "__UNROUTED__":
            continue
        subfolder, dst_name = target  # type: ignore[misc]
        for skill in ACTIVE_SKILLS:
            dst = ROOT / "skills" / skill / subfolder / dst_name
            if not dst.exists():
                drifts.append(f"MISSING  {dst.relative_to(ROOT)}")
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    f"DRIFT    {dst.relative_to(ROOT)} differs from canonical/{rel}"
                )
            checked += 1

    if drifts:
        for d in drifts:
            print(d)
        print(f"\nFAIL: {len(drifts)} drift(s) detected (checked {checked} pairs).")
        return 1

    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
