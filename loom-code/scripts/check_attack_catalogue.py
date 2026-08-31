#!/usr/bin/env python3
"""Parser and checker for the repo store `docs/loom/ATTACK-CATALOGUE.md`
(plan `docs/loom/plans/2026-08-31-adversarial-audit-station.md` Task 2).
This module is the single owner of the store grammar; other tasks quote
its section headings and instance-line shape verbatim rather than
re-deriving them.

Grammar — three level-2 sections, in any order, each required:

    ## Guarded paths
    - <glob>
    - <glob>
    ...

    ## Instances
    - <class> | <target> | reproduced <YYYY-MM-DD> — pinned by <test-name>
    - <class> | <target> | held <YYYY-MM-DD>
    - <class> | <target> | not-applicable — <reason>

    ## Prose temptations
    - <one shortcut per bullet>

Usage:

    check_attack_catalogue.py <store> --repo <root>
    check_attack_catalogue.py signal --repo <root> --store <store-path>
        [--plan <plan-path>] [--base <ref>]

The legacy positional form (no subcommand) checks the store itself —
grammar, pinning, dating — as described below. `signal` is a second,
verb layered on the SAME `check_store` — a present store runs the
identical grammar/pinning/dating checks the legacy form runs, before
`signal` answers its own question: "did THIS branch's committed diff
against `--base` touch a guarded path, or a prose-contract file, and
does the plan's `Safety-bearing:` header cover that?" — the single
command Step 3.5 of `finishing-a-development-branch/SKILL.md` runs. An
ABSENT store (path does not exist — the adopting-repo-without-a-store
case) is not an error: `signal` prints stderr `attack catalogue:
absent` and degrades both stdout lines to N/A (guarded-hits=0;
prose-hits is still computed from the six built-in prose-contract
globs below, independent of the store), exit 0. A store that EXISTS
but is unreadable, or fails the grammar OR any `check_store` refusal
below (`unpinned` / `dangling` / `undated` / `unguarded` /
`incomplete` / `malformed`), is never degraded this way — it exits 1
with the family's `Error: …` line, exactly like the legacy form; so
does a `--plan` whose `Safety-bearing:` header itself raises
(misplaced / miscased / indented / unclosed fence), naming the plan
path and the parser's message. `--base`
defaults to `git merge-base HEAD origin/main`, falling back to
`git merge-base HEAD main`; if neither resolves, `signal` fails CLOSED
(exit 2) rather than silently diffing an empty range. Only the
COMMITTED diff is considered — a dirty worktree contributes nothing
extra to `changed`. Exit 3 when the plan declares `Safety-bearing: no`
but a guarded path was hit anyway (a `reproduced` vector per this
module's own grammar, until a RED test lands and `## Instances` names
it). See `signal`'s own `--help` for the exact flag list.

One `## Instances` bullet is exactly one `<class> | <target> | <status>`
line — a well-formed line MUST have both `|` separators; a line with
zero or one `|` (or an unrecognized `<status>`) is `malformed`, never
silently dropped from the count. `pinned by` resolution proves only
that the named test EXISTS somewhere a runner would collect it, never
that it actually exercises the class/target it is pinned to — that
relevance judgment is for a human (or the spec-reviewer) reading the
test body, not this parser.

Exit codes:

    0 — every section present, `## Guarded paths` non-empty, every
        `reproduced` instance names a `pinned by` test that resolves
        (a `def <name>` in some `test_*.py` under `--repo`, or the name
        appearing inside a `.sh` file under a `tests/` directory under
        `--repo`), every `held` instance carries a date. Prints one
        summary line with counts to stdout.
    1 — any refusal below fires; each prints one line to stderr naming
        the offending line's content and the refusal kind:

        unpinned    — a `reproduced` entry has no `pinned by`
        dangling    — the named test resolves to no `def <name>` in any
                       `test_*.py` under --repo (module-level or a
                       class-body method, resolved by parsing the AST —
                       a `def` sitting inside a docstring or comment
                       never counts), nor a name on a real command line
                       in a `.sh` file under a `tests/` directory (a
                       `.sh` line is comment-stripped first — a name
                       appearing only after `#`, or on a line whose
                       first non-space character is `#`, never counts)
        undated     — a `held` entry has no date
        unguarded   — `## Guarded paths` is empty or absent
        incomplete  — any of the three sections is missing
        malformed   — an `## Instances` status starts with `reproduced`
                       / `held` / `not-applicable` but does not fully
                       match that status's grammar (e.g. `pinned by`
                       with no name after it), or matches none of the
                       three tokens at all

A `pinned by` name resolving to a real, collected test proves only that
the name EXISTS somewhere a runner would find it — this module never
checks whether that test actually exercises the named vector. That
relevance judgment is out of scope for a machine check; the
spec-reviewer judges it by reading the test body against the vector.

Stdlib only.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import functools
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Sibling resolves off sys.path[0], its own directory (same idiom as
# check_scenario_coverage.py's `from adjudication_split import ...`).
# Copying this script alone (no sibling plan_card.py) is a real shape —
# `signal`'s `--plan` handling fails loud on it below rather than
# letting a raw ModuleNotFoundError traceback surface.
try:
    import plan_card
except ImportError:
    plan_card = None

_SECTION_NAMES = ("Guarded paths", "Instances", "Prose temptations")

_HEADING_2_LINE = re.compile(r"^##\s+(.*?)\s*$")
_BULLET_LINE = re.compile(r"^-\s*(.+)$")

# One `## Instances` bullet: `<class> | <target> | <status>`.
_INSTANCE_LINE = re.compile(
    r"^(?P<klass>[^|]+?)\s*\|\s*(?P<target>[^|]+?)\s*\|\s*(?P<status>.+)$"
)

_REPRODUCED_STATUS = re.compile(
    r"^reproduced\s+(?P<date>\S+)(?:\s*—\s*pinned by\s*(?P<test>\S*))?\s*$"
)
_HELD_STATUS = re.compile(r"^held(?:\s+(?P<date>\S+))?\s*$")
_NOT_APPLICABLE_STATUS = re.compile(
    r"^not-applicable\s*—\s*(?P<reason>.+)$"
)



@dataclass
class Instance:
    klass: str
    target: str
    verdict: str  # "reproduced" | "held" | "not-applicable" | "malformed"
    line: str  # the raw bullet text, for diagnostics
    date: str | None = None
    pinned_by: str | None = None
    reason: str | None = None


@dataclass
class Store:
    guarded_paths: list[str] = field(default_factory=list)
    instances: list[Instance] = field(default_factory=list)
    prose_temptations: list[str] = field(default_factory=list)
    sections_present: set = field(default_factory=set)


class StoreError(Exception):
    """A refusal: (kind, message) — message names the offending line."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind
        self.message = message


