#!/usr/bin/env python3
"""The loom checker -- the single deterministic layer of the loom flow.

Every rule here RECOMPUTES its fact from the repository (the intent file,
the manifest, the git diff, or the generated attestation). No rule
trusts an agent's claim about itself; concept-model §7 is explicit that
this layer stops missed steps, not a goal-directed agent.

Sub-commands (the CLI contract other stations depend on):

    loom_checker.py --list-rules
    loom_checker.py intent <path> [--commit-msg <file>]
    loom_checker.py intake <station> <change-id>
    loom_checker.py push [--head <ref>] [--hook]
    loom_checker.py publish --confirm-authorized --title <text> --body-file <absolute-path>
    loom_checker.py finalize-review <change-id> --input <review-input.json>
    loom_checker.py standing <path-to-intent>
    loom_checker.py contract --require <major.minor>

Exit codes: 0 pass, 1 a rule failed (`BLOCK <rule.id>: <reason>` on
stderr), 2 usage or internal error. Any unexpected exception fails
closed as exit 2 -- a checker that cannot decide never says "fine".

Schemas are not restated here: the required frontmatter fields, sections,
station names, interface-surface defaults and artifact paths are read
from `loom-code/contract/manifest.yaml`, which is the versioned contract
package this checker ships with.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

from git_exec import run_git  # sibling module (no __init__.py, no conftest)


def _contract_dir() -> Path:
    """Where the contract package sits. In the plugin it is a sibling of
    `scripts/`; in the Codex scaffold copy (concept-model §7a) the checker
    is copied next to its own `contract/`, so both layouts resolve."""
    here = Path(__file__).resolve()
    candidates = (here.parents[1] / "contract", here.parent / "contract")
    for candidate in candidates:
        if (candidate / "manifest.yaml").is_file():
            return candidate
    return candidates[0]  # nothing found: fail loudly on the first read


CONTRACT_DIR = _contract_dir()
MANIFEST_PATH = CONTRACT_DIR / "manifest.yaml"

USAGE = __doc__.split("Sub-commands (the CLI contract other stations depend on):", 1)[1]

RULES: list[tuple[str, str]] = [
    (
        "contract.requires",
        "A consumer plugin's requires-contract floor is met by this contract manifest version: "
        "the same major, and a minor at or above the required one.",
    ),
    (
        "contract.charter-complete",
        "Every artifact in the contract manifest carries a complete `charter:` block -- "
        "non-empty answers/readers/must/must_not/edits_after, a must_not goes_to naming "
        "another artifact in the table, and a signoff naming a real station.",
    ),
    (
        "intake.confirmed",
        "write-spec / write-plan accept only an intent whose status line reads `confirmed <date>` "
        "with a date the calendar has; `closed <date> — PR #<N>` or `closed <date> — branch <name>` "
        "is blocked -- that change is closed and a new change starts from a new intent. closed is "
        "terminal either way: reopening it -- reverting the status line, or branching from a trunk "
        "that already carries the close -- is blocked the same way, recomputed from the branch's "
        "own history and the trunk's copy of the file, not from the status line alone.",
    ),
    (
        "intake.confirmed-behavior",
        "write-plan accepts a product change only when its spec carries a "
        "`confirmed-behavior: <date> @<spec-blob-sha7>` line naming the spec as it stands.",
    ),
    (
        "intake.test-case-pair",
        "Every task in a newly authored plan names the intent Acceptance lines it owns, "
        "and each named line has positive plus negative or boundary test cases.",
    ),
    (
        "intake.spec-ready",
        "write-plan accepts a needs-design: yes change only when its spec exists and carries "
        "an explicit `pre-build-review: required|not-required — <reason>` declaration. Review "
        "independence is enforced by the write-spec station, not persisted in a ledger.",
    ),
    (
        "intent.kind-recompute",
        "kind: engineering is rejected when the diff touches a declared interface-surface glob.",
    ),
    (
        "intent.needs-design-reason",
        "The needs-design line carries a reason and appears verbatim in the message of the "
        "commit that last changed the intent's status, needs-design or lane line.",
    ),
    (
        "intent.needs-design-recompute",
        "needs-design: no is rejected when the diff touches a declared interface-surface glob.",
    ),
    (
        "intent.product-no-identifiers",
        "A product intent's Problem section names no file path, code identifier or script filename.",
    ),
    (
        "intent.schema",
        "The intent file carries every required frontmatter field and H2 section declared in the contract manifest.",
    ),
    (
        "plan.field-caps",
        "A plan whose frontmatter carries a `charter:` key (any value, presence only) caps each "
        "task's Test and Risk lines at 40 words, its Files line at 8 comma-separated entries "
        "(a comma inside backticks does not split), each numbered `## Risks` item at 40 words, "
        "and each `## Current State Evidence` bullet at 30 words -- CJK runs with no internal "
        "whitespace count as one word by len(text.split()); a task missing its Files, Test or "
        "Risk line blocks too. A plan with no `charter:` line is skipped entirely.",
    ),
    (
        "spec.req-grammar",
        "Every Requirements entry reads `REQ-<n> — <name>` with n contiguous from 1, "
        "unique, and points at an Acceptance number the intent actually carries.",
    ),
    (
        "spec.ui-flows-recompute",
        "While the diff touches a declared interface-surface glob, the spec's UI flows section "
        "carries at least one prose line (outside fences, indented code and HTML comments) with an arrow and "
        "at least four visible characters on each side. This is a structural floor only -- "
        "whether the flow says anything true or useful is the reviewer lens's job, not a "
        "keyword list's. Runs at write-plan intake only.",
    ),
    (
        "standing.product-principles-reject",
        "A product change is rejected until PRINCIPLES.md is ratified: a `ratified-by: <name> "
        "<YYYY-MM-DD>` signature with a real date, over three or more distinct non-negotiables.",
    ),
    (
        "standing.silence",
        "KICKOFF-DEFAULTS `standing-docs: waived` silences the WARN only, never the product rejection.",
    ),
    (
        "standing.warn",
        "A missing PRINCIPLES.md or DESIGN.md prints the fixed three-line WARN and never blocks.",
    ),
]

RULES.append((
    "push.attestation",
    "The branch carries one generated attestation whose functional-content digest, "
    "successful executions, command identities, and passing reviewer verdicts validate "
    "without replaying package tests or adversarial probes.",
))


class UsageError(Exception):
    """Bad invocation or an unreadable operand -- exit 2, never exit 0."""


def list_rules(out=sys.stdout) -> int:
    for rule_id, description in sorted(RULES):
        out.write(f"{rule_id}\t{description}\n")
    return 0


def report(failures: list[tuple[str, str]], err=sys.stderr) -> int:
    for rule_id, reason in failures:
        err.write(f"BLOCK {rule_id}: {reason}\n")
    return 1 if failures else 0



_COMMENT = re.compile(r"\s+#\s.*$")
_FRONTMATTER_LINE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
_ANNOTATION = re.compile(r"[【\[(].*$")

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


GIT_TIMEOUT = 30  # a hung git is a failure, not a pass


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


_CONTENT_TREE_CACHE: dict[tuple[str, str, tuple[str, ...]], str | None] = {}


def functional_content_digest(
    repo: Path, sha: str, change_id: str, manifest: dict | None = None
) -> str | None:
    """Return a Git-derived identity with only declared publication metadata
    for this change excluded. The declaration is repo-neutral; replacing
    ``<change-id>`` scopes every pattern so another change's evidence remains
    ordinary functional content."""
    contract = manifest if manifest is not None else load_manifest()
    patterns = tuple(
        str(pattern).replace("<change-id>", change_id)
        for pattern in contract.get("publication_only_paths", [])
    )
    key = (sha, change_id, patterns)
    if key in _CONTENT_TREE_CACHE:
        return _CONTENT_TREE_CACHE[key]
    listing = git_maybe(repo, "ls-tree", "-r", sha)
    if listing is None:
        _CONTENT_TREE_CACHE[key] = None
        return None

    matchers = [glob_to_regex(pattern) for pattern in patterns]
    kept: list[str] = []
    for line in listing.splitlines():
        if not line or "\t" not in line:
            continue
        path = line.split("\t", 1)[1]
        if not any(matcher.fullmatch(path) for matcher in matchers):
            kept.append(line)
    digest = _hash_object_stdin(repo, "\n".join(kept))
    _CONTENT_TREE_CACHE[key] = digest
    return digest




def _hash_object_stdin(repo: Path, content: str) -> str | None:
    """`git hash-object --stdin -t blob` over `content` -- `run_git` (the
    shared git-invocation body) has no stdin plumbing, and adding it there
    is a change to a file outside this one; this one call stays local and
    uses the same encoding discipline (`git_exec.run_git`'s own
    docstring): UTF-8 text with `surrogateescape` on both sides."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "hash-object", "--stdin", "-t", "blob"],
            input=content, capture_output=True, timeout=GIT_TIMEOUT,
            text=True, encoding="utf-8", errors="surrogateescape",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()




ATTESTATION_SCHEMA = "loom-attestation/v1"
ATTESTATION_KEYS = {
    "schema", "change_id", "content_digest", "executions", "verdicts", "findings"
}


