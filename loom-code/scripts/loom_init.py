#!/usr/bin/env python3
"""Scaffold the loom queue layer into a repo, then prove it.

`python3 loom_init.py [repo-root]` (default: cwd) mints the queue-layer
skeleton from the templates shipped beside this script:

  docs/loom/backlog/README.md   — charter instance (templates/backlog-README.md)
  docs/loom/memory/README.md    — practice-memory charter instance
                                  (templates/memory-README.md); the practice-memory store that `loom-memory` and the
  knowledge-triage references tell a reader to consult
  docs/loom/KICKOFF-DEFAULTS.md — kickoff-defaults skeleton
                                  (templates/KICKOFF-DEFAULTS.md); an empty
                                  `## On-ramp standing choices` section, the
                                  home for repo-level on-ramp decisions
  docs/loom/PURPOSE.md          — purpose skeleton (templates/PURPOSE.md);
                                  a prompt for the author to fill in, never
                                  pre-filled prose — see its own file header
  docs/loom/plans/.gitkeep      — git cannot track an empty directory;
  docs/loom/specs/.gitkeep        without the keep-file the scaffolded dirs
                                  would silently vanish from the target
                                  repo's first commit/clone

Semantics (plan docs/loom/plans/2026-08-10-loom-init-scaffold.md, Task 1):
the scaffold is a POINT-IN-TIME copy, not a synced one — each minted file
opens with a vintage stamp `<!-- scaffolded by loom-init (loom-code
<version>) -->` (version read from the plugin.json beside this script's
parent; `unknown` on any read failure) and thereafter belongs to the
target repo. No drift checking, ever.

Never overwrites: an existing `docs/loom/backlog/` (an adopted store) or
an existing `docs/loom/KICKOFF-DEFAULTS.md` (human-owned choices)
refuses with one explanatory line and exit 1, writing nothing.

Self-verify: after writing, the sibling `backlog_index.py` (resolved via
Path(__file__).parent) runs `--validate` with cwd at the target repo;
its exit code is relayed, and nonzero makes this script exit 1 — a
scaffold that the live validator rejects is a failure, not a success
with caveats.
"""

from __future__ import annotations

import json
import subprocess
import pathlib
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
PLUGIN_JSON = SCRIPT_DIR.parent / ".claude-plugin" / "plugin.json"
BACKLOG_INDEX = SCRIPT_DIR / "backlog_index.py"


def _plugin_version() -> str:
    """The loom-code plugin version, or 'unknown' on any read failure."""
    try:
        version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return "unknown"
    if isinstance(version, str) and version:
        return version
    return "unknown"


def _instantiate(template: Path, dest: Path, stamp: str) -> None:
    dest.write_text(
        stamp + "\n" + template.read_text(encoding="utf-8"), encoding="utf-8"
    )


def _self_verify(target: Path) -> int:
    """Run the sibling validator against the fresh store; relay its exit
    code; return 0 only when it is 0."""
    proc = subprocess.run(
        [sys.executable, str(BACKLOG_INDEX), "--validate"],
        capture_output=True,
        text=True,
        cwd=target,
    )
    print(f"loom-init: backlog_index --validate exit {proc.returncode}")
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        print("loom-init: FAIL — self-verify red (--validate); the scaffold does not pass the live validators")
        return 1
    return 0


