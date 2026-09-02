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

import json
import os
import re
import shlex
import subprocess
import sys
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
        "A consumer plugin's requires-contract floor is met by this contract manifest version.",
    ),
    (
        "intake.confirmed",
        "write-spec / write-plan accept only an intent whose status line reads `confirmed <date>`.",
    ),
    (
        "intake.confirmed-behavior",
        "write-plan accepts a product change only when its spec carries a `confirmed-behavior: <date>` line.",
    ),
    (
        "intake.spec-pass",
        "write-plan accepts a needs-design: yes change only when the latest spec review round is all PASS or PASS_WITH_NOTES.",
    ),
    (
        "intent.needs-design-reason",
        "The needs-design line carries a reason and the same line appears verbatim in the intent's commit message.",
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
        "push.dismissed-by-reviewer",
        "Every dismissed finding names a dispatch reviewer, blind-runner or adversary who never implemented it.",
    ),
    (
        "push.open-findings-closed",
        "Every open_findings entry in review.json is resolved or dismissed.",
    ),
    (
        "push.probes-package-tests",
        "review.json probes[] records a package-test run for this branch whose result is pass.",
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
        "push.reviewer-ne-implementer",
        "No reviewer, blind-runner or adversary in the dispatch record also implemented the change.",
    ),
    (
        "push.verdicts-ge-2",
        "The latest review round carries at least two distinct fresh-context reviewers.",
    ),
    (
        "standing.product-principles-reject",
        "A product change is rejected while the repo has no ratified PRINCIPLES.md.",
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
    declared = kickoff_defaults(repo).get("interface-surfaces")
    if declared:
        return [part.strip() for part in declared.split(",") if part.strip()], (
            "docs/loom/KICKOFF-DEFAULTS.md"
        )
    for entry in manifest.get("kickoff_defaults", []):
        if entry.get("name") == "interface-surfaces":
            return [part.strip() for part in entry["default"].split(",")], "manifest default"
    raise UsageError("the contract manifest declares no interface-surfaces default.")


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


def branch_base(repo: Path) -> str:
    """The commit this branch grew from. An unresolvable base is fatal:
    the alternative -- diffing against nothing and seeing no changes --
    turns every diff-recomputing rule into a silent pass."""
    for candidate in TRUNK_CANDIDATES:
        merge_base = git_maybe(repo, "merge-base", "HEAD", candidate)
        if merge_base:
            return merge_base
    raise UsageError(
        "no branch base resolves in "
        f"{repo} (tried {', '.join(TRUNK_CANDIDATES)}); the diff cannot be recomputed."
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
    failures += check_product_no_identifiers(front, sections)

    reason_failures, needs_design = check_needs_design_reason(front, commit_msg, repo)
    failures += reason_failures

    if needs_design == "no":
        failures += check_needs_design_recompute(repo, manifest, out)

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


def check_product_no_identifiers(front, sections) -> list[tuple[str, str]]:
    """A product Problem is written for the person with the problem: it may
    not name the code that will change (concept-model §2b)."""
    if front.get("kind", "").strip() != "product":
        return []
    problem = sections.get("Problem", "")
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


def check_needs_design_reason(front, commit_msg: Path | None, repo: Path):
    """`needs-design` carries a reason, and the intent's commit message
    repeats the line verbatim (concept-model §2b). With no `--commit-msg`
    (the post-commit and station calls) the message is HEAD's own, read
    from git -- the check is never skipped for want of a flag."""
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
        message, source = git_text(repo, "log", "-1", "--format=%B"), "HEAD"
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


def check_needs_design_recompute(repo: Path, manifest, out) -> list[tuple[str, str]]:
    """`needs-design: no` is a claim; the diff is the fact."""
    globs, source = interface_surfaces(repo, manifest)
    out.write(f"interface-surfaces ({source}): {', '.join(globs)}\n")
    matchers = [glob_to_regex(pattern) for pattern in globs]
    touched = sorted(
        path
        for path in changed_paths(repo)
        if any(matcher.match(path) for matcher in matchers)
    )
    if not touched:
        return []
    return [
        (
            "intent.needs-design-recompute",
            "`needs-design: no` but the diff touches a declared interface "
            f"surface: {', '.join(touched[:5])}.",
        )
    ]


CHANGE_ID = re.compile(r"[A-Za-z0-9._-]+")
CONFIRMED = re.compile(r"confirmed \d{4}-\d{2}-\d{2}(\s+#.*)?")

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
    front, _sections = parse_document(read_text(intent_path))

    status = front.get("status", "").strip()
    if not CONFIRMED.fullmatch(status):
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

    failures: list[tuple[str, str]] = []
    needs_design = front.get("needs-design", "").strip().split()[:1]
    if station == "write-plan" and needs_design[:1] == ["yes"]:
        failures += check_spec_pass(manifest, repo, change_id)
        if front.get("kind", "").strip() == "product":
            failures += check_confirmed_behavior(manifest, repo, change_id)
    return report(failures, err)


def check_spec_pass(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
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
    if "spec" not in str(review.get("scope", "")).lower():
        return [("intake.spec-pass", "review.json scope does not cover the spec.")]
    round_number, verdicts = latest_round(review.get("verdicts", []))
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
    if not any(str(probe.get("kind")) == "adversarial" for probe in review.get("probes", [])):
        return [
            (
                "intake.spec-pass",
                "no `adversarial` probe recorded for the spec; the spec lens is "
                "read + adversarial, and only the read half ran.",
            )
        ]
    return []


def check_confirmed_behavior(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
    """Decision point ② leaves exactly one trace: the spec's
    `confirmed-behavior:` line (concept-model §2c)."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # already reported by intake.spec-pass
    front, _ = parse_document(read_text(spec_path))
    if not front.get("confirmed-behavior", "").strip():
        return [
            (
                "intake.confirmed-behavior",
                "kind: product but the spec has no `confirmed-behavior: <date>` line; "
                "decision point ② has not happened.",
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
    failures += check_verdicts(review)

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
    listing = git_text(repo, "show", "--name-only", "--pretty=format:", head_sha)
    touched = sorted({line for line in listing.splitlines() if line.strip()})
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


PROBE_TIMEOUT = 1800  # 30 minutes: a package suite that never ends is a fail


def check_probes_package_tests(repo: Path, review, reviewed_id: str | None,
                               out=sys.stdout):
    """A recorded test run is not evidence -- the RUN is. The record only
    says which commit was tested and what to type; the checker then types it
    itself in a clean tree that is the reviewed tree, and the exit code it
    observes decides (concept-model §7). The agent's own `result` is kept as
    a record and never believed."""
    reasons: list[str] = []
    for probe in review.get("probes", []):
        if not isinstance(probe, dict) or str(probe.get("kind")) != "package-tests":
            continue
        command = str(probe.get("command", "")).strip()
        label = command or "<no command>"
        if not command:
            reasons.append("a package-tests probe records no command")
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
        try:
            observed = subprocess.run(
                command, shell=True, cwd=str(repo), capture_output=True,
                text=True, timeout=PROBE_TIMEOUT,
            ).returncode
        except subprocess.TimeoutExpired:
            reasons.append(f"`{label}` did not finish within {PROBE_TIMEOUT}s")
            continue
        out.write(
            f"package-tests `{label}`: observed exit code {observed} "
            f"(recorded result: {probe.get('result')!r})\n"
        )
        if observed != 0:
            reasons.append(f"`{label}` exited {observed} when the checker ran it")
            continue
        return []
    detail = "; ".join(reasons) if reasons else "no package-tests probe recorded at all"
    return [("push.probes-package-tests", f"no usable package-tests probe: {detail}.")]


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


RATIFIED_BY = re.compile(r"^ratified-by:\s*\S.*$", re.MULTILINE)
NON_NEGOTIABLES = re.compile(r"^##\s+non-negotiables\b", re.IGNORECASE)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
MIN_NON_NEGOTIABLES = 3


def unratified_reason(text: str) -> str | None:
    """Ratified is two things, not one (concept-model §8): the signature
    line AND a Non-negotiables section with something in it. A signature over
    an empty document ratifies nothing, so the section is counted here."""
    if not RATIFIED_BY.search(text):
        return "carries no `ratified-by: <name> <date>` line"
    items, inside = 0, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = bool(NON_NEGOTIABLES.match(line))
            continue
        if inside and LIST_ITEM.match(line):
            items += 1
    if items < MIN_NON_NEGOTIABLES:
        return (
            "has no `## Non-negotiables` section carrying at least "
            f"{MIN_NON_NEGOTIABLES} list items (found {items})"
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