def _find_sections(text: str) -> dict[str, list[str]]:
    """Map section name -> list of bullet-content lines. A section
    heading not among `_SECTION_NAMES` is ignored.

    Raises `StoreError("malformed", …)` if any of `_SECTION_NAMES`
    appears as a `## ` heading more than once — a dict-assignment
    `sections[name] = bullets` would otherwise let the later heading
    silently replace the earlier one's bullets rather than refusing."""
    lines = text.splitlines()
    heading_idxs = []
    for i, line in enumerate(lines):
        m = _HEADING_2_LINE.match(line)
        if m:
            heading_idxs.append((i, m.group(1)))

    sections: dict[str, list[str]] = {}
    for pos, (idx, name) in enumerate(heading_idxs):
        end = heading_idxs[pos + 1][0] if pos + 1 < len(heading_idxs) else len(lines)
        if name not in _SECTION_NAMES:
            continue
        if name in sections:
            raise StoreError(
                "malformed",
                f"Error: malformed — duplicate '## {name}' section heading "
                f"— a later '## {name}' would silently replace the earlier "
                f"one's bullets.",
            )
        body = lines[idx + 1:end]
        bullets = []
        for line in body:
            m = _BULLET_LINE.match(line.strip())
            if m:
                bullets.append(m.group(1).strip())
        sections[name] = bullets
    return sections


