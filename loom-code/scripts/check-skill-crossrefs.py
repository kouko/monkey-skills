#!/usr/bin/env python3
"""CI gate: dead-link validator for loom-code skill cross-references.

Walks every ``loom-code/skills/*/SKILL.md`` and, for each RELATIVE
markdown link ``](path)``, resolves the target against that SKILL.md's
directory and asserts the target exists on disk.

Skipped (not a relative on-disk target):
- ``http://`` / ``https://`` URLs
- anchor-only links (``#section``)
- absolute paths (``/etc/...``)

A trailing ``#anchor`` on an otherwise-relative link is stripped before
the existence check (e.g. ``references/guide.md#step-2`` checks
``references/guide.md``).

Caveat: only INLINE links ``](target)`` are checked. Reference-style
link definitions (``[id]: path``) and inline links carrying a title
attribute (``](path "title")``) are NOT covered — the loom-code SKILL.md
convention is title-less inline links, so this matches today's corpus; a
future author adding a reference-style link should not assume coverage.

- Exit 0: every relative cross-ref resolves.
- Exit 1: one or more targets are missing; each is printed to stderr as
  ``<skill-md-path>: <link>``.

Pure stdlib. The core scan is the importable function
``find_broken_crossrefs(skills_dir) -> list[str]`` so it can be tested
hermetically; the ``__main__`` block runs it over the real skills tree
(resolved relative to this script's location, so it works from the repo
root) and sets the exit code.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Markdown inline link: `](target)`. We only need the target group; the
# link text before `[` is irrelevant to existence checking.
_LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Default skills tree, relative to this script: <repo>/loom-code/skills.
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def _is_relative_ondisk_link(target: str) -> bool:
    """True only for links that name a relative on-disk path.

    Excludes URLs (scheme://), anchor-only links (#...), and absolute
    paths (/...). Protocol-relative ``//host`` is treated as external.
    """
    if target.startswith("#"):
        return False
    if target.startswith("/"):
        return False
    if "://" in target:
        return False
    return True


def _strip_anchor(target: str) -> str:
    """Drop a trailing ``#anchor`` fragment before the existence check."""
    return target.split("#", 1)[0]


def find_broken_crossrefs(skills_dir) -> list[str]:
    """Return one ``<skill-md-path>: <link>`` string per broken cross-ref.

    Scans ``<skills_dir>/*/SKILL.md``. A link is broken when its target
    (relative, anchor stripped) does not exist on disk relative to the
    SKILL.md's own directory. Empty list == all links resolve.
    """
    skills_dir = Path(skills_dir)
    broken: list[str] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        base = skill_md.parent
        for raw_target in _LINK_RE.findall(text):
            target = raw_target.strip()
            if not _is_relative_ondisk_link(target):
                continue
            path_part = _strip_anchor(target)
            if not path_part:
                # Link was anchor-only after stripping (e.g. `]( #x)`).
                continue
            resolved = (base / path_part)
            if not resolved.exists():
                broken.append(f"{skill_md}: {target}")
    return broken


def main() -> int:
    broken = find_broken_crossrefs(_DEFAULT_SKILLS_DIR)
    if broken:
        for entry in broken:
            print(entry, file=sys.stderr)
        print(
            f"\nFAIL: {len(broken)} broken skill cross-reference(s) "
            f"(target missing on disk).",
            file=sys.stderr,
        )
        return 1
    print("OK: all relative skill cross-references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
