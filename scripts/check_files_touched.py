#!/usr/bin/env python3
"""Parse a plan's per-task `Files touched` declarations and `done(<sha>)` join keys.

PURPOSE — measurement prototype for the declared-vs-actual `Files touched`
check (docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md):
join each plan task's declared file set to the commit that resolved it, so a
later layer can compare declaration against `git show` reality.

SCOPE — three layers:
  * PARSE: plan markdown in, per-task `(declared_paths, sha_or_None)`
    structures out (`parse_plan` / `parse_plan_text` -> `PlanParse`);
  * VERDICT: pure set arithmetic over (declared, actual, plan_path) per
    rule variant R1/R2/R3 (`verdict_r1/r2/r3`, `evaluate_task`) — variant
    semantics frozen in
    docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md;
  * GIT + CLI: `actual_files(repo, sha)` reads the commit's touched paths
    via `git show --name-only --no-renames --format= <sha>` (`--no-renames`
    is a plan-Kickoff decision: a rename contributes BOTH the old and the
    new path — frozen key cell 8); `main()` joins the layers into a
    per-task per-variant verdict report.

CLI:
  python3 scripts/check_files_touched.py <plan-path>
      [--repo <path>] [--variant R1|R2|R3|all]
  --repo defaults to the current directory; --variant defaults to all.
  At the CLI boundary an ABSOLUTE plan path is reconciled to its
  repo-relative spelling (relative to --repo) before verdicts run — the
  R3 plan-file exclude compares against git's repo-relative actual paths
  and would silently no-op on the absolute spelling.

The exit contract is `EXIT_CONTRACT` below (appended to this docstring at
import time and shown in --help).

Field lines that match a field name but fail to parse are collected into
`PlanParse.parse_errors`, never silently dropped (the citation-checker
empty-pass lesson, source brief §Decision).

IDIOM PROVENANCE — the two parsing idioms are COPIED (not imported) from
loom-code/scripts/check_scenario_coverage.py:58-68:
  * the bold-optional field-line regex (`- **Field**:` and the plain
    `- Field:` form real plans use), field names swapped to
    `Files touched` / `Status`;
  * the section-boundary idiom, adapted one level up: task blocks open at
    `## Task <N>` so the boundary here is the next `## ` heading only —
    `### ` subheadings stay INSIDE a task block, exactly as upstream keeps
    `#### Scenario:` inside a `### Requirement:` scope. The upstream
    limitation carries over unchanged: a `## `-prefixed line inside a
    fenced code block is still mistaken for a real heading (accepted —
    fixture plans must not embed fenced `## Task` lines).

Token normalization (frozen key cell 10,
docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md): strip
surrounding whitespace, backticks, and a leading `./`; a `NEW: <path>`
token (plan-format.md:79) normalizes to the proposed path itself.

Stdlib only (re / dataclasses / pathlib).
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Single source for the CLI exit contract — shown in --help (epilog) and
# appended to the module docstring below.
EXIT_CONTRACT = """\
Exit contract:
  0  every compared task is OK under the selected variant(s); NO_JOIN rows
     report loudly but do not gate while the plan retains >=1 join key
     (documented decision: the un-joinable task never renders OK, and
     gating on it would fail every plan still mid-flight)
  1  at least one task flagged (UNDER or OVER) under a selected variant,
     a done(<sha>) join key that did not resolve in --repo, or >=1 parse
     error — a corrupt ledger line (e.g. `done (sha)`) must never yield
     an all-clear, unlike a well-formed sha-less Status (mid-flight
     pending/claimed/blocked) which stays a non-gating NO_JOIN
  2  loud-empty: the parse yielded 0 tasks, or 0 join keys (no task
     carries Status: done(<sha>)) — a plan with no ledger must never
     produce an all-clear (source brief §Decision); wins over exit 1
