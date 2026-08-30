#!/usr/bin/env python3
"""Fog-monotonicity gate for a decision-map store.

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` §Fog entries. A fog entry (`F-<n>`) present at a base
git ref is legal in the current MAP.md only if it is still present
(text may shrink), or it graduated into a ticket (that ticket's
`graduated-from: F-<n>`), or it moved verbatim into Out-of-scope.
Any other disappearance is a violation — exit 2 naming the vanished
id.

Base ref resolution: `--base <git-ref>` if given, else the merge-base
of HEAD with the repo's resolved default branch (origin/HEAD's
symbolic-ref target, falling back to a local/remote `main` or
`master`). The base MAP.md is read via `git show <ref>:<path>` — never
the working tree alone — and parsed through `map_store`'s own
document parser, never a private regex.

Exit codes (canonical §Command surface split):
    0 — clean: no vanished fog id, or no base MAP.md exists at the
        resolved base ref (a brand-new map has nothing to compare).
    1 — operational error: the map directory/MAP.md is missing or
        unreadable, or the repo itself is unreadable (not a git
        repository, or no base ref could be resolved).
    2 — violation: a base fog id vanished with no shrink/graduation/
        out-of-scope record, or a MAP.md (current or base) fails
        schema parsing.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import map_store  # noqa: E402

_OUT_OF_SCOPE_ID = re.compile(r"^(?P<id>F-\d+)\s*:")


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def _is_git_repo(repo_root: Path) -> bool:
    result = _run_git(["rev-parse", "--is-inside-work-tree"], repo_root)
    return result.returncode == 0


def resolve_default_branch(repo_root: Path) -> str | None:
    """origin/HEAD's symbolic-ref target if set, else the first of a
    local or remote `main`/`master` that exists. None if neither is
    resolvable.

    When origin/HEAD resolves to a name with no LOCAL branch of that
    name (e.g. a clone whose local tracking branch was later deleted,
    leaving only `refs/remotes/origin/<name>`), falls back to the
    `origin/<name>` form — `merge-base` needs a ref that actually
    exists, and the bare name is not one."""
    result = _run_git(
        ["symbolic-ref", "refs/remotes/origin/HEAD"], repo_root
    )
    if result.returncode == 0:
        name = result.stdout.strip().rsplit("/", 1)[-1]
        local_check = _run_git(["rev-parse", "--verify", f"refs/heads/{name}"], repo_root)
        if local_check.returncode == 0:
            return name
        return f"origin/{name}"
    for candidate in ("main", "master"):
        for ref in (f"refs/heads/{candidate}", f"refs/remotes/origin/{candidate}"):
            check = _run_git(["rev-parse", "--verify", ref], repo_root)
            if check.returncode == 0:
                return candidate if ref.startswith("refs/heads/") else f"origin/{candidate}"
    return None


def resolve_base_ref(repo_root: Path, explicit_base: str | None) -> str | None:
    """The base ref: `explicit_base` verbatim if given, else the
    merge-base of HEAD with the resolved default branch. None if no
    default branch or no merge-base could be found."""
    if explicit_base is not None:
        return explicit_base
    default_branch = resolve_default_branch(repo_root)
    if default_branch is None:
        return None
    result = _run_git(["merge-base", "HEAD", default_branch], repo_root)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def read_base_map_text(repo_root: Path, base_ref: str, map_md_path: Path) -> str | None:
    """The base ref's MAP.md text via `git show <ref>:<path>`, or None
    if MAP.md did not exist at that ref (a brand-new map)."""
    rel = map_md_path.resolve().relative_to(repo_root.resolve())
    result = _run_git(["show", f"{base_ref}:{rel.as_posix()}"], repo_root)
    if result.returncode != 0:
        return None
    return result.stdout


def _out_of_scope_ids(out_of_scope_lines: list[str]) -> set[str]:
    ids: set[str] = set()
    for line in out_of_scope_lines:
        match = _OUT_OF_SCOPE_ID.match(line.strip())
        if match:
            ids.add(match.group("id"))
    return ids


def _graduated_owners(map_dir: Path) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    tickets_dir = map_dir / "tickets"
    if not tickets_dir.is_dir():
        return owners
    for ticket_path in sorted(tickets_dir.glob("*.md")):
        try:
            ticket = map_store.read_ticket(ticket_path)
        except (map_store.MapStoreError, map_store.SchemaViolation):
            continue
        if ticket.frontmatter.graduated_from:
            owners.setdefault(ticket.frontmatter.graduated_from, []).append(
                ticket_path.name
            )
    return owners


def check_fog_monotonicity(
    map_dir: Path, repo_root: Path, base_ref: str | None
) -> tuple[int, str]:
    """Returns `(exit_code, message)` per this module's exit-code
    contract."""
    map_dir = Path(map_dir)
    if not map_dir.is_dir():
        return 1, f"map directory not found: {map_dir}"

    try:
        current_doc = map_store.read_map(map_dir)
    except map_store.MapStoreError as exc:
        return 1, str(exc)
    except map_store.SchemaViolation as exc:
        return 2, str(exc)

    if not _is_git_repo(repo_root):
        return 1, f"repo root is not a git repository: {repo_root}"

    resolved_base_ref = resolve_base_ref(repo_root, base_ref)
    if resolved_base_ref is None:
        return 1, f"could not resolve a base ref for {repo_root}"

    base_text = read_base_map_text(repo_root, resolved_base_ref, current_doc.path)
    if base_text is None:
        return 0, f"{current_doc.path} has no base version at {resolved_base_ref!r} (new map) — clean"

    try:
        base_doc = map_store.parse_map_document(base_text, current_doc.path)
    except map_store.SchemaViolation as exc:
        return 2, f"base MAP.md at {resolved_base_ref!r} fails to parse: {exc}"

    current_ids = {fog.id for fog in current_doc.fog_entries}
    out_of_scope_ids = _out_of_scope_ids(current_doc.out_of_scope)
    graduated_owners = _graduated_owners(map_dir)
    graduated_ids = set(graduated_owners)
    overlap = sorted(current_ids.intersection(out_of_scope_ids | graduated_ids))
    if overlap:
        return 2, (
            "fog id is reused while its graduated/Out-of-scope history remains: "
            + ", ".join(overlap)
        )
    duplicate_graduations = sorted(
        fog_id for fog_id, owners in graduated_owners.items() if len(owners) > 1
    )
    if duplicate_graduations:
        return 2, (
            "fog entry graduated more than once: "
            + ", ".join(duplicate_graduations)
        )

    base_out_of_scope_ids = _out_of_scope_ids(base_doc.out_of_scope)
    reused_retired = sorted(current_ids.intersection(base_out_of_scope_ids))
    if reused_retired:
        return 2, (
            "fog id reuses base Out-of-scope history: "
            + ", ".join(reused_retired)
        )
    vanished_history = sorted(base_out_of_scope_ids - out_of_scope_ids)
    if vanished_history:
        return 2, (
            "Out-of-scope fog history vanished: " + ", ".join(vanished_history)
        )
    base_fog_ids = {fog.id for fog in base_doc.fog_entries}
    max_base_fog = max(
        (
            int(fog_id.removeprefix("F-"))
            for fog_id in base_fog_ids | base_out_of_scope_ids
        ),
        default=-1,
    )
    non_monotonic_fog = sorted(
        fog_id
        for fog_id in current_ids - base_fog_ids
        if int(fog_id.removeprefix("F-")) <= max_base_fog
    )
    if non_monotonic_fog:
        return 2, (
            "new fog id is not monotonic: " + ", ".join(non_monotonic_fog)
        )

    base_da = {item.id: item for item in base_doc.destination_acceptance}
    current_da = {item.id: item for item in current_doc.destination_acceptance}
    for da_id, old in base_da.items():
        current = current_da.get(da_id)
        if current is not None and current.text != old.text:
            return 2, (
                f"Destination acceptance id {da_id} was reused for different text"
            )
        if current is None and da_id not in current_doc.retired_da_ids:
            return 2, (
                f"Destination acceptance id {da_id} vanished without retired-da history"
            )
    max_base_da = max((item.number for item in base_doc.destination_acceptance), default=0)
    non_monotonic_da = sorted(
        item.id
        for item in current_doc.destination_acceptance
        if item.id not in base_da and item.number <= max_base_da
    )
    if non_monotonic_da:
        return 2, (
            "new Destination acceptance id is not monotonic: "
            + ", ".join(non_monotonic_da)
        )

    for fog in base_doc.fog_entries:
        if fog.id in current_ids or fog.id in out_of_scope_ids:
            continue
        if fog.id in graduated_ids:
            continue
        return 2, (
            f"fog entry {fog.id!r} present at base ref {resolved_base_ref!r} "
            f"has vanished from {current_doc.path}: it is neither still "
            "present, graduated (recorded via a ticket's "
            "'graduated-from'), nor moved to Out-of-scope"
        )

    return 0, f"{current_doc.path} is fog-monotonicity clean"


# --- CLI -------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify fog-id monotonicity: no silent disappearance "
        "of F-<n> ids; reuse of retired ids is review-enforced "
        "(map-format.md §Fog entries)."
    )
    parser.add_argument("target", help="path to the map directory")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root (default: git rev-parse --show-toplevel of the "
        "target's directory, falling back to cwd)",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="base git ref to compare against (default: merge-base of "
        "HEAD with the repo's resolved default branch)",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    repo_root = map_store.resolve_repo_root(
        args.repo_root, target if target.is_dir() else target.parent
    )
    code, message = check_fog_monotonicity(target, repo_root, args.base)
    if code == 0:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
