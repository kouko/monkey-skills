#!/usr/bin/env python3
"""Distribute canonical/* files to each active skill as byte-identical functional copies.

SSOT-and-functional-copy pattern (spec Decision #14):
  scripts/canonical/<file>      -> single source of truth (authored here)
  <skill>/<subfolder>/<file>    -> byte-identical functional copy (Edit forbidden)

Routing:
  - core-loop / 4d-reflection / 5d-effectiveness / orthogonal-axes /
    verification-gates / audit-trail-spec  -> references/
  - jlreq-summary / clreq-summary / requirements-for-japanese-text-layout-summary
    -> typography/
  - nict-en-ja-zh / opus-en-zh-tw / wmt-* -> corpus/
  - glossary-*--*.md (bidirectional pair files) -> glossary/
  - manual-entries-*--*.md -> NOT distributed (per-skill authored, not SSOT)

Workflow:
  1. Edit a file under scripts/canonical/.
  2. Run `python3 scripts/distribute.py` from the plugin root.
  3. Commit the canonical edit AND the functional-copy updates in the same commit.

CI runs `verify-drift.py` to enforce byte-identical copies.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "scripts" / "canonical"

ACTIVE_SKILLS = [
    "translation-i18n",
    "translation-doc",
    "translation-creative",
    "translation-audit",
]

REFERENCE_FILES = {
    "core-loop.md",
    "4d-reflection.md",
    "5d-effectiveness.md",
    "orthogonal-axes.md",
    "verification-gates.md",
    "audit-trail-spec.md",
    "protect-pass-spec.md",
}

TYPOGRAPHY_FILES = {
    "jlreq-summary.md",
    "clreq-summary.md",
    "requirements-for-japanese-text-layout-summary.md",
}

CORPUS_FILES = {
    "nict-en-ja-zh.md",
    "opus-en-zh-tw.md",
    "wmt-en-ja.md",
    "wmt-en-zh.md",
}

GLOSSARY_PREFIX = "glossary-"

# Canonical files that are NOT distributed (per-skill authored, not SSOT).
NON_DISTRIBUTED = {
    # manual-entries-*--*.md handled via prefix below
}
NON_DISTRIBUTED_PREFIX = "manual-entries-"


def route(filename: str) -> str | None:
    """Return target subfolder name, or None if file is not distributed."""
    if filename.startswith(NON_DISTRIBUTED_PREFIX):
        return None
    if filename in REFERENCE_FILES:
        return "references"
    if filename in TYPOGRAPHY_FILES:
        return "typography"
    if filename in CORPUS_FILES:
        return "corpus"
    if filename.startswith(GLOSSARY_PREFIX):
        return "glossary"
    return "__UNROUTED__"


def main() -> int:
    if not CANONICAL.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL}", file=sys.stderr)
        return 2

    distributed = 0
    skipped = 0
    unrouted: list[str] = []

    for src in sorted(CANONICAL.iterdir()):
        if not src.is_file():
            continue
        target = route(src.name)
        if target is None:
            print(f"SKIP  (per-skill, not SSOT): {src.name}")
            skipped += 1
            continue
        if target == "__UNROUTED__":
            unrouted.append(src.name)
            continue
        for skill in ACTIVE_SKILLS:
            dst_dir = ROOT / skill / target
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / src.name
            shutil.copyfile(src, dst)
        distributed += 1
        print(f"OK    {src.name} -> {target}/ x {len(ACTIVE_SKILLS)} skills")

    for name in unrouted:
        print(f"WARN  unrouted (no matching subfolder rule): {name}")

    print(
        f"\nSummary: distributed={distributed} skipped={skipped} "
        f"unrouted={len(unrouted)} skills={len(ACTIVE_SKILLS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