"""

__doc__ += "\n" + EXIT_CONTRACT

# `## Task <N>` opens a task block (plan-format.md:45). The id is captured
# as a STRING (group 1), never cast to int: an optional single trailing
# letter (`## Task 3a`, `## Task 3b`) is a real plan shape — a split of an
# original numbered task — and must resolve to its own distinct id rather
# than silently vanish (a letter-suffixed heading that doesn't match this
# pattern still matches `_TASK_BOUNDARY` below and gets swallowed as a
# boundary with zero parse_errors). Multi-letter suffixes (`3ab`) are not
# supported — same fate as before, accepted limitation.
_TASK_HDR = re.compile(r"^##\s+Task\s+(\d+[A-Za-z]?)\b.*$", re.MULTILINE)

# A task block ends at the next level-2 heading (`## Task <M>` or a plan
# section like `## Notes`). `###` is deliberately NOT a boundary — see the
# module docstring's idiom-provenance note.
_TASK_BOUNDARY = re.compile(r"^##\s", re.MULTILINE)

# Bold-optional field lines (idiom copied from check_scenario_coverage.py's
# `_BRIEF_ITEM_LINE`, two deliberate deltas): `(.*)` — not `(.+)` — so an
# empty value still MATCHES the field name and can be reported as a parse
# error instead of vanishing; and the post-colon whitespace is `[ \t]*` —
# not `\s*` — because `\s` matches `\n` and would let an empty-valued line
# capture the NEXT line as its value.
_FILES_TOUCHED_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Files touched(?:\*\*)?\s*:[ \t]*(.*?)[ \t]*$",
    re.MULTILINE)
_STATUS_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Status(?:\*\*)?\s*:[ \t]*(.*?)[ \t]*$", re.MULTILINE)

# Progress-ledger vocabulary (plan-format.md:106): only `done(<sha>)`
# carries a join key; the other three are valid and sha-less.
#
# The optional `(?:\s+.*)?` tail (Task 2, wiring gap 3b) admits a real
# annotated ledger line — docs/loom/plans/2026-07-25-company-total-
# revenue.md:254's `done(c301c7be)  # spec-reviewer PASS; ...` — without
# over-broadening: a tail is only absorbed when it is separated from the
# closing `)` by whitespace, so it stays general (not hard-required to
# start with `#`) while a genuinely sha-less Status (`pending`, `blocked`)
# or a foreign-vocabulary token still falls through to `_STATUS_SHALESS`
# and its parse_error, unchanged.
_STATUS_DONE = re.compile(r"^done\(([0-9a-fA-F]{7,40})\)(?:\s+.*)?$")
_STATUS_SHALESS = re.compile(r"^(?:pending|claimed\(@[^)]+\)|blocked)$")

_NEW_TOKEN_PREFIX = re.compile(r"^NEW\s*:\s*")

# Trailing parenthetical annotation (Task 7) — real shape:
# docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md:24, a
# post-PASS amendment note after the FINAL backticked path. The greedy
# `.*\`` pins group 1 to the LAST backtick in the value, so the rule only
# fires when a backtick-CLOSED token precedes a parenthesized group at END
# of value. Bare (unbackticked) tokens never match — their behavior is
# unchanged, parens inside them are NOT disambiguated.
_TRAILING_PAREN_ANNOTATION = re.compile(r"^(.*`)\s*\(.*\)\s*$")

# A backtick-CLOSED token followed by anything non-blank (after the
# annotation strip above has already run) is malformed — the tail is
# neither path nor sanctioned annotation. Only fires on backticked tokens;
# bare tokens keep their current behavior.
_BACKTICKED_TOKEN_TAIL = re.compile(r"^`[^`]+`\s*\S")


def _is_continuation_line(line: str) -> bool:
    """True when `line` continues a wrapped field value (Task 6).

    A continuation line is an INDENTED line that is not a new `- ` bullet,
    not a heading, and not blank — real wrapped shapes:
    docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md:48-49
    (trailing comma + indented path) and
    docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md Task 10
    (no value on the field line at all). The `- ` exclusion is what keeps a
    following `- Context paths:` bullet — and its indented `- ` sub-items —
    OUT of the declared set.
    """
    if line[:1] not in (" ", "\t"):
        return False
    stripped = line.strip()
    if not stripped or stripped.startswith("- ") or stripped.startswith("#"):
        return False
    return True


@dataclass(frozen=True)
class TaskDeclaration:
    """One task's parsed declaration: normalized declared paths + join key."""
    declared_paths: frozenset[str]
    sha: str | None


@dataclass
class PlanParse:
    """Parse result for one plan: task id (string — plain "3" or
    letter-suffixed "3a"/"3b", see `_TASK_HDR`) -> declaration, plus every
    field line that matched a field name but could not be parsed."""
    tasks: dict[str, TaskDeclaration] = field(default_factory=dict)
    parse_errors: list[str] = field(default_factory=list)


