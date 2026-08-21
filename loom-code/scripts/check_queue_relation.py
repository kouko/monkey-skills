"""Gate a handoff brief's `## Queue relation` declaration against the
live backlog store.

Renamed and reworked per plan docs/loom/plans/2026-08-21-dissolve-
direction-layer.md, Task 4. Two changes came with the rename:

  - The old module's unlanded-change advisory half (a set of
    functions that watched a now-retired per-repo "now" list) is
    DELETED, not carried forward.
  - `in-queue:`/`displaces:` names are resolved against live
    `status: bet` entries under `docs/loom/backlog/` instead of that
    retired list.

Grammar SSOT: `loom-code/skills/brainstorming/references/
handoff-brief-format.md` `### `## Queue relation``. Exactly three
canonical forms resolve the gate; any other wording (including
`pending`, a missing section, or a malformed line) is unresolved.

No-queue-layer posture: a repo with no `docs/loom/backlog/` directory
at all has nothing for this gate to check against, so this check
reports a loud `N/A` on stdout and exits 0 — never a silent skip.
This mirrors `loom-memory`'s own N/A posture (report the reason,
loudly, at exit 0) rather than gating a repo that never adopted the
queue layer.

Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from backlog_index import CLOSED_STATUS_VOCABULARY, _entry_files, parse_frontmatter

# --- `## Queue relation` gate -------------------------------------------

_QUEUE_HEADING_RE = re.compile(r"^##\s+Queue relation\s*$")
_IN_QUEUE_RE = re.compile(r"^in-queue:\s*(?P<name>.+?)\s*$")
_UNQUEUED_RE = re.compile(r"^unqueued\s*—\s*.+$")
_DISPLACES_RE = re.compile(r"^displaces:\s*(?P<name>.+?)\s*—\s*.+$")


def _find_queue_relation_value(brief_text: str) -> str | None:
    """The `## Queue relation` line's value (stripped), or None if the
    section heading is absent entirely."""
    lines = brief_text.splitlines()
    for i, raw in enumerate(lines):
        if _QUEUE_HEADING_RE.match(raw):
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
            return None
    return None


def live_bet_names(store: Path) -> list[str]:
    """Names (frontmatter `name`, falling back to the filename stem) of
    every live (non-archived) `status: bet` entry under `store`, in
    `_entry_files()` order.

    Raises ValueError (caller decides exit codes) on a status outside the
    closed status vocabulary — mirrors the sibling `## Now`-line builder in
    backlog_index.py's stated policy: malformed frontmatter must fail
    loudly, never be silently dropped from the queue it might belong to."""
    names: list[str] = []
    for path, is_archived in _entry_files(store):
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        status = frontmatter.get("status")
        if status not in CLOSED_STATUS_VOCABULARY:
            raise ValueError(
                f"{path.name}: entry has status {status!r}, outside the "
                "closed status vocabulary"
            )
        if is_archived or status != "bet":
            continue
        names.append(frontmatter.get("name", path.stem))
    return names


@dataclass
class QueueRelationResult:
    status: str  # "resolved" | "unresolved"
    message: str = ""
    named_entry: str | None = None


def resolve_queue_relation(
    brief_text: str, bet_names: list[str]
) -> QueueRelationResult:
    """Resolve a brief's `## Queue relation` line against the canonical
    grammar. `bet_names` is the list of live `status: bet` entry names
    (see `live_bet_names`) — a name cited by `in-queue:` or
    `displaces:` must appear in it, or the declaration is unresolved
    (a typo must not silently satisfy the gate). `unqueued — <reason>`
    never needs `bet_names` to be non-empty — it is the resolvable
    answer precisely when there is nothing live to queue against."""
    value = _find_queue_relation_value(brief_text)
    if value is None:
        return QueueRelationResult(
            "unresolved", "no '## Queue relation' line found in the brief"
        )

    match = _IN_QUEUE_RE.match(value)
    if match is not None:
        name = match.group("name")
        if name not in bet_names:
            return QueueRelationResult(
                "unresolved",
                f"in-queue names '{name}', which does not match any live "
                "'status: bet' entry under docs/loom/backlog/",
                named_entry=name,
            )
        return QueueRelationResult("resolved", value, named_entry=name)

    if _UNQUEUED_RE.match(value):
        return QueueRelationResult("resolved", value)

    match = _DISPLACES_RE.match(value)
    if match is not None:
        name = match.group("name")
        if name not in bet_names:
            return QueueRelationResult(
                "unresolved",
                f"displaces names '{name}', which does not match any live "
                "'status: bet' entry under docs/loom/backlog/",
                named_entry=name,
            )
        return QueueRelationResult("resolved", value, named_entry=name)

    # `pending`, or any other wording — unresolved.
    return QueueRelationResult("unresolved", value)


def build_queue_relation_question(
    result: QueueRelationResult, bet_names: list[str]
) -> str:
    """The exact user-facing question for an `unresolved`
    `QueueRelationResult` — what `main()` prints to stderr and the
    caller must relay verbatim. Lists the actual live bet names
    instead of a generic placeholder, so the reader sees the real
    candidate set rather than syntax."""
    if bet_names:
        names_clause = "live bet entries: " + ", ".join(
            f"'{n}'" for n in bet_names
        )
    else:
        names_clause = (
            "no live bet entries exist yet — `in-queue:`/`displaces:` "
            "cannot resolve until one does"
        )

    if result.named_entry is not None:
        return (
            f"Queue relation: '{result.named_entry}' does not match any "
            f"live bet backlog entry ({names_clause}). Is this arc "
            "`in-queue:` naming one of those entries exactly, `unqueued "
            "— <reason>`, or `displaces:` naming one of those entries "
            "followed by ' — <reason>'?"
        )
    return (
        f"Queue relation: is this arc `in-queue:` naming a live bet "
        f"entry ({names_clause}), `unqueued — <reason>`, or `displaces:` "
        "naming a live bet entry followed by ' — <reason>'? Record the "
        "answer in the brief's '## Queue relation' section."
    )


# --- CLI -----------------------------------------------------------------


def _resolve_repo_root(explicit: str | None, brief_dir: Path) -> Path:
    if explicit is not None:
        return Path(explicit)
    try:
        # grounding: in-repo precedent loom_init.py:108 (same flag) +
        # `git rev-parse --help`
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=brief_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gate a brief's '## Queue relation' declaration "
                    "against live 'status: bet' backlog entries."
    )
    parser.add_argument("brief_path", help="path to the handoff brief file")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root used to locate docs/loom/backlog/ (default: "
             "`git rev-parse --show-toplevel` of the brief's directory, "
             "falling back to cwd)",
    )
    args = parser.parse_args(argv)

    brief_path = Path(args.brief_path)
    repo_root = _resolve_repo_root(args.repo_root, brief_path.parent)

    store = repo_root / "docs" / "loom" / "backlog"
    if not store.is_dir():
        print(
            "queue-relation: N/A — no queue layer in this repo "
            "(docs/loom/backlog/ absent)"
        )
        return 0

    if not brief_path.is_file():
        print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
        return 1
    brief_text = brief_path.read_text(encoding="utf-8")

    try:
        bet_names = live_bet_names(store)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    result = resolve_queue_relation(brief_text, bet_names)

    if result.status == "resolved":
        print(f"Queue relation in {brief_path} is resolved ({result.message}).")
        return 0

    question = build_queue_relation_question(result, bet_names)
    print(f"Error: {brief_path}: {question}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