def _command_digest(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


def validate_attestation(
    repo: Path, head_sha: str, change_id: str, attestation: object,
    manifest: dict | None = None,
) -> list[tuple[str, str]]:
    """Validate generated evidence without executing the recorded programs."""
    rule = "push.attestation"
    if not isinstance(attestation, dict) or set(attestation) != ATTESTATION_KEYS:
        return [(rule, "attestation has an unknown or incomplete schema")]
    if attestation.get("schema") != ATTESTATION_SCHEMA:
        return [(rule, f"unsupported attestation schema {attestation.get('schema')!r}")]
    if attestation.get("change_id") != change_id:
        return [(rule, "attestation change_id does not match its path")]
    expected = functional_content_digest(repo, head_sha, change_id, manifest)
    if expected is None or attestation.get("content_digest") != expected:
        return [(rule, "attestation functional content digest does not match the selected tree")]

    executions = attestation.get("executions")
    if not isinstance(executions, list) or not executions:
        return [(rule, "attestation records no successful functional executions")]
    package_runs = 0
    adversarial_runs = 0
    for execution in executions:
        if not isinstance(execution, dict):
            return [(rule, "attestation contains a malformed execution")]
        command = execution.get("command")
        if not isinstance(command, str) or not command.strip():
            return [(rule, "attestation execution has no command")]
        if execution.get("command_digest") != _command_digest(command):
            return [(rule, "attestation execution command digest is forged or corrupted")]
        if execution.get("result") != "pass":
            return [(rule, "attestation contains a non-passing execution")]
        if execution.get("kind") == "package-tests":
            package_runs += 1
            declared, _ = declared_test_command(repo)
            if command != declared:
                return [(rule, "package-tests execution does not match the declared package command")]
        elif execution.get("kind") == "adversarial":
            adversarial_runs += 1
            artifact = execution.get("artifact")
            if not isinstance(artifact, str) or not artifact.strip():
                return [(rule, "adversarial execution names no artifact")]
            if not command_names_artifact(command, artifact):
                return [(rule, "adversarial command does not name its artifact")]
            if not command_executes_artifact(command, artifact):
                return [(rule, "adversarial command must execute the artifact directly")]
            if not git_ok(repo, "cat-file", "-e", f"{head_sha}:{artifact}"):
                return [(rule, "adversarial execution names no committed artifact")]
        else:
            return [(rule, "attestation contains an unknown execution kind")]
    if package_runs != 1:
        return [(rule, "attestation must record exactly one package-tests execution")]
    if adversarial_runs < 1:
        return [(rule, "attestation records no adversarial execution")]

    verdicts = attestation.get("verdicts")
    if not isinstance(verdicts, list) or not verdicts:
        return [(rule, "attestation records no reviewer verdict")]
    reviewers = {str(v.get("reviewer", "")).strip() for v in verdicts if isinstance(v, dict)}
    reviewers.discard("")
    if len(reviewers) < 2:
        return [(rule, "attestation needs two distinct reviewers")]
    for verdict in verdicts:
        if not isinstance(verdict, dict) or verdict.get("verdict") not in {
            "PASS", "PASS_WITH_NOTES"
        }:
            return [(rule, "attestation contains a malformed or non-passing reviewer verdict")]
    if not isinstance(attestation.get("findings"), list):
        return [(rule, "attestation findings must be a list")]
    return []


def repo_root(start: Path) -> Path:
    """The git work tree holding `start` -- every path rule is relative to it."""
    anchor = start if start.is_dir() else start.parent
    top = git_maybe(anchor, "rev-parse", "--show-toplevel")
    if not top:
        raise UsageError(f"{anchor} is not inside a git work tree.")
    return Path(top)


def parse_document(text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Split a loom artifact into its `key: value` frontmatter (the lines
    between the H1 and the first H2) and its H2 sections, keyed by the
    heading with any 【annotation】 stripped."""
    front: dict[str, str] = {}
    sections: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    if text.startswith("﻿"):
        text = text[1:]
    for line in text.splitlines():
        if line.startswith("﻿"):
            # A BOM must never make a key invisible to frontmatter parsing --
            # a commit could otherwise smuggle a `status:` change past every
            # rule that reads it (spec REQ-1, W0-04 round-3 finding).
            line = line[1:]
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(body).strip()
            current = _ANNOTATION.sub("", line[3:]).strip()
            body = []
            continue
        if current is not None:
            body.append(line)
            continue
        if line.startswith("#") or not line.strip():
            continue
        match = _FRONTMATTER_LINE.match(line)
        if match:
            front[match.group(1)] = _COMMENT.sub("", match.group(2)).strip()
    if current is not None:
        sections[current] = "\n".join(body).strip()
    return front, sections


def artifact_path(manifest, artifact: str, change_id: str, repo: Path) -> Path:
    template = manifest["artifacts"][artifact]["path"]
    return repo / template.replace("<change-id>", change_id)




def _squeeze(text: str) -> str:
    return " ".join(text.split())


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

# Separate from TRUNK_CANDIDATES on purpose (W0-02): branch_base()'s
# @{upstream} keeps the change branch's own remote copy, which is exactly
# what a reopen check must NOT trust as "the trunk" -- an upstream that is
# the change branch itself would let a reopen check its own history and
# call that the trunk.
REOPEN_TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master")

# The branch names loom treats as the trunk; standing on one is the P13 hole.
TRUNK_BRANCH_NAMES = frozenset({"main", "master"})

# Host plumbing: exactly what the Codex scaffold writes into the adopting
# repo (loom-code/scripts/codex_scaffold.py -- SHIM_COMMAND, CHECKER_COPY,
# HOOK_DIR + SIBLING_MODULES, CONTRACT_COPY), never a surface any rule reads
# as the change's diff (W4-02 finding F3). This is scoped to those specific
# files, not to the whole `.codex/hooks/` directory: an adopting repo may
# keep its own gate scripts there too (R22-O3, this repo does), and a
# directory-wide exemption made that real gate code invisible to the intent
# recomputes.
HOST_PLUMBING_FILES = frozenset(
    {
        ".codex/hooks/loom-checker",  # codex_scaffold.SHIM_COMMAND
        ".codex/hooks/loom_checker.py",  # codex_scaffold.CHECKER_COPY
        ".codex/hooks/git_exec.py",  # codex_scaffold.HOOK_DIR/SIBLING_MODULES
        ".codex/hooks/loom_record_fire.py",  # codex_scaffold.HOOK_DIR/SIBLING_MODULES
        ".codex/hooks/.loom-hook-fired",  # codex_scaffold.MARKER
    }
)
HOST_PLUMBING_DIR_PREFIX = ".codex/hooks/contract/"  # codex_scaffold.CONTRACT_COPY


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


def cmd_intent(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    path, commit_msg = None, None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--commit-msg":
            if not rest:
                raise UsageError("--commit-msg needs a file path.")
            commit_msg = Path(rest.pop(0))
        elif path is None:
            path = Path(token)
        else:
            raise UsageError(f"unexpected argument {token!r}.")
    if path is None:
        raise UsageError("intent needs a path to the intent file.")
    if not path.is_file():
        raise UsageError(f"no intent file at {path}")

    manifest = load_manifest()
    repo = repo_root(path)
    front, sections = parse_document(read_text(path))
    failures: list[tuple[str, str]] = []

    failures += check_intent_schema(manifest, front, sections)
    failures += check_map_exists(repo, front)
    failures += check_product_no_identifiers(front, sections)
    failures += check_lane_schema(front)
    failures += check_lane_reason(front, commit_msg, repo, path, out)

    reason_failures, needs_design = check_needs_design_reason(
        front, commit_msg, repo, path, out
    )
    failures += reason_failures

    kind = front.get("kind", "").strip()
    if needs_design == "no" or kind == "engineering":
        touched = touched_interface_surfaces(repo, manifest, out)
        if needs_design == "no":
            failures += check_needs_design_recompute(touched)
        if kind == "engineering":
            failures += check_kind_recompute(touched)

    return report(failures, err)


def check_intent_schema(manifest, front, sections) -> list[tuple[str, str]]:
    """Every required field/section from the manifest, recomputed."""
    failures = []
    for field in manifest["artifacts"]["intent"]["fields"]:
        if not field.get("required"):
            continue
        name, kind = field["name"], field["kind"]
        holder = front if kind == "frontmatter" else sections
        value = holder.get(name, "").strip()
        if not value:
            failures.append(
                ("intent.schema", f"required {kind} `{name}` is missing or empty.")
            )
            continue
        allowed = field.get("values")
        if allowed and value not in allowed:
            failures.append(
                ("intent.schema", f"`{name}: {value}` is not one of {allowed}.")
            )
    return failures


MAP_ORIGINATOR = re.compile(r"^map:\s*(\S+)$")


def check_map_exists(repo: Path, front) -> list[tuple[str, str]]:
    """A `map:` id names a Map that exists.

    `start_delivery.py` writes both sides at once, but an intent written or
    edited by hand carries free text, and a dangling id points the reader at
    a Map that is not there while the change looks map-originated (W3
    adversary P13). Both spellings of the same claim are resolved: the
    `map:` field and an `originator: map:<id>`."""
    failures = []
    claims: list[tuple[str, str]] = []
    map_id = front.get("map", "").strip()
    if map_id:
        claims.append(("map", map_id))
    originator = front.get("originator", "").strip()
    if (match := MAP_ORIGINATOR.match(originator)):
        claims.append(("originator", match.group(1)))
    for field, value in claims:
        if not (repo / "docs" / "loom" / "maps" / value / "MAP.md").is_file():
            failures.append((
                "intent.schema",
                f"`{field}: {'map:' if field == 'originator' else ''}{value}` names a "
                f"Map that does not exist: no docs/loom/maps/{value}/MAP.md. An intent "
                "cannot originate in a Map that is not there.",
            ))
    return failures


IDENTIFIER_PATTERNS = [
    (
        re.compile(
            r"(?<![\w./-])[\w.-]+\.(?:py|sh|bash|zsh|js|jsx|ts|tsx|json|ya?ml|toml|md"
            r"|rb|go|rs|java|c|h|cpp|sql|css|html)(?![\w/])"
        ),
        "a file or script name",
    ),
    (re.compile(r"(?<![\w./-])[\w.-]+/[\w./-]+"), "a file path"),
    (re.compile(r"\b\w+\(\s*\)"), "a function call"),
    (re.compile(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b"), "a snake_case identifier"),
    (re.compile(r"\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b"), "a camelCase identifier"),
]


# Two things a person with the problem writes that the patterns above read
# as code, and that no amount of plain-English discipline removes: the name
# of the device they use, and a date written with slashes. They are masked
# out (replaced by spaces, so every other match keeps its offsets) before
# the patterns run; everything else still counts.
CONSUMER_PRODUCT_NAMES = re.compile(
    r"\b(?:iPhone|iPadOS|iPad|iOS|macOS|eBay|iCloud|iMac|tvOS|watchOS)\b"
)
DATE_LIKE_FRACTION = re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")


def mask_allowed_tokens(problem: str) -> str:
    for pattern in (CONSUMER_PRODUCT_NAMES, DATE_LIKE_FRACTION):
        problem = pattern.sub(lambda match: " " * len(match.group(0)), problem)
    return problem


def check_product_no_identifiers(front, sections) -> list[tuple[str, str]]:
    """A product Problem is written for the person with the problem: it may
    not name the code that will change (concept-model §2b)."""
    if front.get("kind", "").strip() != "product":
        return []
    problem = mask_allowed_tokens(sections.get("Problem", ""))
    failures = []
    for pattern, what in IDENTIFIER_PATTERNS:
        match = pattern.search(problem)
        if match:
            failures.append(
                (
                    "intent.product-no-identifiers",
                    f"the Problem section of a product intent names {what}: "
                    f"{match.group(0)!r}.",
                )
            )
    return failures


NEEDS_DESIGN_GRAMMAR = re.compile(r"^(yes|no)\s*(?:—|–|--)\s*(\S.*)$")


FRONTMATTER_DECISION = ("status:", "needs-design:")


def deciding_commit(
    repo: Path, relative: str, prefixes: tuple[str, ...] = FRONTMATTER_DECISION
) -> str | None:
    """The newest commit that CHANGED the intent's `status:` or
    `needs-design:` line -- the one that decided something. `prefixes`
    generalizes this to another frontmatter line with the same discipline
    (the `lane:` switch line reuses it below) without touching the
    needs-design/status callers, which keep the default.

    Reading the newest touching commit instead made every later edit to the
    intent body (a new open question, an evidence path) owe the needs-design
    line, which is not what concept-model §2b asks for: the line belongs on
    the commit that writes or changes the decision (W2 re-review NF-4)."""
    for sha in git_text(repo, "log", "--format=%H", "--", relative).splitlines():
        if not sha.strip():
            continue
        if _decides_in_frontmatter(repo, sha, relative, prefixes=prefixes):
            return sha
    return None


HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def frontmatter_end(text: str) -> int:
    """The 1-based line number where the front matter stops: the first `## `
    heading. Everything at or after it is body -- an example `status:` line
    inside a fence decides nothing."""
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            return number
    return len(text.splitlines()) + 1


def _decides_in_frontmatter(
    repo: Path, sha: str, relative: str, prefixes: tuple[str, ...] = FRONTMATTER_DECISION
) -> bool:
    """Did this commit change a `status:`/`needs-design:` line (or another
    `prefixes` line) that lived in the intent's FRONT MATTER? A quoted or
    fenced copy in the body is an example, not a decision (W2 re-review)."""
    diff = git_text(repo, "show", "--format=", "--unified=0", sha, "--", relative)
    after = frontmatter_end(git_maybe(repo, "show", f"{sha}:{relative}") or "")
    before = frontmatter_end(git_maybe(repo, "show", f"{sha}^:{relative}") or "")
    old_line = new_line = 0
    for line in diff.splitlines():
        if (header := HUNK_HEADER.match(line)):
            old_line, new_line = int(header.group(1)), int(header.group(2))
            continue
        if line[:3] in ("+++", "---"):
            continue
        marker, body = line[:1], line[1:]
        if marker == "+":
            decisive = body.lstrip().startswith(prefixes) and new_line < after
            new_line += 1
        elif marker == "-":
            decisive = body.lstrip().startswith(prefixes) and old_line < before
            old_line += 1
        else:
            old_line += 1
            new_line += 1
            continue
        if decisive:
            return True
    return False


SQUASH_SUBJECT = re.compile(r" \(#\d+\)\s*$")


def _squash_note(repo: Path, relative: str, sha: str) -> str | None:
    """Does `sha` have the SHAPE of a GitHub "Squash and merge" commit on
    the trunk? Three conditions, all git topology or subject shape -- never
    message text, so a hand-written subject that merely LOOKS like a squash
    cannot forge the exception (W0-01 adversary: the fake-`(#1)`-off-main
    case):

    1. single parent -- the squash button makes a plain commit, not a
       2-parent merge (a real `--no-ff` merge already passes today by a
       different path and is untouched by this function);
    2. the subject ends ` (#<n>)` -- exactly what GitHub writes;
    3. `sha` is on the trunk's first-parent chain (REOPEN_TRUNK_CANDIDATES
       -- the same four names `branch_base()` resolves against, minus
       `@{upstream}` for the reason documented at that constant: a
       branch's own upstream must never stand in as "the trunk" here).
       This is checked by literal MEMBERSHIP in
       `git rev-list --first-parent <candidate>`, not by
       `merge-base --is-ancestor` -- ancestry alone proves `sha` is
       *reachable* from the candidate, which a hand-written, single-parent
       `... (#<n>)` commit on a side branch also is once that branch is
       merged into the candidate with a real (`--no-ff`) merge commit; it
       is reachable but never walked by a first-parent traversal, since a
       first-parent walk steps over the merge commit straight to the
       candidate's OWN previous first parent and never descends into the
       merged-in branch. The membership walk is O(history) in the worst
       case (it lists the candidate's entire first-parent chain to check
       one sha) -- cheap in practice because the trunk's first-parent
       chain is short relative to full history including side branches.

    These three are all this function can verify offline: it has no way to
    ask GitHub whether `sha` really came from a "Squash and merge" click,
    or whether the source branch's HEAD really carried the needs-design
    line -- PR provenance is not fetchable from a local clone. The note
    says exactly that, and states the shape-match as shape, not as a
    verified squash. What is actually relied on is that the line was
    already checked, verbatim, on the branch commit BEFORE it could reach
    the trunk -- by this same rule running as the push gate on that
    branch -- so the line is assumed carried forward, not re-derived here.

    Residual: a commit hand-written with this exact shape (single parent,
    `... (#<n>)` subject) and pushed straight to the trunk without going
    through a reviewed branch -- bypassing the push gate that would have
    checked the line -- is accepted by this exception too. That path is
    governed by branch protection (who may push directly to the trunk),
    not by this rule; this rule only recognizes the shape, it cannot tell
    a real squash-merge from a direct push that mimics it.

    Returns the printable note when all three shape conditions hold, else
    None -- the note itself is the evidence for "why did it say that"
    (concept-model §2b), not a bare pass.
    """
    parents = git_maybe(repo, "log", "-1", "--format=%P", sha)
    if parents is None or len(parents.split()) != 1:
        return None
    subject = git_maybe(repo, "log", "-1", "--format=%s", sha)
    if subject is None or not SQUASH_SUBJECT.search(subject):
        return None
    for candidate in REOPEN_TRUNK_CANDIDATES:
        if git_maybe(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") is None:
            continue
        first_parent_chain = git_maybe(repo, "rev-list", "--first-parent", candidate)
        if first_parent_chain is None or sha not in first_parent_chain.split():
            continue
        return (
            f"intent.needs-design-reason: commit {sha[:7]} ({relative}) has the "
            f"shape of a GitHub squash on {candidate}'s first-parent chain "
            f"(single parent, subject {subject!r}); PR provenance is not "
            "verifiable offline, so this is not a confirmed squash -- the "
            "needs-design line is assumed carried by the branch that the push "
            "gate checked before this commit reached the trunk."
        )
    return None


def check_needs_design_reason(
    front, commit_msg: Path | None, repo: Path, path: Path, out=sys.stdout
):
    """`needs-design` carries a reason, and the intent's commit message
    repeats the line verbatim (concept-model §2b). With no `--commit-msg`
    (the post-commit and station calls) the message is that of the last commit
    that TOUCHED THIS INTENT, not HEAD's -- reading HEAD made the rule pass or
    fail on whatever happened to be committed last, so one unrelated commit
    after the intent broke it and one unrelated commit carrying the line
    could satisfy it (W2 re-review F5). The check is never skipped for want
    of a flag."""
    raw = front.get("needs-design", "").strip()
    if not raw:
        return [], None
    match = NEEDS_DESIGN_GRAMMAR.match(raw)
    if not match:
        return (
            [
                (
                    "intent.needs-design-reason",
                    f"`needs-design: {raw}` does not match `yes | no — <reason>`.",
                )
            ],
            raw.split()[0] if raw.split() else None,
        )
    verdict = match.group(1)
    sha, relative = None, None
    if commit_msg is not None:
        if not commit_msg.is_file():
            raise UsageError(f"no commit message file at {commit_msg}")
        message, source = read_text(commit_msg), str(commit_msg)
    else:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        sha = deciding_commit(repo, relative)
        if sha is None:
            message, source = "", f"{relative} (no commit has decided it yet)"
        else:
            message = git_text(repo, "show", "-s", "--format=%B", sha)
            source = f"commit {sha[:7]}, which last changed status/needs-design"
    line = f"needs-design: {raw}"
    if _squeeze(line) not in _squeeze(message):
        # `--commit-msg` names an exact message to check and is never the
        # station's own recompute (deciding_commit() ran, if at all, only in
        # the else branch above) -- the squash exception only ever applies
        # to a commit this function itself found via git topology.
        if sha is not None and relative is not None:
            note = _squash_note(repo, relative, sha)
            if note is not None:
                out.write(note + "\n")
                return [], verdict
        return (
            [
                (
                    "intent.needs-design-reason",
                    f"the commit message ({source}) does not carry the line `{line}`.",
                )
            ],
            verdict,
        )
    return [], verdict


LANE_LINE_PREFIX = ("lane:",)

# `lane: express` / `lane: gate-only` / `lane: full`, but NEVER bare: every
# legal value carries dated user attribution, either the DECLARED suffix
# `— declared <YYYY-MM-DD> by <name>` (day-one, no round/wave reference) or
# the SWITCH suffix `— switched <YYYY-MM-DD> by <name>, from <wave
# <n>|round <n>>` (mid-flight). Intent Acceptance 1 says it in so many
# words: "宣告或切換都帶日期與人" -- declaring, not only switching, carries
# date and person (wave-end:1 adversary finding 1-01) -- so a BARE `lane:
# express`, with no suffix at all, is not a legal value; `by <name>` is
# mandatory in both suffixes (plan Risk: the checker cannot tell a user
# from an agent, so requiring `by <name>` is the only machine-checkable
# trace that someone is named), and either suffix missing it, or missing
# the date, fails the whole match rather than silently matching just the
# bare name -- a truncated line is rejected instead of read as if nothing
# had been declared. `full` is legal in both suffix forms (the intent's
# own Proposed outcome point 1 says reverting to `full` is "隨時可以，同樣
# 一行", always possible with the same kind of line).
LANE_GRAMMAR = re.compile(
    r"^(?P<name>express|gate-only|full)\s*(?:—|–|--)\s*"
    r"(?:"
    r"declared\s+(?P<declared_date>\d{4}-\d{2}-\d{2})\s+by\s+(?P<declared_by>[^,]+?)"
    r"|"
    r"switched\s+(?P<date>\d{4}-\d{2}-\d{2})\s+by\s+(?P<by>[^,]+?)\s*,\s*from\s+"
    r"(?P<unit>wave|round)\s+(?P<n>\d+)"
    r")"
    r"\s*$"
)


def check_lane_schema(front) -> list[tuple[str, str]]:
    """`lane:` is optional, but when present it must carry dated user
    attribution -- the declared suffix `— declared <YYYY-MM-DD> by <name>`
    or the switch suffix `— switched <YYYY-MM-DD> by <name>, from <wave
    <n>|round <n>>`, both WITH `by <name>` -- a bare `lane: express` (no
    suffix at all), or a suffix that omits who wrote it, is unrecoverable
    and blocks here rather than being silently accepted as a plain
    declaration."""
    raw = front.get("lane", "").strip()
    if not raw or LANE_GRAMMAR.match(raw):
        return []
    return [
        (
            "intent.schema",
            f"`lane: {raw}` does not match the declared grammar `express | "
            "gate-only | full — declared <YYYY-MM-DD> by <name>` or the switch "
            "grammar `<name> — switched <YYYY-MM-DD> by <name>, from <wave "
            "<n>|round <n>>` -- a bare lane name with no dated attribution is "
            "not a legal value.",
        )
    ]


def check_lane_reason(
    front, commit_msg: Path | None, repo: Path, path: Path, out=sys.stdout
) -> list[tuple[str, str]]:
    """The `lane:` line, declared or switched, must appear verbatim in the
    message of the commit that last changed it -- the same discipline
    `check_needs_design_reason` applies to `status:`/`needs-design:`,
    reused here (`deciding_commit`/`_decides_in_frontmatter` take a
    `prefixes` argument for exactly this) since only the user may write
    this line and its provenance matters the same way."""
    raw = front.get("lane", "").strip()
    if not raw:
        return []
    sha = relative = None
    if commit_msg is not None:
        if not commit_msg.is_file():
            raise UsageError(f"no commit message file at {commit_msg}")
        message, source = read_text(commit_msg), str(commit_msg)
    else:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        sha = deciding_commit(repo, relative, prefixes=LANE_LINE_PREFIX)
        if sha is None:
            message, source = "", f"{relative} (no commit has decided it yet)"
        else:
            message = git_text(repo, "show", "-s", "--format=%B", sha)
            source = f"commit {sha[:7]}, which last changed lane"
    line = f"lane: {raw}"
    if _squeeze(line) not in _squeeze(message):
        if sha is not None and relative is not None:
            note = _squash_note(repo, relative, sha)
            if note is not None:
                out.write(note + "\n")
                return []
        return [
            (
                "intent.needs-design-reason",
                f"the commit message ({source}) does not carry the line `{line}`.",
            )
        ]
    return []






TEMPLATES_GLOB = "**/templates/**"


def touched_interface_surfaces(repo: Path, manifest, out) -> list[str]:
    """The changed paths that land on a declared interface surface, and a
    printed line saying which globs were used -- the answer to "why did it
    say that" is never a mystery. Both `intent.needs-design-recompute` and
    `intent.kind-recompute` read this one recomputation.

    Only the `**/templates/**` glob match is narrowed by artifact type: it
    also matches an agent-filled `.md` template that no user ever reads, so
    a match against THIS glob alone counts only when `_artifact_type_for`
    types the path `code` -- an `.md`/`.jinja` template stays excluded, a
    `.tsx`/`.py` one still counts. A match against any OTHER glob -- the
    manifest default (`**/cli/**`, `**/api/**`, `**/commands/**`,
    `**/*.tsx`) or one a repo added via KICKOFF-DEFAULTS -- counts
    regardless of type: a CLI help `.md` under `**/cli/**` is a user
    surface exactly as much as a `.py` one is. This does not let an agent
    narrow the surface, because `artifact-types` in KICKOFF-DEFAULTS is
    reserved (the checker never reads it, per the manifest note); the type
    mapping is the contract's own `artifact_types:` table, fixed regardless
    of what a repo declares."""
    globs, source = interface_surfaces(repo, manifest)
    matchers = [(pattern, glob_to_regex(pattern)) for pattern in globs]
    touched = sorted(
        path
        for path in changed_paths(repo)
        if any(
            matcher.match(path)
            and (
                pattern != TEMPLATES_GLOB
                or _artifact_type_for(manifest, path) == "code"
            )
            for pattern, matcher in matchers
        )
    )
    out.write(
        f"interface-surfaces ({source}): {', '.join(globs)} "
        f"(non-code paths under {TEMPLATES_GLOB} excluded)\n"
    )
    return touched


def check_needs_design_recompute(touched: list[str]) -> list[tuple[str, str]]:
    """`needs-design: no` is a claim; the diff is the fact."""
    if not touched:
        return []
    return [
        (
            "intent.needs-design-recompute",
            "`needs-design: no` but the diff touches a declared interface "
            f"surface: {', '.join(touched[:5])}.",
        )
    ]


def check_kind_recompute(touched: list[str]) -> list[tuple[str, str]]:
    """`kind:` is a claim too, and it is the one that switches off all three
    product rules at once -- the PRINCIPLES.md rejection, the plain-words
    Problem, and decision point (2) (W2 adversary P05). `needs-design` is
    already recomputed against the interface globs; the same recomputation
    answers `kind:`, so an `engineering` label over a diff that edits what
    the user reads or types is refused.

    Note what is NOT here: a declared `needs-design: yes` on its own does not
    make a change product. Reason (b) of concept-model §2b -- many states or
    objects and no spec -- is a legitimate engineering reason to write a
    spec, and §4 gives engineering a needs-design: yes path that simply
    skips decision point (2). Only the diff says "user surface"."""
    if not touched:
        return []
    return [
        (
            "intent.kind-recompute",
            "`kind: engineering` but the diff touches a user surface: "
            f"{', '.join(touched[:5])}. Either `kind: product` (which brings "
            "the ratified PRINCIPLES.md, the plain-words Problem and decision "
            "point 2 with it), or keep the change off the declared interface "
            "surfaces -- docs/loom/KICKOFF-DEFAULTS.md `interface-surfaces` "
            "can only ADD globs, never remove one.",
        )
    ]


CHANGE_ID = re.compile(r"[A-Za-z0-9._-]+")
# `status:` grammar (contract/manifest.yaml, contract/templates/intent.md):
# `open | confirmed <date> | closed <date> — PR #<N> | closed <date> —
# branch <name> | withdrawn — <reason>`, each alternative allowing a
# trailing ` #...` comment, shared by intake.confirmed and intent validation.
# Groups: 1=confirmed date, 2=PR-form closed date, 3=PR number,
# 4=branch-form closed date, 5=branch name. Only one of (2,3)/(4,5) is
# ever non-None on a match -- `_status_closed_info` picks the pair that fired.
_STATUS_CLOSED_ALT = (
    r"closed (\d{4}-\d{2}-\d{2}) — PR #(\d+)"
    r"|closed (\d{4}-\d{2}-\d{2}) — branch ([A-Za-z0-9._/-]+)"
)
STATUS = re.compile(
    r"(?:open"
    r"|confirmed (\d{4}-\d{2}-\d{2})"
    rf"|{_STATUS_CLOSED_ALT}"
    r"|withdrawn — .+)"
    r"(?:\s+#.*)?"
)

# The literal text before the closed alternative's first capture group --
# "closed " -- derived from _STATUS_CLOSED_ALT rather than hand-copied, so
# the reopen recompute below and the grammar cannot drift apart (W0-02).
STATUS_CLOSED_LITERAL = _STATUS_CLOSED_ALT.split("(", 1)[0]
# `git log -G` uses POSIX ERE; `[[:space:]]*` mirrors the optional
# whitespace parse_document()'s frontmatter line already strips between
# `status:` and its value, so the history search and the grammar agree on
# a hand-edited line too.
REOPEN_LOG_PATTERN = rf"^status:[[:space:]]*{STATUS_CLOSED_LITERAL}"

INTAKE_STATIONS = ("write-spec", "write-plan")  # the two stations that accept an intent


def _status_closed_info(match: re.Match) -> tuple[str, str, str] | None:
    """`(date, kind, identifier)` for a `STATUS` match that hit either
    closed alternative -- `kind` is `"PR"` or `"branch"`, `identifier` the
    PR number or the branch name. None when `match` did not hit a closed
    alternative at all (W1-03)."""
    if match.group(2) is not None:
        return match.group(2), "PR", match.group(3)
    if match.group(4) is not None:
        return match.group(4), "branch", match.group(5)
    return None


def _status_closed_descriptor(kind: str, identifier: str) -> str:
    """The human-readable naming of a closed status's identifier -- `PR
    #<n>` or `branch <name>` -- shared by every message that reports a
    closed intent (W1-03)."""
    return f"PR #{identifier}" if kind == "PR" else f"branch {identifier}"


def _status_closed_descriptor_from_text(text: str) -> str | None:
    """The closed-status descriptor (`PR #<n>` or `branch <name>`) from
    `text`'s frontmatter status line, or None when the status is anything
    else (including absent/malformed)."""
    front, _sections = parse_document(text)
    match = STATUS.fullmatch(front.get("status", "").strip())
    if match is None:
        return None
    info = _status_closed_info(match)
    if info is None:
        return None
    _date, kind, identifier = info
    return _status_closed_descriptor(kind, identifier)


def check_intent_not_reopened(repo: Path, intent_path: Path, change_id: str, out) -> tuple[str, str] | None:
    """`intake.confirmed`'s terminal rule (REQ-2, W0-02): a reopen is caught
    even when the intent file's OWN current status line has been changed
    back to `confirmed`, by recomputing two things the file's current
    content cannot hide:

    (i) the branch's own history of the file -- `git log -G` for a line
        that ever read `status: closed ...` -- so reverting the status
        line back to `confirmed` does not un-close the change; and
    (ii) the trunk's current copy of the file -- so a branch cut before the
         close, from a trunk that already carries it, is caught too.

    Neither is a flag an agent writes; both are recomputed from the
    repository. When no trunk ref resolves at all, case (ii) is reported as
    absent (not as a pass) rather than silently skipped."""
    intent_rel = intent_path.relative_to(repo)
    log_output = git_maybe(repo, "log", "--format=%H", f"-G{REOPEN_LOG_PATTERN}", "--", str(intent_rel))
    for commit in (log_output or "").splitlines():
        commit = commit.strip()
        if not commit:
            continue
        content = git_maybe(repo, "show", f"{commit}:{intent_rel}")
        if content is None:
            continue
        descriptor = _status_closed_descriptor_from_text(content)
        if descriptor is not None:
            return (
                "intake.confirmed",
                f"{change_id} was closed ({descriptor}) and closed intents "
                "are not reopened; start a new intent",
            )

    for candidate in REOPEN_TRUNK_CANDIDATES:
        if git_maybe(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") is None:
            continue
        content = git_maybe(repo, "show", f"{candidate}:{intent_rel}")
        if content is not None:
            descriptor = _status_closed_descriptor_from_text(content)
            if descriptor is not None:
                return (
                    "intake.confirmed",
                    f"{change_id} was closed ({descriptor}) and closed intents "
                    "are not reopened; start a new intent",
                )
        break
    else:
        out.write(
            "intake.confirmed: no trunk ref resolves among "
            f"{', '.join(REOPEN_TRUNK_CANDIDATES)}; the trunk copy check is absent.\n"
        )
    return None


def cmd_intake(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    if len(args) < 2:
        raise UsageError("intake needs a station and a change-id.")
    station, change_id = args[0], args[1]
    if not CHANGE_ID.fullmatch(change_id):
        raise UsageError(
            f"{change_id!r} is not a change-id; expected [A-Za-z0-9._-]+ "
            "(the id is spliced into a path, so nothing else is accepted)."
        )
    if len(args) > 2:
        raise UsageError(f"unexpected argument {args[2]!r}.")
    if station not in INTAKE_STATIONS:
        raise UsageError(
            f"unknown station {station!r}; intake covers {' and '.join(INTAKE_STATIONS)}."
        )

    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    intent_path = artifact_path(manifest, "intent", change_id, repo)

    if not intent_path.is_file():
        return report(
            [("intake.confirmed", f"no intent file at {intent_path.relative_to(repo)}.")],
            err,
        )
    front, sections = parse_document(read_text(intent_path))

    status = front.get("status", "").strip()
    match = STATUS.fullmatch(status)
    confirmed_date = match.group(1) if match else None
    closed_info = _status_closed_info(match) if match else None
    if closed_info is not None:
        closed_date, kind, identifier = closed_info
        descriptor = _status_closed_descriptor(kind, identifier)
        if not is_real_date(closed_date):
            return report(
                [
                    (
                        "intake.confirmed",
                        f"`status: closed {closed_date} — {descriptor}` names "
                        "something that is not a real date.",
                    )
                ],
                err,
            )
        return report(
            [
                (
                    "intake.confirmed",
                    f"{station} accepts only `status: confirmed <date>`; this change "
                    f"is closed ({descriptor}) and closed intents are not reopened; "
                    "start a new intent.",
                )
            ],
            err,
        )
    reopen_failure = check_intent_not_reopened(repo, intent_path, change_id, out)
    if reopen_failure is not None:
        return report([reopen_failure], err)

    if confirmed_date is None:
        shown = status or "absent (= open)"
        return report(
            [
                (
                    "intake.confirmed",
                    f"{station} accepts only `status: confirmed <date>`; status is {shown}.",
                )
            ],
            err,
        )
    if not is_real_date(confirmed_date):
        return report(
            [
                (
                    "intake.confirmed",
                    f"`status: confirmed {confirmed_date}` names something "
                    "that is not a real date.",
                )
            ],
            err,
        )

    failures: list[tuple[str, str]] = []
    if station == "write-plan":
        failures += check_test_case_pairs(manifest, repo, change_id, sections)
        failures += check_plan_field_caps_at(manifest, repo, change_id)

    kind = front.get("kind", "").strip()
    needs_design = front.get("needs-design", "").strip().split()[:1]
    yes_at_write_plan = station == "write-plan" and needs_design == ["yes"]

    touched: list[str] = []
    if kind == "engineering" or yes_at_write_plan:
        touched = touched_interface_surfaces(repo, manifest, out)
    if kind == "engineering":
        failures += check_kind_recompute(touched)

    failures += check_req_grammar(manifest, repo, change_id, sections)

    if yes_at_write_plan:
        failures += check_spec_ready(manifest, repo, change_id)
        failures += check_ui_flows_recompute(manifest, repo, change_id, touched)
        if kind == "product":
            failures += check_confirmed_behavior(manifest, repo, change_id, err)
    return report(failures, err)


# --- spec body grammar (W2 adversaries P03, P06) ---------------------------

REQ_LINE = re.compile(r"^\s*(?:[-*+]\s+)?REQ-(\d+)\s*(?:—|–|--)\s*(\S.*)$")
ACCEPTANCE_POINTER = re.compile(r"(?:→|->)\s*Acceptance\s*#(\d+)")


def acceptance_count(intent_sections: dict[str, str]) -> int:
    """How many things the user said "done means this" about."""
    body = intent_sections.get("Acceptance", "")
    return sum(1 for line in body.splitlines() if LIST_ITEM.match(line))


def check_req_grammar(manifest, repo: Path, change_id: str, intent_sections):
    """The Requirements grammar the contract manifest declares, recomputed.

    `REQ-<n> — <name>` ids are what a plan task, a finding and a blind-run
    line all point at, so a skipped number, a reused one, or a requirement
    that answers to no Acceptance line breaks addressability everywhere
    downstream (W2 adversary P03). The manifest declared the grammar from
    the start; until now nothing read it."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # a missing spec is intake.spec-ready's business, not this rule
    _front, sections = parse_document(read_text(spec_path))
    if "Requirements" not in sections:
        return []  # already reported as a schema gap by the spec's own review
    body = sections["Requirements"]

    entries: list[tuple[int, str, str]] = []   # (number, name, block text)
    current: list[str] = []
    for line in body.splitlines():
        match = REQ_LINE.match(line)
        if match:
            entries.append((int(match.group(1)), match.group(2).strip(), ""))
            current = []
        elif entries:
            current.append(line)
        if entries:
            number, name, _ = entries[-1]
            entries[-1] = (number, name, "\n".join(current))

    if not entries:
        return [
            (
                "spec.req-grammar",
                f"{spec_path.relative_to(repo)} has a `## Requirements` section "
                "with no `REQ-<n> — <name>` line in it; the ids are what plan "
                "tasks, findings and the blind-run report point at.",
            )
        ]

    failures = []
    seen: set[int] = set()
    for position, (number, _name, _block) in enumerate(entries, start=1):
        if number in seen:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} appears twice; every requirement id is used "
                    "once, so a finding against one of them is unambiguous.",
                )
            )
        elif number != position:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} is the {position}th requirement; the ids run "
                    f"contiguously from 1, so this one has to be REQ-{position}.",
                )
            )
        seen.add(number)

    total = acceptance_count(intent_sections)
    for number, name, block in entries:
        pointers = [int(value) for value in ACCEPTANCE_POINTER.findall(name + "\n" + block)]
        if not pointers:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} carries no `→ Acceptance #<n>`; a requirement "
                    "that answers to no acceptance line is not something the "
                    "user asked for.",
                )
            )
            continue
        for pointer in pointers:
            if not 1 <= pointer <= total:
                failures.append(
                    (
                        "spec.req-grammar",
                        f"REQ-{number} points at Acceptance #{pointer}, but the "
                        f"intent carries {total} acceptance line(s).",
                    )
                )
    return failures