def _is_iso_date(value: str) -> bool:
    """True only for a real ISO calendar date (`YYYY-MM-DD`, no
    out-of-range month/day) — `\\S+` in `_REPRODUCED_STATUS` /
    `_HELD_STATUS` would otherwise accept any non-space token."""
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_future_date(value: str) -> bool:
    """True when `value` (already confirmed `_is_iso_date`) is strictly
    after today's UTC calendar date — a `reproduced`/`held` date has no
    business being in the future; without this a typo'd year makes an
    entry look freshly re-verified forever."""
    return (
        datetime.date.fromisoformat(value)
        > datetime.datetime.now(datetime.timezone.utc).date()
    )


def parse_store(text: str) -> Store:
    """Parse the store's raw text into a `Store`. Does not validate — a
    missing section simply leaves the corresponding list empty and its
    name absent from `sections_present`; call `check_store` to enforce
    the refusal rules."""
    sections = _find_sections(text)
    store = Store()
    store.sections_present = set(sections.keys())

    store.guarded_paths = list(sections.get("Guarded paths", []))
    store.prose_temptations = list(sections.get("Prose temptations", []))

    for raw in sections.get("Instances", []):
        m = _INSTANCE_LINE.match(raw)
        if not m:
            # Not a well-formed `<class> | <target> | <status>` line at
            # all (fewer than two `|`) — this must still surface as a
            # refusal, never silently drop the bullet from the count
            # (deleting a `|` must not be a way to make an inconvenient
            # entry disappear).
            store.instances.append(
                Instance(klass="", target="", verdict="malformed", line=raw)
            )
            continue
        klass = m.group("klass").strip()
        target = m.group("target").strip()
        status = m.group("status").strip()

        if status.startswith("reproduced"):
            rm = _REPRODUCED_STATUS.match(status)
            # `test` is None when "— pinned by" was never attempted (the
            # legal unpinned case check_store flags separately), "" when
            # "pinned by" was attempted but named nothing (a bypass CQ-2
            # closes: that must never resolve as a legal unpinned entry),
            # and a real value otherwise.
            if (
                rm is None
                or rm.group("test") == ""
                or not _is_iso_date(rm.group("date"))
                or _is_future_date(rm.group("date"))
            ):
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
                store.instances.append(
                    Instance(
                        klass=klass,
                        target=target,
                        verdict="reproduced",
                        line=raw,
                        date=rm.group("date"),
                        pinned_by=rm.group("test"),
                    )
                )
            continue

        if status.startswith("held"):
            hm = _HELD_STATUS.match(status)
            if hm is None or (
                hm.group("date") is not None
                and (
                    not _is_iso_date(hm.group("date"))
                    or _is_future_date(hm.group("date"))
                )
            ):
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
                store.instances.append(
                    Instance(
                        klass=klass,
                        target=target,
                        verdict="held",
                        line=raw,
                        date=hm.group("date"),
                    )
                )
            continue

        if status.startswith("not-applicable"):
            nm = _NOT_APPLICABLE_STATUS.match(status)
            if nm is None:
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
                store.instances.append(
                    Instance(
                        klass=klass,
                        target=target,
                        verdict="not-applicable",
                        line=raw,
                        reason=nm.group("reason").strip(),
                    )
                )
            continue

        # Status names none of the three tokens at all.
        store.instances.append(
            Instance(klass=klass, target=target, verdict="malformed", line=raw)
        )

    return store


def guarded_path_globs(store: Store) -> list[str]:
    """The `## Guarded paths` bullets, in document order."""
    return list(store.guarded_paths)


