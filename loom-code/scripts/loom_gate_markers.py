"""Gate-marker CLI for loom-code's mechanical push gates.

The SDD orchestrator runs this to mint the markers that
`hooks/git-guard.py` (built in parallel on this branch) reads before
allowing a push. Marker contract (frozen; every field asserted by
`test_loom_gate_markers.py`):

Dir: `<git-dir>/loom/` resolved via `git rev-parse --git-dir` from
`--repo` (default cwd); created if missing.

- `review-pass.json`  {"schema": 1, "branch", "head_sha", "verdict",
  "written_at", optional "base_sha"/"patch_id"} — written via one of TWO
  paths. `review-pass --verdict-file <file>`: ONLY after the reviewer's
  verdict text passes schema validation (the audit's schema gate: a
  marker can only exist if a schema-valid verdict text exists).
  NEEDS_REVISION never mints a marker (exit 3); a malformed verdict
  never mints one either (exit 4, missing keys listed). Quote
  verification (below) does NOT gate this marker. The
  `origin_quote_tiers` field this marker used to carry remains removed;
  quote results stay ephemeral, with one aggregated advisory when a
  quote matches only after normalisation.
  `mint --review-na-record-only`: ONLY after re-verifying every file
  changed vs the default branch's merge-base is record-class per the
  `requesting-code-review/SKILL.md` §Classification: contract-class vs
  record-class SSOT (see `_is_contract_class_md` /
  `_record_only_offending_files`) — no verdict text, no docs/code-review
  arm dispatch, and no origin-quote verification.
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
import unicodedata
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

# A finding whose `dimension:` both parses and falls in this docs-arm set is
# exempt from `origin:`; everything else — code-arm, unrecognized, or
# unparseable (absent/empty) — requires it (fail closed, see
# `_origin_required`).
_DOCS_ARM_DIMENSIONS = {
    "omission", "ambiguity", "inconsistency", "incorrect-fact",
    "missing-population",
}
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


_SHA_UNRESOLVABLE = "sha-unresolvable"
_FILE_ABSENT = "file-absent"
_NOT_A_FILE = "not-a-file"
_UNDECODABLE_BLOB = "undecodable-blob"


def _show_committed_file(
    repo: Path, head_sha: str, path: str
) -> tuple[str | None, str | None]:
    """Read `path` as it exists at `head_sha` in the git object store —
    NEVER the worktree (brief §Resolved Questions 1: an uncommitted edit
    must not be able to satisfy the quote check).

    Returns `(content, failure_kind)`: `failure_kind` is None on success,
    `_SHA_UNRESOLVABLE` when `head_sha` does not resolve to a commit,
    `_FILE_ABSENT` when `git cat-file -t <sha>:<path>` exits non-zero —
    which covers both "path genuinely absent at that sha" AND, when the
    linked commit object is NOT present in the local object store,
    "path is a submodule gitlink" (see the THIRD verified quirk below;
    the two are NOT distinguished by this helper in that state),
    `_NOT_A_FILE` when `cat-file -t` exits zero but reports a type
    other than `blob` — a directory (git tree) is one measured case,
    and a submodule gitlink whose linked commit object IS present in
    the local object store (type `commit`) is a second, also covered
    below — or `_UNDECODABLE_BLOB` when the blob is not valid UTF-8.

    Reuses `_git`'s subprocess invocation shape but NOT its collapse-to-
    `None` contract (Task 2 Reuse-adequacy) — GREEN needs these failure
    modes distinguishable. The sha is checked to resolve to a commit
    FIRST, independently of the file read: `git show <sha>:<path>` on an
    unresolvable sha can print a misleading "exists on disk, but not in"
    message (a verified git quirk — a 40-hex-char string that resolves
    to no object still gets treated as a treeish by `<rev>:<path>`
    parsing), so failure-kind is never inferred from that command's
    stderr text.

    A SECOND verified quirk, caught in code-quality review: `git show
    <sha>:<dir>` also exits 0 — it prints a git-generated tree listing
    (`tree <hash>:<dir>` followed by the directory's entries), not
    repository content. Without a type check, a quote naming any
    filename in that listing (or the literal word "tree") mints with no
    knowledge of any real document. `git cat-file -t <sha>:<path>` is
    checked and must report `blob` before `git show` ever runs, so a
    directory is refused as `_NOT_A_FILE` before its listing is read.

    A THIRD verified quirk, caught in code-quality review round 2 and
    CORRECTED in round 3 after a reviewer reproduced the opposite of an
    earlier, unconditional version of this paragraph: a submodule path
    (a gitlink, git tree entry mode 160000) classifies CONDITIONALLY on
    whether the linked commit object happens to be present in this
    repo's local object store — that is state, not a fixed property of
    gitlinks, and both states are real:

    - Object ABSENT locally (the common case — nobody has fetched the
      submodule into this repo): `git cat-file -t <sha>:<path>` exits
      128 ("could not get object info") instead of exiting 0 with a
      non-blob type, and `git show <sha>:<path>` fails outright too.
      Measured against a throwaway repo holding a gitlink whose target
      commit is never fetched (`git update-index --add --cacheinfo
      160000,<sub-sha>,mysub` then commit, object store otherwise
      lacking `<sub-sha>`): both commands fail outright rather than
      reporting a type or a listing. This lands in `_FILE_ABSENT`.
    - Object PRESENT locally (e.g. after `git fetch <path-to-submodule-
      repo> <branch>:refs/remotes/<name>/<branch>` pulls the linked
      commit into THIS repo's own object store — an ordinary fetch, no
      exotic config): `git cat-file -t <sha>:<path>` exits 0 and
      reports type `commit`, and `git show <sha>:<path>` exits 0 and
      prints that commit's log rather than failing. This lands in
      `_NOT_A_FILE`, the same branch a directory takes, just with type
      `commit` instead of `tree`. Exercised by a live test (grep
      `classifies_gitlink_with_object_present` in the test module).

    Either way this helper never returns real repository content for a
    gitlink, so no code path mints a quote from one — but the "does not
    exist" message the caller prints for `_FILE_ABSENT` is imprecise in
    the object-absent state (the path does exist, just not as a
    `<sha>:<path>`-resolvable object this helper can read), and this
    helper cannot tell "path genuinely absent" from "path is a
    submodule whose object is missing locally" apart in that state.

    SYMLINK POLICY (decided here, not left implicit): a symlink's git
    object type is ALSO `blob` — its content is the literal target path
    string, e.g. `../other.md`. This helper does not special-case that:
    `git cat-file -t` reports `blob`, so a symlink is read and matched
    like any other blob. This is a deliberate policy choice, not a gap
    the type check missed. The contract this helper serves is "verify
    the quote against `path`'s committed content at `head_sha`" — a
    symlink's committed content genuinely IS its target string, so
    matching against it is correct per that contract's letter, and
    distinguishing symlinks would need a second `ls-tree`/mode lookup
    for a case with no measured incidence in this repo's findings.
    """
    if _git(repo, "rev-parse", "--verify", "-q", f"{head_sha}^{{commit}}") is None:
        return None, _SHA_UNRESOLVABLE
    try:
        type_result = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-t", f"{head_sha}:{path}"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None, _SHA_UNRESOLVABLE
    if type_result.returncode != 0:
        return None, _FILE_ABSENT
    if type_result.stdout.strip() != "blob":
        return None, _NOT_A_FILE
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{head_sha}:{path}"],
            capture_output=True,
        )
    except OSError:
        return None, _SHA_UNRESOLVABLE
    if result.returncode != 0:
        return None, _FILE_ABSENT
    try:
        content = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None, _UNDECODABLE_BLOB
    return content, None


def default_branch_ref(repo: Path) -> str | None:
    """Best-effort default-branch ref for merge-base computation.

    Tries origin/HEAD's symbolic ref, then local `main`, then local
    `master`. Returns None when none resolve — callers then omit the
    patch-id fields entirely (fail-closed: the fallback never activates
    for that marker; strict head_sha equality remains the only path).

    Returns a revision NAME, not a fetch target — one of three shapes:
    `origin/<branch>` (from origin/HEAD, `refs/remotes/` prefix
    stripped), a bare local `main` / `master`, or None. A return with
    no remote component (the bare-local shape) is a LOCAL-ONLY ref:
    comparing against it answers "am I current with my own local
    main", which is a false all-clear — callers must not treat it as
    equivalent to the `origin/<branch>` shape. What a caller then DOES
    about that is the caller's policy, not this function's.
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
    ref = default_branch_ref(repo)
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


# §Classification: contract-class vs record-class (Task 14) — the SAME
# path rule as `requesting-code-review/SKILL.md`'s own heading of that
# name (Task 8's SSOT): "Contract-class = paths matching
# `<plugin>/skills/**/*.md`, `<plugin>/agents/*.md`, `<plugin>/hooks/*.md`,
# `<plugin>/scripts/*.md` excluding any `README*`/`CHANGELOG*` basename.
# Record-class = everything else (incl. `docs/**`)." That SKILL.md
# heading is the ONE place the rule TEXT lives; this regex is the ONE
# place it is ENCODED in Python (doc-mirrors-code lockstep) — never
# re-derive it independently elsewhere in this file.
_CONTRACT_CLASS_RE = re.compile(
    r"^[^/]+/(?:skills/.+|agents/[^/]+|hooks/[^/]+|scripts/[^/]+)\.md$"
)
_EXEMPT_BASENAME_PREFIXES = ("README", "CHANGELOG")


def _is_contract_class_md(path: str) -> bool:
    """True iff `path` (repo-relative, forward-slash separated) is a
    contract-class `.md` file per the rcr SSOT above. Only meaningful
    for `.md` paths — the SSOT's classification is scoped to `.md`
    routing decisions only; callers must reject non-`.md` paths
    themselves (see `_record_only_offending_files`)."""
    if not _CONTRACT_CLASS_RE.match(path):
        return False
    basename = path.rsplit("/", 1)[-1]
    return not basename.startswith(_EXEMPT_BASENAME_PREFIXES)


def _record_only_offending_files(changed_files: list[str]) -> list[str]:
    """Files in `changed_files` that disqualify a record-only branch:
    any non-`.md` file, or any `.md` file that is contract-class per
    `_is_contract_class_md`. Order-preserving; an empty return means
    the whole set is record-class and the exemption may mint."""
    return [
        f for f in changed_files if not f.endswith(".md") or _is_contract_class_md(f)
    ]


def _record_only_changed_files(repo: Path) -> list[str] | None:
    """Files changed on the current branch vs the merge-base with the
    default branch — mirrors `git diff --name-only $(git merge-base
    HEAD main)` from the plan's Task 14 spec, but resolves the default
    branch via `default_branch_ref` (origin/HEAD, else local `main`/
    `master`) rather than hardcoding `main`, so throwaway repos with no
    `origin` remote still resolve. Returns None when the default
    branch or the merge-base cannot be resolved (fail-closed: the
    caller refuses to mint rather than guessing an empty diff)."""
    ref = default_branch_ref(repo)
    if ref is None:
        return None
    merge_base = _git(repo, "merge-base", ref, "HEAD")
    if merge_base is None:
        return None
    # --no-renames: WITHOUT it, git's default rename detection collapses
    # a contract->record rename (e.g. `git mv agents/foo.md
    # docs/foo-notes.md` plus a small edit) into ONLY the new path — the
    # contract-class OLD path would never reach
    # `_record_only_offending_files`, letting a branch that moved a
    # contract file mint the exemption. Forcing add/delete pairs keeps
    # BOTH sides of any rename visible to the classifier.
    diff_output = _git(
        repo, "diff", "--no-renames", "--name-only", merge_base, "HEAD"
    )
    if diff_output is None:
        return None
    if diff_output == "":
        return []
    return diff_output.splitlines()


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


def _parse_origin(
    origin_value: str | None,
) -> tuple[tuple[str, str] | None, str | None]:
    """The ONE place `origin:` values parse — collapses what were two
    duplicate split/blank-check/quoted-check copies (grammar validation,
    quote extraction), whose drift let three mutants survive undetected
    in the extraction copy alone (deleted blank-check, deleted
    quoted-check, `find`->`rfind` split). One parse site makes that
    mutant class impossible to express.

    Returns `(spec, problem)`: `problem` is None iff `origin_value` is
    `none` or a grammar-valid `<path> :: "<quote>"`, else a violation
    description. `spec` is `(path, quote)` — quote WITHOUT its wrapping
    `"` — when extracted; None for `none`, absent, or malformed.

    Split on the FIRST ` :: `: a path may not contain it, a quote may —
    so the first occurrence is the boundary (§Notes kickoff decision,
    corrected 2026-08-02: the earlier "split on the LAST ` :: `"
    mis-parsed a quote containing the separator into a truncated path
    and an unquoted remainder). No backslash-escape convention. The
    quote's interior must be non-blank: `""` and `"   "` are refused —
    an empty quote is not a verbatim quote, and Task 2 verifies by
    substring, so an empty quote would match every file and pass the
    whole gate as a well-formed origin.

    No minimum length or width beyond non-blank (amendment 2026-08-02,
    user decision, deleting a display-width floor that shipped and was
    then measured against this repo's committed `.md` files: the
    benefit it bought was small next to the review cost of getting
    there. The axis was wrong, not the constant — see the plan's
    §Notes for the measurement and the four superseded token/width
    rules it replaced)."""
    if origin_value is None:
        return None, "no origin: line"
    value = origin_value.strip()
    if value == "none":
        return None, None
    idx = value.find(" :: ")
    if idx == -1:
        return None, (
            f"origin: {origin_value!r} is not 'none' or '<path> :: \"<quote>\"'"
        )
    # `path` is always non-empty here: `value` is already stripped (so
    # value[0] is non-whitespace) and the separator starts with a space,
    # so idx can never be 0 — value[:idx] always contains value[0].
    path, quote = value[:idx], value[idx + 4 :]
    if len(quote) < 2 or quote[0] != '"' or quote[-1] != '"':
        return None, f"origin: {origin_value!r} quote is not fully quoted"
    inner = quote[1:-1]
    if not inner.strip():
        return None, f"origin: {origin_value!r} quote is empty or blank"
    return (path, inner), None


def _origin_grammar_problem(origin_value: str | None) -> str | None:
    """Thin wrapper over `_parse_origin`: the problem text (Task 1)."""
    return _parse_origin(origin_value)[1]


def _origin_path_quote(origin_value: str | None) -> tuple[str, str] | None:
    """Thin wrapper over `_parse_origin`: the extracted spec (Task 2)."""
    return _parse_origin(origin_value)[0]


def _finding_quote_status(
    origin_value: str | None,
    repo: Path,
    head_sha: str | None,
    file_cache: dict[str, tuple[str | None, str | None]],
) -> str:
    """Return this finding's ephemeral quote-verification status.

    `"absent"` means no `origin:` line exists at all,
    `"none"` when the value is literally `none`, `"malformed"` when a
    value is present but not grammar-valid, and grammar-valid quotes are
    checked against `head_sha`'s committed content.

    Failure statuses reuse `_show_committed_file`'s vocabulary:
    `unverified-sha-unresolvable`, `unverified-file-absent`,
    `unverified-not-a-file`, `unverified-undecodable-blob`, or (the file
    read fine but never contained the quote) `unverified-quote-absent`.
    A verifying quote returns `verified-exact` or `verified-normalised`.

    No status blocks marker minting; only `_finding_problems`' grammar
    validation can refuse. `head_sha` is guarded because verification must
    never call `_show_committed_file` without a resolvable commit."""
    if origin_value is None:
        return "absent"
    if origin_value.strip() == "none":
        return "none"
    spec = _origin_path_quote(origin_value)
    if spec is None:
        return "malformed"
    path, quote = spec
    if head_sha is None:
        return f"unverified-{_SHA_UNRESOLVABLE}"
    if path not in file_cache:
        file_cache[path] = _show_committed_file(repo, head_sha, path)
    content, failure_kind = file_cache[path]
    if failure_kind is not None:
        return f"unverified-{failure_kind}"
    tier = _quote_match_tier(content, quote)
    if tier is None:
        return "unverified-quote-absent"
    return f"verified-{tier}"


# §Notes kickoff decision (quote-match strictness): fold typographic
# quotes/dashes/NBSP to their ASCII equivalents. Deliberately narrow —
# only the marks the decision names, nothing broader.
_TYPOGRAPHIC_FOLD = {
    "‘": "'",  # LEFT SINGLE QUOTATION MARK
    "’": "'",  # RIGHT SINGLE QUOTATION MARK
    "“": '"',  # LEFT DOUBLE QUOTATION MARK
    "”": '"',  # RIGHT DOUBLE QUOTATION MARK
    "–": "-",  # EN DASH
    "—": "-",  # EM DASH
    " ": " ",  # NO-BREAK SPACE
}


def _normalize_for_quote_match(text: str) -> str:
    """NFC-normalize, fold typographic quotes/dashes/NBSP to ASCII, then
    collapse each run of whitespace to a single space. Case-sensitive;
    does NOT strip `**` or backticks (§Notes kickoff decision — the SAME
    normaliser is applied to both the quote and the haystack)."""
    text = unicodedata.normalize("NFC", text)
    for typographic, ascii_form in _TYPOGRAPHIC_FOLD.items():
        text = text.replace(typographic, ascii_form)
    return re.sub(r"\s+", " ", text)


def _quote_match_tier(haystack: str, quote: str) -> str | None:
    """"exact" if `quote` occurs byte-for-byte in `haystack`; "normalised"
    if it occurs only after both sides pass through the identical
    normaliser; else None. Two-stage per §Notes kickoff decision — this
    repo hard-wraps prose, so a truthful one-line quote of a multi-line
    passage fails byte-exact matching by construction."""
    if quote in haystack:
        return "exact"
    if _normalize_for_quote_match(quote) in _normalize_for_quote_match(haystack):
        return "normalised"
    return None


class _FindingInfo:
    """One `- severity:` finding block's sibling-field values, as read by
    `_iter_findings`. `dimension_value`/`origin_value` are None when the
    field is absent OR duplicated (a duplicate is unparseable, not
    resolved first/last-wins — see `_iter_findings`)."""

    __slots__ = (
        "start_line",
        "where_ok",
        "dimension_value",
        "origin_value",
        "duplicate_origin",
        "duplicate_dimension",
    )

    def __init__(
        self,
        start_line: int,
        where_ok: bool,
        dimension_value: str | None,
        origin_value: str | None,
        duplicate_origin: bool,
        duplicate_dimension: bool,
    ) -> None:
        self.start_line = start_line
        self.where_ok = where_ok
        self.dimension_value = dimension_value
        self.origin_value = origin_value
        self.duplicate_origin = duplicate_origin
        self.duplicate_dimension = duplicate_dimension


def _iter_findings(text: str):
    """Yield one `_FindingInfo` per `- severity:` finding block. Shared by
    `_finding_problems` (Task 1's grammar/requirement checks) and
    `_quote_verification_statuses` (Task 8's real quote verification) so both
    read `origin:` through the identical block-scoping rule — a value nested
    inside e.g. a `note: |` block-literal must never count as a sibling
    field of either reader."""
    lines = text.splitlines()
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
        yield _FindingInfo(
            start_line=start + 1,
            where_ok=where_ok,
            # Two or more `dimension:` (or `origin:`) lines in one block is
            # malformed: YAML readers disagree on which value wins (first
            # vs last), so a duplicate is treated as unparseable rather
            # than resolved either way — fail closed (§Pinned dimension
            # partition).
            dimension_value=(
                dimension_values[0] if len(dimension_values) == 1 else None
            ),
            origin_value=origin_values[0] if len(origin_values) == 1 else None,
            duplicate_origin=len(origin_values) > 1,
            duplicate_dimension=len(dimension_values) > 1,
        )


def _finding_problems(text: str) -> list[str]:
    """Every `- severity:` finding block must carry a path-like `where:`,
    and — unless its `dimension:` both parses and falls in the docs-arm
    set — an `origin:` line valued `none` or `<path> :: "<quote>"`
    (§Pinned dimension partition; requirement is the default, the
    docs-arm exemption is the explicit branch).

    That exemption governs only whether `origin:` must be CARRIED. An
    `origin:` line that IS present is grammar-checked on every arm,
    docs included — the exemption never excuses a malformed value a
    docs-arm finding chose to write (bare path, unterminated quote,
    blank quote). Skipping this on the exempt branch was a real bug: a
    docs-arm finding with a malformed `origin:` used to sail through
    with no `origin:` requirement AND no grammar check on the one it
    carried, minting clean.

    A duplicate `dimension:` line is refused here for the SAME reason a
    duplicate `origin:` is (whole-branch review finding 3, mirroring the
    prior `origin:` fix onto `dimension:`): which of two `dimension:`
    values is intended is genuinely ambiguous, and `dimension` directly
    decides whether the docs-arm exemption applies. Before this check, a
    duplicate `dimension:` line was invisible to `_finding_problems`; a duplicate
    could therefore mint whenever the separate origin requirement happened
    to be satisfied. Refusing the ambiguity keeps the docs-arm exemption
    fail-closed, matching duplicate `origin:` handling."""
    problems: list[str] = []
    for info in _iter_findings(text):
        if not info.where_ok:
            problems.append(
                f"finding at line {info.start_line}: no where: line with a "
                "path-like token in its block"
            )
        if info.duplicate_dimension:
            problems.append(
                f"finding at line {info.start_line}: duplicate dimension: "
                "lines (exactly one is required)"
            )
        if info.duplicate_origin:
            problems.append(
                f"finding at line {info.start_line}: duplicate origin: lines "
                "(exactly one is required)"
            )
        elif info.origin_value is None:
            if _origin_required(info.dimension_value):
                problems.append(
                    f"finding at line {info.start_line}: no origin: line"
                )
        else:
            origin_problem = _origin_grammar_problem(info.origin_value)
            if origin_problem:
                problems.append(
                    f"finding at line {info.start_line}: {origin_problem}"
                )
    return problems


def _quote_verification_statuses(
    text: str, repo: Path, head_sha: str | None
) -> list[str]:
    """Verify each finding's origin against committed HEAD content.

    Results are intentionally ephemeral: they support the normalised-match
    advisory without creating a durable cross-round store. One file cache is
    shared across the verdict so repeated quotes from one path invoke git once.
    """
    file_cache: dict[str, tuple[str | None, str | None]] = {}
    statuses = []
    for info in _iter_findings(text):
        if info.duplicate_origin:
            statuses.append("duplicate")
            continue
        statuses.append(
            _finding_quote_status(info.origin_value, repo, head_sha, file_cache)
        )
    return statuses


def _print_normalised_quote_advisory(quote_statuses: list[str]) -> None:
    """Print one aggregated advisory for quotes needing normalisation."""
    normalised_count = quote_statuses.count("verified-normalised")
    if normalised_count:
        plural = "" if normalised_count == 1 else "s"
        print(
            f"loom-gate-markers: {normalised_count} origin quote{plural} "
            "matched only after normalisation."
        )


def _cmd_review_pass(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"loom-gate-markers: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    verdict, problems = validate_verdict_text(text)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")

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

    head_sha = _git(repo, "rev-parse", "HEAD")
    if branch is None or head_sha is None:
        print("loom-gate-markers: cannot resolve HEAD.", file=sys.stderr)
        return 2

    quote_statuses = _quote_verification_statuses(text, repo, head_sha)

    # Quote verification does not gate the mint: a finding whose quote
    # does not verify — absent, file absent, not a file, undecodable, or
    # sha unresolvable — leaves an ephemeral status, and the mint proceeds.
    # Only the deterministic grammar check (`problems`, above) still refuses — it
    # fails CLOSED (never a silent fail-open exemption), but is NOT
    # false-positive-free: two indent-drift shapes (an outlier first
    # field; a tab against spaces) over-refuse a well-formed verdict,
    # tracked OPEN at
    # docs/loom/backlog/2026-08-02-finding-block-field-scanner-false-refuses-on-indent-drift.md.
    # Quote verification, measured on this repo, was blocking a push on
    # exactly the tail of findings it could never see anyway — which is
    # why it no longer gates.
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
    _print_normalised_quote_advisory(quote_statuses)
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


def _cmd_mint(repo: Path, marker_dir: Path, args: argparse.Namespace) -> int:
    """`mint --review-na-record-only` — the record-only continuity
    exemption (Task 14). Mints `review-pass.json` WITHOUT any verdict
    text and WITHOUT dispatching either review arm, IFF every file
    changed vs the default branch's merge-base is record-class per the
    rcr SSOT (`_record_only_offending_files`). Any offending file (a
    contract-class `.md`, or any non-`.md` file at all) refuses to
    mint, loudly, naming every offender — never a partial mint."""
    if not args.review_na_record_only:
        print(
            "loom-gate-markers: mint requires --review-na-record-only "
            "(the only mint mode currently defined).",
            file=sys.stderr,
        )
        return 2

    changed_files = _record_only_changed_files(repo)
    if changed_files is None:
        print(
            "loom-gate-markers: cannot resolve the default branch or its "
            "merge-base with HEAD — refusing to mint.",
            file=sys.stderr,
        )
        return 2
    if not changed_files:
        print(
            "loom-gate-markers: no files changed vs the merge-base — the "
            "record-only exemption requires a non-empty, all-record-class "
            "file list (rcr SKILL.md §Process Step 1's Record-only branch "
            "bullet); refusing to mint.",
            file=sys.stderr,
        )
        return 3

    offenders = _record_only_offending_files(changed_files)
    if offenders:
        print(
            "loom-gate-markers: record-only exemption refused — the "
            "following changed file(s) are not record-class per rcr "
            "SKILL.md §Classification: contract-class vs record-class:",
            file=sys.stderr,
        )
        for path in offenders:
            print(f"  - {path}", file=sys.stderr)
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
        "verdict": "PASS",
        "written_at": _now_iso(),
    }
    patch_id_fields = compute_patch_id(repo)
    if patch_id_fields is not None:
        payload["base_sha"], payload["patch_id"] = patch_id_fields
    path = _write_marker(marker_dir, "review-pass.json", payload)
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

    # `validate` takes no --repo, so it has no HEAD to verify a quote
    # against — quote verification is a `review-pass`-only step. Say so
    # loudly here rather than passing silently: a silent skip on exactly
    # the pre-flight path `requesting-code-review` Step 3 tells reviewers
    # to use would be a fail-open (§Notes kickoff decision).
    quoted_origin_count = sum(
        1 for info in _iter_findings(text) if _origin_path_quote(info.origin_value)
    )
    if quoted_origin_count:
        print(
            "loom-gate-markers: quote verification did not run for "
            f"{quoted_origin_count} quoted origin(s) — `validate` takes "
            "no --repo and cannot check committed content. Run "
            "review-pass to verify."
        )

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
    `mint --review-na-record-only` /
    `validate --verdict-file <path> [--suite-line "<text>"]`,
    each of the first four with optional `--repo <path>` (default
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

    mt = subparsers.add_parser("mint")
    mt.add_argument("--repo", default=".", help="repo path (default: cwd)")
    mt.add_argument(
        "--review-na-record-only",
        action="store_true",
        help="mint review-pass.json without a review, IFF every file "
        "changed vs the default branch's merge-base is record-class "
        "(rcr SKILL.md §Classification: contract-class vs record-class)",
    )
    mt.set_defaults(func=_cmd_mint)

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