# What counts as a flow line, and nothing else counts (W2 re-review NF-2).
# An arrow alone is not a flow: it shows up inside mermaid and python fences,
# inside HTML comments, and inside `N/A -> see the concept model`. So the
# arrow is searched only in prose the user would actually read, and both
# sides of it have to say something.
FENCE = re.compile(r"^\s*(?:```|~~~)")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
ARROW = re.compile(r"\u2192|->")
# A flow line is recognised STRUCTURALLY: an arrow with enough text on each
# side of it. Three rounds of keyword patches (`n/a`, `none`, `沒有`, ...)
# each reopened, because "a spelling of nothing" is unbounded and a checker
# that guesses at meaning is a checker that can be talked around. What
# survives is the shape; whether the flow is TRUE or USEFUL is the reviewer
# lens's job, and the rule says so.
VISIBLE = re.compile(r"[^\W_]", re.UNICODE)
MIN_VISIBLE_PER_SIDE = 4

# Leading markdown markers, stripped repeatedly: quote, heading, list item.
LINE_MARKER = re.compile(r"^\s*(?:>|#{1,6}|[-*+]|\d+[.)])\s*")
EMPHASIS = str.maketrans("", "", "*_~`")


def strip_markup(line: str) -> str:
    """One line, minus the markdown that decorates it: leading quote /
    heading / list markers, table pipes, emphasis characters."""
    text = line.replace("|", " ")
    while True:
        stripped = LINE_MARKER.sub("", text, count=1)
        if stripped == text:
            break
        text = stripped
    return text.translate(EMPHASIS).strip()


