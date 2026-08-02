"""Gate-marker CLI for loom-code's mechanical push gates.

The SDD orchestrator runs this to mint the markers that
`hooks/git-guard.py` (built in parallel on this branch) reads before
allowing a push. Marker contract (frozen; every field asserted by
`test_loom_gate_markers.py`):

Dir: `<git-dir>/loom/` resolved via `git rev-parse --git-dir` from
`--repo` (default cwd); created if missing.

- `review-pass.json`  {"schema": 1, "branch", "head_sha", "verdict",
  "written_at", optional "base_sha"/"patch_id"} — written ONLY after
  the reviewer's verdict text passes schema validation (the audit's
  schema gate: a marker can only exist if a schema-valid verdict text
  exists). NEEDS_REVISION never mints a marker (exit 3); a malformed
  verdict never mints one either (exit 4, missing keys listed).
- `verified.json`     {"schema": 1, "head_sha", "run_cmd", "exit_code",
  "output_tail", "written_at", optional "base_sha"/"patch_id"} — minted
  ONLY after `--run "<cmd>"` actually executes in `--repo` and exits 0;
  records the command run + a bounded tail of its captured output. This
  is auditability, NOT unforgeability: an agent can still pass
  `--run "true"` and mint a marker with no real suite behind it. The
  bar is raised from "type any string" to "a real command must run and
  exit 0, and is recorded" — local execution cannot cryptographically
  prove a genuine suite ran.
- `base_sha`/`patch_id` (both markers, both optional): merge-base with
  the default branch and `git diff base..HEAD | git patch-id --stable`
  at write time, recorded ONLY when every step resolves (default
  branch found, merge-base succeeds, diff+patch-id subprocesses
  succeed, output non-empty). Any failure omits BOTH fields — never a
  partial pair — so `hooks/git-guard.py` falls back to strict
  `head_sha` equality. Lets a message-only amend or a
  content-preserving rebase keep passing the push gate without a
  fresh review (see `compute_patch_id`).
- `waiver.json`       {"schema": 1, "scope": "push", "reason",
  "written_at"} — requires a real justification (>= 10 chars) and
  shouts on stderr that the review gate is being bypassed one-shot.

Exit codes: 0 marker written; 2 not a git repo; 3 NEEDS_REVISION
verdict; 4 malformed/nonconforming input. Writes are atomic
(tmp file + os.replace); existing markers are overwritten silently
(latest wins).

`validate --verdict-file <path> [--suite-line "<text>"]` is a
dry-run of the exact same schema checks, but reports EVERY violation
in one pass instead of exiting on the first (today's writers exit-4
on the first problem, forcing a fix/rerun/fix retry loop). Writes
nothing; takes no `--repo` (no marker write, no HEAD resolution
needed). Exit 0 when clean, 4 when any violation is found.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_VERDICTS = {"PASS", "PASS_WITH_NOTES", "NEEDS_REVISION"}
MIN_WAIVER_REASON_CHARS = 10

# NOTE: value-capturing regexes use [^\S\n]* (horizontal whitespace),
# not \s*, after the colon — under re.M, \s* spans the newline and
# wrongly captures the NEXT line as the value of an empty key.
_KEY_RE = {
    "standards_version": re.compile(
        r"^\s*standards_version:[^\S\n]*(\S.*)$", re.M
    ),
    "verdict": re.compile(r"^\s*verdict:[^\S\n]*([A-Z_]+)[^\S\n]*$", re.M),
    "dimension_scores": re.compile(r"^\s*dimension_scores:", re.M),
}
_FINDING_RE = re.compile(r"^\s*-\s*severity\s*:")
_WHERE_RE = re.compile(r"^\s*where\s*:[^\S\n]*(\S.*)$")
_DIMENSION_RE = re.compile(r"^\s*dimension\s*:[^\S\n]*(.*)$")
_ORIGIN_RE = re.compile(r"^\s*origin\s*:[^\S\n]*(.*)$")
_INDENT_RE = re.compile(r"^[ \t]*")

# §Pinned dimension partition (verified disjoint 2026-08-02). A finding
# whose `dimension:` both parses and falls in the docs-arm set is
# exempt from `origin:`; everything else — code-arm, unrecognized, or
# unparseable (absent/empty) — requires it (fail closed, see
# `_origin_required`).
_CODE_ARM_DIMENSIONS = {
    "security", "architecture", "correctness", "naming", "tests",
    "refactoring", "cross-task-coherence", "external-surface-grounding",
    "principles-conformance", "deliberate-simplification",
}
_DOCS_ARM_DIMENSIONS = {
    "omission", "ambiguity", "inconsistency", "incorrect-fact",
    "missing-population",
}


def _check_arm_disjoint(code_arm: set[str], docs_arm: set[str]) -> None:
    """Raise if `code_arm` and `docs_arm` share any dimension name.

    Makes the pin's "verified disjoint" claim load-bearing rather than
    a comment: a future edit that lets a dimension into both sets would
    make `_origin_required`'s docs-arm lookup ambiguous. Not an `assert`
    statement — those are stripped under `python -O`, and this check
    must still fire then."""
    overlap = code_arm & docs_arm
    if overlap:
        raise AssertionError(
            "_CODE_ARM_DIMENSIONS and _DOCS_ARM_DIMENSIONS overlap on "
            f"{sorted(overlap)} — §Pinned dimension partition requires "
            "them disjoint"
        )


_check_arm_disjoint(_CODE_ARM_DIMENSIONS, _DOCS_ARM_DIMENSIONS)
_TOP_KEY_RE = re.compile(r"^\S+\s*:")
_PASSED_RE = re.compile(r"(\d+) passed")
# where: value counts as location-like if it has a path separator /
# extension dot, or is a bare commit SHA (reviewer output contract
# allows `where: <commit SHA>`).
_PATHLIKE_RE = re.compile(r"[/.]|\b[0-9a-f]{7,40}\b")
# Word-boundary so green "2 xfailed" summaries don't trip the filter
# while "3 failed" / "1 error" still do.
_SUITE_REJECT_RE = re.compile(r"\b(failed|errors?)\b")


def _git(repo: Path, *args: str) -> str | None:
    """Run git in `repo`; return stripped stdout, or None on any failure."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _default_branch_ref(repo: Path) -> str | None:
    """Best-effort default-branch ref for merge-base computation.

    Tries origin/HEAD's symbolic ref, then local `main`, then local
    `master`. Returns None when none resolve — callers then omit the
    patch-id fields entirely (fail-closed: the fallback never activates
    for that marker; strict head_sha equality remains the only path).
    """
    origin_head = _git(repo, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")
    if origin_head:
        ref = origin_head.removeprefix("refs/remotes/")
        if _git(repo, "rev-parse", "--verify", "-q", ref) is not None:
            return ref
    for candidate in ("main", "master"):
        if _git(repo, "rev-parse", "--verify", "-q", candidate) is not None:
            return candidate
    return None


def compute_patch_id(repo: Path) -> tuple[str, str] | None:
    """(base_sha, patch_id) for merge-base(default-branch, HEAD)..HEAD.

    Returns None on ANY resolution/subprocess/parse failure — the two
    fields are then simply omitted from the marker (fail-closed: a
    missing pair means the patch-id fallback never activates; strict
    head_sha equality is the only path `git-guard.py` can take).
    """
    ref = _default_branch_ref(repo)
    if ref is None:
        return None
    base_sha = _git(repo, "merge-base", ref, "HEAD")
    if base_sha is None:
        return None
    try:
        diff = subprocess.run(
            ["git", "-C", str(repo), "diff", f"{base_sha}..HEAD"],
            capture_output=True,
            text=True,
        )
        if diff.returncode != 0:
            return None
        patch_id_result = subprocess.run(
            ["git", "-C", str(repo), "patch-id", "--stable"],
            input=diff.stdout,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if patch_id_result.returncode != 0 or not patch_id_result.stdout.strip():
        return None
    return base_sha, patch_id_result.stdout.split()[0]


def resolve_marker_dir(repo: Path) -> Path | None:
    """Return `<git-dir>/loom` for `repo`, or None if not a git repo."""
    git_dir = _git(repo, "rev-parse", "--git-dir")
    if git_dir is None:
        return None
    git_path = Path(git_dir)
    if not git_path.is_absolute():
        git_path = repo / git_path
    return git_path / "loom"


def _write_marker(marker_dir: Path, name: str, payload: dict) -> Path:
    """Atomically write `payload` as JSON to `marker_dir/name`; return path."""
    marker_dir.mkdir(parents=True, exist_ok=True)
    path = marker_dir / name
    fd, tmp = tempfile.mkstemp(dir=str(marker_dir), prefix=name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_verdict_text(text: str) -> tuple[str | None, list[str]]:
    """Validate reviewer verdict text against the schema gate.

    Returns (verdict_value, problems). `verdict_value` is None unless a
    well-formed verdict line with an allowed value was found. `problems`
    is empty iff the text is schema-valid (verdict value included).
    Tolerant line-regex matching — the input is YAML-ish, not strict YAML.
    """
    problems: list[str] = []

    sv = _KEY_RE["standards_version"].search(text)
    if not sv:
        problems.append("standards_version: missing or empty")

    verdict: str | None = None
    vm = _KEY_RE["verdict"].search(text)
    if not vm:
        problems.append("verdict: missing")
    elif vm.group(1) not in ALLOWED_VERDICTS:
        problems.append(
            f"verdict: invalid value {vm.group(1)!r} "
            f"(allowed: {', '.join(sorted(ALLOWED_VERDICTS))})"
        )
    else:
        verdict = vm.group(1)

    if not _KEY_RE["dimension_scores"].search(text):
        problems.append("dimension_scores: block missing")

    problems.extend(_finding_problems(text))
    return verdict, problems


def _origin_required(dimension_value: str | None) -> bool:
    """True unless `dimension_value` both parses and is in the docs-arm
    set. The requirement is the default; the docs-arm exemption is the
    only branch that returns False — an absent (`None`), empty/
    whitespace-only, or unrecognized value all require `origin:`
    (§Pinned dimension partition, fail-closed clause)."""
    if dimension_value is None:
        return True
    value = dimension_value.strip()
    if not value:
        return True
    return value not in _DOCS_ARM_DIMENSIONS


def _origin_grammar_problem(origin_value: str | None) -> str | None:
    """None if `origin_value` is `none` or `<path> :: "<quote>"`; else a
    description of the violation. Grammar only — the quote is not
    checked against any file here (Task 2). Split on the FIRST ` :: `:
    a path may not contain it, a quote may — so the first occurrence is
    the boundary (§Notes kickoff decision, corrected 2026-08-02: the
    earlier "split on the LAST ` :: `" mis-parsed a quote containing the
    separator into a truncated path and an unquoted remainder). No
    backslash-escape convention. The quote's interior must be non-blank:
    `""` and `"   "` are refused — an empty quote is not a verbatim
    quote, and Task 2 verifies by substring, so an empty quote would
    match every file and pass the whole gate as a well-formed origin."""
    if origin_value is None:
        return "no origin: line"
    value = origin_value.strip()
    if value == "none":
        return None
    idx = value.find(" :: ")
    if idx == -1:
        return f"origin: {origin_value!r} is not 'none' or '<path> :: \"<quote>\"'"
    # `path` is always non-empty here: `value` is already stripped (so
    # value[0] is non-whitespace) and the separator starts with a space,
    # so idx can never be 0 — value[:idx] always contains value[0].
    path, quote = value[:idx], value[idx + 4 :]
    if len(quote) < 2 or quote[0] != '"' or quote[-1] != '"':
        return f"origin: {origin_value!r} quote is not fully quoted"
    if not quote[1:-1].strip():
        return f"origin: {origin_value!r} quote is empty or blank"
    return None


def _finding_problems(text: str) -> list[str]:
    """Every `- severity:` finding block must carry a path-like `where:`,
    and — unless its `dimension:` both parses and falls in the docs-arm
    set — an `origin:` line valued `none` or `<path> :: "<quote>"`
    (§Pinned dimension partition; requirement is the default, the
    docs-arm exemption is the explicit branch)."""
    lines = text.splitlines()
    problems: list[str] = []
    starts = [i for i, line in enumerate(lines) if _FINDING_RE.match(line)]
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        # A dedented top-level key also terminates the block.
        for j in range(start + 1, end):
            if _TOP_KEY_RE.match(lines[j]):
                end = j
                break
        where_ok = False
        dimension_values: list[str] = []
        origin_values: list[str] = []
        # Sibling fields (where:/dimension:/origin:) must sit at the SAME
        # column as the first NON-BLANK line following `- severity:` — not
        # at any indentation. A line nested deeper (e.g. inside a `note: |`
        # block-literal that happens to quote `dimension: ...` from a
        # pasted verdict-schema example) is content, not a sibling field,
        # and must not be read as one. The column is whatever indent the
        # block actually uses (never a hardcoded width), so a well-formed
        # finding indented at 6 spaces mints exactly like one at 4. A blank
        # line right after `- severity:` is ordinary formatting, not a
        # signal — it is skipped when hunting for the column.
        column = None
        for line in lines[start + 1 : end]:
            if line.strip():
                column = _INDENT_RE.match(line).group(0)
                break
        if column is not None:
            for line in lines[start + 1 : end]:
                if _INDENT_RE.match(line).group(0) != column:
                    continue
                wm = _WHERE_RE.match(line)
                if wm and _PATHLIKE_RE.search(wm.group(1)):
                    where_ok = True
                dm = _DIMENSION_RE.match(line)
                if dm:
                    dimension_values.append(dm.group(1))
                om = _ORIGIN_RE.match(line)
                if om:
                    origin_values.append(om.group(1))
        if not where_ok:
            problems.append(
                f"finding at line {start + 1}: no where: line with a "
                "path-like token in its block"
            )
        # Two or more `dimension:` (or `origin:`) lines in one block is
        # malformed: YAML readers disagree on which value wins (first vs
        # last), so a duplicate is treated as unparseable rather than
        # resolved either way — fail closed, same direction as the rest
        # of this predicate (§Pinned dimension partition, fail-closed
        # clause).
        dimension_value = dimension_values[0] if len(dimension_values) == 1 else None
        if len(origin_values) > 1:
            problems.append(
                f"finding at line {start + 1}: duplicate origin: lines "
                "(exactly one is required)"
            )
        elif _origin_required(dimension_value):
            origin_value = origin_values[0] if origin_values else None
            origin_problem = _origin_grammar_problem(origin_value)
            if origin_problem:
                problems.append(f"finding at line {start + 1}: {origin_problem}")
    return problems


def _cmd_review_pass(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"loom-gate-markers: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    verdict, problems = validate_verdict_text(text)
    if problems:
        print(
            "loom-gate-markers: verdict text failed schema validation; "
            "no marker written:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 4
    if verdict == "NEEDS_REVISION":
        print(
            "loom-gate-markers: verdict is NEEDS_REVISION — a failed review "
            "does not mint a pass marker.",
            file=sys.stderr,
        )
        return 3

    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    head_sha = _git(repo, "rev-parse", "HEAD")
    if branch is None or head_sha is None:
        print("loom-gate-markers: cannot resolve HEAD.", file=sys.stderr)
        return 2
    payload = {
        "schema": 1,
        "branch": branch,
        "head_sha": head_sha,
        "verdict": verdict,
        "written_at": _now_iso(),
    }
    patch_id_fields = compute_patch_id(repo)
    if patch_id_fields is not None:
        payload["base_sha"], payload["patch_id"] = patch_id_fields
    path = _write_marker(marker_dir, "review-pass.json", payload)
    print(path)
    return 0


def validate_suite_line(line: str) -> list[str]:
    """All problems with `line` as a green pytest-style summary; []
    when clean. Used only by `_cmd_validate` (the dry-run text check).
    The `verified` WRITE path no longer accepts a self-typed suite line —
    it executes a real command via `run_verification` instead."""
    problems: list[str] = []
    m = _PASSED_RE.search(line)
    if not m or int(m.group(1)) == 0:
        problems.append(
            f'suite_line: {line!r} has no "N passed" (N > 0) — not a green run'
        )
    if _SUITE_REJECT_RE.search(line.lower()):
        problems.append(
            f"suite_line: {line!r} contains a failed/error token — not a green run"
        )
    return problems


# Bounded tail of the verification run's combined stdout+stderr, recorded
# in the marker for a human/auditor to inspect. 4 KB is enough to carry a
# pytest summary line plus context without bloating the marker file.
VERIFY_OUTPUT_TAIL_CHARS = 4000


def run_verification(repo: Path, command: str) -> tuple[int, str]:
    """Execute `command` in `repo` via the shell; return (exit_code,
    output_tail) where output_tail is the last VERIFY_OUTPUT_TAIL_CHARS
    chars of combined stdout+stderr. A launch failure (OSError) is
    reported as a non-zero exit so the caller mints no marker.

    HONEST RESIDUAL (do not over-claim): this binds the `verified` marker
    to a command that really ran and really exited 0, and records that
    command — but it is NOT cryptographic proof a genuine test suite ran.
    An agent can still pass `--run "true"`. This raises the bar from
    "type a suite-line string" (zero execution) to "a real command must
    run and exit 0, and is recorded for auditability"; local execution
    cannot guarantee more."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return 1, f"loom-gate-markers: could not launch --run command: {exc}"
    combined = (result.stdout or "") + (result.stderr or "")
    return result.returncode, combined[-VERIFY_OUTPUT_TAIL_CHARS:]


def _cmd_verified(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    command = args.run
    exit_code, output_tail = run_verification(repo, command)
    if exit_code != 0:
        print(
            f"loom-gate-markers: verification command exited {exit_code} "
            f"(not a green run); no marker written. Command: {command!r}",
            file=sys.stderr,
        )
        return 4

    head_sha = _git(repo, "rev-parse", "HEAD")
    if head_sha is None:
        print("loom-gate-markers: cannot resolve HEAD.", file=sys.stderr)
        return 2
    payload = {
        "schema": 1,
        "head_sha": head_sha,
        "run_cmd": command,
        "exit_code": exit_code,
        "output_tail": output_tail,
        "written_at": _now_iso(),
    }
    patch_id_fields = compute_patch_id(repo)
    if patch_id_fields is not None:
        payload["base_sha"], payload["patch_id"] = patch_id_fields
    path = _write_marker(marker_dir, "verified.json", payload)
    print(path)
    return 0


def _cmd_waiver(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    reason = args.reason.strip()
    if len(reason) < MIN_WAIVER_REASON_CHARS:
        print(
            "loom-gate-markers: waiver reason must be a real justification "
            f"(>= {MIN_WAIVER_REASON_CHARS} chars); no marker written.",
            file=sys.stderr,
        )
        return 4

    path = _write_marker(
        marker_dir,
        "waiver.json",
        {
            "schema": 1,
            "scope": "push",
            "reason": args.reason,
            "written_at": _now_iso(),
        },
    )
    print(
        "loom-gate-markers: WARNING — waiver written. This BYPASSES the "
        "review gate for the next push (one-shot). Reason recorded: "
        f"{args.reason}",
        file=sys.stderr,
    )
    print(path)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Dry-run schema check: same rules `review-pass`/`verified` apply
    at write time, but reports EVERY violation in one pass instead of
    exiting on the first (today's writers exit-4 on the first problem,
    forcing a fix-rerun-fix retry loop). Writes nothing; needs no repo."""
    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"loom-gate-markers: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    _, problems = validate_verdict_text(text)
    if args.suite_line is not None:
        problems += validate_suite_line(args.suite_line)

    if problems:
        print("loom-gate-markers: validation found problems:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 4
    print("loom-gate-markers: clean — no violations found.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry: `review-pass --verdict-file <path>` /
    `verified --run "<cmd>"` / `waiver --reason "<text>"` /
    `validate --verdict-file <path> [--suite-line "<text>"]`,
    each of the first three with optional `--repo <path>` (default
    cwd). `validate` is a dry-run text check — no repo, no marker
    write — so it takes no `--repo`."""
    parser = argparse.ArgumentParser(
        description="Write loom gate markers for hooks/git-guard.py"
    )
    # --repo lives ONLY on the subparsers (post-subcommand position).
    # Defining it on the parent too is a silent-wrong-repo trap: argparse
    # subparser defaults clobber the parent-parsed value, so
    # `--repo /x review-pass ...` would fall back to cwd. The
    # pre-subcommand form now fails loudly (unrecognized argument).
    subparsers = parser.add_subparsers(dest="command", required=True)

    rp = subparsers.add_parser("review-pass")
    rp.add_argument("--repo", default=".", help="repo path (default: cwd)")
    rp.add_argument("--verdict-file", required=True)
    rp.set_defaults(func=_cmd_review_pass)

    vf = subparsers.add_parser("verified")
    vf.add_argument("--repo", default=".", help="repo path (default: cwd)")
    vf.add_argument(
        "--run",
        required=True,
        help="verification command to execute in --repo; the marker is "
        "minted ONLY if it exits 0 (records the command + output tail)",
    )
    vf.set_defaults(func=_cmd_verified)

    wv = subparsers.add_parser("waiver")
    wv.add_argument("--repo", default=".", help="repo path (default: cwd)")
    wv.add_argument("--reason", required=True)
    wv.set_defaults(func=_cmd_waiver)

    vd = subparsers.add_parser("validate")
    vd.add_argument("--verdict-file", required=True)
    vd.add_argument("--suite-line", default=None)

    args = parser.parse_args(argv)
    if args.command == "validate":
        return _cmd_validate(args)
    repo = Path(args.repo)
    marker_dir = resolve_marker_dir(repo)
    if marker_dir is None:
        print(f"loom-gate-markers: not a git repository: {repo}", file=sys.stderr)
        return 2
    return args.func(repo, marker_dir, args)


if __name__ == "__main__":
    raise SystemExit(main())