def _defined_function_names(path: Path) -> set[str]:
    """Every `def`/`async def` name at module level or inside a class
    body in `path`, resolved by parsing the AST — so a `def` sitting
    inside a docstring, a comment, or any other string literal can never
    satisfy a `pinned by` claim the way a raw-text scan would. Unreadable
    or unparsable files resolve to no names rather than raising.

    Memoized on (path, mtime) — `_test_name_defined_under_repo` walks
    every `test_*.py` under `--repo` PER instance, so an N-instance store
    re-parsed every test file N times without this; keying on mtime (not
    path alone) means an edit between two calls in the same process is
    still picked up rather than serving a stale parse."""
    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        return set()
    return set(_defined_function_names_cached(str(path), mtime_ns))


@functools.lru_cache(maxsize=None)
def _defined_function_names_cached(path_str: str, mtime_ns: int) -> frozenset[str]:
    try:
        text = Path(path_str).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return frozenset()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return frozenset()

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
    return frozenset(names)


def _strip_sh_comments(text: str) -> str:
    """A simple line-based comment strip for a `.sh` file: a line whose
    first non-space character is `#` is dropped entirely, and the `#…`
    tail of any other line is dropped too. Not a shell parser — it does
    not know about `#` inside a quoted string — but good enough to keep
    a name that appears only in a comment from grounding a `pinned by`
    claim, which is the only thing this search needs."""
    kept_lines = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        kept_lines.append(line.split("#", 1)[0])
    return "\n".join(kept_lines)


# Path components a runner never collects tests from — a pin resolved
# only under one of these (or any hidden dir, "." prefix) is dangling
# even when the `def`/name literally exists on disk.
_EXCLUDED_DIR_NAMES = {
    "vendor",
    "node_modules",
    ".git",
    "__pycache__",
    "site-packages",
    ".venv",
    "venv",
    "build",
    "dist",
}


def _under_excluded_dir(path: Path, repo: Path) -> bool:
    try:
        rel_dir_parts = path.relative_to(repo).parts[:-1]
    except ValueError:
        rel_dir_parts = path.parts[:-1]
    return any(
        part.lower() in _EXCLUDED_DIR_NAMES or part.startswith(".")
        for part in rel_dir_parts
    )


def _test_name_defined_under_repo(name: str, repo: Path) -> bool:
    for path in repo.rglob("test_*.py"):
        if _under_excluded_dir(path, repo):
            continue
        if name in _defined_function_names(path):
            return True

    for tests_dir in repo.rglob("tests"):
        if not tests_dir.is_dir():
            continue
        if _under_excluded_dir(tests_dir / "x", repo):
            continue
        for sh_path in tests_dir.glob("*.sh"):
            try:
                text = sh_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if re.search(rf"\b{re.escape(name)}\b", _strip_sh_comments(text)):
                return True

    return False


def check_store(store: Store, repo: Path) -> list[StoreError]:
    """Every refusal the store fires, in a stable order: `incomplete`
    first (a missing section makes further checks meaningless for that
    section), then `unguarded`, then per-instance checks in document
    order."""
    errors: list[StoreError] = []

    missing = [name for name in _SECTION_NAMES if name not in store.sections_present]
    if missing:
        errors.append(
            StoreError(
                "incomplete",
                "Error: incomplete — missing section(s) "
                + ", ".join(f"'## {n}'" for n in missing),
            )
        )

    if not store.guarded_paths:
        errors.append(
            StoreError(
                "unguarded",
                "Error: unguarded — '## Guarded paths' is empty or absent — "
                "at least one glob is required.",
            )
        )

    for inst in store.instances:
        if inst.verdict == "malformed":
            errors.append(
                StoreError(
                    "malformed",
                    f"Error: malformed — status does not match the "
                    f"reproduced/held/not-applicable grammar "
                    f"— line: '{inst.line}'",
                )
            )
        elif inst.verdict == "reproduced":
            if not inst.pinned_by:
                errors.append(
                    StoreError(
                        "unpinned",
                        f"Error: unpinned — reproduced entry has no 'pinned by' "
                        f"— line: '{inst.line}'",
                    )
                )
            elif not _test_name_defined_under_repo(inst.pinned_by, repo):
                errors.append(
                    StoreError(
                        "dangling",
                        f"Error: dangling — test name '{inst.pinned_by}' not found "
                        f"— line: '{inst.line}'",
                    )
                )
        elif inst.verdict == "held":
            if not inst.date:
                errors.append(
                    StoreError(
                        "undated",
                        f"Error: undated — held entry has no date "
                        f"— line: '{inst.line}'",
                    )
                )

    return errors


