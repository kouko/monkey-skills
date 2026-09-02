#!/usr/bin/env python3
"""The loom checker -- the single deterministic layer of the loom flow.

Every rule here RECOMPUTES its fact from the repository (the intent file,
the manifest, the git diff, review.json, the dispatch record). No rule
trusts an agent's claim about itself; concept-model §7 is explicit that
this layer stops missed steps, not a goal-directed agent.

Sub-commands (the CLI contract other stations depend on):

    loom_checker.py --list-rules
    loom_checker.py intent <path> [--commit-msg <file>]
    loom_checker.py intake <station> <change-id>
    loom_checker.py push [--head <ref>] [--hook]
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
import subprocess
import sys
from datetime import date
from pathlib import Path

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
        "intake.confirmed",
        "write-spec / write-plan accept only an intent whose status line reads `confirmed <date>` "
        "with a date the calendar has.",
    ),
    (
        "intake.confirmed-behavior",
        "write-plan accepts a product change only when its spec carries a "
        "`confirmed-behavior: <date> @<spec-blob-sha7>` line naming the spec as it stands.",
    ),
    (
        "intake.after-task-budget",
        "A plan may mark two tasks `review: after-task` for free; every further "
        "one carries a reason on its own task line.",
    ),
    (
        "intake.spec-pass",
        "write-plan accepts a needs-design: yes change only when the latest spec review round "
        "carries at least two distinct reviewers all passing, every verdict records a spec_sha "
        "equal to the spec's current identity, and the round carries a `scope: spec` "
        "adversarial probe.",
    ),
    (
        "intent.kind-recompute",
        "kind: engineering is rejected when the diff touches a declared interface-surface glob.",
    ),
    (
        "intent.needs-design-reason",
        "The needs-design line carries a reason and appears verbatim in the message of the "
        "commit that last changed the intent's status or needs-design line.",
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
        "push.frozen-store-untouched",
        "No commit between the branch base and reviewed_sha writes into a frozen store "
        "(docs/loom/plans, specs, backlog, design or archive); only each store's own "
        "ARCHIVED.md marker stays writable.",
    ),
    (
        "push.dismissed-by-reviewer",
        "Every dismissed finding names a dispatch reviewer, blind-runner or adversary who never implemented it.",
    ),
    (
        "push.dispatch-covers-tasks",
        "Every commit between the branch base and reviewed_sha that touches code, spec, skill "
        "or gate work carries a `Task:` trailer, and every id those trailers name is claimed by "
        "an implementer dispatch entry.",
    ),
    (
        "push.open-findings-closed",
        "Every open_findings entry in review.json is resolved or dismissed.",
    ),
    (
        "push.probes-adversarial",
        "A change carrying a code / spec / skill / gate artifact records at least three "
        "adversarial probes against the reviewed commit, and each one still passes.",
    ),
    (
        "push.probes-package-tests",
        "The checker re-runs the package-test command KICKOFF-DEFAULTS declares, at the "
        "reviewed tree, and believes its own exit code: the recorded result is not trusted, "
        "the probe's sha must be the reviewed commit, and its recorded command must be the "
        "declared one.",
    ),
    (
        "push.review-schema",
        "review.json carries every key the contract manifest declares, with the container type its template shows.",
    ),
    (
        "push.review-only-head",
        "HEAD is a review-only commit that touches nothing but docs/loom/<change-id>/review.json.",
    ),
    (
        "push.reviewed-sha",
        "review.json reviewed_sha names the commit HEAD^, so the reviewed tree is the pushed tree.",
    ),
    (
        "push.second-vendor-honoured",
        "A second vendor named in KICKOFF-DEFAULTS either appears in the latest "
        "round's verdicts or that round records why it could not.",
    ),
    (
        "push.reviewer-ne-implementer",
        "No reviewer, blind-runner or adversary in the dispatch record also implemented the change.",
    ),
    (
        "push.verdicts-ge-2",
        "The latest review round carries at least two distinct fresh-context reviewers, and "
        "blocks when any verdict in that round is not passing.",
    ),
    (
        "spec.req-grammar",
        "Every Requirements entry reads `REQ-<n> — <name>` with n contiguous from 1, "
        "unique, and points at an Acceptance number the intent actually carries.",
    ),
    (
        "spec.ui-flows-recompute",
        "While the diff touches a declared interface-surface glob, the spec's UI flows section "
        "carries at least one prose line (outside fences and HTML comments) with an arrow and "
        "at least four visible characters on each side. This is a structural floor only -- "
        "whether the flow says anything true or useful is the reviewer lens's job, not a "
        "keyword list's.",
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


PASSING_VERDICTS = {"PASS", "PASS_WITH_NOTES"}

_COMMENT = re.compile(r"\s+#\s.*$")
_FRONTMATTER_LINE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
_ANNOTATION = re.compile(r"[【\[(].*$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="surrogateescape")


def load_manifest(path: Path = MANIFEST_PATH):
    return yaml.safe_load(read_text(path))


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
    for line in text.splitlines():
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


def latest_round(verdicts: list[dict]) -> tuple[int, list[dict]]:
    """Only the newest round decides; earlier NEEDS_REVISION rounds are the
    history that produced it (concept-model §5 state machine)."""
    if not verdicts:
        return 0, []
    numbered = [(int(entry.get("round", 1)), entry) for entry in verdicts]
    newest = max(number for number, _ in numbered)
    return newest, [entry for number, entry in numbered if number == newest]


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

# The branch names loom treats as the trunk; standing on one is the P13 hole.
TRUNK_BRANCH_NAMES = frozenset({"main", "master"})


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
    diff must be checked against the whole diff, staging area included."""
    merge_base = branch_base(repo)
    paths: set[str] = set()
    for command in (
        ("diff", "--name-only", merge_base, "HEAD"),
        ("diff", "--name-only", "HEAD"),
        ("diff", "--name-only", "--cached", "HEAD"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        for line in git_text(repo, *command).splitlines():
            if line.strip():
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

    reason_failures, needs_design = check_needs_design_reason(
        front, commit_msg, repo, path
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


def deciding_commit(repo: Path, relative: str) -> str | None:
    """The newest commit that CHANGED the intent's `status:` or
    `needs-design:` line -- the one that decided something.

    Reading the newest touching commit instead made every later edit to the
    intent body (a new open question, an evidence path) owe the needs-design
    line, which is not what concept-model §2b asks for: the line belongs on
    the commit that writes or changes the decision (W2 re-review NF-4)."""
    for sha in git_text(repo, "log", "--format=%H", "--", relative).splitlines():
        if not sha.strip():
            continue
        if _decides_in_frontmatter(repo, sha, relative):
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


def _decides_in_frontmatter(repo: Path, sha: str, relative: str) -> bool:
    """Did this commit change a `status:`/`needs-design:` line that lived in
    the intent's FRONT MATTER? A quoted or fenced copy in the body is an
    example, not a decision (W2 re-review)."""
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
            decisive = body.lstrip().startswith(FRONTMATTER_DECISION) and new_line < after
            new_line += 1
        elif marker == "-":
            decisive = body.lstrip().startswith(FRONTMATTER_DECISION) and old_line < before
            old_line += 1
        else:
            old_line += 1
            new_line += 1
            continue
        if decisive:
            return True
    return False


def check_needs_design_reason(front, commit_msg: Path | None, repo: Path, path: Path):
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


def touched_interface_surfaces(repo: Path, manifest, out) -> list[str]:
    """The changed paths that land on a declared interface surface, and a
    printed line saying which globs were used -- the answer to "why did it
    say that" is never a mystery. Both `intent.needs-design-recompute` and
    `intent.kind-recompute` read this one recomputation."""
    globs, source = interface_surfaces(repo, manifest)
    out.write(f"interface-surfaces ({source}): {', '.join(globs)}\n")
    matchers = [glob_to_regex(pattern) for pattern in globs]
    return sorted(
        path
        for path in changed_paths(repo)
        if any(matcher.match(path) for matcher in matchers)
    )


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
CONFIRMED = re.compile(r"confirmed (\d{4}-\d{2}-\d{2})(\s+#.*)?")

INTAKE_STATIONS = ("write-spec", "write-plan")  # the two stations that accept an intent


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
    confirmed = CONFIRMED.fullmatch(status)
    if not confirmed:
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
    if not is_real_date(confirmed.group(1)):
        return report(
            [
                (
                    "intake.confirmed",
                    f"`status: confirmed {confirmed.group(1)}` names something "
                    "that is not a real date.",
                )
            ],
            err,
        )

    failures: list[tuple[str, str]] = []
    failures += check_after_task_budget(manifest, repo, change_id)

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
        failures += check_spec_pass(manifest, repo, change_id, err)
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
        return []  # a missing spec is intake.spec-pass's business, not this rule
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
FLOW_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
# Every spelling of "there is no interface", in the two languages the loom
# artifacts are written in.
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
        if not inside_fence:
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


AFTER_TASK_FREE = 2

# A plan's task line, per templates/plan.md:
# `**<id> <title>**  after: <ids>  review: after-task[ — <reason>]`
TASK_LINE = re.compile(
    r"^(?:[-*+]\s+)?\*\*(?P<id>[A-Za-z0-9][A-Za-z0-9._-]*)[^*]*\*\*(?P<rest>.*)$"
)


def check_after_task_budget(manifest, repo: Path, change_id: str):
    """Two `review: after-task` tasks are free; the rest justify themselves.

    The budget is not a hard cap (concept-model §5) -- it is a prompt to
    say why this task cannot wait for the wave. Without the reason the
    marker is free, and a plan can turn every task into a checkpoint
    without anyone noticing the cost."""
    plan_path = artifact_path(manifest, "plan", change_id, repo)
    if not plan_path.is_file():
        return []
    unjustified: list[str] = []
    seen = 0
    for line in read_text(plan_path).splitlines():
        match = TASK_LINE.match(line.strip())
        if not match:
            continue
        rest = match.group("rest")
        if "review: after-task" not in _squeeze(rest):
            continue
        seen += 1
        if seen <= AFTER_TASK_FREE:
            continue
        tail = _squeeze(rest).split("review: after-task", 1)[1]
        if not re.match(r"\s*(?:—|–|--)\s*\S", tail):
            unjustified.append(match.group("id"))
    if unjustified:
        return [
            (
                "intake.after-task-budget",
                f"{seen} tasks are marked `review: after-task`; past the first "
                f"{AFTER_TASK_FREE}, each carries `— <reason>` on its own task line. "
                f"Missing on: {', '.join(unjustified)}.",
            )
        ]
    return []


SPEC_LENSES = {"spec", "docs", "spec-adversarial"}


def spec_scoped_verdicts(review) -> tuple[list[dict], str | None]:
    """The verdicts that reviewed the SPEC, out of a file that accumulates.

    review.json holds every round of a change, and each round overwrites the
    file-level `scope` line. Reading the newest round alone lets a passing
    wave-end round answer for a spec nobody reviewed, and lets a failing one
    block a spec that passed. A round says what it looked at on its own
    verdicts (`scope: spec…`); records written before rounds carried a scope
    fall back to the file-level line plus the reviewer's lens."""
    entries = [entry for entry in review.get("verdicts", []) if isinstance(entry, dict)]
    explicit = [
        entry
        for entry in entries
        if str(entry.get("scope", "")).strip().lower().startswith("spec")
    ]
    if explicit:
        return explicit, None
    unscoped = [entry for entry in entries if not str(entry.get("scope", "")).strip()]
    if not unscoped:
        return [], (
            "review.json records no round scoped to the spec; every round it "
            "carries reviewed something else."
        )
    if "spec" not in str(review.get("scope", "")).lower():
        return [], "review.json scope does not cover the spec."
    by_lens = [
        entry for entry in unscoped
        if str(entry.get("lens", "")).strip().lower() in SPEC_LENSES
    ]
    if not by_lens:
        return [], (
            "review.json carries no verdict from a spec-side lens "
            f"({', '.join(sorted(SPEC_LENSES))}); the spec was not what was reviewed."
        )
    return by_lens, None


def is_spec_adversarial_probe(probe) -> bool:
    """The red-team half of the spec lens, and only that half.

    review.json accumulates every round of a change, so an unscoped
    adversarial probe -- one recorded against the code, or against nothing
    in particular -- used to answer for a spec no adversary ever attacked.
    The probe says what it attacked on itself now: `scope: spec`, or it is
    not the spec's red team."""
    if not isinstance(probe, dict) or str(probe.get("kind")) != "adversarial":
        return False
    return str(probe.get("scope", "")).strip().lower().startswith("spec")


def check_spec_pass(manifest, repo: Path, change_id: str, err=sys.stderr) -> list[tuple[str, str]]:
    """write-plan accepts a needs-design: yes change only after the spec's
    own review round passed (concept-model §5, §7)."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return [("intake.spec-pass", f"needs-design: yes but no spec at {spec_path.relative_to(repo)}.")]
    review_path = artifact_path(manifest, "review", change_id, repo)
    if not review_path.is_file():
        return [
            (
                "intake.spec-pass",
                f"no review.json at {review_path.relative_to(repo)}; the spec was never reviewed.",
            )
        ]
    review = json.loads(read_text(review_path))
    spec_verdicts, selection_failure = spec_scoped_verdicts(review)
    if selection_failure:
        return [("intake.spec-pass", selection_failure)]
    round_number, verdicts = latest_round(spec_verdicts)
    reviewers = {str(entry.get("reviewer", "")) for entry in verdicts}
    if len(reviewers) < 2:
        return [
            (
                "intake.spec-pass",
                f"the latest spec review round ({round_number}) carries "
                f"{len(reviewers)} reviewer(s); two independent ones are required.",
            )
        ]
    failed = [
        f"{entry.get('reviewer')}={entry.get('verdict')}"
        for entry in verdicts
        if str(entry.get("verdict")) not in PASSING_VERDICTS
    ]
    if failed:
        return [
            (
                "intake.spec-pass",
                f"the latest spec review round ({round_number}) is not passing: "
                f"{', '.join(failed)}.",
            )
        ]
    # The spec lens is read AND adversarial (concept-model §5, §6): two
    # passing readers without a red-team is half a review.
    if not any(is_spec_adversarial_probe(probe) for probe in review.get("probes", [])):
        return [
            (
                "intake.spec-pass",
                "no `adversarial` probe carrying `scope: spec` is recorded; the "
                "spec lens is read + adversarial, and an unscoped probe does not "
                "say the spec was what it attacked.",
            )
        ]
    return check_spec_freshness(repo, spec_path, review, verdicts, round_number, err)


def check_spec_freshness(repo, spec_path, review, verdicts, round_number, err):
    """A pass is a pass over a particular text.

    Rewrite the spec after its round and the verdict is about a document that
    no longer exists, and the only freshness rule that used to exist
    (`push.reviewed-sha`) fires at push -- after the plan and the whole build
    (W2 adversary P09). There is one way to answer the question and no
    fallback: the round's own verdicts carry `spec_sha`, or the round cannot
    say what it read and does not pass (W2 re-review F3/F4)."""
    current = spec_identity(spec_path)
    relative = spec_path.relative_to(repo).as_posix()
    # EVERY reviewer of the round, not any of them: two reviewers who read
    # different texts are not two readings of this spec, and one reviewer who
    # recorded nothing leaves their own verdict unattached to any text.
    silent = [
        str(entry.get("reviewer", "?"))
        for entry in verdicts
        if not str(entry.get("spec_sha", "")).strip()
    ]
    if silent:
        return [
            (
                "intake.spec-pass",
                f"{', '.join(sorted(set(silent)))} recorded no `spec_sha` in "
                f"spec review round {round_number}, so nothing says which text "
                f"they read -- the spec could have been rewritten afterwards "
                f"and nothing would notice. Record spec_sha in the spec round "
                f"({current[:7]} for {relative} as it stands); "
                f"{recompute_command(relative)}.",
            )
        ]
    stale = [
        f"{entry.get('reviewer', '?')}={str(entry['spec_sha']).strip()[:7]}"
        for entry in verdicts
        if not sha_agrees(str(entry["spec_sha"]).strip(), current)
    ]
    if stale:
        return [
            (
                "intake.spec-pass",
                f"spec review round {round_number} read {', '.join(stale)} but "
                f"{relative} is now {current[:7]} -- spec changed after "
                f"review; send it round again. To check the value yourself, "
                f"{recompute_command(relative)}.",
            )
        ]
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
PREFIX_WORDS = {"sudo", "command", "env", "nohup", "time", "nice", "builtin", "exec", "xargs"}
# `bash -c "git push"` / `sh -c` / `zsh -c` / `dash -c` hand the checker a
# shell line as a single quoted argument -- shlex has already unquoted it, so
# it is re-read as a shell line of its own, exactly like `eval`'s payload.
SHELL_PROGRAMS = {"bash", "sh", "zsh", "dash"}


def _tokenise(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:  # an unbalanced quote is still worth judging
        return segment.split()


def _strip_prefix(tokens: list[str]) -> list[str]:
    """Drop `VAR=…` assignments and wrapper words that precede the program."""
    index = 0
    while index < len(tokens) and (
        ASSIGNMENT.match(tokens[index]) or tokens[index] in PREFIX_WORDS
    ):
        index += 1
    return tokens[index:]


def _subcommand(tokens: list[str], value_options: set[str]) -> str | None:
    """The first word that is neither an option nor an option's value."""
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
        return token
    return None


def is_push_command(command: str) -> bool:
    """True when any segment of this shell line pushes or opens/merges a PR."""
    for segment in SEGMENT_SPLIT.split(command):
        tokens = _strip_prefix(_tokenise(segment))
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program == "eval":
            # `eval "git push"`: shlex already removed the quoting, so the
            # payload is re-read as a shell line of its own.
            if is_push_command(" ".join(tokens[1:])):
                return True
        elif program in SHELL_PROGRAMS and "-c" in tokens[1:]:
            # `bash -c "git push"` / `sh -c` / `zsh -c` / `dash -c`: the
            # argument after `-c` is itself a shell line, same as eval's.
            index = tokens.index("-c")
            if index + 1 < len(tokens) and is_push_command(tokens[index + 1]):
                return True
        elif program == "git":
            if _subcommand(tokens[1:], GIT_VALUE_OPTIONS) == "push":
                return True
        elif program == "gh":
            rest = tokens[1:]
            if _subcommand(rest, set()) == "pr":
                after = rest[rest.index("pr") + 1:]
                if _subcommand(after, set()) in {"create", "merge"}:
                    return True
    return False


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
    if not is_push_command(command):
        return 0
    cwd = payload.get("cwd")
    if cwd:
        os.chdir(cwd)
    rc = _cmd_push(rest, out, err)
    return 2 if rc == 1 else rc   # hosts block on exit 2


def _cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    head = "HEAD"
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token == "--head":
            if not rest:
                raise UsageError("--head needs a ref.")
            head = rest.pop(0)
        else:
            raise UsageError(f"unexpected argument {token!r}.")

    manifest = load_manifest()
    repo = repo_root(Path.cwd())
    head_sha = git_maybe(repo, "rev-parse", head)
    if not head_sha:
        raise UsageError(f"cannot resolve {head!r} in {repo}.")

    review_rel, failures = check_review_only_head(manifest, repo, head_sha)
    if review_rel is None:
        return report(failures, err)

    raw = git_text(repo, "show", f"{head_sha}:{review_rel}")
    try:
        review = json.loads(raw)
    except json.JSONDecodeError as exc:
        return report([("push.review-schema", f"{review_rel} is not valid JSON: {exc}")], err)
    if not isinstance(review, dict):
        return report([("push.review-schema", f"{review_rel} is not a JSON object.")], err)

    failures += check_review_schema(manifest, review, review_rel)
    recorded = str(review.get("reviewed_sha", "")).strip()
    reviewed_id = (
        git_maybe(repo, "rev-parse", "--verify", f"{recorded}^{{commit}}")
        if SHA_HEX.fullmatch(recorded)
        else None
    )

    failures += check_reviewed_sha(repo, head_sha, recorded, reviewed_id)
    failures += check_open_findings_closed(review)
    failures += check_probes_package_tests(repo, review, reviewed_id, out)
    failures += check_probes_adversarial(repo, review, reviewed_id, out)
    failures += check_verdicts(review)
    failures += check_second_vendor_honoured(repo, review)
    failures += check_dispatch_covers_tasks(repo, review, reviewed_id)
    failures += check_frozen_store_untouched(repo, reviewed_id)

    # `dispatch[]` lives inside the review.json that was read out of the
    # reviewed commit's tree, so both identity rules recompute from a
    # committed record and never from the working tree (concept-model §2e).
    implementers, reviewers, dispatch_error = parse_dispatch(review)
    failures += check_reviewer_ne_implementer(review, implementers, reviewers, dispatch_error)
    failures += check_dismissed_by_reviewer(review, implementers, reviewers, dispatch_error)
    return report(failures, err)


SHA_HEX = re.compile(r"[0-9a-f]{7,40}")


def check_review_only_head(manifest, repo: Path, head_sha: str):
    """A checkpoint push rides on a review-only commit: exactly one file,
    and that file is this change's review.json (concept-model §2e)."""
    # `--name-only` lets rename detection collapse a delete and an add into
    # one path, so a commit that renames a tracked file INTO the review path
    # deletes that file while the gate counts one path. `--raw
    # --no-renames` reports the delete and the add separately, which is what
    # "touches nothing but review.json" has to mean.
    listing = git_text(
        repo, "show", "--raw", "--no-renames", "--pretty=format:", head_sha
    )
    touched = sorted(
        {
            line.split("\t", 1)[1].strip()
            for line in listing.splitlines()
            if "\t" in line and line.startswith(":")
        }
    )
    template = manifest["artifacts"]["review"]["path"]
    is_review = glob_to_regex(template.replace("<change-id>", "*"))
    reviews = [path for path in touched if is_review.match(path)]
    if len(touched) == 1 and reviews:
        return reviews[0], []
    detail = ", ".join(touched) if touched else "nothing"
    return None, [
        (
            "push.review-only-head",
            f"HEAD must touch only {template}; it touches {detail}.",
        )
    ]


def review_container_types(manifest) -> dict[str, type]:
    """The declared container per key, taken from the artifact's own
    template -- the schema is declared once, in the contract package."""
    template = MANIFEST_PATH.parent / "templates" / manifest["artifacts"]["review"]["template"]
    return {key: type(value) for key, value in json.loads(read_text(template)).items()}


def check_review_schema(manifest, review, review_rel: str) -> list[tuple[str, str]]:
    """Nothing downstream may read a key that was never checked to exist."""
    types = review_container_types(manifest)
    failures = []
    for field in manifest["artifacts"]["review"]["fields"]:
        if not field.get("required"):
            continue
        name = field["name"]
        if name not in review:
            failures.append(("push.review-schema", f"{review_rel} has no `{name}` key."))
            continue
        expected = types.get(name)
        if expected is not None and not isinstance(review[name], expected):
            failures.append(
                (
                    "push.review-schema",
                    f"`{name}` is {type(review[name]).__name__}, not "
                    f"{expected.__name__} as the template declares.",
                )
            )
    recorded = str(review.get("reviewed_sha", "")).strip()
    if recorded and not SHA_HEX.fullmatch(recorded):
        failures.append(
            (
                "push.review-schema",
                f"`reviewed_sha: {recorded}` is not 7-40 lowercase hex digits.",
            )
        )
    failures += check_questions(review, review_rel)
    return failures


# `questions[]` records what the user was asked at a decision point. It is
# optional -- a change with no fork asks nothing -- but a present one is
# checked, because an unchecked optional key is a key nobody may read.
QUESTION_TYPES = frozenset({"what", "behaviour", "done", "consequence"})


def check_questions(review, review_rel: str) -> list[tuple[str, str]]:
    if "questions" not in review:
        return []
    entries = review["questions"]
    if not isinstance(entries, list):
        return [
            (
                "push.review-schema",
                f"`questions` is {type(entries).__name__}, not list as the "
                "template declares.",
            )
        ]
    failures = []
    for index, entry in enumerate(entries):
        where = f"{review_rel} questions[{index}]"
        if not isinstance(entry, dict):
            failures.append(("push.review-schema", f"{where} is not an object."))
            continue
        if not isinstance(entry.get("decision_point"), int):
            failures.append(
                ("push.review-schema", f"{where} has no integer `decision_point`.")
            )
        if not str(entry.get("text", "")).strip():
            failures.append(("push.review-schema", f"{where} has no `text`."))
        kind = str(entry.get("type", ""))
        if kind not in QUESTION_TYPES:
            failures.append(
                (
                    "push.review-schema",
                    f"{where} `type: {kind or '(absent)'}` is not one of "
                    f"{'|'.join(sorted(QUESTION_TYPES))}.",
                )
            )
    return failures


def check_reviewed_sha(repo: Path, head_sha: str, recorded: str, reviewed_id: str | None):
    """The reviewed tree must be the tree being pushed. Compared as object
    ids resolved by git, never as strings: a prefix compare accepts a
    reviewed_sha that names no commit at all."""
    parent = git_maybe(repo, "rev-parse", "--verify", f"{head_sha}^{{commit}}^")
    if not parent:
        return [("push.reviewed-sha", "HEAD has no parent commit to have reviewed.")]
    if reviewed_id is None:
        return [
            (
                "push.reviewed-sha",
                f"reviewed_sha {recorded or '(empty)'} names no commit in this repo.",
            )
        ]
    if reviewed_id != parent:
        return [
            (
                "push.reviewed-sha",
                f"reviewed_sha resolves to {reviewed_id[:8]} but HEAD^ is {parent[:8]}; "
                "the reviewed commit is not the one being pushed.",
            )
        ]
    return []


def check_open_findings_closed(review) -> list[tuple[str, str]]:
    open_ones = [
        str(entry.get("id", "<no id>"))
        for entry in review.get("open_findings", [])
        if isinstance(entry, dict) and not entry.get("resolved") and not entry.get("dismissed")
    ]
    if open_ones:
        return [
            (
                "push.open-findings-closed",
                f"{len(open_ones)} finding(s) neither resolved nor dismissed: "
                f"{', '.join(open_ones)}.",
            )
        ]
    return []


# A command that exits 0 for reasons unrelated to the thing it claims to
# have run. `true` is the whole attack: it is a real command, it really
# exits 0, and it tests nothing.
TRIVIAL_COMMANDS = frozenset({"true", ":", "/bin/true", "/usr/bin/true", "exit"})

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


def is_trivial_command(command: str) -> bool:
    """True when the command's exit code says nothing about any artifact."""
    stripped = command.strip()
    if not stripped:
        return True
    head = stripped.split()[0]
    if head in TRIVIAL_COMMANDS:
        return True
    # `test -f x`, `[ -f x ]` -- shell predicates, not runs of anything.
    return head in {"test", "["}


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


def artifact_argv(repo: Path, artifact: str) -> list[str]:
    """How to RUN `artifact`, chosen from the file rather than from prose.

    The recorded command is a record of what an agent says it did; running
    it hands the exit code to a shell pipeline the agent wrote, and
    `python3 case.py ; true` then exits 0 whatever the case does. The
    checker runs the file itself, so the exit code it observes is the
    file's.
    """
    path = repo / artifact
    suffix = Path(artifact).suffix.lower()
    if suffix == ".py":
        return [sys.executable, artifact]
    if suffix == ".sh":
        return ["bash", artifact]
    if path.is_file() and os.access(path, os.X_OK):
        return [os.path.join(".", artifact)]
    raise ValueError(
        f"{artifact} is not runnable: it is neither a .py nor a .sh file, and "
        "carries no executable bit, so there is no way to execute the case it "
        "claims to be"
    )


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


def check_probes_package_tests(repo: Path, review, reviewed_id: str | None,
                               out=sys.stdout):
    """A recorded test run is not evidence -- the RUN is. The record only
    says which commit was tested and what to type; the checker then types it
    itself in a clean tree that is the reviewed tree, and the exit code it
    observes decides (concept-model §7). The agent's own `result` is kept as
    a record and never believed."""
    expected, source = declared_test_command(repo)
    if expected is None:
        return [
            (
                "push.probes-package-tests",
                "this repo declares no package-test command and none can be "
                "recomputed from it; record `- package-tests: <command>` (or "
                "`- package-tests: none — <why>`) in docs/loom/KICKOFF-DEFAULTS.md "
                "so the recorded run has something to be checked against",
            )
        ]
    if expected.strip().lower() == NO_PACKAGE_TESTS:
        out.write(
            f"package-tests: none — declared in {source}; no run is owed and "
            "the review station records the gap\n"
        )
        return []

    reasons: list[str] = []
    for probe in review.get("probes", []):
        if not isinstance(probe, dict) or str(probe.get("kind")) != "package-tests":
            continue
        command = str(probe.get("command", "")).strip()
        label = command or "<no command>"
        if not command:
            reasons.append("a package-tests probe records no command")
            continue
        if _squeeze(command) != _squeeze(expected):
            reasons.append(
                f"`{label}` is not this repo's test command `{expected}` "
                f"({source}); a command that exits 0 for another reason is not "
                "a test run"
            )
            continue
        sha = str(probe.get("sha", "")).strip()
        probe_id = (
            git_maybe(repo, "rev-parse", "--verify", f"{sha}^{{commit}}")
            if SHA_HEX.fullmatch(sha)
            else None
        )
        if probe_id is None or reviewed_id is None or probe_id != reviewed_id:
            reasons.append(f"`{label}` ran against sha {sha or '(absent)'}, not the reviewed commit")
            continue
        artifact = str(probe.get("artifact", "")).strip()
        if artifact and not git_ok(repo, "cat-file", "-e", f"{reviewed_id}:{artifact}"):
            reasons.append(f"`{label}` names artifact {artifact}, absent from the reviewed tree")
            continue
        if git_text(repo, "status", "--porcelain").strip():
            reasons.append(
                f"`{label}` cannot be re-run: the working tree is not clean, so what "
                "would be tested is not the reviewed tree"
            )
            continue
        # What runs is the DECLARED command, read as argv and executed with
        # no shell: the recorded string has already been checked to equal
        # it, and handing a shell a string an agent wrote hands it the
        # exit code too.
        try:
            argv = argv_for(expected)
        except ValueError as exc:
            reasons.append(f"the declared command `{expected}` cannot be run: {exc}")
            break
        try:
            observed = subprocess.run(
                argv, cwd=str(repo), capture_output=True,
                text=True, timeout=PROBE_RUN_TIMEOUT,
            ).returncode
        except FileNotFoundError:
            reasons.append(f"the declared command `{expected}` names no program on PATH")
            break
        except subprocess.TimeoutExpired:
            reasons.append(f"`{expected}` did not finish within {PROBE_RUN_TIMEOUT}s")
            continue
        out.write(
            f"package-tests `{expected}`: observed exit code {observed} "
            f"(recorded result: {probe.get('result')!r})\n"
        )
        if observed != 0:
            advice = (
                ""
                if source == "docs/loom/KICKOFF-DEFAULTS.md"
                else (
                    " — this command was not declared but recomputed from "
                    f"{source}; if it is the wrong one, declare "
                    "`package-tests:` in docs/loom/KICKOFF-DEFAULTS.md rather "
                    "than leaving the gate guessing"
                )
            )
            reasons.append(
                f"`{label}` exited {observed} when the checker ran it{advice}"
            )
            continue
        return []
    detail = "; ".join(reasons) if reasons else "no package-tests probe recorded at all"
    return [("push.probes-package-tests", f"no usable package-tests probe: {detail}.")]


# The artifact types whose review demands the adversarial action
# (concept-model §6: code -> mutation/fuzz or >=3 abuse cases, spec ->
# red-team, skill/gate -> the attack catalogue). A change touching none of
# them -- documentation, memory, evidence -- owes no adversarial probe.
ADVERSARIAL_TYPES = frozenset({"code", "spec", "skill", "gate"})

ADVERSARIAL_FLOOR = 3


def artifact_types(manifest, paths) -> set[str]:
    """The §6 type of each changed path: first matching glob in the
    manifest's declared order wins, which is why `**` sits last there."""
    rules = [(glob_to_regex(entry["glob"]), entry["type"])
             for entry in manifest["artifact_types"]]
    found = set()
    for path in paths:
        for pattern, kind in rules:
            if pattern.match(path):
                found.add(kind)
                break
    return found


def check_probes_adversarial(repo: Path, review, reviewed_id: str | None,
                             out=sys.stdout):
    """Same discipline as the package-tests rule: the record says which
    commit was attacked and what to type, and the checker types it itself.
    An adversarial case that only ran in the adversary's head is not
    evidence, and one that no longer passes is not a regression eval."""
    try:
        manifest = load_manifest()
        changed = changed_paths(repo)
    except (UsageError, OSError, KeyError) as exc:
        return [("push.probes-adversarial", f"cannot recompute artifact types: {exc}")]

    # The review file is the output of reviewing, never part of what is
    # reviewed; left in, its `.json` extension falls through to `code` and
    # every change on earth would owe an adversary.
    is_review = glob_to_regex(manifest["artifacts"]["review"]["path"].replace("<change-id>", "*"))
    changed = {path for path in changed if not is_review.match(path)}

    kinds = artifact_types(manifest, changed) & ADVERSARIAL_TYPES
    if not kinds:
        return []

    usable = 0
    reasons: list[str] = []
    for probe in review.get("probes", []):
        if not isinstance(probe, dict) or str(probe.get("kind")) != "adversarial":
            continue
        command = str(probe.get("command", "")).strip()
        label = command or "<no command>"
        if not command:
            reasons.append("an adversarial probe records no command")
            continue
        if is_trivial_command(command):
            reasons.append(
                f"`{label}` exits 0 without running anything; an adversarial "
                "case is a file the checker can execute, not a shell builtin"
            )
            continue
        artifact = str(probe.get("artifact", "")).strip()
        if not artifact:
            reasons.append(
                f"`{label}` names no artifact; the case must be a committed file"
            )
            continue
        if reviewed_id is None or not git_ok(
            repo, "cat-file", "-e", f"{reviewed_id}:{artifact}"
        ):
            reasons.append(
                f"`{label}` names artifact {artifact}, absent from the reviewed tree"
            )
            continue
        try:
            named = command_names_artifact(command, artifact)
        except ValueError as exc:
            reasons.append(f"`{label}` is not a parseable command line: {exc}")
            continue
        if not named:
            reasons.append(
                f"`{label}` passes its artifact {artifact} to nothing — no "
                "argument of the command is that path, so a mention in a "
                "trailing comment or in an unrelated word is all there is, "
                "and what actually ran cannot be recomputed from the record"
            )
            continue
        sha = str(probe.get("sha", "")).strip()
        probe_id = (
            git_maybe(repo, "rev-parse", "--verify", f"{sha}^{{commit}}")
            if SHA_HEX.fullmatch(sha)
            else None
        )
        if probe_id is None or reviewed_id is None or probe_id != reviewed_id:
            reasons.append(
                f"`{label}` ran against sha {sha or '(absent)'}, not the reviewed commit"
            )
            continue
        if git_text(repo, "status", "--porcelain").strip():
            reasons.append(
                f"`{label}` cannot be re-run: the working tree is not clean, so what "
                "would be attacked is not the reviewed tree"
            )
            continue
        try:
            argv = artifact_argv(repo, artifact)
        except ValueError as exc:
            reasons.append(str(exc))
            continue
        try:
            observed = subprocess.run(
                argv, cwd=str(repo), capture_output=True,
                text=True, timeout=PROBE_RUN_TIMEOUT,
            ).returncode
        except (FileNotFoundError, PermissionError) as exc:
            reasons.append(f"{artifact} could not be executed: {exc}")
            continue
        except subprocess.TimeoutExpired:
            reasons.append(f"{artifact} did not finish within {PROBE_RUN_TIMEOUT}s")
            continue
        out.write(
            f"adversarial {artifact}: observed exit code {observed} "
            f"(recorded command: {label!r}, recorded result: {probe.get('result')!r})\n"
        )
        if observed != 0:
            reasons.append(
                f"{artifact} exited {observed} when the checker ran it — a case "
                "that no longer passes is not a regression eval, whatever the "
                "recorded command wraps it in"
            )
            continue
        usable += 1

    if usable >= ADVERSARIAL_FLOOR:
        return []
    detail = "; ".join(reasons) if reasons else "none recorded"
    return [
        (
            "push.probes-adversarial",
            f"this change touches {', '.join(sorted(kinds))}, which needs "
            f"{ADVERSARIAL_FLOOR} adversarial probes; {usable} are usable ({detail}).",
        )
    ]


TASK_TRAILER = re.compile(r"^Task:\s*(\S+)\s*$", re.MULTILINE)


def commit_paths(repo: Path, sha: str) -> set[str]:
    """Every path one commit touches, with rename detection off."""
    listing = git_text(repo, "show", "--raw", "--no-renames", "--pretty=format:", sha)
    return {
        line.split("\t", 1)[1].strip()
        for line in listing.splitlines()
        if "\t" in line and line.startswith(":")
    }


def check_dispatch_covers_tasks(repo: Path, review, reviewed_id: str | None):
    """Every commit that changes real work names the task it belongs to.

    `Task: <id>` trailers are how progress is derived (concept-model §2d)
    and `dispatch[]` is how "who wrote this" is recomputed (§2e). The pair
    only holds if the trailer is on the commit that did the work: a trailer
    parked on a docs commit while the code commit carries none leaves that
    code belonging to no task, and no dispatch entry can be checked against
    it. A commit touching only documentation, the review record, the intent,
    the plan or evidence owes no trailer -- none of it is dispatched work.
    """
    if reviewed_id is None:
        return []
    try:
        base = branch_base(repo)
        manifest = load_manifest()
    except (UsageError, OSError, KeyError) as exc:
        return [("push.dispatch-covers-tasks", f"cannot recompute the branch base: {exc}")]

    is_review = glob_to_regex(
        manifest["artifacts"]["review"]["path"].replace("<change-id>", "*")
    )
    shas = [
        line.strip()
        for line in git_text(repo, "log", "--format=%H", f"{base}..{reviewed_id}").splitlines()
        if line.strip()
    ]

    claimed: set[str] = set()
    untrailered: list[tuple[str, str]] = []
    for sha in shas:
        paths = {path for path in commit_paths(repo, sha) if not is_review.match(path)}
        kinds = artifact_types(manifest, paths) & ADVERSARIAL_TYPES
        message = git_text(repo, "log", "-1", "--format=%B", sha)
        ids = {match.group(1) for match in TASK_TRAILER.finditer(message)}
        claimed |= ids
        if kinds and not ids:
            untrailered.append((sha[:8], ", ".join(sorted(kinds))))

    if untrailered:
        listing = "; ".join(f"{sha} touches {kinds}" for sha, kinds in untrailered)
        return [
            (
                "push.dispatch-covers-tasks",
                f"no `Task:` trailer on {len(untrailered)} commit(s) that change "
                f"dispatched work: {listing}. Progress is derived from those "
                "trailers, so this work belongs to no planned task.",
            )
        ]
    if not claimed:
        return []

    dispatched = {
        str(entry.get("task", "")).strip()
        for entry in review.get("dispatch", [])
        if isinstance(entry, dict) and str(entry.get("role", "")).strip() == "implementer"
    }
    missing = sorted(claimed - dispatched)
    if missing:
        return [
            (
                "push.dispatch-covers-tasks",
                f"{len(claimed)} task(s) carry a `Task:` trailer on this branch but "
                f"{', '.join(missing)} name no implementer dispatch entry; the "
                "record lost a writer or the work was never dispatched.",
            )
        ]
    return []


# The stores loom 1.0 froze: old plans, specs, briefs, backlog and design
# notes stay where they are and are never converted (concept-model §10, the
# hard switch). Their own ARCHIVED.md marker is the one file a change may
# still write, because closing a store is how a store gets frozen.
FROZEN_STORES = ("plans", "specs", "backlog", "design", "archive")
FROZEN_STORE_RE = re.compile(
    r"^docs/loom/(?:" + "|".join(FROZEN_STORES) + r")/(?:.*/)?(?P<name>[^/]+)$"
)


def check_frozen_store_untouched(repo: Path, reviewed_id: str | None):
    """A frozen store is frozen in fact, not in prose.

    `docs/loom/BACKLOG.md` said "no reads, no writes" and nothing recomputed
    it, so a station could keep writing plans into the store the switch
    retired and every reader would go on trusting it (W3 adversary P07). The
    diff between the branch base and the reviewed commit is the fact."""
    if reviewed_id is None:
        return []
    try:
        base = branch_base(repo)
    except (UsageError, OSError) as exc:
        return [("push.frozen-store-untouched", f"cannot recompute the branch base: {exc}")]
    touched = sorted({
        line.strip()
        for line in git_text(
            repo, "diff", "--name-only", base, reviewed_id
        ).splitlines()
        if line.strip()
    })
    written = [
        path for path in touched
        if (match := FROZEN_STORE_RE.match(path)) and match.group("name") != "ARCHIVED.md"
    ]
    if not written:
        return []
    return [
        (
            "push.frozen-store-untouched",
            f"{len(written)} path(s) under a frozen store changed on this branch: "
            f"{', '.join(written[:5])}. Loom 1.0 froze docs/loom/"
            f"{{{','.join(FROZEN_STORES)}}}/ in place -- nothing converts them and "
            "nothing writes to them; only each store's ARCHIVED.md marker stays "
            "writable. New work belongs in docs/loom/intent/ and "
            "docs/loom/<change-id>/.",
        )
    ]


# The vendor behind each CLI a repo can name as its second opinion.
VENDOR_OF_CLI = {"codex": "openai", "gemini": "google", "claude": "anthropic"}


def check_second_vendor_honoured(repo: Path, review):
    """A second vendor the repo chose is used, or the round says why not.

    Choosing a second vendor is the user's call (concept-model §5) and the
    checker does not require one. What it does require is that a recorded
    choice is not silently dropped: either that vendor reviewed this round,
    or the round carries `fallback: <cli> missing at <date>` and everyone
    can see the review ran single-vendor."""
    declared = kickoff_defaults(repo).get("second-vendor", "").strip()
    if not declared or declared.lower() == "none":
        return []
    cli = declared.split()[0].lower()
    wanted = VENDOR_OF_CLI.get(cli, cli)
    _round, verdicts = latest_round(
        [entry for entry in review.get("verdicts", []) if isinstance(entry, dict)]
    )
    if not verdicts:
        return []
    used = {str(entry.get("vendor", "")).strip().lower() for entry in verdicts}
    if wanted in used:
        return []
    # The fallback is a dated statement about THIS cli, not a free-text
    # field: `n/a` is not a reason the second opinion is missing, and a
    # fallback naming some other tool explains nothing about this one.
    grammar = re.compile(rf"{re.escape(cli)} missing at \d{{4}}-\d{{2}}-\d{{2}}")
    written = [
        str(entry.get("fallback", "")).strip()
        for entry in verdicts
        if str(entry.get("fallback", "")).strip()
    ]
    if any(grammar.fullmatch(value) for value in written):
        return []
    saw = f"; it records fallback {written[0]!r}" if written else ""
    return [
        (
            "push.second-vendor-honoured",
            f"KICKOFF-DEFAULTS names `second-vendor: {declared}` ({wanted}), but the "
            f"latest round used {', '.join(sorted(used)) or 'nothing'} and no verdict "
            f"records `fallback: \"{cli} missing at <YYYY-MM-DD>\"`{saw}.",
        )
    ]


def scored_verdicts(review) -> tuple[int, list[dict]]:
    """The latest round's verdicts, minus entries that name no reviewer or
    carry no verdict -- an unreadable entry is not a second opinion."""
    usable = [
        entry
        for entry in review.get("verdicts", [])
        if isinstance(entry, dict)
        and str(entry.get("reviewer", "")).strip()
        and str(entry.get("verdict", "")).strip()
    ]
    return latest_round(usable)


def check_verdicts(review) -> list[tuple[str, str]]:
    round_number, verdicts = scored_verdicts(review)
    reviewers = {str(entry["reviewer"]).strip() for entry in verdicts}
    failures = []
    if len(reviewers) < 2:
        failures.append(
            (
                "push.verdicts-ge-2",
                f"review round {round_number} carries {len(reviewers)} distinct "
                "reviewer(s) with a readable verdict; two fresh contexts are required.",
            )
        )
    not_passing = [
        f"{entry['reviewer']}={entry['verdict']}"
        for entry in verdicts
        if str(entry["verdict"]) not in PASSING_VERDICTS
    ]
    if not_passing:
        failures.append(
            (
                "push.verdicts-ge-2",
                f"review round {round_number} is not passing: {', '.join(not_passing)}.",
            )
        )
    return failures


REVIEWING_ROLES = {"reviewer", "blind-runner", "adversary"}
DISPATCH_KEYS = ("task", "role", "agent_id", "model", "started")


def parse_dispatch(review) -> tuple[set[str], set[str], str | None]:
    """Split `review["dispatch"]` into implementer and reviewing agent ids.

    §0 is explicit that a FORGED record is out of scope; an absent, empty or
    unreadable one is not -- it makes both identity rules undecidable, and an
    undecidable rule blocks. `fresh_context` is a record field, not a
    recomputable condition (concept-model §7), so nothing here reads it."""
    entries = review.get("dispatch")
    if not isinstance(entries, list) or not entries:
        return set(), set(), (
            "review.json carries no `dispatch` entries; who reviewed and who "
            "implemented cannot be recomputed."
        )
    implementers: set[str] = set()
    reviewers: set[str] = set()
    for number, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            return set(), set(), f"dispatch entry {number} is not an object."
        missing = [key for key in DISPATCH_KEYS if not str(entry.get(key, "")).strip()]
        if missing:
            return set(), set(), (
                f"dispatch entry {number} is missing {', '.join(missing)}; "
                "the record cannot be recomputed."
            )
        agent, role = str(entry["agent_id"]), str(entry["role"])
        if role == "implementer":
            implementers.add(agent)
        elif role in REVIEWING_ROLES:
            reviewers.add(agent)
    return implementers, reviewers, None


def check_reviewer_ne_implementer(review, implementers: set[str], reviewers: set[str],
                                  dispatch_error: str | None):
    if dispatch_error:
        return [("push.reviewer-ne-implementer", dispatch_error)]
    if not reviewers:
        return [
            (
                "push.reviewer-ne-implementer",
                "review.json dispatch[] records no reviewer, blind-runner or adversary.",
            )
        ]
    both = sorted(implementers & reviewers)
    if both:
        return [
            (
                "push.reviewer-ne-implementer",
                f"agent(s) {', '.join(both)} both implemented and reviewed this change.",
            )
        ]
    _round, verdicts = scored_verdicts(review)
    unknown = sorted({str(entry["reviewer"]).strip() for entry in verdicts} - reviewers)
    if unknown:
        return [
            (
                "push.reviewer-ne-implementer",
                f"verdict reviewer(s) {', '.join(unknown)} were never dispatched as "
                "reviewer, blind-runner or adversary in review.json dispatch[].",
            )
        ]
    return []


DISMISSED_BY = re.compile(r"\bby\s+(\S+)\s*$")


def dismissed_by(entry: dict) -> str | None:
    """Who dismissed this finding. `dismissed` may be an object carrying
    `by`, or the prose form concept-model §2e writes,
    `dismissed: "<reason> by <who>"` -- both name the same field."""
    value = entry.get("dismissed")
    if isinstance(value, dict) and str(value.get("by", "")).strip():
        return str(value["by"]).strip()
    if str(entry.get("by", "")).strip():
        return str(entry["by"]).strip()
    if isinstance(value, str):
        match = DISMISSED_BY.search(value.strip())
        if match:
            return match.group(1)
    return None


def check_dismissed_by_reviewer(review, implementers: set[str], reviewers: set[str],
                                dispatch_error: str | None):
    """Only a non-implementing reviewer may wave a finding away
    (concept-model §5); the checker recomputes that from dispatch[]."""
    dismissals = [
        entry
        for entry in review.get("open_findings", [])
        if isinstance(entry, dict) and entry.get("dismissed")
    ]
    if not dismissals:
        return []
    if dispatch_error:
        return [("push.dismissed-by-reviewer", dispatch_error)]
    failures = []
    for entry in dismissals:
        finding = str(entry.get("id", "<no id>"))
        who = dismissed_by(entry)
        if not who:
            failures.append(
                (
                    "push.dismissed-by-reviewer",
                    f"finding {finding} is dismissed but names nobody; write "
                    "`dismissed: \"<reason> by <agent_id>\"`.",
                )
            )
            continue
        if who in implementers or who not in reviewers:
            failures.append(
                (
                    "push.dismissed-by-reviewer",
                    f"finding {finding} was dismissed by {who}, who is not a "
                    "non-implementing reviewer, blind-runner or adversary in dispatch[].",
                )
            )
    return failures


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


COMMANDS = {
    "intent": cmd_intent,
    "intake": cmd_intake,
    "push": cmd_push,
    "standing": cmd_standing,
    "contract": cmd_contract,
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
