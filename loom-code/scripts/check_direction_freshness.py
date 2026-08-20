"""Report unlanded changes to the direction layer.

`docs/loom/DIRECTION.md`'s `## Now` section, plus one
`docs/loom/backlog/<name>.md` file per entry named there, are the
GOVERNING FILES this check watches. For each local branch other than
the base branch, a file counts as an unlanded change only when it is
in the intersection of two sets:

    - files the branch itself changed since its merge-base with the
      base branch (``git diff --name-only <merge-base>..<branch>``)
    - files whose content still differs from the base branch right now
      (``git diff --name-only <base> <branch>``)

Ancestry (``git merge-base --is-ancestor``) is deliberately NOT used:
under squash merge a landed branch's tip is not an ancestor of the
base branch, so ancestry misreports every branch as unmerged. The
intersection test above clears a squash-landed branch correctly,
because its content no longer differs from the base once landed.

This module shells out to git — `backlog_index.py` deliberately does
not (see its own comments at lines 60, 70-73, 502), and that boundary
is why this check lives in a separate module rather than a new flag on
the old one.

This check REPORTS; it never blocks or raises for an unhealthy repo
state — a missing `DIRECTION.md`, or a `DIRECTION.md` with no
`## Now` section, yields an empty list rather than an exception. The
same holds when the git plumbing itself fails (`--repo-root` pointed
at a non-git directory, or any other git-inspection failure):
`find_unlanded_direction_changes` catches it, announces the
degradation on stderr, and still returns a list rather than raising —
see the containment comment at that function's git calls.

# grounding: four git plumbing surfaces used throughout this module —
# `diff --name-only`, `merge-base`, `for-each-ref --format=%(refname:short)`,
# `log -1 --format=%as` — one module-level cite covers all four, they
# are the same well-established git plumbing:
#   - `diff --name-only` + `merge-base`: in-repo precedent
#     review_scope.py:268 and review_scope.py:223 (same flags, same
#     purpose); also live-measured against this repo's own branches in
#     this task's plan (docs/loom/plans/2026-08-20-direction-queue-gate.md,
#     Task 1 `External surfaces`) — 6 branches sampled, intersection
#     test flagged 2 and cleared 4 correctly.
#   - `for-each-ref --format=%(refname:short)`: live-verified —
#     `git for-each-ref --format='%(refname:short)' refs/heads/` run
#     against this repo returned one short branch name per line (22
#     local branches, `main` among them), matching this module's use.
#   - `log -1 --format=%as`: live-verified — `git log -1 --format=%as
#     HEAD` run against this repo returned `2026-08-19`, an ISO date
#     with no extra formatting, matching this module's use.

Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_NOW_HEADING_RE = re.compile(r"^##\s+Now\s*$")
_HEADING_RE = re.compile(r"^##\s+")
_NOW_ENTRY_RE = re.compile(r"^-\s+(?P<name>.+?)\s+—\s+.*$")


def _git_lines(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _parse_now_entry_names(direction_text: str) -> list[str] | None:
    """Names listed under `## Now`, or ``None`` if there is no such
    heading at all (distinct from a heading present but empty)."""
    lines = direction_text.splitlines()
    in_now = False
    found_heading = False
    names: list[str] = []
    for line in lines:
        if _NOW_HEADING_RE.match(line):
            in_now = True
            found_heading = True
            continue
        if in_now and _HEADING_RE.match(line):
            break
        if in_now:
            match = _NOW_ENTRY_RE.match(line)
            if match:
                names.append(match.group("name"))
    return names if found_heading else None


def _governing_files(repo_root: Path) -> list[str]:
    """Repo-relative paths (posix separators, matching git's own
    ``diff --name-only`` output) of the files this check watches, or an
    empty list when the direction layer isn't set up (missing file, or
    no `## Now` section)."""
    direction_path = repo_root / "docs" / "loom" / "DIRECTION.md"
    if not direction_path.exists():
        return []
    now_names = _parse_now_entry_names(direction_path.read_text(encoding="utf-8"))
    if now_names is None:
        return []
    files = ["docs/loom/DIRECTION.md"]
    files.extend(f"docs/loom/backlog/{name}.md" for name in now_names)
    return files


def find_unlanded_direction_changes(
    repo_root: Path, base_branch: str = "main"
) -> list[str]:
    """Every governing-file change that a local branch (other than
    `base_branch`) still carries and the base branch does not.

    Returns formatted strings ``"<branch> — <path> (tip <date>)"``,
    one per (branch, path) hit, so one glance is enough to dismiss a
    false positive. Returns an empty list when the direction layer
    isn't set up — see `_governing_files`."""
    governing = set(_governing_files(repo_root))
    if not governing:
        return []

    # Containment boundary: this whole advisory body is wrapped here,
    # at the call site inside `find_unlanded_direction_changes` itself
    # — not inside `_git_lines` — because the function's own docstring
    # and the module docstring both promise "REPORTS; never gates" as
    # a property of this function's return value, not of any one git
    # plumbing call. `repo_root` not being a git work tree (`git
    # for-each-ref` exit 128), and `git` itself being unavailable
    # (`FileNotFoundError`) are the two reachable failure modes; either
    # must degrade to an empty/partial advisory, never propagate. A
    # swallowed failure is still announced on stderr (Rule 12,
    # fail-loud) so an empty advisory reads as "could not inspect",
    # never as "nothing unlanded".
    try:
        branches = _git_lines(
            repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads/"
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(
            f"Warning: unlanded-direction-change advisory is incomplete — "
            f"could not list branches under {repo_root} via git ({exc}).",
            file=sys.stderr,
        )
        return []

    findings: list[str] = []
    for branch in branches:
        if branch == base_branch:
            continue
        try:
            merge_base = subprocess.run(
                ["git", "-C", str(repo_root), "merge-base", base_branch, branch],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            branch_changed = set(
                _git_lines(repo_root, "diff", "--name-only", f"{merge_base}..{branch}")
            )
            still_differs = set(
                _git_lines(repo_root, "diff", "--name-only", base_branch, branch)
            )
            unlanded = branch_changed & still_differs & governing
            if not unlanded:
                continue
            tip_date = subprocess.run(
                ["git", "-C", str(repo_root), "log", "-1", "--format=%as", branch],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(
                f"Warning: unlanded-direction-change advisory is incomplete — "
                f"could not inspect branch '{branch}' under {repo_root} via "
                f"git ({exc}).",
                file=sys.stderr,
            )
            continue
        for path in sorted(unlanded):
            findings.append(f"{branch} — {path} (tip {tip_date})")
    return findings


# --- `## Queue relation` gate -------------------------------------------
#
# Grammar SSOT: `loom-code/skills/brainstorming/references/
# handoff-brief-format.md` `### `## Queue relation``. Exactly three
# canonical forms resolve the gate; any other wording (including
# `pending`, a missing section, or a malformed line) is unresolved.
# This check is the only thing in this module that blocks — see the
# module docstring: Task 1's heuristic never gates.

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


@dataclass
class QueueRelationResult:
    status: str  # "resolved" | "unresolved"
    message: str = ""
    named_entry: str | None = None


def resolve_queue_relation(
    brief_text: str, now_names: list[str]
) -> QueueRelationResult:
    """Resolve a brief's `## Queue relation` line against the canonical
    grammar. `now_names` is the list parsed from `## Now` (see
    `_parse_now_entry_names`) — a name cited by `in-queue:` or
    `displaces:` must appear in it, or the declaration is unresolved
    (a typo must not silently satisfy the gate)."""
    value = _find_queue_relation_value(brief_text)
    if value is None:
        return QueueRelationResult(
            "unresolved", "no '## Queue relation' line found in the brief"
        )

    match = _IN_QUEUE_RE.match(value)
    if match is not None:
        name = match.group("name")
        if name not in now_names:
            return QueueRelationResult(
                "unresolved",
                f"in-queue names '{name}', which does not match any entry "
                "name parsed from DIRECTION.md's '## Now' section (each "
                "entry must read '- <name> — ...' with an em dash "
                "'—', not a hyphen)",
                named_entry=name,
            )
        return QueueRelationResult("resolved", value, named_entry=name)

    if _UNQUEUED_RE.match(value):
        return QueueRelationResult("resolved", value)

    match = _DISPLACES_RE.match(value)
    if match is not None:
        name = match.group("name")
        if name not in now_names:
            return QueueRelationResult(
                "unresolved",
                f"displaces names '{name}', which does not match any entry "
                "name parsed from DIRECTION.md's '## Now' section (each "
                "entry must read '- <name> — ...' with an em dash "
                "'—', not a hyphen)",
                named_entry=name,
            )
        return QueueRelationResult("resolved", value, named_entry=name)

    # `pending`, or any other wording — unresolved.
    return QueueRelationResult("unresolved", value)


def build_queue_relation_question(result: QueueRelationResult) -> str:
    """The exact user-facing question for an `unresolved`
    `QueueRelationResult` — what `main()` prints to stderr and the
    caller must relay verbatim."""
    if result.named_entry is not None:
        return (
            f"Queue relation: '{result.named_entry}' does not match any "
            "entry name parsed from DIRECTION.md's '## Now' section "
            "(each entry must read '- <name> — ...' with an em dash "
            "'—', not a hyphen). Is this arc `in-queue: "
            "<entry-name>` (name it exactly as it appears in ## Now), "
            "`unqueued — <reason>`, or `displaces: <entry-name> — "
            "<reason>`?"
        )
    return (
        "Queue relation: is this arc `in-queue: <entry-name>`, "
        "`unqueued — <reason>`, or `displaces: <entry-name> — "
        "<reason>`? Record the answer in the brief's '## Queue "
        "relation' section."
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
        description="Report unlanded direction-layer changes (advisory) "
                    "and gate on a brief's '## Queue relation' "
                    "declaration (blocking)."
    )
    parser.add_argument("brief_path", help="path to the handoff brief file")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root used to locate docs/loom/DIRECTION.md and the "
             "branches to scan (default: `git rev-parse --show-toplevel` "
             "of the brief's directory, falling back to cwd)",
    )
    args = parser.parse_args(argv)

    brief_path = Path(args.brief_path)
    repo_root = _resolve_repo_root(args.repo_root, brief_path.parent)

    # Task 1's advisory findings print on every run, including exit 2 —
    # the reader meets them while already stopped, not in a report they
    # can scroll past.
    findings = find_unlanded_direction_changes(repo_root)
    for finding in findings:
        print(f"Unlanded direction change: {finding}")

    if not brief_path.is_file():
        print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
        return 1
    brief_text = brief_path.read_text(encoding="utf-8")

    direction_path = repo_root / "docs" / "loom" / "DIRECTION.md"
    now_names: list[str] = []
    if direction_path.is_file():
        parsed = _parse_now_entry_names(
            direction_path.read_text(encoding="utf-8")
        )
        if parsed is not None:
            now_names = parsed

    result = resolve_queue_relation(brief_text, now_names)

    if result.status == "resolved":
        print(f"Queue relation in {brief_path} is resolved ({result.message}).")
        return 0

    question = build_queue_relation_question(result)
    print(f"Error: {brief_path}: {question}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