def visible_count(text: str) -> int:
    """Characters that carry content -- letters and digits in any script.
    Counted as CHARACTERS, not words: CJK writes a whole flow with no
    spaces in it."""
    return len(VISIBLE.findall(text))


def prose_lines(body: str) -> list[str]:
    """The body minus fenced code blocks and HTML comments."""
    kept, inside_fence = [], False
    for line in HTML_COMMENT.sub(" ", body).splitlines():
        if FENCE.match(line):
            inside_fence = not inside_fence
            continue
        if inside_fence:
            continue
        if line.startswith(("    ", "\t")):
            # Indented code block (CommonMark): the same semantic class as a
            # fence, so it is not prose either.
            continue
        kept.append(line)
    return kept


def flow_lines(body: str) -> list[str]:
    """`<operation> -> <reaction>` lines: what decision point 2 reads back."""
    found = []
    for line in prose_lines(body):
        text = strip_markup(line)
        arrow = ARROW.search(text)
        if not arrow:
            continue
        left, right = text[:arrow.start()], text[arrow.end():]
        if (visible_count(left) >= MIN_VISIBLE_PER_SIDE
                and visible_count(right) >= MIN_VISIBLE_PER_SIDE):
            found.append(text)
    return found


def check_ui_flows_recompute(manifest, repo: Path, change_id: str, touched: list[str]):
    """`## UI flows: N/A` is a claim; the diff is the fact.

    `intent.needs-design-recompute` only ever ran on the `no` branch, so a
    `needs-design: yes` change could answer "no interface" in its spec while
    editing the CLI and a `.tsx` file, leaving decision point (2) with
    nothing to read back (W2 adversary P06)."""
    if not touched:
        return []
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # intake.spec-pass reports the missing spec
    _front, sections = parse_document(read_text(spec_path))
    body = sections.get("UI flows", "")
    if flow_lines(body):
        return []
    shown = _squeeze(body)[:40] or "(empty)"
    return [
        (
            "spec.ui-flows-recompute",
            f"{spec_path.relative_to(repo)} carries no `<operation> -> "
            f"<reaction>` line under `## UI flows` (it says {shown!r}) while "
            f"the diff touches a declared interface surface: "
            f"{', '.join(touched[:5])}. A flow line is prose -- not inside a "
            "``` fence or an HTML comment -- carrying an arrow with at least "
            f"{MIN_VISIBLE_PER_SIDE} visible characters on each side, e.g. "
            "`todo add --due 2026-09-10 'buy milk' -> the todo is stored with "
            "its due date`. That is a shape check only: whether the flow is "
            "true, complete or worth reading is the reviewer's judgement, not "
            "this rule's. Write one per operation; that section IS decision "
            "point 2.",
        )
    ]


# --- spec freshness (W2 adversaries P02, P09) ------------------------------

CONFIRMED_BEHAVIOR_GRAMMAR = re.compile(
    r"^(\d{4}-\d{2}-\d{2})(?:\s+@([0-9a-f]{7,40}))?$"
)
CONFIRMED_BEHAVIOR_LINE = re.compile(rb"^confirmed-behavior:.*\n?", re.MULTILINE)

def blob_sha(data: bytes) -> str:
    """`git hash-object` without shelling out -- the same value git stores."""
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def spec_identity(spec_path: Path) -> str:
    """The one blob sha both freshness rules compare against: the spec WITHOUT
    its `confirmed-behavior:` line.

    Two reasons it is not simply `git hash-object spec.md`. The confirmation
    line names this value, so hashing the whole file would make it a hash of
    itself; and decision point 2 writes that line AFTER the reviewers read the
    text, so a whole-file hash would make every confirmation invalidate the
    review that preceded it."""
    return blob_sha(CONFIRMED_BEHAVIOR_LINE.sub(b"", spec_path.read_bytes(), count=1))


def recompute_command(relative: str) -> str:
    return (
        "recompute it with `git hash-object <(grep -v '^confirmed-behavior:' "
        f"{relative})`"
    )


def sha_agrees(recorded: str, current: str) -> bool:
    """Either abbreviation is a prefix of the other; git shortens freely."""
    recorded, current = recorded.strip().lower(), current.strip().lower()
    return bool(recorded) and (current.startswith(recorded) or recorded.startswith(current))


# A plan's task line, per templates/plan.md:
# `**<id> <title>**  after: <ids>  acceptance: <numbers>`
TASK_LINE = re.compile(
    r"^(?:[-*+]\s+)?\*\*(?P<id>[A-Za-z0-9][A-Za-z0-9._-]*)[^*]*\*\*(?P<rest>.*)$"
)
TASK_ACCEPTANCE = re.compile(r"(?:^|\s)acceptance:\s*(.*?)\s*$", re.IGNORECASE)
VALID_ACCEPTANCE_REFS = re.compile(r"[0-9]{1,9}(?:\s*,\s*[0-9]{1,9})*")
TEST_CASE = re.compile(
    r"(?:^|[.;]\s*)A(?P<number>\d+)\s+positive:\s*(?P<positive>[^;]+?)\s*;\s*"
    r"(?P<kind>negative|boundary):\s*(?P<opposite>.+?)"
    r"(?=\s*(?:[.;]\s*A\d+\s+positive:|$))",
    re.IGNORECASE,
)


def check_test_case_pairs(
    manifest, repo: Path, change_id: str, intent_sections: dict[str, str]
) -> list[tuple[str, str]]:
    """A new plan owns every Acceptance line and pairs both sides of its tests.

    Plans authored before this contract remain byte-compatible when their
    first committed form used the old task grammar. A new plan cannot
    self-exempt later by deleting its ownership markers or charter line."""
    plan_path = artifact_path(manifest, "plan", change_id, repo)
    if not plan_path.is_file():
        return []
    plan_text = read_text(plan_path)
    _front, plan_sections = parse_document(plan_text)
    task_dag = plan_sections.get("Task DAG", "")
    headers = [
        match
        for raw_line in task_dag.splitlines()
        if (match := TASK_LINE.match(raw_line.strip()))
    ]
    relative_plan = plan_path.relative_to(repo).as_posix()
    first_commit_log = git_maybe(
        repo, "log", "--diff-filter=A", "--reverse", "--format=%H", "HEAD", "--", relative_plan
    )
    first_commit = first_commit_log.splitlines()[0] if first_commit_log else None
    if first_commit:
        original_plan = git_maybe(repo, "show", f"{first_commit}:{relative_plan}")
        if original_plan is not None:
            _original_front, original_sections = parse_document(original_plan)
            original_headers = [
                match
                for raw_line in original_sections.get("Task DAG", "").splitlines()
                if (match := TASK_LINE.match(raw_line.strip()))
            ]
            if original_headers and not any(
                TASK_ACCEPTANCE.search(match.group("rest"))
                for match in original_headers
            ):
                return []

    failures: list[tuple[str, str]] = []
    if not headers:
        failures.append(
            ("intake.test-case-pair", "a newly authored plan requires at least one task.")
        )
    acceptance_numbers = {
        int(match.group(1))
        for raw_line in intent_sections.get("Acceptance", "").splitlines()
        if (match := re.match(r"^\s*(\d+)[.)]\s+\S", raw_line))
    }
    if intent_sections.get("Open questions", "").strip() != "- none":
        failures.append(
            (
                "intake.test-case-pair",
                "a newly authored plan requires intent Open questions to be exactly `- none`.",
            )
        )

    fields = _parse_plan_task_fields(task_dag)
    owned: set[int] = set()
    for header in headers:
        task_id = header.group("id")
        if MEMORY_TASK_ID.match(task_id):
            continue
        marker = TASK_ACCEPTANCE.search(header.group("rest"))
        if marker is None:
            failures.append(
                ("intake.test-case-pair", f"{task_id} carries no `acceptance: <numbers>` marker.")
            )
            continue
        raw_marker = marker.group(1).strip()
        if not VALID_ACCEPTANCE_REFS.fullmatch(raw_marker):
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} carries malformed Acceptance references.",
                )
            )
            continue
        raw_references = [value.strip() for value in raw_marker.split(",")]
        references = [int(value) for value in raw_references]
        nonexistent = sorted(set(references) - acceptance_numbers)
        if nonexistent:
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} references nonexistent Acceptance lines: "
                    f"{', '.join(map(str, nonexistent))}.",
                )
            )
        owned.update(set(references) & acceptance_numbers)
        cases = {
            int(match.group("number")): match
            for match in TEST_CASE.finditer(str(fields.get(task_id, {}).get("Test") or ""))
            if any(ch.isalnum() for ch in match.group("positive"))
            and any(ch.isalnum() for ch in match.group("opposite"))
        }
        missing_cases = sorted(set(references) - set(cases))
        if missing_cases:
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} lacks a non-empty positive plus negative or boundary pair for "
                    f"Acceptance: {', '.join(map(str, missing_cases))}.",
                )
            )

    uncovered = sorted(acceptance_numbers - owned)
    if uncovered:
        failures.append(
            (
                "intake.test-case-pair",
                "intent Acceptance lines are owned by no task: "
                f"{', '.join(map(str, uncovered))}.",
            )
        )
    return failures


# --- plan.field-caps (W1-01) -----------------------------------------------

PLAN_FIELD_CAP_TEST = 40
PLAN_FIELD_CAP_RISK = 40
PLAN_FIELD_CAP_FILES = 8
PLAN_FIELD_CAP_RISKS_ITEM = 40
PLAN_FIELD_CAP_CSE_BULLET = 30

TASK_FIELD_LINE = re.compile(r"^-\s*(Files|Test|Risk):\s*(.*)$")
NUMBERED_ITEM = re.compile(r"^\d+\.\s+(\S.*)$")
BULLET_ITEM = re.compile(r"^-\s+(\S.*)$")


def _split_respecting_backticks(text: str) -> list[str]:
    """Comma-split `text`, except a comma sitting inside a `backtick span`
    never splits -- a generated fixture path legitimately containing a
    comma must still count as one Files entry (W1-01 adversary pin)."""
    entries: list[str] = []
    current: list[str] = []
    in_backtick = False
    for ch in text:
        if ch == "`":
            in_backtick = not in_backtick
            current.append(ch)
        elif ch == "," and not in_backtick:
            entries.append("".join(current))
            current = []
        else:
            current.append(ch)
    entries.append("".join(current))
    return [entry.strip() for entry in entries if entry.strip()]


def _parse_plan_task_fields(task_dag_text: str) -> dict[str, dict[str, str | None]]:
    """One dict per task id, `{"Files": ..., "Test": ..., "Risk": ...}`,
    values `None` when the task's block carries no such line at all --
    distinct from an empty value, which the task did write."""
    tasks: dict[str, dict[str, str | None]] = {}
    current_id: str | None = None
    for raw_line in task_dag_text.splitlines():
        line = raw_line.strip()
        header = TASK_LINE.match(line)
        if header:
            current_id = header.group("id")
            tasks[current_id] = {"Files": None, "Test": None, "Risk": None}
            continue
        if current_id is None:
            continue
        field_match = TASK_FIELD_LINE.match(line)
        if field_match:
            tasks[current_id][field_match.group(1)] = field_match.group(2)
    return tasks


def _plan_numbered_items(text: str) -> list[str]:
    items = []
    for raw_line in text.splitlines():
        match = NUMBERED_ITEM.match(raw_line.strip())
        if match:
            items.append(match.group(1))
    return items


def _plan_bullets(text: str) -> list[str]:
    items = []
    for raw_line in text.splitlines():
        match = BULLET_ITEM.match(raw_line.strip())
        if match:
            items.append(match.group(1))
    return items


def check_plan_field_caps(plan_text: str) -> list[tuple[str, str]]:
    """Recomputed per-field caps on a charter-stamped plan (W1-01).

    Skipped entirely -- no output at all -- when the plan's frontmatter
    carries no `charter:` key; presence is the stamp, not any particular
    value, so grandfathering is by template, not by date (concept-model
    §5, plan Risk #1)."""
    front, sections = parse_document(plan_text)
    if "charter" not in front:
        return []

    failures: list[tuple[str, str]] = []

    tasks = _parse_plan_task_fields(sections.get("Task DAG", ""))
    for task_id, fields in tasks.items():
        for field, cap in (("Files", PLAN_FIELD_CAP_FILES), ("Test", PLAN_FIELD_CAP_TEST), ("Risk", PLAN_FIELD_CAP_RISK)):
            value = fields.get(field)
            if value is None:
                failures.append(("plan.field-caps", f"{task_id}.{field} missing"))
                continue
            if field == "Files":
                entries = _split_respecting_backticks(value)
                if len(entries) > cap:
                    failures.append((
                        "plan.field-caps",
                        f"{task_id}.Files {len(entries)} entries, cap {cap}",
                    ))
            else:
                words = len(value.split())
                if words > cap:
                    failures.append((
                        "plan.field-caps",
                        f"{task_id}.{field} {words} words, cap {cap}",
                    ))

    for index, item in enumerate(_plan_numbered_items(sections.get("Risks", "")), start=1):
        words = len(item.split())
        if words > PLAN_FIELD_CAP_RISKS_ITEM:
            failures.append((
                "plan.field-caps",
                f"Risks#{index} {words} words, cap {PLAN_FIELD_CAP_RISKS_ITEM}",
            ))

    cse = sections.get("Current State Evidence", "")
    for index, item in enumerate(_plan_bullets(cse), start=1):
        words = len(item.split())
        if words > PLAN_FIELD_CAP_CSE_BULLET:
            failures.append((
                "plan.field-caps",
                f"Current State Evidence#{index} {words} words, cap {PLAN_FIELD_CAP_CSE_BULLET}",
            ))

    return failures