# The six prose-contract globs `signal` checks `changed` paths against,
# independent of anything the store's `## Guarded paths` section names
# (module docstring "signal" paragraph). Every entry here has a `**/`
# prefix except the last, which is deliberately root-anchored.
_PROSE_CONTRACT_GLOBS = (
    "**/SKILL.md",
    "**/agents/*.md",
    "**/hooks/*.md",
    "**/references/*-packet.md",
    "**/references/*-prompt.md",
    "rules/*.md",
)


def _glob_matches(glob: str, path: str) -> bool:
    """True when `path` (a `/`-separated repo-relative path) matches
    `glob`. Two shapes only — the repo's real guarded-path globs never
    use any other (module docstring): a `**/` prefix matches its
    remainder as a basename pattern at any depth AND at the root; any
    other glob matches `path` in full, with `*` never crossing `/`."""
    if glob.startswith("**/"):
        rest = glob[3:]
        rest_segment_count = len(rest.split("/"))
        path_segments = path.split("/")
        if rest_segment_count > len(path_segments):
            return False
        candidate = "/".join(path_segments[-rest_segment_count:])
        return _match_single_glob(rest, candidate)
    return _match_single_glob(glob, path)


def _match_single_glob(glob: str, path: str) -> bool:
    """`glob` against `path` in full, `*` translated to "not a `/`"."""
    regex = "".join("[^/]*" if ch == "*" else re.escape(ch) for ch in glob)
    return re.fullmatch(regex, path) is not None


class GitError(Exception):
    """A `git` invocation exited nonzero. `_changed_paths`/`_tracked_paths`
    raise this rather than returning `[]` — an empty list is
    indistinguishable from a clean diff/empty repo, so a git failure
    would otherwise silently read as N/A (wb-verdict-arm-b-r2 N1)."""

    def __init__(self, stderr: str) -> None:
        super().__init__(stderr)
        self.stderr = stderr


def _git_run(repo: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )


def _resolve_base(repo: Path, explicit: str | None) -> str | None:
    """base=`--base` resolved to a real sha via `rev-parse` when given,
    then required to be a commit (not a tree/blob) that is a STRICT
    ancestor of HEAD (`merge-base --is-ancestor` true AND not HEAD
    itself) — a base equal to HEAD, or a tree object that happens to
    `rev-parse` cleanly, would otherwise silently empty the diff range
    (wb-verdict-arm-a-r2 N1, t35b-audit). Falls back to `merge-base HEAD
    origin/main`, then `merge-base HEAD main`, when no `--base` is given.
    None (never an empty string) on every failure — the caller fails
    CLOSED rather than diffing an empty range (module docstring)."""
    if explicit:
        result = _git_run(repo, "rev-parse", explicit)
        sha = result.stdout.strip()
        if result.returncode != 0 or not sha:
            return None
        kind = _git_run(repo, "cat-file", "-t", sha).stdout.strip()
        if kind != "commit":
            return None
        head = _git_run(repo, "rev-parse", "HEAD").stdout.strip()
        if not head or sha == head:
            return None
        ancestor = _git_run(repo, "merge-base", "--is-ancestor", sha, "HEAD")
        if ancestor.returncode != 0:
            return None
        return sha
    for other in ("origin/main", "main"):
        result = _git_run(repo, "merge-base", "HEAD", other)
        sha = result.stdout.strip()
        if result.returncode == 0 and sha:
            return sha
    return None


