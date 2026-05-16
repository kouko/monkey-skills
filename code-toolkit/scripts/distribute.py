#!/usr/bin/env python3
"""Distribute canonical standards / rubrics / checklists from
``domain-teams:code-team`` into ``code-toolkit`` skills as functional copies.

Layout:

    canonical SSOT
      ../domain-teams/skills/code-team/{standards,rubrics,checklists}/<file>

    functional copy (this plugin)
      code-toolkit/skills/<skill>/{standards,rubrics,checklists}/<file>

Each functional copy is *(HTML header)+(canonical bytes)*. The header points
back to the SSOT path and forbids in-place editing. ``verify-drift.py``
regenerates the expected payload and byte-diffs it against what is on disk;
any mismatch fails the CI gate.

Pure stdlib (P1-E). Cross-plugin variant of the ``legal-toolkit/scripts/``
pattern, with the canonical layer living in a sibling plugin instead of in
this plugin's own ``canonical/`` directory.

Workflow
========
1. Land all edits in ``domain-teams/skills/code-team/`` (canonical).
2. In the same commit run ``python3 code-toolkit/scripts/distribute.py``.
3. ``code-toolkit/scripts/verify-drift.py`` runs in CI and fails on byte diff.

Routing table is hand-maintained — there is no auto-skip. Adding or removing
a consuming skill = update ROUTE in the same commit.
"""
from __future__ import annotations

import sys
from pathlib import Path

# code-toolkit/ — parent of scripts/
ROOT = Path(__file__).resolve().parent.parent

# monkey-skills/ repo root — parent of code-toolkit/, sibling of domain-teams/
REPO_ROOT = ROOT.parent

# Canonical knowledge layer in sibling plugin
CODE_TEAM_ROOT = REPO_ROOT / "domain-teams" / "skills" / "code-team"

# Routing table — canonical sub-path (relative to code-team/) → list of
# functional-copy destinations (relative to code-toolkit/).
#
# Update in the SAME commit that adds or removes a consuming skill — there is
# no auto-discovery.
_SDD_STANDARDS_DIR = "skills/subagent-driven-development/standards"
_SDD_RUBRICS_DIR = "skills/subagent-driven-development/rubrics"
_SDD_CHECKLISTS_DIR = "skills/subagent-driven-development/checklists"

ROUTE: dict[str, list[str]] = {
    # tdd-iron-law owns its own functional copy of the TDD standard so the
    # skill can ship without subagent-driven-development. subagent-driven-
    # development keeps its own copy too so the implementer / reviewer
    # subagents can load all seven standards via a single resource path.
    "standards/tdd-standard.md": [
        "skills/tdd-iron-law/standards/tdd-standard.md",
        f"{_SDD_STANDARDS_DIR}/tdd-standard.md",
    ],
    "standards/naming-and-functions.md": [
        f"{_SDD_STANDARDS_DIR}/naming-and-functions.md",
    ],
    "standards/pragmatic-principles.md": [
        f"{_SDD_STANDARDS_DIR}/pragmatic-principles.md",
    ],
    "standards/solid-principles.md": [
        f"{_SDD_STANDARDS_DIR}/solid-principles.md",
    ],
    "standards/refactoring-standard.md": [
        f"{_SDD_STANDARDS_DIR}/refactoring-standard.md",
    ],
    "standards/app-security-standard.md": [
        f"{_SDD_STANDARDS_DIR}/app-security-standard.md",
    ],
    "standards/character-encoding-security.md": [
        f"{_SDD_STANDARDS_DIR}/character-encoding-security.md",
    ],
    "rubrics/quality-gate.md": [
        f"{_SDD_RUBRICS_DIR}/quality-gate.md",
    ],
    "rubrics/arch-gate.md": [
        f"{_SDD_RUBRICS_DIR}/arch-gate.md",
    ],
    "checklists/security-checklist.md": [
        f"{_SDD_CHECKLISTS_DIR}/security-checklist.md",
    ],
    "checklists/spec-consistency.md": [
        f"{_SDD_CHECKLISTS_DIR}/spec-consistency.md",
    ],
}


def header_for(canonical_subpath: str) -> str:
    """Return the HTML comment header prepended to every functional copy.

    P1-D: the header MUST appear as the first bytes of the functional copy
    and MUST name the canonical SSOT path so a human grepping the copy sees
    where to edit instead.
    """
    return (
        "<!--\n"
        "FUNCTIONAL COPY — DO NOT EDIT IN PLACE\n"
        f"SSOT: domain-teams/skills/code-team/{canonical_subpath}\n"
        "Sync via: code-toolkit/scripts/distribute.py\n"
        "-->\n\n"
    )


def expected_payload(canonical_subpath: str) -> bytes:
    """Return the byte content the functional copy on disk MUST equal."""
    src = CODE_TEAM_ROOT / canonical_subpath
    return header_for(canonical_subpath).encode("utf-8") + src.read_bytes()


def distribute(route: dict[str, list[str]] | None = None) -> int:
    """Copy each canonical file (with SSOT header prepended) to every routed
    destination. Returns the number of files written. Creates parent dirs as
    needed. Raises ``FileNotFoundError`` if a canonical file in ROUTE is
    absent — there is no auto-skip.
    """
    if route is None:
        route = ROUTE

    written = 0
    for canonical_subpath, dests in route.items():
        src = CODE_TEAM_ROOT / canonical_subpath
        if not src.is_file():
            raise FileNotFoundError(
                f"canonical missing: {src.relative_to(REPO_ROOT)}"
            )
        payload = expected_payload(canonical_subpath)
        for rel_dst in dests:
            dst = ROOT / rel_dst
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(payload)
            written += 1
            print(
                f"[deploy] code-team:{canonical_subpath} "
                f"-> code-toolkit/{rel_dst}"
            )
    return written


def main() -> int:
    if not CODE_TEAM_ROOT.is_dir():
        print(
            f"ERROR: code-team canonical root not found: "
            f"{CODE_TEAM_ROOT.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 2
    try:
        n = distribute()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"\nOK: deployed {n} functional copies from code-team.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
