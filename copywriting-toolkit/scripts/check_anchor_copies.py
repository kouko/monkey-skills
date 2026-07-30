#!/usr/bin/env python3
"""Verify byte-identity of the two INLINE-duplicated Tier 1 standards files
named in copywriting-toolkit/CLAUDE.md's "INLINE-duplicate clarification"
and "Inline-Duplication Drift Risk" sections:

- ``persuasion-psychology-anchor.md`` — 5 copies across the Phase-4 drafter
  skills (short-form, mid-form, long-form-extended, long-form-pasona,
  light-action). Canonical: copywriting-long-form-extended — the largest
  consumer of the framework (long-form copy leans hardest on persuasion
  psychology depth) and its original home in this plugin's INLINE-duplicate
  set.
- ``sns-evolution-aisas-ulssas.md`` — 2 copies (long-form-pasona,
  light-action). Canonical: copywriting-long-form-pasona — the larger of
  the two consumers and the framework's original home in this plugin.

This script does NOT decide correctness of content, only identity: every
listed copy must be byte-for-byte equal to its canonical. CLAUDE.md's
"Inline-Duplication Drift Risk" section pre-authorizes this exact script
("a sync script is acceptable") in lieu of cross-skill loading at runtime.

- Exit 0: every copy matches its canonical.
- Exit 1: drift or a missing file, with a unified diff (or MISSING marker)
  printed per failure so the failure is actionable from the CLI.

Pure stdlib.
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"

PSYCHOLOGY_CANONICAL = "copywriting-long-form-extended/standards/persuasion-psychology-anchor.md"
PSYCHOLOGY_COPIES = [
    "copywriting-short-form/standards/persuasion-psychology-anchor.md",
    "copywriting-mid-form/standards/persuasion-psychology-anchor.md",
    "copywriting-light-action/standards/persuasion-psychology-anchor.md",
    "copywriting-long-form-pasona/standards/persuasion-psychology-anchor.md",
]

AISAS_CANONICAL = "copywriting-long-form-pasona/standards/sns-evolution-aisas-ulssas.md"
AISAS_COPIES = [
    "copywriting-light-action/standards/sns-evolution-aisas-ulssas.md",
]

GROUPS = [
    ("persuasion-psychology-anchor.md", PSYCHOLOGY_CANONICAL, PSYCHOLOGY_COPIES),
    ("sns-evolution-aisas-ulssas.md", AISAS_CANONICAL, AISAS_COPIES),
]


def _read_or_none(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


def _diff_summary(label: str, canonical_rel: str, copy_rel: str, expected: bytes, actual: bytes) -> str:
    exp_lines = expected.decode("utf-8", errors="replace").splitlines()
    act_lines = actual.decode("utf-8", errors="replace").splitlines()
    diff_lines = list(
        difflib.unified_diff(
            exp_lines,
            act_lines,
            fromfile=f"canonical ({canonical_rel})",
            tofile=f"copy ({copy_rel})",
            lineterm="",
        )
    )
    max_lines = 50
    if len(diff_lines) > max_lines:
        diff_lines = diff_lines[:max_lines] + [
            f"... ({len(diff_lines) - max_lines} more diff lines truncated)"
        ]
    body = "\n".join(f"    {line}" for line in diff_lines)
    return f"DRIFT  {label}: {copy_rel}\n{body}"


def check_all(skills_root: Path) -> list[str]:
    """Return a list of failure strings; empty means every copy matches."""
    failures: list[str] = []
    for label, canonical_rel, copy_rels in GROUPS:
        canonical_path = skills_root / canonical_rel
        expected = _read_or_none(canonical_path)
        if expected is None:
            failures.append(f"MISSING-CANONICAL  {label}: {canonical_rel}")
            continue
        for copy_rel in copy_rels:
            copy_path = skills_root / copy_rel
            actual = _read_or_none(copy_path)
            if actual is None:
                failures.append(f"MISSING            {label}: {copy_rel}")
                continue
            if actual == expected:
                continue
            failures.append(_diff_summary(label, canonical_rel, copy_rel, expected, actual))
    return failures


def main(skills_root: Path = SKILLS_ROOT) -> int:
    failures = check_all(skills_root)
    if failures:
        for failure in failures:
            print(failure)
        print(f"\nFAIL: {len(failures)} drift/missing issue(s) detected.")
        return 1
    print(
        f"OK: all {len(PSYCHOLOGY_COPIES)} persuasion-psychology-anchor.md copies "
        f"+ {len(AISAS_COPIES)} sns-evolution-aisas-ulssas.md copy(ies) "
        "match their canonical."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