def _changed_paths(repo: Path, base: str) -> list[str]:
    """`git diff --name-only <base>..HEAD` — the committed diff only; a
    dirty worktree contributes nothing extra (module docstring)."""
    result = _git_run(repo, "diff", "--name-only", f"{base}..HEAD")
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def _tracked_paths(repo: Path) -> list[str]:
    result = _git_run(repo, "ls-files")
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def _outside_repo_error(path: Path, repo: Path, label: str) -> str | None:
    """None when `path` resolves inside `repo`; else the exact `Error:
    … is outside --repo …` line — `--store`/`--plan` living outside the
    repo being diffed lets an attacker point the station at a foreign,
    friendlier catalogue while the real one goes unread
    (wb-verdict-arm-a-r2 N1, cross-trust-boundary class)."""
    try:
        path.resolve().relative_to(repo.resolve())
    except ValueError:
        return f"Error: {label} '{path}' is outside --repo '{repo}'"
    return None


def _run_signal(
    repo: Path, store_path: Path, plan_path: Path | None, base_override: str | None
) -> int:
    for path, label in ((store_path, "store"), (plan_path, "plan")):
        if path is None:
            continue
        err = _outside_repo_error(path, repo, label)
        if err is not None:
            print(err, file=sys.stderr)
            return 1

    base = _resolve_base(repo, base_override)
    if base is None:
        if base_override:
            print(
                "attack catalogue: base unresolved — "
                f"{base_override} is not a strict ancestor commit of HEAD",
                file=sys.stderr,
            )
        else:
            print("attack catalogue: base unresolved", file=sys.stderr)
        return 2

    try:
        changed = _changed_paths(repo, base)
    except GitError as exc:
        print(f"attack catalogue: git failed — {exc.stderr}", file=sys.stderr)
        return 2
    prose_hits = [
        path
        for path in changed
        if any(_glob_matches(g, path) for g in _PROSE_CONTRACT_GLOBS)
    ]

    header = "absent"
    if plan_path is not None:
        if plan_card is None:
            print(
                "Error: signal needs plan_card.py beside "
                "check_attack_catalogue.py (copy both, or run the plugin "
                "form)",
                file=sys.stderr,
            )
            return 1
        try:
            plan_text = plan_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Error: cannot read plan '{plan_path}': {exc}", file=sys.stderr)
            return 1
        try:
            parsed = plan_card.safety_bearing(plan_text)
        except ValueError as exc:
            print(
                f"Error: bad 'Safety-bearing:' header in plan '{plan_path}': "
                f"{exc}",
                file=sys.stderr,
            )
            return 1
        header = "absent" if parsed is None else parsed[0]

    if not store_path.exists():
        # An absent store is the adopting-repo-without-a-store case, not a
        # refusal — degrade to N/A on both lines (guarded paths are simply
        # unknowable) rather than exit 1, which is reserved for a store
        # that EXISTS but is unreadable/malformed (module docstring).
        print("attack catalogue: absent", file=sys.stderr)
        print(
            "adversarial audit: N/A — attack catalogue: absent; "
            f"header={header}; base={base}; changed={len(changed)}; "
            f"guarded-hits=0; prose-hits={len(prose_hits)}"
        )
        print(
            "cold reader: N/A — attack catalogue: absent; "
            f"base={base}; changed={len(changed)}; prose-hits={len(prose_hits)}"
        )
        return 0

    try:
        store_text = store_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: cannot read store '{store_path}': {exc}", file=sys.stderr)
        return 1
    try:
        store = parse_store(store_text)
    except StoreError as exc:
        print(exc.message, file=sys.stderr)
        return 1
    try:
        store_errors = check_store(store, repo)
    except OSError as exc:
        print(f"Error: cannot scan repo '{repo}': {exc}", file=sys.stderr)
        return 1
    if store_errors:
        # A present store never degrades to N/A — the same refusals the
        # legacy form runs (unpinned/dangling/undated/unguarded/
        # incomplete/malformed) apply here too, so a corrupted store
        # cannot skip the station by looking superficially well-formed.
        for err in store_errors:
            print(err.message, file=sys.stderr)
        return 1
    guarded_globs = guarded_path_globs(store)

    try:
        tracked = _tracked_paths(repo)
    except GitError as exc:
        print(f"attack catalogue: git failed — {exc.stderr}", file=sys.stderr)
        return 2
    for glob in guarded_globs:
        if not any(_glob_matches(glob, path) for path in tracked):
            print(
                f"WARNING: guarded-path glob matches no tracked file: "
                f"'{glob}'",
                file=sys.stderr,
            )

    guarded_hits = [
        path for path in changed if any(_glob_matches(g, path) for g in guarded_globs)
    ]

    audit_status = "fired —" if (header == "yes" or guarded_hits) else "N/A —"
    print(
        f"adversarial audit: {audit_status} header={header}; base={base}; "
        f"changed={len(changed)}; guarded-hits={len(guarded_hits)}; "
        f"prose-hits={len(prose_hits)}"
    )
    reader_status = "fired —" if prose_hits else "N/A —"
    print(
        f"cold reader: {reader_status} base={base}; changed={len(changed)}; "
        f"prose-hits={len(prose_hits)}"
    )

    if header == "no" and guarded_hits:
        print(
            "attack catalogue: STOP — Safety-bearing: no but "
            f"{len(guarded_hits)} guarded path(s) hit: {', '.join(guarded_hits)}",
            file=sys.stderr,
        )
        return 3

    return 0