def check_plan_field_caps_at(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
    """Same rule, applied to a change's own `plan.md` when it exists -- the
    shape `check_after_task_budget` uses, reused at intake and push."""
    plan_path = artifact_path(manifest, "plan", change_id, repo)
    if not plan_path.is_file():
        return []
    return check_plan_field_caps(read_text(plan_path))


# --- plan.edits-after-commit (W1-02) ----------------------------------------

# Only the explicit `landed: <sha>` annotation counts. A bare hex-looking
# token is not enough: ordinary words spelt from hex letters ("defaced",
# "cafe") would otherwise send an unauthorised addition to `dispatch`
# instead of `spec` (round-5 finding).
MEMORY_TASK_ID = re.compile(r"^W\d+-memory$", re.IGNORECASE)

# The plan charter's `edits_after` policy ids this rule actually
# implements (W1-02 fix round): recomputed against
# `manifest.artifacts.plan.charter.edits_after` at every run rather than
# assumed, so a manifest id with no matching branch here fails closed
# instead of silently drifting from the code (the "second drift surface"
# named in the design finding).



















































PRE_BUILD_REVIEW = re.compile(
    r"^(required|not-required)\s*(?:—|–|--)\s*(\S.*)$", re.IGNORECASE
)






def check_spec_ready(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
    """Require the spec and its explicit risk decision, without a review ledger."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return [("intake.spec-ready", f"needs-design: yes but no spec at {spec_path.relative_to(repo)}.")]
    spec_front, _ = parse_document(read_text(spec_path))
    declaration = spec_front.get("pre-build-review", "").strip()
    if not declaration or PRE_BUILD_REVIEW.fullmatch(declaration) is None:
        return [(
            "intake.spec-ready",
            "`pre-build-review` must be `required|not-required — <reason>`.",
        )]
    return []






def check_confirmed_behavior(
    manifest, repo: Path, change_id: str, err=sys.stderr
) -> list[tuple[str, str]]:
    """Decision point ② leaves exactly one trace: the spec's
    `confirmed-behavior:` line (concept-model §2c).

    The line names the text the user was shown -- `<date> @<spec-blob-sha7>`,
    where the sha is `git hash-object` over the spec WITHOUT this line (the
    file as it stood the moment before the agent wrote the confirmation, so
    the value is not a hash of itself). Rewrite the spec afterwards and the
    confirmation is about a behaviour nobody agreed to (W2 adversary P02)."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # already reported by intake.spec-pass
    front, _ = parse_document(read_text(spec_path))
    raw = front.get("confirmed-behavior", "").strip()
    if not raw:
        return [
            (
                "intake.confirmed-behavior",
                "kind: product but the spec has no "
                "`confirmed-behavior: <date> @<spec-blob-sha7>` line; "
                "decision point ② has not happened.",
            )
        ]
    current = spec_identity(spec_path)
    relative = spec_path.relative_to(repo).as_posix()
    match = CONFIRMED_BEHAVIOR_GRAMMAR.match(raw)
    if not match or not match.group(2):
        return [
            (
                "intake.confirmed-behavior",
                f"`confirmed-behavior: {raw}` does not match "
                f"`<date> @<spec-blob-sha7>`; the sha names the text the user "
                f"was actually shown ({current[:7]} for {relative} as it "
                f"stands) -- {recompute_command(relative)}.",
            )
        ]
    if not is_real_date(match.group(1)):
        return [
            (
                "intake.confirmed-behavior",
                f"`confirmed-behavior: {raw}` names {match.group(1)!r}, which "
                "is not a real date.",
            )
        ]
    recorded = match.group(2)
    if not sha_agrees(recorded, current):
        return [
            (
                "intake.confirmed-behavior",
                f"the user confirmed spec @{recorded}, but {relative} is now "
                f"@{current[:7]} -- the "
                "visible behaviour changed after decision point ②; show it "
                "again and rewrite the line.",
            )
        ]
    return []


# A shell line is not a regex target: `git -C /x push`, `git --git-dir=… push`,
# `eval "git push"` and `make it; git push` all have to be recognised, and
# `git pushd` / `git commit -m "push"` must not be. So each `;`/`&&`/`||`/`|`
# segment is tokenised and its FIRST non-option word after the program name is
# compared to the verb -- the way the shell would read it.
SEGMENT_SPLIT = re.compile(r"\|\||&&|[;\n|&]")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Options that swallow the next word, so it is a value and never the verb.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
GH_VALUE_OPTIONS = {"-R", "--repo", "--hostname"}
GIT_REPOSITORY_ENV = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GH_REPO"}
ENV_VALUE_OPTIONS = {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"}
PREFIX_WORDS = {"sudo", "command", "env", "nohup", "time", "nice", "builtin", "exec", "xargs"}
# `bash -c "git push"` / `sh -c` / `zsh -c` / `dash -c` hand the checker a
# shell line as a single quoted argument -- shlex has already unquoted it, so
# it is re-read as a shell line of its own, exactly like `eval`'s payload.
SHELL_PROGRAMS = {"bash", "sh", "zsh", "dash"}


def _shell_segments(command: str) -> list[str]:
    """Split on shell operators outside quotes; malformed input stays strict."""
    segments: list[str] = []
    start = 0
    quote: str | None = None
    escaped = False
    dynamic = False
    index = 0
    while index < len(command):
        character = command[index]
        if escaped:
            escaped = False
        elif character == "\\" and quote != "'":
            escaped = True
        elif (
            character == "$"
            and quote != "'"
            and index + 1 < len(command)
            and command[index + 1] == "("
        ):
            dynamic = True
        elif character == "`" and quote != "'":
            dynamic = True
        elif quote:
            if character == quote:
                quote = None
        elif character in {"'", '"'}:
            quote = character
        elif character in ";\n|&":
            segments.append(command[start:index])
            if (
                character in "|&"
                and index + 1 < len(command)
                and command[index + 1] == character
            ):
                index += 1
            start = index + 1
        index += 1
    if quote or escaped or dynamic:
        return SEGMENT_SPLIT.split(command)
    segments.append(command[start:])
    return segments


def _tokenise(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:  # an unbalanced quote is still worth judging
        return segment.split()


def _strip_prefix(tokens: list[str]) -> list[str]:
    """Drop `VAR=…` assignments and wrapper words that precede the program."""
    index = 0
    while index < len(tokens):
        if ASSIGNMENT.match(tokens[index]):
            index += 1
            continue
        wrapper = Path(tokens[index]).name
        if wrapper not in PREFIX_WORDS:
            break
        index += 1
        if wrapper == "env":
            while index < len(tokens) and tokens[index].startswith("-"):
                option = tokens[index]
                index += 2 if option in ENV_VALUE_OPTIONS else 1
    return tokens[index:]


def _subcommand_at(tokens: list[str], value_options: set[str]) -> tuple[int, str] | None:
    """The position and value of the first non-option, non-value word."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return None
        if token in value_options:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return index, token
    return None


def _subcommand(tokens: list[str], value_options: set[str]) -> str | None:
    """The first word that is neither an option nor an option's value."""
    found = _subcommand_at(tokens, value_options)
    return found[1] if found else None


def is_push_command(command: str) -> bool:
    """True when any segment of this shell line pushes or opens/merges a PR."""
    if is_git_push_command(command):
        return True
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program == "eval":
            if is_push_command(" ".join(tokens[1:])):
                return True
        elif program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_push_command(tokens[index + 1]):
                return True
        elif program == "gh":
            rest = tokens[1:]
            found = _subcommand_at(rest, GH_VALUE_OPTIONS)
            if found and found[1] == "pr":
                after = rest[found[0] + 1:]
                if _subcommand(after, GH_VALUE_OPTIONS) in {"create", "merge"}:
                    return True
    return False


def is_pr_create_command(command: str) -> bool:
    """True when a shell segment creates a PR."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens or Path(tokens[0]).name != "gh":
            continue
        rest = tokens[1:]
        found = _subcommand_at(rest, GH_VALUE_OPTIONS)
        if found and found[1] == "pr":
            after = rest[found[0] + 1:]
            if _subcommand(after, GH_VALUE_OPTIONS) == "create":
                return True
    return False


def is_pr_merge_command(command: str) -> bool:
    """True when a shell segment merges a PR."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens or Path(tokens[0]).name != "gh":
            continue
        rest = tokens[1:]
        found = _subcommand_at(rest, GH_VALUE_OPTIONS)
        if found and found[1] == "pr":
            after = rest[found[0] + 1:]
            if _subcommand(after, GH_VALUE_OPTIONS) == "merge":
                return True
    return False


def github_repo_from_origin(repo: Path) -> str | None:
    """Return GH_REPO syntax derived from the literal configured origin URL."""
    url = git_maybe(repo, "remote", "get-url", "origin")
    if not url:
        return None
    match = re.fullmatch(r"https?://([^/]+)/([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        match = re.fullmatch(r"git@([^:]+):([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        match = re.fullmatch(r"ssh://git@([^/]+)/([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        return None
    host, owner, name = match.groups()
    return f"{host}/{owner}/{name}"


def is_canonical_pr_create_command(repo: Path, command: str) -> bool:
    """True only for one function-proof, origin-bound PR creation command."""
    trusted = shutil.which("gh")
    trusted_env = shutil.which("env")
    gh_repo = github_repo_from_origin(repo)
    if not trusted or not trusted_env or not gh_repo:
        return False
    gh_tokens = _tokenise(command)
    expected_prefix = [
        "command", str(Path(trusted_env).resolve()), f"LOOM_REPO_ROOT={repo.resolve()}",
        f"GH_REPO={gh_repo}", str(Path(trusted).resolve()), "pr", "create",
    ]
    trailing = gh_tokens[7:]
    repo_overrides = {"-R", "--repo", "--hostname"}
    has_repo_override = any(
        token in repo_overrides
        or token.startswith("--repo=")
        or token.startswith("--hostname=")
        or (token.startswith("-R") and token != "-R")
        for token in trailing
    )
    return (
        gh_tokens[:7] == expected_prefix
        and not has_repo_override
        and command == render_quote_all(gh_tokens)
    )


def canonical_pr_create_repo(command: str) -> Path | None:
    """Return the selected repo only when the whole PR-create form is trusted."""
    tokens = _tokenise(command)
    if len(tokens) < 7 or not tokens[2].startswith("LOOM_REPO_ROOT="):
        return None
    selected = Path(tokens[2].split("=", 1)[1])
    if not selected.is_absolute() or not selected.is_dir():
        return None
    try:
        repo = repo_root(selected.resolve())
    except UsageError:
        return None
    if repo.resolve() != selected.resolve():
        return None
    return repo if is_canonical_pr_create_command(repo, command) else None


def check_pr_create_remote_head(repo: Path, command: str) -> str | None:
    """Require PR creation to reference the already-published current HEAD."""
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = git_maybe(repo, "rev-parse", "HEAD")
    if not branch or not head:
        return "PR creation requires a current symbolic branch and commit"

    tokens = _tokenise(command)
    head_values: list[str] = []
    for index, token in enumerate(tokens):
        if token in {"--head", "-H"} and index + 1 < len(tokens):
            head_values.append(tokens[index + 1])
        elif token.startswith("--head="):
            head_values.append(token.split("=", 1)[1])
        elif token.startswith("-H") and token != "-H":
            head_values.append(token[2:])
        if token == "--body-file" and (
            index + 1 >= len(tokens) or not Path(tokens[index + 1]).is_absolute()
        ):
            return "PR body file must be an absolute path"
        if token.startswith("--body-file=") and not Path(token.split("=", 1)[1]).is_absolute():
            return "PR body file must be an absolute path"
    if head_values != [branch]:
        if not head_values:
            return f"PR creation requires explicit current branch head {branch!r}"
        else:
            return f"PR head must be the current branch {branch!r}"

    gh_repo = github_repo_from_origin(repo)
    trusted_gh = shutil.which("gh")
    if not gh_repo or not trusted_gh:
        return "PR creation requires a trusted GitHub origin and gh executable"
    repo_parts = gh_repo.split("/")
    host, owner, name = repo_parts[0], repo_parts[-2], repo_parts[-1]
    try:
        # GitHub CLI documents the endpoint form plus --hostname and --jq:
        # https://cli.github.com/manual/gh_api
        # GitHub documents this reference endpoint and its object.sha response:
        # https://docs.github.com/en/rest/git/refs#get-a-reference
        observed = subprocess.run(
            [str(Path(trusted_gh).resolve()), "api", "--hostname", host,
             f"repos/{owner}/{name}/git/ref/heads/{quote(branch, safe='')}",
             "--jq", ".object.sha"],
            cwd=repo, capture_output=True, text=True, timeout=30,
            env={**os.environ, "GH_REPO": gh_repo, "LOOM_REPO_ROOT": str(repo)},
        )
    except (OSError, subprocess.TimeoutExpired):
        observed = None
    if observed is not None and observed.returncode == 0 and observed.stdout.strip() == head:
        return None
    return f"remote branch {branch!r} must already equal reviewed HEAD {head}"


def is_git_push_command(command: str) -> bool:
    """True when any shell segment can reach a Git push."""
    for segment in _shell_segments(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program == "eval":
            if is_git_push_command(" ".join(tokens[1:])):
                return True
        elif program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_git_push_command(tokens[index + 1]):
                return True
        elif program == "git" and _subcommand(tokens[1:], GIT_VALUE_OPTIONS) == "push":
            return True
    return False


def git_dash_c_push_cwd(command: str, fallback: str) -> str | None:
    """Return the one unambiguous repository selected by every Git push.

    The host-reported cwd is authoritative only when a push has no directory
    override. An absolute ``-C`` anchors later relative ``-C`` options. A
    relative first ``-C``, another directory-changing option, a missing or
    invalid directory, or pushes selecting distinct repositories is unsafe
    because the hook cannot prove which repository the shell will push.
    """
    selected_roots: set[str] = set()
    shell_root: Path | None = None
    repository_env_changed = False
    for segment in _shell_segments(command):
        raw_tokens = _tokenise(segment)
        tokens = _strip_prefix(raw_tokens)
        if not tokens:
            continue
        if any(Path(token).name == "env" for token in raw_tokens) and any(
            token.startswith("-C")
            or token == "--chdir"
            or token.startswith("--chdir=")
            for token in raw_tokens
        ):
            return None
        segment_changes_repository_env = any(
            ASSIGNMENT.match(token)
            and token.split("=", 1)[0] in GIT_REPOSITORY_ENV
            for token in raw_tokens
        )
        program = Path(tokens[0]).name.lstrip("(")
        if program == "export" and any(
            token.split("=", 1)[0] in GIT_REPOSITORY_ENV
            for token in tokens[1:]
        ):
            segment_changes_repository_env = True
        repository_env_changed = (
            repository_env_changed or segment_changes_repository_env
        )
        if program in {"cd", "pushd"}:
            directory_args = [
                token for token in tokens[1:]
                if token != "--" and not token.startswith("-")
            ]
            if len(directory_args) != 1:
                return None
            candidate = Path(directory_args[0])
            if candidate.is_absolute():
                shell_root = candidate
            elif shell_root is not None:
                shell_root = shell_root / candidate
            else:
                return None
            if not shell_root.is_dir():
                return None
            continue
        if program == "popd":
            return None
        if program == "eval" and is_push_command(" ".join(tokens[1:])):
            return None
        if program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_push_command(tokens[index + 1]):
                return None
        if any(Path(token).name == "xargs" for token in raw_tokens) and is_push_command(segment):
            return None
        if program == "gh" and is_push_command(segment):
            if repository_env_changed or any(
                token.startswith("-R")
                or token == "--repo"
                or token.startswith("--repo=")
                for token in tokens[1:]
            ):
                return None
            if is_pr_merge_command(segment) and shell_root is None:
                return None
            root = shell_root if shell_root is not None else Path(fallback)
            selected_roots.add(str(root.resolve()))
            continue
        if program != "git" or _subcommand(tokens[1:], GIT_VALUE_OPTIONS) != "push":
            continue
        if repository_env_changed:
            return None
        selected = shell_root
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "-C":
                if index + 1 >= len(tokens):
                    return None
                candidate = Path(tokens[index + 1])
                if candidate.is_absolute():
                    selected = candidate
                elif selected is not None:
                    selected = selected / candidate
                else:
                    return None
                index += 2
                continue
            if token.startswith("-C") or token in {"--git-dir", "--work-tree"}:
                return None
            if token.startswith("--git-dir=") or token.startswith("--work-tree="):
                return None
            if token in GIT_VALUE_OPTIONS:
                index += 2
                continue
            if token.startswith("-"):
                index += 1
                continue
            break
        root = selected if selected is not None else Path(fallback)
        if not root.is_dir():
            return None
        selected_roots.add(str(root.resolve()))
    if len(selected_roots) > 1:
        return None
    return next(iter(selected_roots)) if selected_roots else None


CANONICAL_PUSH_FLAGS = ["--no-follow-tags", "--recurse-submodules=no", "-u", "--no-verify"]
# Git documents these push options and their effects:
# https://git-scm.com/docs/git-push
SAFE_REMOTE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def quote_all_shell_token(token: str) -> str:
    """Render one argv token without leaving any shell expansion position."""
    return "'" + token.replace("'", "'\"'\"'") + "'"


def render_quote_all(tokens: list[str]) -> str:
    return " ".join(quote_all_shell_token(token) for token in tokens)


def canonical_git_push(
    command: str, fallback: str
) -> tuple[Path | None, str | None, str | None]:
    """Validate the complete shell bytes for the one supported Git push."""
    trusted = shutil.which("git")
    if not trusted:
        return None, None, "the hook environment has no trusted Git executable"
    trusted_git = str(Path(trusted).resolve())
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as exc:
        return None, None, f"the Git push command has malformed quoting: {exc}"
    if command != render_quote_all(tokens):
        return None, None, "the entire Git push command must use canonical quote-all rendering"
    if len(tokens) < 2 or tokens[0] != "command":
        return None, None, "the Git push must begin with the standard command builtin"
    if tokens[1] != trusted_git or not Path(tokens[1]).is_absolute():
        return None, None, f"the Git executable must be the trusted absolute path {trusted_git!r}"

    index = 2
    selected = Path(fallback)
    if index < len(tokens) and tokens[index] == "-C":
        if index + 1 >= len(tokens) or not Path(tokens[index + 1]).is_absolute():
            return None, None, "Git -C must name the selected repository by absolute path"
        selected = Path(tokens[index + 1])
        index += 2
    try:
        repo = repo_root(selected.resolve())
    except UsageError as exc:
        return None, None, str(exc)
    if "-C" in tokens[1:index] and selected.resolve() != repo.resolve():
        return None, None, "Git -C must name the selected repository root exactly"

    required = ["push", *CANONICAL_PUSH_FLAGS]
    if tokens[index:index + len(required)] != required:
        return None, None, (
            "Git push must use exactly --no-follow-tags --recurse-submodules=no -u --no-verify"
        )
    tail = tokens[index + len(required):]
    if len(tail) != 2:
        return None, None, "Git push must name one literal remote and one explicit refspec"
    remote, refspec = tail
    if not SAFE_REMOTE.fullmatch(remote):
        return None, None, f"Git push remote {remote!r} is not a safe literal name"
    if remote != "origin":
        return None, None, "the Git push remote must be literal 'origin'"

    head = git_text(repo, "rev-parse", "HEAD")
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not branch:
        return None, None, "the selected repository has no current symbolic branch"
    expected = f"{head}:refs/heads/{branch}"
    if refspec != expected:
        return None, None, f"Git push refspec must be exactly {expected!r}, got {refspec!r}"
    return repo, head, None


def read_hook_payload(stdin=sys.stdin) -> dict | None:
    """PreToolUse payload (Claude Code and Codex share the shape) when the
    checker is invoked as a hook; None when run from a terminal or with an
    empty stdin. Malformed JSON is a UsageError → exit 2 (fail-closed)."""
    if stdin is None or stdin.isatty():
        return None
    raw = stdin.read()
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"hook payload is not JSON: {exc}")
    if not isinstance(payload, dict):
        raise UsageError("hook payload must be a JSON object.")
    return payload


def cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`--hook` is what selects hook mode, never the shape of stdin: a
    checker run from a station (or a terminal, or any harness that hands it
    a pipe nobody ever closes) must never block on `stdin.read()`."""
    rest = list(args)
    if "--hook" not in rest:
        return _cmd_push(rest, out, err)
    rest.remove("--hook")

    payload = read_hook_payload()
    if payload is None:
        raise UsageError("push --hook expects a PreToolUse JSON payload on stdin.")
    # The matcher is the tool name, so every Bash command arrives here; only
    # push-shaped commands are judged.
    command = str((payload.get("tool_input") or {}).get("command", ""))
    canonical_pr_repo = canonical_pr_create_repo(command)
    push_shaped = canonical_pr_repo is not None or is_push_command(command)
    git_push = is_git_push_command(command)
    malformed_canonical_push = False
    if not push_shaped:
        # A malformed quote can defeat the permissive recogniser, but not a
        # command that visibly starts with the canonical command trust root
        # and trusted executable.
        trusted = shutil.which("git")
        trusted_prefix = (
            f"{quote_all_shell_token('command')} "
            f"{quote_all_shell_token(str(Path(trusted).resolve()))}"
            if trusted
            else ""
        )
        malformed_canonical_push = bool(
            trusted_prefix
            and command.startswith(trusted_prefix)
            and quote_all_shell_token("push") in command
        )
        if not malformed_canonical_push:
            return 0
    cwd = str(payload.get("cwd") or os.getcwd())
    if git_push or malformed_canonical_push:
        repo, immutable_head, refspec_error = canonical_git_push(command, cwd)
        if refspec_error:
            print(f"BLOCK push.attestation: {refspec_error}", file=err)
            return 2
        assert repo is not None and immutable_head is not None
        os.chdir(repo)
        rc = _cmd_push(["--head", immutable_head, "--require-live-head"] + rest, out, err)
        return 2 if rc == 1 else rc

    # A metadata-only PR create carries its own function-proof repository
    # selection. Other gh actions keep the existing conservative parser.
    pr_create = canonical_pr_repo is not None or is_pr_create_command(command)
    if pr_create and canonical_pr_repo is None:
        print(
            "BLOCK push.attestation: PR creation must use the canonical "
            "trusted-gh command from loom-code:ship",
            file=err,
        )
        return 2
    push_cwd = str(canonical_pr_repo) if canonical_pr_repo else git_dash_c_push_cwd(command, cwd)
    if push_cwd is None:
        print(
            "BLOCK push.attestation: ambiguous repository selection; "
            "use one absolute git -C path, or cd to one absolute path first",
            file=err,
        )
        return 2
    os.chdir(push_cwd)
    if pr_create:
        remote_error = check_pr_create_remote_head(Path.cwd(), command)
        if remote_error:
            print(f"BLOCK push.attestation: {remote_error}", file=err)
            return 2
    rc = _cmd_push(rest, out, err)
    if pr_create and rc == 0:
        remote_error = check_pr_create_remote_head(Path.cwd(), command)
        if remote_error:
            print(f"BLOCK push.attestation: {remote_error}", file=err)
            return 2
    return 2 if rc == 1 else rc   # hosts block on exit 2


PUBLISH_REDIRECT_ENV = {
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_NAMESPACE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_EXEC_PATH", "GIT_SSH",
    "GIT_SSH_COMMAND", "GIT_PROXY_COMMAND", "GIT_CONFIG", "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS", "GH_HOST", "GH_REPO",
}

PUBLISH_REDIRECT_CONFIG = (
    r"^(remote\.origin\.(pushurl|proxy|vcs|receivepack|uploadpack)"
    r"|url\..*\.(push)?insteadof|core\.sshcommand)$"
)

PUBLISH_EXECUTABLE_DIRS = (
    Path("/usr/bin"), Path("/usr/local/bin"), Path("/opt/homebrew/bin"),
    Path("/home/linuxbrew/.linuxbrew/bin"),
)


def resolve_publish_executable(name: str) -> str | None:
    """Resolve publication tools from host install roots, never caller PATH."""
    for directory in PUBLISH_EXECUTABLE_DIRS:
        candidate = directory / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
    return None


def run_publish_external(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run one trusted publication argv; kept as a seam for isolated tests."""
    return subprocess.run(argv, capture_output=True, text=True, timeout=30, **kwargs)


def _publish_usage(reason: str, err) -> int:
    err.write(f"publish: {reason}\n")
    return 2


def _publish_block(reason: str, err) -> int:
    return report([("push.attestation", reason)], err)


def _publish_origin_state(repo: Path, expected_branch: str) -> tuple[str | None, str | None]:
    """Return the single literal origin URL or a publication identity error."""
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != expected_branch:
        return None, "symbolic branch changed before publication"
    origin_urls = (git_maybe(repo, "config", "--get-all", "remote.origin.url") or "").splitlines()
    if len(origin_urls) != 1:
        return None, "literal origin must have exactly one fetch URL"
    redirect_config = git_maybe(repo, "config", "--get-regexp", PUBLISH_REDIRECT_CONFIG)
    if redirect_config:
        return None, (
            "origin redirection, transport, remote executable, pushurl, insteadOf, "
            "sshCommand, or proxy configuration must be removed"
        )
    return origin_urls[0], None


def _publish_args(args: list[str]) -> tuple[str, Path] | str:
    authorized = False
    title: str | None = None
    body_file: Path | None = None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--confirm-authorized":
            if authorized:
                return "--confirm-authorized may appear only once"
            authorized = True
        elif token in {"--title", "--body-file"}:
            if not rest:
                return f"{token} needs a value"
            value = rest.pop(0)
            if token == "--title":
                if title is not None:
                    return "--title may appear only once"
                title = value
            else:
                if body_file is not None:
                    return "--body-file may appear only once"
                body_file = Path(value)
        else:
            return f"unexpected argument {token!r}"
    if not authorized:
        return "--confirm-authorized is required after Ship decision point ③"
    if not title or not title.strip():
        return "--title needs non-empty text"
    if body_file is None or not body_file.is_absolute():
        return "--body-file must name an absolute path"
    if not body_file.is_file() or not os.access(body_file, os.R_OK):
        return f"--body-file is not a readable file: {body_file}"
    return title, body_file


def _publish_env(repo_identity: str, repo: Path, trusted_paths: tuple[str, str]) -> dict[str, str]:
    env = {
        key: value for key, value in os.environ.items()
        if key not in PUBLISH_REDIRECT_ENV and not key.startswith("GIT_CONFIG_KEY_")
        and not key.startswith("GIT_CONFIG_VALUE_")
    }
    safe_path = os.pathsep.join(dict.fromkeys(
        [str(Path(path).parent) for path in trusted_paths] + ["/usr/bin", "/bin"]
    ))
    env.update({"GH_REPO": repo_identity, "LOOM_REPO_ROOT": str(repo), "PATH": safe_path})
    return env


def _external_or_block(argv: list[str], *, repo: Path, env: dict[str, str], err):
    try:
        result = run_publish_external(argv, cwd=repo, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _publish_block(f"publication command could not run: {type(exc).__name__}: {exc}", err)
        return None
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
        _publish_block(f"publication command failed: {detail}", err)
        return None
    return result


def cmd_publish(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """Validate and publish one reviewed HEAD without caller-built shell text."""
    parsed = _publish_args(args)
    if isinstance(parsed, str):
        return _publish_usage(parsed, err)
    title, body_file = parsed

    redirected = sorted(
        key for key in os.environ
        if key in PUBLISH_REDIRECT_ENV
        or key.startswith("GIT_CONFIG_KEY_") or key.startswith("GIT_CONFIG_VALUE_")
    )
    if redirected:
        return _publish_usage(
            "remove repository or host redirect environment variables: "
            + ", ".join(redirected), err,
        )

    trusted_git = resolve_publish_executable("git")
    trusted_gh = resolve_publish_executable("gh")
    if not trusted_git or not trusted_gh:
        return _publish_block("publication requires trusted git and gh executables", err)

    previous_path = os.environ.get("PATH")
    os.environ["PATH"] = os.pathsep.join(dict.fromkeys(
        [str(Path(trusted_git).parent), str(Path(trusted_gh).parent), "/usr/bin", "/bin"]
    ))
    try:
        return _cmd_publish_trusted(title, body_file, trusted_git, trusted_gh, out, err)
    finally:
        if previous_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = previous_path


def _cmd_publish_trusted(
    title: str, body_file: Path, trusted_git: str, trusted_gh: str,
    out=sys.stdout, err=sys.stderr,
) -> int:
    try:
        repo = repo_root(Path.cwd()).resolve()
    except UsageError as exc:
        return _publish_block(str(exc), err)

    head = git_maybe(repo, "rev-parse", "HEAD")
    branch = git_maybe(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    if not head or not branch or not git_ok(repo, "check-ref-format", "--branch", branch):
        return _publish_block("publication requires a safe current symbolic branch and HEAD", err)
    origin_url, origin_error = _publish_origin_state(repo, branch)
    if origin_error:
        return _publish_block(origin_error, err)
    identity = github_repo_from_origin(repo)
    if not identity:
        return _publish_block("literal origin is not a supported GitHub repository URL", err)
    env = _publish_env(identity, repo, (trusted_git, trusted_gh))

    if _cmd_push(["--head", head, "--require-live-head"], out, err) != 0:
        return 1
    out.write(f"Attestation validated for {head}\n")

    base_result = _external_or_block(
        # gh repo view accepts [HOST/]OWNER/REPO and exposes defaultBranchRef:
        # https://cli.github.com/manual/gh_repo_view
        [trusted_gh, "repo", "view", identity, "--json", "defaultBranchRef",
         "--jq", ".defaultBranchRef.name"],
        repo=repo, env=env, err=err,
    )
    if base_result is None:
        return 1
    base = base_result.stdout.strip()
    if not base or base == branch or not git_ok(repo, "check-ref-format", "--branch", base):
        return _publish_block("origin default branch is missing, unsafe, or equals the head branch", err)
    out.write(f"Publication target: {identity} base {base}\n")

    remote_result = _external_or_block(
        # Git documents ls-remote as the read-only remote-ref query:
        # https://git-scm.com/docs/git-ls-remote
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if remote_result is None:
        return 1
    remote_lines = [line for line in remote_result.stdout.splitlines() if line.strip()]
    if len(remote_lines) > 1:
        return _publish_block("origin returned multiple remote branch identities", err)
    remote_head = remote_lines[0].split()[0] if remote_lines else None
    if remote_head and remote_head != head:
        if not git_ok(repo, "cat-file", "-e", f"{remote_head}^{{commit}}") or not git_ok(
            repo, "merge-base", "--is-ancestor", remote_head, head
        ):
            return _publish_block(
                "remote branch is unknown or diverged; fetch and reconcile it before publishing",
                err,
            )

    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before push", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before push: {origin_error or 'origin URL changed'}", err
        )
    if remote_head != head:
        push_result = _external_or_block(
            [trusted_git, "-C", str(repo), "push", *CANONICAL_PUSH_FLAGS,
             "origin", f"{head}:refs/heads/{branch}"],
            repo=repo, env=env, err=err,
        )
        if push_result is None:
            return 1

    verify_result = _external_or_block(
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if verify_result is None:
        return 1
    verified = [line.split()[0] for line in verify_result.stdout.splitlines() if line.strip()]
    if verified != [head]:
        return _publish_block("origin branch does not resolve to the selected HEAD after push", err)
    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before PR creation", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )

    host, owner, name = identity.split("/", 2)
    # GitHub's pulls endpoint exposes both head/base repository identity and SHA:
    # https://docs.github.com/en/rest/pulls/pulls#list-pull-requests
    pulls_endpoint = (
        f"repos/{quote(owner, safe='')}/{quote(name, safe='')}/pulls"
        f"?state=open&head={quote(f'{owner}:{branch}', safe='')}"
    )
    list_result = _external_or_block(
        [trusted_gh, "api", "--hostname", host, pulls_endpoint],
        repo=repo, env=env, err=err,
    )
    if list_result is None:
        return 1
    try:
        candidates = json.loads(list_result.stdout)
    except json.JSONDecodeError as exc:
        return _publish_block(f"cannot decode existing PR response: {exc}", err)
    if not isinstance(candidates, list):
        return _publish_block("existing PR response is not a list", err)
    urls: list[str] = []
    expected_repo = f"{owner}/{name}"
    for candidate in candidates:
        try:
            candidate_url = candidate["html_url"]
            head_data, base_data = candidate["head"], candidate["base"]
            matches = (
                head_data["sha"] == head
                and head_data["repo"]["full_name"].casefold() == expected_repo.casefold()
                and base_data["ref"] == base
                and base_data["repo"]["full_name"].casefold() == expected_repo.casefold()
                and isinstance(candidate_url, str) and candidate_url.startswith("https://")
            )
        except (KeyError, TypeError, AttributeError):
            matches = False
        if not matches:
            return _publish_block("existing pull request identity does not match origin, HEAD, and base", err)
        urls.append(candidate_url)
    if len(urls) > 1:
        return _publish_block("multiple open pull requests match the current branch", err)

    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )
    pre_create_remote = _external_or_block(
        [trusted_git, "-C", str(repo), "ls-remote", "--heads", "origin",
         f"refs/heads/{branch}"], repo=repo, env=env, err=err,
    )
    if pre_create_remote is None:
        return 1
    current_remote = [
        line.split()[0] for line in pre_create_remote.stdout.splitlines() if line.strip()
    ]
    if current_remote != [head]:
        return _publish_block("remote branch moved before PR creation", err)
    if git_text(repo, "rev-parse", "HEAD") != head:
        return _publish_block("live HEAD moved before PR creation", err)
    current_origin, origin_error = _publish_origin_state(repo, branch)
    if origin_error or current_origin != origin_url:
        return _publish_block(
            f"publication identity changed before PR creation: "
            f"{origin_error or 'origin URL changed'}", err,
        )

    if urls:
        out.write(f"PR already exists: {urls[0]}\n")
        return 0

    create_result = _external_or_block(
        [trusted_gh, "pr", "create", "--base", base, "--head", branch,
         "--title", title, "--body-file", str(body_file)],
        repo=repo, env=env, err=err,
    )
    if create_result is None:
        return 1
    url = create_result.stdout.strip()
    if not url:
        return _publish_block("gh pr create returned no pull request URL", err)
    out.write(f"Published PR: {url}\n")
    return 0


def _cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    head = "HEAD"
    require_live_head = False
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--head":
            if not rest:
                raise UsageError("--head needs a ref.")
            head = rest.pop(0)
        elif token == "--require-live-head":
            require_live_head = True
        else:
            raise UsageError(f"unexpected argument {token!r}.")

    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    head_sha = git_maybe(repo, "rev-parse", head)
    if not head_sha:
        raise UsageError(f"cannot resolve {head!r} in {repo}.")

    # The 1.1 publication path reads one generated attestation from the
    # branch delta. It validates content identity and recorded outcomes but
    # deliberately does not replay functional executables.
    attestation_template = manifest.get("artifacts", {}).get("attestation", {}).get("path")
    if not attestation_template:
        raise UsageError("contract manifest declares no attestation artifact.")
    matcher = glob_to_regex(attestation_template.replace("<change-id>", "*"))
    candidates = sorted(path for path in changed_paths(repo) if matcher.fullmatch(path))
    if len(candidates) != 1:
        return report([(
            "push.attestation",
            f"branch must carry exactly one generated attestation; found {len(candidates)}",
        )], err)
    attestation_rel = candidates[0]
    match = re.fullmatch(
        re.escape(attestation_template).replace(re.escape("<change-id>"), r"(?P<change_id>[^/]+)"),
        attestation_rel,
    )
    if match is None:
        return report([("push.attestation", "cannot derive change id from attestation path")], err)
    try:
        attestation = json.loads(git_text(repo, "show", f"{head_sha}:{attestation_rel}"))
    except (UsageError, json.JSONDecodeError) as exc:
        return report([("push.attestation", f"cannot read generated attestation: {exc}")], err)
    failures = validate_attestation(
        repo, head_sha, match.group("change_id"), attestation, manifest
    )
    if require_live_head and git_text(repo, "rev-parse", "HEAD") != head_sha:
        failures.append(("push.attestation", "live HEAD moved during publication validation"))
    return report(failures, err)










_EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # git's constant empty-tree object
_REGULAR_FILE_MODE = "100644"
# The intent artifact's path template as the checker itself expects it
# (contract/manifest.yaml `artifacts.intent.path`). `check_close_commit_shape`
# checks the live manifest against this constant before trusting it to build
# a path matcher -- manifest drift must fail closed, not silently match
# nothing (or something wider than intended) (spec REQ-1, W0-04 round-3
# addition).






















# `questions[]` records what the user was asked at a decision point. It is
# optional -- a change with no fork asks nothing -- but a present one is
# checked, because an unchecked optional key is a key nobody may read.








# A command that exits 0 for reasons unrelated to the thing it claims to
# have run. `true` is the whole attack: it is a real command, it really
# exits 0, and it tests nothing.

# How a repo's package-test command is recomputed when KICKOFF-DEFAULTS
# does not name one: first marker present wins, in this order (the build
# station's §6 detection order, same list, same result).
TEST_COMMAND_MARKERS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("pyproject.toml", "pytest.ini", "tox.ini", "setup.cfg"), "python3 -m pytest -q"),
    (("package.json",), "npm test"),
    (("Cargo.toml",), "cargo test"),
    (("go.mod",), "go test ./..."),
)

NO_PACKAGE_TESTS = "none"




def command_names_artifact(command: str, artifact: str) -> bool:
    """True when one argument of `command` IS `artifact`.

    A substring test cannot tell `python3 attack0.py` from
    `python3 noop.py  # attack0.py`: both contain the path, only one runs
    it. The command is read the way a shell reads it -- a trailing `#`
    comment dropped, then split into arguments -- and the artifact has to
    be one of those arguments. `./x/y.py` and `x/y.py` name the same file
    and both count.
    """
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    wanted = os.path.normpath(artifact)
    return any(os.path.normpath(token) == wanted for token in tokens)


# A declared command is executed argv-style, so anything the shell would
# have to interpret makes it undeclarable rather than silently reinterpreted.
SHELL_METACHARACTERS = re.compile(r"[;&|<>()$`*?\[\]{}\n]")

# 10 minutes for one artifact or one declared suite; overridable so a test
# can force the TimeoutExpired branches without waiting 10 minutes.
PROBE_RUN_TIMEOUT = int(os.environ.get("LOOM_PROBE_RUN_TIMEOUT", "600"))


def argv_for(command: str) -> list[str]:
    """`command` as an argv list, or ValueError if a shell would be needed."""
    if SHELL_METACHARACTERS.search(command):
        raise ValueError(
            "it contains shell metacharacters; declare a plain argv command "
            "(a program and its arguments) instead"
        )
    tokens = shlex.split(command, comments=True)
    if not tokens:
        raise ValueError("it is empty")
    return tokens




def command_executes_artifact(command: str, artifact: str) -> bool:
    """True when argv directly executes the named Python, shell, or executable file."""
    tokens = argv_for(command)
    wanted = os.path.normpath(artifact)
    suffix = Path(artifact).suffix.lower()
    if suffix == ".py":
        python = Path(tokens[0]).name.startswith("python")
        direct = len(tokens) >= 2 and os.path.normpath(tokens[1]) == wanted
        pytest_direct = (
            len(tokens) >= 4 and tokens[1:3] == ["-m", "pytest"]
            and os.path.normpath(tokens[3]) == wanted
        )
        return python and (direct or pytest_direct)
    if suffix == ".sh":
        return len(tokens) >= 2 and Path(tokens[0]).name in {"bash", "sh"} and os.path.normpath(tokens[1]) == wanted
    return os.path.normpath(tokens[0]) in {wanted, os.path.join(".", wanted)}


def declared_test_command(repo: Path) -> tuple[str | None, str]:
    """The repo's own package-test command, and where it was read from.

    A recorded probe is compared against THIS, so that a command which
    exits 0 without running the suite cannot stand in for the suite. The
    repo's own KICKOFF-DEFAULTS line wins, because only the repo knows;
    otherwise the same markers the build station reads are read here."""
    declared = kickoff_defaults(repo).get("package-tests", "").strip()
    if declared:
        return declared, "docs/loom/KICKOFF-DEFAULTS.md"
    for markers, command in TEST_COMMAND_MARKERS:
        if any((repo / marker).is_file() for marker in markers):
            return command, f"detected {markers[0]}"
    for pattern in ("test_*.py", "*_test.py"):
        if next(repo.rglob(pattern), None) is not None:
            return "python3 -m pytest -q", f"detected {pattern} files"
    return None, ""




# The artifact types whose review demands the adversarial action
# (concept-model §6: code -> mutation/fuzz or >=3 abuse cases, spec ->
# red-team, skill/gate -> the attack catalogue). A change touching none of
# them -- documentation, memory, evidence -- owes no adversarial probe.


def _artifact_type_for(manifest, path: str) -> str | None:
    """Same first-match-wins order as `artifact_types`, but for one path."""
    for entry in manifest["artifact_types"]:
        if glob_to_regex(entry["glob"]).match(path):
            return entry["type"]
    return None


# W0-02 (small-change lane): the §6 types a small-lane change may touch
# without earning the full lane -- gate and skill are deliberately absent
# (plan risk: "manifest-typed `code` that is not a test -> full lane, even
# one line" generalizes to any type not on this list). `standing` is
# deliberately excluded: intent point 1 and PRINCIPLES.md non-negotiable 2
# say the small lane touches no standing document (PRINCIPLES.md, DESIGN.md,
# docs/loom/KICKOFF-DEFAULTS.md -- KICKOFF lines are gate inputs).

_TEST_NAME_RE = re.compile(r"(?:test_[^/]*|[^/]*_test)\.py\Z")
_REQUIREMENTS_NAME_RE = re.compile(r"requirements[^/]*\.txt\Z")
_CI_CONFIG_EXT_RE = re.compile(r"\.(?:toml|ya?ml|json)\Z")








# Cross-cutting store roots, never one plugin's own tree: `docs/` holds the
# loom store (records, memory, KICKOFF-DEFAULTS, maps) shared by every
# plugin, and a repo-root `evidence/` directory is checkpoint scratch, not
# code. Neither should force a two-plugin verdict alongside a real plugin
# directory like `loom-code/`.








































_NO_CANONICAL_TREE = (
    "no canonical (this checker is the .codex/hooks/ copy, or no contract "
    "package sits beside it)"
)












# The stores loom 1.0 froze: old plans, specs, briefs, backlog and design
# notes stay where they are and are never converted (concept-model §10, the
# hard switch). Their own ARCHIVED.md marker is the one file a change may
# still write, because closing a store is how a store gets frozen.
# The only file a frozen store may still receive is its OWN marker, at the
# store root -- an ARCHIVED.md nested anywhere deeper is content, not a marker.




# The vendor behind each CLI a repo can name as its second opinion.




































STANDING_WARN = (
    "WARN: this repo has no {missing} yet.",
    "WARN: without it, the review station cannot check any change for consistency "
    "against what this product is supposed to be.",
    "WARN: say the word and I will write one; to stop seeing this, record "
    "`standing-docs: waived — <reason> (<date>)` in docs/loom/KICKOFF-DEFAULTS.md.",
)


def cmd_standing(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    if not args:
        raise UsageError("standing needs a path to the intent file.")
    if len(args) > 1:
        raise UsageError(f"unexpected argument {args[1]!r}.")
    intent_path = Path(args[0])
    if not intent_path.is_file():
        raise UsageError(f"no intent file at {intent_path}")

    repo = repo_root(intent_path)
    front, _ = parse_document(read_text(intent_path))
    principles = find_standing_doc(repo, "PRINCIPLES.md")
    design = find_standing_doc(repo, "DESIGN.md")
    waived = kickoff_defaults(repo).get("standing-docs", "").strip() == "waived"

    missing = [name for name, path in (("PRINCIPLES.md", principles), ("DESIGN.md", design)) if path is None]
    if missing and not waived:
        for line in STANDING_WARN:
            err.write(line.format(missing=" or ".join(missing)) + "\n")

    failures: list[tuple[str, str]] = []
    if front.get("kind", "").strip() == "product":
        # standing.silence: the waiver above silenced the WARN and stops here.
        if principles is None:
            failures.append(
                (
                    "standing.product-principles-reject",
                    "kind: product but this repo has no PRINCIPLES.md; "
                    "a waiver silences the WARN only, never this rejection.",
                )
            )
        else:
            reason = unratified_reason(read_text(principles))
            if reason:
                failures.append(
                    (
                        "standing.product-principles-reject",
                        f"{principles.relative_to(repo)} {reason}, so it was never ratified.",
                    )
                )
    return report(failures, err)


# Byte-identical to loom-design's validate_principles_output.py (parity test:
# loom-design/scripts/principles/test_principles_checker_parity.py): a
# non-empty name, a space, then an ISO date the calendar actually has.
# `ratified-by: pending — kouko to confirm` is a placeholder, not a signature
# (W2 re-review F1).
RATIFIED_BY_ANY = re.compile(r"^ratified-by:.*$", re.MULTILINE)
RATIFIED_BY = re.compile(r"^ratified-by:\s*\S.+\s(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def is_real_date(value: str) -> bool:
    """`9999-99-99` has the shape and is not a day."""
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
NON_NEGOTIABLES = re.compile(r"^##\s+non-negotiables\b", re.IGNORECASE)

# --- non-negotiables counting ----------------------------------------------
# Kept byte-identical to loom-design's validate_principles_output.py on
# purpose: the two live in plugins that cannot import each other, and
# loom-design/scripts/principles/test_principles_checker_parity.py runs both
# over one fixture table, so a drift here is a failing test rather than a
# silent disagreement about whether a constitution is ratified.
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
PUNCTUATION = re.compile(r"[^\w\s]+")
MIN_WORDS_PER_ITEM = 3
MIN_NON_NEGOTIABLES = 3


def normalise_item(line: str) -> str:
    body = LIST_MARKER.sub("", line)
    return " ".join(PUNCTUATION.sub(" ", body.lower()).split())


def substantive_non_negotiables(body: str) -> list[str]:
    """The normalised items that actually say something, de-duplicated.

    An item under three words is a slogan, not a commitment, and two items
    that normalise to the same string are one item typed twice -- counting
    raw lines let `it must be fast` three times ratify a constitution
    (W2 adversary P04)."""
    seen: set[str] = set()
    kept: list[str] = []
    for line in body.splitlines():
        if not LIST_ITEM.match(line):
            continue
        item = normalise_item(line)
        if len(item.split()) < MIN_WORDS_PER_ITEM or item in seen:
            continue
        seen.add(item)
        kept.append(item)
    return kept


def unratified_reason(text: str) -> str | None:
    """Ratified is two things, not one (concept-model §8): the signature
    line AND a Non-negotiables section with something in it. A signature over
    an empty document ratifies nothing, so the section is counted here."""
    match = RATIFIED_BY.search(text)
    if not match:
        if RATIFIED_BY_ANY.search(text):
            return (
                "carries a `ratified-by:` line that is not a signature; the "
                "grammar is `ratified-by: <name> <YYYY-MM-DD>` (a name, one "
                "space, an ISO date) -- a placeholder ratifies nothing"
            )
        return "carries no `ratified-by: <name> <date>` line"
    if not is_real_date(match.group(1)):
        return (
            f"names {match.group(1)!r} on its `ratified-by:` line, which is "
            "not a real date"
        )
    body, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = bool(NON_NEGOTIABLES.match(line))
            continue
        if inside:
            body.append(line)
    items = len(substantive_non_negotiables("\n".join(body)))
    if items < MIN_NON_NEGOTIABLES:
        return (
            "has no `## Non-negotiables` section carrying at least "
            f"{MIN_NON_NEGOTIABLES} list items that are each at least "
            f"{MIN_WORDS_PER_ITEM} words long and distinct from one another "
            f"(found {items})"
        )
    return None


def find_standing_doc(repo: Path, name: str) -> Path | None:
    """Repo root first, then docs/loom/ -- both are in use in the wild."""
    for candidate in (repo / name, repo / "docs" / "loom" / name):
        if candidate.is_file():
            return candidate
    return None


CHARTER_HEADER = (
    "| artifact | answers | readers | must | must not → goes to | sign-off | edits after |\n"
)
CHARTER_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- |\n"


def _charter_join(values) -> str:
    if not isinstance(values, list) or not values:
        return ""
    return "; ".join(str(v) for v in values)


KEBAB_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _edits_after_cell(edits_after) -> str:
    """`<id>: <text>` per entry, joined by '; ' -- the dict shape (W1-02's
    charter-boundaries fix) every `edits_after` entry now carries."""
    if not isinstance(edits_after, list) or not edits_after:
        return ""
    return "; ".join(
        f"{item.get('id', '?')}: {item.get('text', '?')}"
        for item in edits_after if isinstance(item, dict)
    )


def _charter_has_forbidden_chars(value: str) -> bool:
    """A `|` or a newline inside a charter cell would render as extra
    markdown table columns or rows -- reject both."""
    return "|" in value or "\n" in value


def _check_charter_cell_chars(
    name: str, key: str, value: str, failures: list[tuple[str, str]]
) -> None:
    if isinstance(value, str) and _charter_has_forbidden_chars(value):
        failures.append((
            "contract.charter-complete",
            f"{name}.{key} contains a '|' or a newline, which would corrupt "
            f"the rendered table: {value!r}.",
        ))


def check_charter_row(
    name: str, charter: dict, all_names: list[str], stations: set[str]
) -> tuple[list[tuple[str, str]], tuple[str, str, str, str, str, str, str]]:
    """Recompute every column of one charter row against the rules the
    `contract.charter-complete` description promises: non-empty answers/
    readers/must/must_not/edits_after, every must_not item naming a kind
    and a goes_to that is ANOTHER artifact in the table, and a signoff
    naming a real station."""
    failures: list[tuple[str, str]] = []

    answers = charter.get("answers")
    if not isinstance(answers, str) or not answers.strip():
        failures.append(("contract.charter-complete", f"{name}.answers is empty."))
    else:
        _check_charter_cell_chars(name, "answers", answers, failures)

    readers = charter.get("readers")
    if not isinstance(readers, list) or not readers:
        failures.append(("contract.charter-complete", f"{name}.readers is empty."))
    else:
        for item in readers:
            if isinstance(item, str):
                _check_charter_cell_chars(name, "readers", item, failures)

    must = charter.get("must")
    if not isinstance(must, list) or not must:
        failures.append(("contract.charter-complete", f"{name}.must is empty."))
    else:
        for item in must:
            if isinstance(item, str):
                _check_charter_cell_chars(name, "must", item, failures)

    must_not = charter.get("must_not")
    if not isinstance(must_not, list) or not must_not:
        failures.append(("contract.charter-complete", f"{name}.must_not is empty."))
    else:
        for item in must_not:
            if not isinstance(item, dict) or not str(item.get("kind") or "").strip():
                failures.append(
                    ("contract.charter-complete", f"{name}.must_not has an entry with no kind.")
                )
                continue
            _check_charter_cell_chars(name, "must_not.kind", str(item.get("kind")), failures)
            goes_to = str(item.get("goes_to") or "").strip()
            if not goes_to:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry {item['kind']!r} names no goes_to.",
                ))
            elif goes_to == name:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry goes_to names itself ({name!r}); "
                    "it must name another artifact in the table.",
                ))
            elif goes_to not in all_names:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.must_not entry goes_to {goes_to!r} names an artifact "
                    "absent from the table.",
                ))
            else:
                _check_charter_cell_chars(name, "must_not.goes_to", goes_to, failures)

    signoff = charter.get("signoff")
    if not isinstance(signoff, str) or not signoff.strip():
        failures.append(("contract.charter-complete", f"{name}.signoff is empty."))
    elif signoff not in stations:
        failures.append((
            "contract.charter-complete",
            f"{name}.signoff names unknown station {signoff!r}.",
        ))
    else:
        _check_charter_cell_chars(name, "signoff", signoff, failures)

    edits_after = charter.get("edits_after")
    if not isinstance(edits_after, list) or not edits_after:
        failures.append(("contract.charter-complete", f"{name}.edits_after is empty."))
    else:
        seen_ids: set[str] = set()
        for item in edits_after:
            if not isinstance(item, dict):
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after has a non-mapping entry {item!r}.",
                ))
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                failures.append(
                    ("contract.charter-complete", f"{name}.edits_after has an entry with no id.")
                )
            elif not KEBAB_ID.match(item_id):
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after id {item_id!r} is not kebab-case.",
                ))
            elif item_id in seen_ids:
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after id {item_id!r} is not unique within this artifact.",
                ))
            else:
                seen_ids.add(item_id)
            text = item.get("text")
            if not isinstance(text, str) or not text.strip():
                failures.append((
                    "contract.charter-complete",
                    f"{name}.edits_after entry {item.get('id', '?')!r} has no text.",
                ))
            elif isinstance(item_id, str):
                _check_charter_cell_chars(name, "edits_after", text, failures)

    must_not_cell = "; ".join(
        f"{item.get('kind', '?')} → {item.get('goes_to', '?')}"
        for item in must_not if isinstance(item, dict)
    ) if isinstance(must_not, list) else ""
    row = (
        name,
        str(answers) if isinstance(answers, str) and answers.strip() else "",
        _charter_join(readers),
        _charter_join(must),
        must_not_cell,
        str(signoff) if isinstance(signoff, str) and signoff.strip() else "",
        _edits_after_cell(edits_after),
    )
    return failures, row