def _normalize_token(token: str) -> str:
    """Normalize one comma-separated `Files touched` token to a bare path.

    Frozen-key cell-10 semantics: strip surrounding whitespace, a `NEW:`
    marker, surrounding backticks, and a leading `./`. Returns "" when
    nothing remains (caller reports that as a parse error).
    """
    token = token.strip()
    token = _NEW_TOKEN_PREFIX.sub("", token)
    token = token.strip().strip("`").strip()
    if token.startswith("./"):
        token = token[2:]
    return token.strip()


def _parse_files_touched(task_no: str, value: str,
                         errors: list[str]) -> frozenset[str]:
    if not value:
        errors.append(
            f"Task {task_no}: 'Files touched' line has no parseable value")
        return frozenset()
    annotated = _TRAILING_PAREN_ANNOTATION.match(value)
    if annotated:
        # Annotation stripped at VALUE level, before the comma-split — its
        # inner characters (em-dash, `§`, even commas) are prose, not tokens.
        value = annotated.group(1)
    paths: set[str] = set()
    for raw in value.split(","):
        token = _NEW_TOKEN_PREFIX.sub("", raw.strip()).strip()
        if _BACKTICKED_TOKEN_TAIL.match(token):
            errors.append(
                f"Task {task_no}: 'Files touched' token {raw.strip()!r} has "
                f"a non-annotation tail after its closing backtick")
            continue
        normalized = _normalize_token(raw)
        if normalized:
            paths.add(normalized)
        else:
            errors.append(
                f"Task {task_no}: 'Files touched' token {raw!r} "
                f"normalizes to nothing")
    return frozenset(paths)


def _parse_status(task_no: str, value: str, errors: list[str]) -> str | None:
    done = _STATUS_DONE.match(value)
    if done:
        return done.group(1)
    if not _STATUS_SHALESS.match(value):
        errors.append(
            f"Task {task_no}: 'Status' value {value!r} is not in the "
            f"ledger vocabulary (pending | claimed(@agent) | done(<sha>) "
            f"| blocked)")
    return None


def parse_plan_text(text: str) -> PlanParse:
    """Parse plan markdown into per-task declarations.

    Returns a `PlanParse` whose `tasks` maps task id (string; plain "3" or
    letter-suffixed "3a"/"3b") -> `TaskDeclaration(declared_paths, sha)`;
    `sha` is None for any task without a `Status: done(<sha>)` line.
    Unreadable field lines land in `parse_errors`. A task block with no
    `Files touched` line at all yields an empty `declared_paths` without a
    parse error — whether that is acceptable is the verdict layer's policy,
    not the parser's.
    """
    result = PlanParse()
    for hdr in _TASK_HDR.finditer(text):
        task_no = hdr.group(1)
        boundary = _TASK_BOUNDARY.search(text, hdr.end())
        block = text[hdr.end():boundary.start() if boundary else len(text)]

        if task_no in result.tasks:
            result.parse_errors.append(
                f"Task {task_no}: duplicate '## Task {task_no}' heading — "
                f"keeping the first block")
            continue

        declared: frozenset[str] = frozenset()
        lines = block.splitlines()
        i = 0
        while i < len(lines):
            match = _FILES_TOUCHED_LINE.match(lines[i])
            i += 1
            if not match:
                continue
            value = match.group(1)
            continuation: list[str] = []
            while i < len(lines) and _is_continuation_line(lines[i]):
                continuation.append(lines[i].strip())
                i += 1
            if continuation:
                # Wrapped value (Task 6): concatenate field value +
                # continuation lines, then comma-split as usual. A trailing
                # comma is list syntax here, not an empty token — only the
                # NO-continuation empty final token stays a parse error.
                value = " ".join(filter(None, [value, *continuation]))
                value = value.rstrip().removesuffix(",")
            declared |= _parse_files_touched(
                task_no, value, result.parse_errors)

        sha: str | None = None
        for match in _STATUS_LINE.finditer(block):
            parsed = _parse_status(task_no, match.group(1), result.parse_errors)
            if parsed is not None:
                if sha is not None:
                    result.parse_errors.append(
                        f"Task {task_no}: multiple 'Status: done(<sha>)' "
                        f"lines — ambiguous join key, keeping the last")
                sha = parsed

        result.tasks[task_no] = TaskDeclaration(declared_paths=declared, sha=sha)
    return result