def _main_signal(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="check_attack_catalogue.py signal",
        description=(
            "Emit the Step 3.5 attack-catalogue and cold-reader signal "
            "lines for this branch's committed diff against a merge-base "
            "(module docstring 'signal' paragraph)."
        ),
    )
    parser.add_argument("--repo", type=Path, required=True, help="Repo root.")
    parser.add_argument(
        "--store", type=Path, required=True, help="Path to the store markdown file."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=None,
        help="Path to the plan file, for its Safety-bearing header.",
    )
    parser.add_argument(
        "--base",
        default=None,
        help=(
            "Base ref/sha; default: git merge-base HEAD origin/main, else "
            "git merge-base HEAD main."
        ),
    )
    args = parser.parse_args(argv)
    return _run_signal(args.repo, args.store, args.plan, args.base)


def _main_legacy(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parse and check the repo attack-catalogue store "
            "(docs/loom/ATTACK-CATALOGUE.md grammar)."
        )
    )
    parser.add_argument("store", type=Path, help="Path to the store markdown file.")
    parser.add_argument(
        "--repo", type=Path, required=True, help="Repo root, for test-name resolution."
    )
    args = parser.parse_args(argv)

    try:
        text = args.store.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: unreadable — {args.store}: {exc}", file=sys.stderr)
        return 1

    try:
        store = parse_store(text)
    except StoreError as exc:
        print(exc.message, file=sys.stderr)
        return 1

    try:
        errors = check_store(store, args.repo)
    except OSError as exc:
        print(f"Error: cannot scan repo '{args.repo}': {exc}", file=sys.stderr)
        return 1

    if errors:
        for err in errors:
            print(err.message, file=sys.stderr)
        return 1

    print(
        f"OK: {len(store.guarded_paths)} guarded path(s), "
        f"{len(store.instances)} instance(s), "
        f"{len(store.prose_temptations)} prose temptation(s)."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Dispatch to the `signal` subcommand, or the legacy `<store>
    --repo <root>` form — whichever `argv[0]` names (module docstring
    Usage)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "signal":
        return _main_signal(argv[1:])
    return _main_legacy(argv)


if __name__ == "__main__":
    raise SystemExit(main())