def render_charter_table(rows: list[tuple[str, str, str, str, str, str, str]]) -> str:
    lines = [CHARTER_HEADER, CHARTER_SEPARATOR]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |\n")
    return "".join(lines)


def cmd_charter(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py charter [--manifest PATH]` -- the human view of
    `artifacts.<name>.charter` (manifest.yaml is the checker-read SSOT;
    this renders it). Prints one markdown row per artifact in manifest
    order and recomputes `contract.charter-complete` over every row."""
    manifest_path = manifest_path_in_effect()
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--manifest":
            if not rest:
                raise UsageError("--manifest needs a path.")
            manifest_path = Path(rest.pop(0))
        else:
            raise UsageError(f"unexpected argument {token!r}.")
    if not manifest_path.is_file():
        raise UsageError(f"no contract manifest at {manifest_path}")

    manifest = load_manifest(manifest_path)
    artifacts = manifest.get("artifacts")
    if not artifacts:
        out.write(render_charter_table([]))
        return report(
            [(
                "contract.charter-complete",
                "manifest carries no artifacts: mapping (absent or empty) -- "
                "every charter row is missing.",
            )],
            err,
        )
    stations = {
        s["name"] for s in manifest.get("stations", []) if isinstance(s, dict) and s.get("name")
    }
    all_names = list(artifacts.keys())

    failures: list[tuple[str, str]] = []
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for name in all_names:
        entry = artifacts.get(name) or {}
        charter = entry.get("charter")
        if not isinstance(charter, dict):
            failures.append((
                "contract.charter-complete",
                f"{name} has no charter block (`charter:` is missing entirely).",
            ))
            rows.append((name, "", "", "", "", "", ""))
            continue
        row_failures, row = check_charter_row(name, charter, all_names, stations)
        failures.extend(row_failures)
        rows.append(row)

    out.write(render_charter_table(rows))
    return report(failures, err)


def cmd_plan(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py plan <path>` -- runs `plan.field-caps` (and any other
    `plan.*` rule) against one plan file directly, independent of a
    change-id -- the shape the `plan` subcommand's own tests and the
    write-plan / push callers both rely on. This is a raw-content check on
    whatever file `<path>` names, by design: `plan-edits` and `push`
    instead resolve and read the canonical `docs/loom/<change-id>/plan.md`
    for that change-id."""
    if not args:
        raise UsageError("plan needs a path.")
    if len(args) > 1:
        raise UsageError(f"unexpected argument {args[1]!r}.")
    path = Path(args[0])
    if not path.is_file():
        err.write(f"no such plan file: {path}\n")
        return 2
    try:
        text = read_text(path)
    except OSError as exc:
        err.write(f"cannot read plan file {path}: {exc}\n")
        return 2
    return report(check_plan_field_caps(text), err)






REQUIRED_VERSION = re.compile(r"(\d+)\.(\d+)")


def cmd_contract(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py contract --require <major>.<minor>` -- the check
    loom-design and loom-workflow run at station start (concept-model §1).
    Same major and a high enough minor passes; anything else blocks with the
    one instruction the user can act on."""
    required = None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token != "--require":
            raise UsageError(f"unexpected argument {token!r}.")
        if not rest:
            raise UsageError("--require needs a <major>.<minor> version.")
        required = rest.pop(0)
    if required is None:
        raise UsageError("contract needs `--require <major>.<minor>`.")
    wanted = REQUIRED_VERSION.fullmatch(required.strip())
    if not wanted:
        raise UsageError(f"`--require {required}` is not <major>.<minor>.")

    version = str(load_manifest().get("version", "")).strip()
    shipped = REQUIRED_VERSION.match(version)
    if not shipped:
        raise UsageError(f"the contract manifest declares no readable version ({version!r}).")

    same_major = shipped.group(1) == wanted.group(1)
    if same_major and int(shipped.group(2)) >= int(wanted.group(2)):
        out.write(f"contract {version} satisfies requires-contract >={required}\n")
        return 0
    if int(wanted.group(1)) < int(shipped.group(1)):
        # This repo's contract has already moved past the required major --
        # the consuming plugin is what is stale, not loom-code.
        reason = (
            f"this repo ships loom contract {version}, but the consuming plugin "
            f"declares an old contract major (--require {required}); update that "
            "plugin's requires-contract to a supported major."
        )
    else:
        # Either the required major is higher than shipped, or the major
        # matches but the minor floor isn't met -- either way loom-code
        # itself is what needs updating.
        reason = (
            f"this repo ships loom contract {version}, but >={required} is "
            "required — 請更新 loom-code。"
        )
    return report([("contract.requires", reason)], err)


def cmd_finalize_review(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """Run functional verification once and generate content-bound evidence."""
    if not args:
        raise UsageError("finalize-review needs a change-id.")
    change_id, *rest = args
    if len(rest) != 2 or rest[0] != "--input":
        raise UsageError("finalize-review expects `--input <review-input.json>`.")
    input_path = Path(rest[1])
    try:
        review_input = json.loads(read_text(input_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"cannot read review input: {exc}") from exc
    if not isinstance(review_input, dict):
        raise UsageError("review input must be a JSON object.")
    verdicts = review_input.get("verdicts")
    findings = review_input.get("findings", [])
    adversarial = review_input.get("adversarial", [])
    if not isinstance(verdicts, list) or not verdicts:
        return report([("finalize.verdicts", "review input has no verdicts")], err)
    if any(not isinstance(v, dict) or v.get("verdict") not in {
        "PASS", "PASS_WITH_NOTES"
    } for v in verdicts):
        return report([("finalize.verdicts", "every reviewer verdict must pass")], err)
    reviewers = {str(v.get("reviewer", "")).strip() for v in verdicts}
    reviewers.discard("")
    if len(reviewers) < 2:
        return report([("finalize.verdicts", "two distinct reviewers are required")], err)
    if not isinstance(findings, list) or not isinstance(adversarial, list):
        return report([("finalize.schema", "findings and adversarial must be lists")], err)
    if not adversarial:
        return report([("finalize.adversarial", "at least one adversarial artifact is required")], err)

    repo = repo_root(Path.cwd())
    manifest = load_manifest()
    head_sha = git_text(repo, "rev-parse", "HEAD")
    status_before = git_text(repo, "status", "--porcelain")
    if status_before:
        return report([("finalize.clean-tree", "commit functional content before finalizing review")], err)
    config_before = git_text(repo, "config", "--list", "--null")
    package_command, source = declared_test_command(repo)
    if package_command is None or package_command.strip().lower() == NO_PACKAGE_TESTS:
        return report([("finalize.package-tests", f"no executable package command ({source})")], err)
    work: list[tuple[str, str, str]] = [("package-tests", package_command, "")]
    for item in adversarial:
        if not isinstance(item, dict):
            return report([("finalize.adversarial", "malformed adversarial input")], err)
        command = str(item.get("command", "")).strip()
        artifact = str(item.get("artifact", "")).strip()
        if not command or not artifact:
            return report([("finalize.adversarial", "adversarial input needs command and artifact")], err)
        if not command_names_artifact(command, artifact):
            return report([("finalize.adversarial", "command must name its artifact argument")], err)
        if not command_executes_artifact(command, artifact):
            return report([("finalize.adversarial", "command must execute the artifact directly")], err)
        if not git_ok(repo, "cat-file", "-e", f"{head_sha}:{artifact}"):
            return report([("finalize.adversarial", "artifact must exist in the selected commit")], err)
        work.append(("adversarial", command, artifact))

    executions: list[dict] = []
    for kind, command, artifact in work:
        try:
            completed = subprocess.run(
                argv_for(command), cwd=str(repo), capture_output=True, text=True,
                timeout=PROBE_RUN_TIMEOUT,
            )
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            return report([(f"finalize.{kind}", f"execution failed: {exc}")], err)
        if completed.returncode != 0:
            detail = (completed.stdout + completed.stderr).strip()
            suffix = f"\n{detail[-4000:]}" if detail else ""
            return report([(
                f"finalize.{kind}",
                f"`{command}` exited {completed.returncode}{suffix}",
            )], err)
        executions.append({
            "kind": kind, "command": command, "artifact": artifact,
            "result": "pass", "command_digest": _command_digest(command),
        })

    if git_text(repo, "rev-parse", "HEAD") != head_sha:
        return report([("finalize.stable-tree", "HEAD moved during functional verification")], err)
    if git_text(repo, "status", "--porcelain") != status_before:
        return report([("finalize.stable-tree", "working tree or index changed during functional verification")], err)
    if git_text(repo, "config", "--list", "--null") != config_before:
        return report([("finalize.stable-tree", "git configuration changed during functional verification")], err)

    digest = functional_content_digest(repo, head_sha, change_id, manifest)
    if digest is None:
        return report([("finalize.digest", "cannot compute functional content digest")], err)
    attestation = {
        "schema": ATTESTATION_SCHEMA, "change_id": change_id,
        "content_digest": digest, "executions": executions,
        "verdicts": verdicts, "findings": findings,
    }
    target = artifact_path(manifest, "attestation", change_id, repo)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False,
    ) as handle:
        json.dump(attestation, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(target)
    out.write(f"wrote {target.relative_to(repo)} for {digest}\n")
    return 0


COMMANDS = {
    "intent": cmd_intent,
    "intake": cmd_intake,
    "push": cmd_push,
    "publish": cmd_publish,
    "standing": cmd_standing,
    "contract": cmd_contract,
    "charter": cmd_charter,
    "plan": cmd_plan,
    "finalize-review": cmd_finalize_review,
}


def main(argv: list[str], out=sys.stdout, err=sys.stderr) -> int:
    try:
        if not argv:
            raise UsageError("no sub-command given." + USAGE)
        if argv[0] == "--list-rules":
            return list_rules(out)
        command = COMMANDS.get(argv[0])
        if command is None:
            raise UsageError(f"unknown sub-command {argv[0]!r}." + USAGE)
        return command(argv[1:], out, err)
    except UsageError as exc:
        err.write(f"{exc}\n")
        return 2
    except Exception as exc:  # fail-closed: an undecidable check never passes
        err.write(f"loom_checker internal error: {type(exc).__name__}: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
