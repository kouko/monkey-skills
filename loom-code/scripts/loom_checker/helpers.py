from __future__ import annotations

from loom_checker.parsing import _COMMENT

from datetime import date
from git_exec import run_git
from pathlib import Path
import os
import re
import sys
import yaml


def _contract_dir() -> Path:
    """Where the contract package sits. In the plugin it is a sibling of
    `scripts/`; in the Codex scaffold copy (concept-model §7a) the checker
    is copied next to its own `contract/`, so both layouts resolve."""
    here = Path(__file__).resolve()
    candidates = (
        here.parents[2] / "contract",
        here.parents[1] / "contract",
        here.parent / "contract",
    )
    for candidate in candidates:
        if (candidate / "manifest.yaml").is_file():
            return candidate
    return candidates[0]


CONTRACT_DIR = _contract_dir()


MANIFEST_PATH = CONTRACT_DIR / "manifest.yaml"


class UsageError(Exception):
    """Bad invocation or an unreadable operand -- exit 2, never exit 0."""


def report(failures: list[tuple[str, str]], err=sys.stderr) -> int:
    for rule_id, reason in failures:
        err.write(f"BLOCK {rule_id}: {reason}\n")
    return 1 if failures else 0


def is_real_date(value: str) -> bool:
    """Return whether value is an actual ISO calendar date."""
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="surrogateescape")


def manifest_path_in_effect() -> Path:
    """The manifest the checker reads: `LOOM_MANIFEST_PATH` when set (a
    test points it at a scratch copy so nothing writes into the tree),
    else the plugin's own contract manifest."""
    override = os.environ.get("LOOM_MANIFEST_PATH", "").strip()
    return Path(override) if override else MANIFEST_PATH


def load_manifest(path: Path | None = None):
    return yaml.safe_load(read_text(path if path is not None else manifest_path_in_effect()))


GIT_TIMEOUT = 30


def git_maybe(repo: Path, *args: str) -> str | None:
    """Stripped stdout, or None when git fails, is missing, or times out."""
    return run_git(repo, *args, timeout=GIT_TIMEOUT)


def git_text(repo: Path, *args: str) -> str:
    """Same, but a failure is undecidable and fails closed -- the caller
    must never read a git error as "nothing changed"."""
    output = git_maybe(repo, *args)
    if output is None:
        raise UsageError(f"`git {' '.join(args)}` failed or timed out in {repo}.")
    return output


def git_ok(repo: Path, *args: str) -> bool:
    """True when git exits 0 (used for existence probes like cat-file -e)."""
    return git_maybe(repo, *args) is not None


def repo_root(start: Path) -> Path:
    """The git work tree holding `start` -- every path rule is relative to it."""
    anchor = start if start.is_dir() else start.parent
    top = git_maybe(anchor, "rev-parse", "--show-toplevel")
    if not top:
        raise UsageError(f"{anchor} is not inside a git work tree.")
    return Path(top)


def artifact_path(manifest, artifact: str, change_id: str, repo: Path) -> Path:
    template = manifest["artifacts"][artifact]["path"]
    return repo / template.replace("<change-id>", change_id)


def kickoff_defaults(repo: Path) -> dict[str, str]:
    """`- <key>: <value> — <reason> (<date>)`, one line per key."""
    path = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        key, sep, rest = stripped[2:].partition(":")
        if not sep or not re.fullmatch(r"[a-z][a-z0-9-]*", key.strip()):
            continue
        value = re.split(r"\s+(?:—|–|--)\s+", rest.strip(), maxsplit=1)[0]
        values[key.strip()] = _COMMENT.sub("", value).strip()
    return values


def interface_surfaces(repo: Path, manifest) -> tuple[list[str], str]:
    """The globs `needs-design` is recomputed against, and where they came
    from -- printed so the answer is never a mystery."""
    default: list[str] = []
    for entry in manifest.get("kickoff_defaults", []):
        if entry.get("name") == "interface-surfaces":
            default = [part.strip() for part in entry["default"].split(",") if part.strip()]
            break
    else:
        raise UsageError("the contract manifest declares no interface-surfaces default.")

    # A repo may ADD its own surfaces; it may not take the contract's away.
    # The narrowing move -- point the key at a glob that matches nothing --
    # is how a `needs-design: no` claim becomes unfalsifiable, so the two
    # sets are unioned rather than one replacing the other.
    declared = kickoff_defaults(repo).get("interface-surfaces")
    extra = [part.strip() for part in (declared or "").split(",") if part.strip()]
    added = [glob for glob in extra if glob not in default]
    if not extra:
        return default, "manifest default"
    if added:
        return default + added, "manifest default + docs/loom/KICKOFF-DEFAULTS.md"
    return default, "manifest default (KICKOFF-DEFAULTS adds nothing new)"


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """`**` crosses directory separators, `*` and `?` do not; a leading
    `**/` also matches zero directories and a trailing `/**` zero children."""
    out, index = [], 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            out.append(r"(?:.*/)?")
            index += 3
        elif pattern.startswith("/**", index) and index + 3 == len(pattern):
            out.append(r"(?:/.*)?")
            index += 3
        elif pattern.startswith("**", index):
            out.append(r".*")
            index += 2
        elif pattern[index] == "*":
            out.append(r"[^/]*")
            index += 1
        elif pattern[index] == "?":
            out.append(r"[^/]")
            index += 1
        else:
            out.append(re.escape(pattern[index]))
            index += 1
    return re.compile("".join(out) + r"\Z")


TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master", "@{upstream}")


REOPEN_TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master")


TRUNK_BRANCH_NAMES = frozenset({"main", "master"})


HOST_PLUMBING_FILES = frozenset(
    {
        ".codex/hooks/loom-checker",  # codex_scaffold.SHIM_COMMAND
        ".codex/hooks/loom_checker.py",  # codex_scaffold.CHECKER_COPY
        ".codex/hooks/git_exec.py",  # codex_scaffold.HOOK_DIR/SIBLING_MODULES
        ".codex/hooks/loom_record_fire.py",  # codex_scaffold.HOOK_DIR/SIBLING_MODULES
        ".codex/hooks/.loom-hook-fired",  # codex_scaffold.MARKER
    }
)


HOST_PLUMBING_DIR_PREFIX = ".codex/hooks/contract/"


def _is_host_plumbing(path: str) -> bool:
    return path in HOST_PLUMBING_FILES or path.startswith(HOST_PLUMBING_DIR_PREFIX)


ON_A_BRANCH = (
    "work on a branch: `git switch -c <change-id>`, then re-run -- "
    "loom recomputes every claim from the branch's diff."
)


def branch_base(repo: Path) -> str:
    """The commit this branch grew from. Two ways this can go wrong, and
    both are fatal, because the alternative -- diffing against nothing and
    seeing no changes -- turns every diff-recomputing rule into a silent
    pass:

    * no trunk resolves at all; and
    * the trunk resolves TO HEAD, which is what a repo with no remote looks
      like while the work is happening on `main` itself (W2 adversary P13).
      `merge-base HEAD main` is then HEAD, the diff is empty, and a
      `needs-design: no` claim passes without ever being tested.
    """
    head = git_maybe(repo, "rev-parse", "HEAD")
    current = git_maybe(repo, "rev-parse", "--abbrev-ref", "HEAD") or ""
    # A branch that has not committed yet also has base == HEAD, and that is
    # fine: the working tree and the untracked files are still in the diff,
    # and the first commit moves HEAD off the base. What is fatal is being ON
    # the trunk, where nothing will ever move.
    on_trunk = current in TRUNK_BRANCH_NAMES
    detached_at_the_base = current == "HEAD"
    for candidate in TRUNK_CANDIDATES:
        merge_base = git_maybe(repo, "merge-base", "HEAD", candidate)
        if not merge_base:
            continue
        if on_trunk or (detached_at_the_base and head and merge_base == head):
            where = f"the trunk branch {current!r}" if on_trunk else "the trunk commit"
            raise UsageError(
                f"HEAD is {where} in {repo} (merge-base HEAD {candidate} "
                f"resolves against it), so the branch diff is empty and every "
                f"recomputed rule would pass a claim it never tested; "
                f"{ON_A_BRANCH}"
            )
        return merge_base
    raise UsageError(
        "no branch base resolves in "
        f"{repo} (tried {', '.join(TRUNK_CANDIDATES)}); the diff cannot be "
        f"recomputed; {ON_A_BRANCH}"
    )


def changed_paths(repo: Path) -> set[str]:
    """Everything this branch changed, committed or not -- a claim about a
    diff must be checked against the whole diff, staging area included.

    The exception is exactly what the Codex scaffold writes (HOST_PLUMBING_FILES /
    HOST_PLUMBING_DIR_PREFIX above), never a surface a user reads -- an adopting
    repo's own hooks under `.codex/hooks/` stay visible. Left directory-wide, the
    scaffold's `contract/templates/**` matched the interface glob (W4-02 F3)."""
    merge_base = branch_base(repo)
    paths: set[str] = set()
    for command in (
        ("diff", "--name-only", merge_base, "HEAD"),
        ("diff", "--name-only", "HEAD"),
        ("diff", "--name-only", "--cached", "HEAD"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        for line in git_text(repo, *command).splitlines():
            if line.strip() and not _is_host_plumbing(line):
                paths.add(line)
    return paths
