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
    loom_checker.py push [--head <ref>] [--base <ref>]
    loom_checker.py standing <path-to-intent>
    loom_checker.py hooks-probe

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
import re
import sys
from pathlib import Path

import yaml

from git_exec import run_git  # sibling module (no __init__.py, no conftest)

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "contract" / "manifest.yaml"

USAGE = __doc__.split("Sub-commands (the CLI contract other stations depend on):", 1)[1]

RULES: list[tuple[str, str]] = [
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
        "push.open-findings-closed",
        "Every open_findings entry in review.json is resolved or dismissed.",
    ),
    (
        "push.probes-package-tests",
        "review.json probes[] records a package-test run for this branch whose result is pass.",
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


def repo_root(start: Path) -> Path:
    """The git work tree holding `start` -- every path rule is relative to it."""
    anchor = start if start.is_dir() else start.parent
    top = run_git(anchor, "rev-parse", "--show-toplevel")
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


def branch_base(repo: Path, base: str | None = None) -> str | None:
    """merge-base with origin/main, else main; None when neither exists."""
    if base:
        return run_git(repo, "rev-parse", base)
    for candidate in ("origin/main", "main"):
        merge_base = run_git(repo, "merge-base", "HEAD", candidate)
        if merge_base:
            return merge_base
    return None


def changed_paths(repo: Path, base: str | None = None) -> set[str]:
    """Everything this branch changed, committed or not -- a claim about a
    diff must be checked against the whole diff, staging area included."""
    paths: set[str] = set()
    merge_base = branch_base(repo, base)
    commands = [
        ("diff", "--name-only", "HEAD"),
        ("diff", "--name-only", "--cached", "HEAD"),
        ("ls-files", "--others", "--exclude-standard"),
    ]
    if merge_base:
        commands.append(("diff", "--name-only", merge_base, "HEAD"))
    for command in commands:
        output = run_git(repo, *command)
        if output:
            paths.update(line for line in output.splitlines() if line.strip())
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
    text = read_text(path)
    front, sections = parse_document(text)
    failures: list[tuple[str, str]] = []

    failures += check_intent_schema(manifest, front, sections)
    failures += check_product_no_identifiers(front, sections)

    reason_failures, needs_design = check_needs_design_reason(front, commit_msg)
    failures += reason_failures

    if needs_design == "no":
        failures += check_needs_design_recompute(repo_root(path), manifest, out)

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


def check_needs_design_reason(front, commit_msg: Path | None):
    """`needs-design` carries a reason, and the intent's commit message
    repeats the line verbatim (concept-model §2b)."""
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
        line = f"needs-design: {raw}"
        if _squeeze(line) not in _squeeze(read_text(commit_msg)):
            return (
                [
                    (
                        "intent.needs-design-reason",
                        f"the commit message does not carry the line `{line}`.",
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


INTAKE_STATIONS = ("write-spec", "write-plan")  # the two stations that accept an intent


def cmd_intake(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    if len(args) < 2:
        raise UsageError("intake needs a station and a change-id.")
    station, change_id = args[0], args[1]
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
    if not status.startswith("confirmed"):
        shown = status or "absent (= open)"
        return report(
            [
                (
                    "intake.confirmed",
                    f"{station} accepts only a confirmed intent; status is {shown}.",
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


def cmd_push(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("push rules land in plan task W0-04")


def cmd_standing(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise NotImplementedError("standing rules land in plan task W0-04")


def cmd_hooks_probe(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    raise UsageError("hooks-probe is reserved and not implemented yet (plan task W0-05)")


COMMANDS = {
    "intent": cmd_intent,
    "intake": cmd_intake,
    "push": cmd_push,
    "standing": cmd_standing,
    "hooks-probe": cmd_hooks_probe,
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