def main(argv: list[str]) -> int:
    target = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not target.is_dir():
        print(f"loom-init: FAIL — target {target} is not a directory")
        return 1

    # Advisory only (plan 2026-08-10-cheap-hardening-batch.md, Task 3): a
    # nested-cwd run silently scaffolds at the wrong depth, but monorepo
    # subdirs adopting their own queue layer are legitimate — warn on
    # stderr, never refuse, never touch the exit code. Any git failure
    # (git absent, not a repo) → silent skip.
    try:
        toplevel = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if toplevel.returncode == 0:
            repo_root = Path(toplevel.stdout.strip()).resolve()
            if repo_root != target:
                print(
                    f"loom-init: note — {target} is not the git repo root "
                    f"({repo_root}); scaffolding here anyway (monorepo "
                    "subdirs are legitimate)",
                    file=sys.stderr,
                )
    except OSError:
        pass

    store = target / "docs" / "loom" / "backlog"
    memory_store = target / "docs" / "loom" / "memory"
    kickoff_defaults = target / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    purpose = target / "docs" / "loom" / "PURPOSE.md"
    if store.is_dir():
        print(
            f"loom-init: refusing — {store} already exists; this repo has "
            "adopted the queue layer and loom-init never overwrites it"
        )
        return 1
    if store.exists():  # a stray FILE at the store path, not adoption
        print(
            f"loom-init: refusing — {store} exists but is not a directory; "
            "inspect and remove it (possibly a crashed scaffold) before "
            "re-running"
        )
        return 1
    if memory_store.is_dir():
        print(
            f"loom-init: refusing — {memory_store} already exists; this "
            "repo has adopted the practice-memory store and loom-init "
            "never overwrites it"
        )
        return 1
    if memory_store.exists():  # a stray FILE at the store path, not adoption
        print(
            f"loom-init: refusing — {memory_store} exists but is not a "
            "directory; inspect and remove it (possibly a crashed "
            "scaffold) before re-running"
        )
        return 1
    if kickoff_defaults.exists():
        print(
            f"loom-init: refusing — {kickoff_defaults} already exists; its "
            "choices are human-owned and loom-init never overwrites them"
        )
        return 1
    if purpose.exists():
        print(
            f"loom-init: refusing — {purpose} already exists; its content "
            "is human-owned and loom-init never overwrites it"
        )
        return 1
    # Whole-branch review 🟡 (2026-08-10): precheck EVERY path the
    # scaffold will touch BEFORE the first write — a stray file at any
    # of them used to crash mid-scaffold, leaving residue that later
    # runs misdescribed as adoption.
    for dirname in ("plans", "specs"):
        clash = target / "docs" / "loom" / dirname
        if clash.exists() and not clash.is_dir():
            print(
                f"loom-init: refusing — {clash} exists but is not a "
                "directory; inspect and remove it before re-running"
            )
            return 1

    stamp = f"<!-- scaffolded by loom-init (loom-code {_plugin_version()}) -->"
    store.mkdir(parents=True)
    memory_store.mkdir(parents=True)
    for dirname in ("plans", "specs"):
        keep_dir = target / "docs" / "loom" / dirname
        keep_dir.mkdir(exist_ok=True)
        (keep_dir / ".gitkeep").touch()
    _instantiate(TEMPLATES_DIR / "backlog-README.md", store / "README.md", stamp)
    _instantiate(TEMPLATES_DIR / "memory-README.md", memory_store / "README.md", stamp)
    _instantiate(TEMPLATES_DIR / "KICKOFF-DEFAULTS.md", kickoff_defaults, stamp)
    _instantiate(TEMPLATES_DIR / "PURPOSE.md", purpose, stamp)

    if _self_verify(target) != 0:
        return 1

    print(
        f"loom-init: OK — queue layer scaffolded at {target} "
        "(backlog charter + KICKOFF-DEFAULTS skeleton + PURPOSE skeleton + "
        "plans/ + specs/), self-verified against backlog_index.py"
    )
    # Dogfood finding #3 (2026-08-21): the charter this just wrote says to
    # use "the repo-root scripts/backlog_index.py when it exists; otherwise
    # the copy shipped inside the loom-code plugin" — and a freshly
    # scaffolded repo has no scripts/ directory, so every command in the
    # charter needs a path the newcomer has no way to know. This script IS
    # inside that plugin, so it can just say where.
    print(
        "loom-init: this repo has no repo-root scripts/ copy, so run the "
        "plugin-shipped tools by absolute path, e.g.\n"
        f"    python3 {pathlib.Path(__file__).resolve().parent}/backlog_index.py "
        "--ready --store docs/loom/backlog"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
