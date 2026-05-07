#!/usr/bin/env python3
"""Distribute canonical/* files to each active skill as byte-identical functional copies.

SSOT-and-functional-copy pattern (spec Decision #14):
  scripts/canonical/<file>      -> single source of truth (authored here)
  <skill>/<subfolder>/<file>    -> byte-identical functional copy (Edit forbidden)

Routing:
  - core-loop / 4d-reflection / 5d-effectiveness / orthogonal-axes /
    verification-gates / audit-trail-spec / protect-pass-spec  -> references/
  - jlreq-summary / clreq-summary / requirements-for-japanese-text-layout-summary
    -> typography/
  - nict-en-ja-zh / opus-en-zh-tw / wmt-* -> corpus/
  - glossary-*--*.md (bidirectional pair files) -> glossary/
  - manual-entries-*--*.md -> NOT distributed (per-skill authored, not SSOT)
  - prompts/<name>.md -> references/prompt-<name>.md (FLATTENED — Anthropic
    flat-folder rule: skill subfolders cannot nest, so prompts/ is collapsed
    into a `prompt-` filename prefix at the skill side)

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
    "translation-novel",
]

REFERENCE_FILES = {
    "core-loop.md",
    "4d-reflection.md",
    "5d-effectiveness.md",
    "orthogonal-axes.md",
    "verification-gates.md",
    "audit-trail-spec.md",
    "protect-pass-spec.md",
    "glossary-resolution-spec.md",
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

# Prompts live under canonical/prompts/<name>.md and get FLATTENED to
# <skill>/references/prompt-<name>.md (Anthropic flat-folder rule —
# skill subfolders cannot nest, so the prompts/ layer is collapsed
# into a `prompt-` filename prefix on distribution).
PROMPT_FILES = {
    "prompts/draft.md",
    "prompts/reflect-4d.md",
    "prompts/reflect-5d.md",
    "prompts/reflect-5d-literary.md",
    "prompts/improve.md",
}

# Canonical files that are NOT distributed (per-skill authored, not SSOT).
NON_DISTRIBUTED = {
    # manual-entries-*--*.md handled via prefix below
}
NON_DISTRIBUTED_PREFIX = "manual-entries-"

# Filesystem noise to skip when scanning canonical/ — these are never authored
# files, so we silently drop them rather than emitting WARN lines on every run.
IGNORED_NAMES = {".DS_Store", ".gitkeep"}


def route(rel_path: str) -> tuple[str, str] | str | None:
    """Map a canonical-relative path to its skill-side destination.

    Returns:
      - None                       -> file is not distributed (per-skill SoT)
      - "__UNROUTED__"             -> no rule matched; caller logs a warning
      - (subfolder, dst_filename)  -> copy canonical/<rel_path> to
                                       <skill>/<subfolder>/<dst_filename>
                                       (dst_filename can rename for flattening)
    """
    if rel_path in PROMPT_FILES:
        # Flatten: prompts/foo.md -> references/prompt-foo.md
        return ("references", f"prompt-{Path(rel_path).name}")

    name = Path(rel_path).name
    # Top-level only: anything still inside a subdirectory we don't know about
    # falls through to __UNROUTED__ (we only support flat top-level routes
    # plus the explicit prompts/ flattening above; PROMPT_FILES already
    # returned at line above, so any remaining "/" is unknown).
    if "/" in rel_path:
        return "__UNROUTED__"

    if name.startswith(NON_DISTRIBUTED_PREFIX):
        return None
    if name in REFERENCE_FILES:
        return ("references", name)
    if name in TYPOGRAPHY_FILES:
        return ("typography", name)
    if name in CORPUS_FILES:
        return ("corpus", name)
    if name.startswith(GLOSSARY_PREFIX):
        return ("glossary", name)
    return "__UNROUTED__"


def iter_canonical_files() -> list[tuple[str, Path]]:
    """Yield (relative_posix_path, absolute_path) for every file under canonical/.

    Top-level files come back as "<name>"; nested files (e.g. prompts/) come
    back as "<subdir>/<name>". Sorted for deterministic output.

    Filesystem noise is filtered:
      - macOS Finder droppings (.DS_Store, ._*-prefixed AppleDouble files)
      - empty-dir markers (.gitkeep)
      - Python bytecode caches (__pycache__/ trees)
    """
    out: list[tuple[str, Path]] = []
    for p in sorted(CANONICAL.rglob("*")):
        if not p.is_file():
            continue
        if p.name in IGNORED_NAMES or p.name.startswith("._"):
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(CANONICAL).as_posix()
        out.append((rel, p))
    return out


def main() -> int:
    if not CANONICAL.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL}", file=sys.stderr)
        return 2

    distributed = 0
    skipped = 0
    unrouted: list[str] = []

    for rel, src in iter_canonical_files():
        target = route(rel)
        if target is None:
            print(f"SKIP  (per-skill, not SSOT): {rel}")
            skipped += 1
            continue
        if target == "__UNROUTED__":
            unrouted.append(rel)
            continue
        subfolder, dst_name = target  # type: ignore[misc]
        for skill in ACTIVE_SKILLS:
            dst_dir = ROOT / "skills" / skill / subfolder
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / dst_name
            shutil.copyfile(src, dst)
        distributed += 1
        if dst_name == Path(rel).name:
            print(f"OK    {rel} -> {subfolder}/ x {len(ACTIVE_SKILLS)} skills")
        else:
            print(f"OK    {rel} -> {subfolder}/{dst_name} x {len(ACTIVE_SKILLS)} skills (flattened)")

    # Unrouted files warn-only — do NOT exit non-zero (lets repo evolve
    # canonical/ without distribute changes blocking CI; verify-drift.py is
    # the strict gate for byte identity, not distribute.py).
    for name in unrouted:
        print(f"WARN  unrouted (no matching subfolder rule): {name}")

    print(
        f"\nSummary: distributed={distributed} skipped={skipped} "
        f"unrouted={len(unrouted)} skills={len(ACTIVE_SKILLS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