def parse_plan(path: Path | str) -> PlanParse:
    """Read a plan file and parse it — thin wrapper over `parse_plan_text`."""
    return parse_plan_text(Path(path).read_text(encoding="utf-8"))


# --- Verdict layer (Task 3) — pure set arithmetic, no git calls -------------
#
# Variant semantics are the frozen key's §Rule variants table
# (docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md):
#   R1 strict     — flags any set difference, both directions;
#   R2 under-only — flags only `actual − declared ≠ ∅` (the dangerous
#                   direction; OVER may be legitimate drift);
#   R3            — R2 computed after removing the standing excludes from
#                   the ACTUAL set (the plan file under check, and any path
#                   containing `__pycache__/`).
# A task whose sha is None yields NO_JOIN under every variant, never OK.

OK = "OK"
UNDER = "UNDER"
OVER = "OVER"
NO_JOIN = "NO_JOIN"

VARIANTS = ("R1", "R2", "R3")


@dataclass(frozen=True)
class Verdict:
    """One variant's verdict on one task.

    `under` / `over` carry only the paths THIS variant flags (sorted):
    R2/R3 never populate `over` — their verdict ignores that direction.
    When R1 flags both directions at once, `verdict` carries the dominant
    token UNDER (the dangerous direction — matches the frozen key's cell
    rows, which record one dominant token per cell) while both lists stay
    populated for reporting.
    """
    variant: str
    verdict: str  # OK | UNDER | OVER | NO_JOIN
    under: tuple[str, ...] = ()
    over: tuple[str, ...] = ()


def verdict_r1(declared: frozenset[str], actual: frozenset[str]) -> Verdict:
    """R1 strict: any symmetric difference flags."""
    under = tuple(sorted(actual - declared))
    over = tuple(sorted(declared - actual))
    verdict = UNDER if under else (OVER if over else OK)
    return Verdict(variant="R1", verdict=verdict, under=under, over=over)


def verdict_r2(declared: frozenset[str], actual: frozenset[str]) -> Verdict:
    """R2 under-only: flags only `actual − declared ≠ ∅`."""
    under = tuple(sorted(actual - declared))
    return Verdict(variant="R2", verdict=UNDER if under else OK, under=under)


def _normalize_plan_path(plan_path: Path | str) -> str:
    """Normalize the plan path for the R3 exclude comparison — POSIX
    separators, no leading `./` (Path() collapses it) — the same family of
    rules `_normalize_token` applies to declared tokens."""
    return Path(str(plan_path).strip()).as_posix()


def verdict_r3(declared: frozenset[str], actual: frozenset[str],
               plan_path: Path | str) -> Verdict:
    """R3: R2 after removing the standing excludes from the ACTUAL set.

    Exactly two exclude classes (frozen key §Rule variants): the plan file
    under check (normalized-path comparison), and any path containing
    `__pycache__/`. Nothing else — regenerated functional copies and
    manifest mirrors are under-declaration TARGETS, never excludes.
    """
    plan_norm = _normalize_plan_path(plan_path)
    kept = frozenset(
        p for p in actual
        if _normalize_plan_path(p) != plan_norm and "__pycache__/" not in p)
    under = tuple(sorted(kept - declared))
    return Verdict(variant="R3", verdict=UNDER if under else OK, under=under)


def evaluate_task(declaration: TaskDeclaration,
                  actual_paths: frozenset[str] | None,
                  plan_path: Path | str) -> dict[str, Verdict]:
    """Run all three variants on one task; the seam Task 4's CLI calls.

    A declaration with no join key (`sha is None`) yields NO_JOIN under
    every variant — never OK (frozen key cell 7); `actual_paths` is
    ignored in that case because nothing joins the task to a commit.
    """
    if declaration.sha is None:
        return {v: Verdict(variant=v, verdict=NO_JOIN) for v in VARIANTS}
    actual = frozenset(actual_paths or ())
    declared = declaration.declared_paths
    return {
        "R1": verdict_r1(declared, actual),
        "R2": verdict_r2(declared, actual),
        "R3": verdict_r3(declared, actual, plan_path),
    }


# --- Git layer + CLI (Task 4) ------------------------------------------------

