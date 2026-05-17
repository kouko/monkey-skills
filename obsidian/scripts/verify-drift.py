#!/usr/bin/env python3
"""CI gate: verify every language-policy.md functional copy is byte-identical
to the expected payload *(SSOT header + canonical content)*.

- Exit 0: all functional copies match expected.
- Exit 1: drift detected or a functional copy is missing. Each failure prints
  path + first-diff-line so the failure is actionable in CI logs.
- Exit 2: setup error (canonical file absent).

Repair locally with ``python3 obsidian/scripts/distribute.py``.

Pure stdlib (pathlib, sys, argparse). No network, no third-party deps.
Imports routing table + expected-payload helper from distribute.py so the
two scripts cannot disagree on what "expected" means.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    CANONICAL,
    OBSIDIAN_ROOT,
    TARGETS,
    expected_payload,
)


def _first_diff_line(expected: bytes, actual: bytes) -> str | None:
    """Return the first line where expected and actual diverge, or None."""
    exp_lines = expected.decode("utf-8", errors="replace").splitlines()
    act_lines = actual.decode("utf-8", errors="replace").splitlines()
    for i, (e, a) in enumerate(zip(exp_lines, act_lines)):
        if e != a:
            return f"line {i + 1}: expected {e!r}, got {a!r}"
    if len(exp_lines) != len(act_lines):
        return (
            f"line count mismatch: expected {len(exp_lines)}, got {len(act_lines)}"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify every language-policy.md functional copy is byte-identical "
            "to the expected payload (SSOT header + canonical). "
            "Exit 0 = all match; exit 1 = drift; exit 2 = setup error. "
            "Fix drift with: python3 obsidian/scripts/distribute.py"
        )
    )
    # MVP: --help only; no positional args needed.
    parser.parse_args(argv)

    if not CANONICAL.is_file():
        print(
            f"ERROR: canonical missing: "
            f"{CANONICAL.relative_to(OBSIDIAN_ROOT.parent)}",
            file=sys.stderr,
        )
        return 2

    expected = expected_payload()
    failures: list[str] = []
    checked = 0

    for rel_dst in TARGETS:
        dst = OBSIDIAN_ROOT / rel_dst
        if not dst.is_file():
            failures.append(f"MISSING  obsidian/{rel_dst}")
            continue
        actual = dst.read_bytes()
        checked += 1
        if actual == expected:
            continue
        diff = _first_diff_line(expected, actual)
        failures.append(
            f"DRIFT    obsidian/{rel_dst}"
            + (f"\n         first diff: {diff}" if diff else "")
        )

    if failures:
        for line in failures:
            print(line)
        print(
            f"\nFAIL: drift detected "
            f"(checked {checked} of {len(TARGETS)} functional copies)."
            f"\nFix: python3 obsidian/scripts/distribute.py"
        )
        return 1

    print(
        f"OK: all {checked} functional copies match canonical + SSOT header."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