def actual_files(repo: Path | str, sha: str) -> frozenset[str]:
    """Repo-relative paths touched by commit `sha`.

    Runs `git show --name-only --no-renames --format= <sha>`. The
    `--no-renames` flag is the plan-Kickoff decision (plan §Notes): with
    default rename detection `--name-only` prints only the rename's NEW
    path, but the old path's deletion still collides with a sibling task
    touching it — the disjointness oracle needs BOTH sides (frozen key
    cell 8). Raises `subprocess.CalledProcessError` when the sha does not
    resolve; the CLI reports that loudly, never as an all-clear.
    """
    out = subprocess.run(
        ["git", "-C", str(repo), "show", "--name-only", "--no-renames",
         "--format=", sha],
        check=True, capture_output=True, text=True).stdout
    return frozenset(line for line in out.splitlines() if line)


def _repo_relative_plan_path(plan_arg: Path, repo: Path) -> str:
    """Reconcile the CLI's plan-path spelling to repo-relative.

    The R3 plan-file exclude compares against git's repo-relative actual
    paths, so an ABSOLUTE plan argument must be re-spelled relative to
    --repo or the exclude silently no-ops (Task-3 reviewer seam). A plan
    outside --repo keeps its given spelling — it cannot appear in a commit
    of that repo anyway.
    """
    try:
        return plan_arg.resolve().relative_to(repo).as_posix()
    except ValueError:
        return plan_arg.as_posix()


def _task_sort_key(task_id: str) -> tuple[int, str]:
    """Numeric-then-letter sort key for a task id (Task 1: ids became
    strings so `## Task 3a`/`3b` can parse). Plain `sorted(parse.tasks)`
    would sort lexicographically ("10" before "2"); this key keeps the
    reported order matching plan order — numeric part first, then the
    optional trailing letter ("3" < "3a" < "3b" < "4" < "10"). A task id
    that doesn't match the plain/letter-suffixed shape (should not occur —
    `_TASK_HDR` only ever captures that shape) sorts last, by string, rather
    than raising.
    """
    m = re.match(r"^(\d+)([A-Za-z]?)$", task_id)
    if not m:
        return (10**9, task_id)
    return (int(m.group(1)), m.group(2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Compare each plan task's declared `Files touched` "
                     "set against the files its done(<sha>) commit "
                     "actually touched, under rule variants R1/R2/R3."),
        epilog=EXIT_CONTRACT,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan_path", help="plan markdown file to check")
    parser.add_argument("--repo", default=".",
                        help="git repository the shas resolve in "
                             "(default: current directory)")
    parser.add_argument("--variant", choices=[*VARIANTS, "all"],
                        default="all",
                        help="rule variant to report (default: all)")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    plan_rel = _repo_relative_plan_path(Path(args.plan_path), repo)

    parse = parse_plan(args.plan_path)
    for err in parse.parse_errors:
        print(f"parse-error: {err}", file=sys.stderr)

    if not parse.tasks:
        print(f"EMPTY: 0 tasks parsed from {args.plan_path} — refusing to "
              f"report an all-clear on an empty parse", file=sys.stderr)
        return 2
    if all(decl.sha is None for decl in parse.tasks.values()):
        print(f"EMPTY: 0 join keys — no task in {args.plan_path} carries "
              f"Status: done(<sha>); nothing joins the plan to commits",
              file=sys.stderr)
        return 2

    variants = VARIANTS if args.variant == "all" else (args.variant,)
    flagged = False
    for task_no in sorted(parse.tasks, key=_task_sort_key):
        decl = parse.tasks[task_no]
        actual: frozenset[str] | None = None
        if decl.sha is not None:
            try:
                actual = actual_files(repo, decl.sha)
            except subprocess.CalledProcessError as exc:
                print(f"Task {task_no}: join key {decl.sha} did not resolve "
                      f"in {repo}: {exc.stderr.strip()}", file=sys.stderr)
                flagged = True
                continue
        verdicts = evaluate_task(decl, actual, plan_rel)
        for variant in variants:
            verdict = verdicts[variant]
            line = f"Task {task_no} [{variant}] {verdict.verdict}"
            if verdict.verdict == NO_JOIN:
                line += "  (no done(<sha>) join key — never OK)"
            if verdict.under:
                line += "  under: " + ", ".join(verdict.under)
            if verdict.over:
                line += "  over: " + ", ".join(verdict.over)
            print(line)
            if verdict.verdict in (UNDER, OVER):
                flagged = True
    # Parse errors gate an otherwise-clean run (exit contract): a corrupt
    # ledger line means some declaration/join key was unreadable, so an
    # all-clear would be unearned. The exit-2 checks above still win.
    return 1 if (flagged or parse.parse_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
