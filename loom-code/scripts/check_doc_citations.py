#!/usr/bin/env python3
"""Verify path+anchor and legacy path+line citations in Markdown docs.

Reimplements, as a durable script, the mid-loop ad-hoc check described in
`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` §5: every
backtick-quoted citation like `` `loom-code/scripts/foo.py:123` `` or
`` `docs/loom/BACKLOG.md:10-25` `` is parsed out of a doc, resolved
against the repo root, and checked that the target file exists and that
its line (or, for a range, the range end) does not exceed the file's
line count.

Scope (v1 — Task 1 + Task 2 only):
- Backtick-wrapped `path:line` citations are parsed, as are canonical
  line-less path citations when paired with a following same-line
  verbatim anchor (`path` "anchor"). A bare,
  unbackticked `path:line` in prose is deliberately ignored — backticks
  are the reliable signal that a token is a path-citation rather than
  incidental text (e.g. a ratio, a clock time, a URL fragment); adding
  bare-form parsing would need heuristics to avoid false positives and
  is not needed by the corpus this ships against.
- `§N` / `§N.M` anchors: numbered headings only (`## N.` / `### N.M`,
  any heading level, an optional `§` decoration before the digit
  tolerated since the corpus writes both `## 3.7 …` and `## §1 …`).
  A `§N` adjacent to a backtick `` `doc.md` `` citation on the SAME
  line resolves against that document; a bare `§N` with no document
  named on that line resolves against the containing document itself.
  Cross-line association (a doc named several lines above a `§N`) is a
  known v1 limitation — out of scope, see the plan's Task 2 note.
  Quoted-string (anchor) verification: a paired `"..."` string on the same
  line as a backtick `path:line` citation is verified to occur as a
  substring in the target file; the existing line-bounds check remains as
  a secondary check. No other semantic check.

Read-only: this script never writes to any file it inspects.

Stdlib only (`pathlib`, `re`, `sys`).

Round 2 (2026-07-28, plan Task 3): the round-1 full-corpus dogfood
(`docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md`) measured a
79.7% false-positive rate, 95% of it one pattern — docs cite files by
bare name or partial path (`kpi_spine_view.py:1116`), trusting doc-level
context, which the literal repo-root-relative resolver above cannot
follow. When a cited path does not resolve directly under the repo root,
`resolve_cited_path` falls back to a repo-wide suffix match (does any
real file's path END WITH the cited string?):

- Exactly one match: resolve against it and bounds-check as normal.
- Zero or multiple matches: the citation is UNCHECKED — a third bucket,
  distinct from both "resolves cleanly" and "finding". This is
  deliberate, not a gap: asserting "file not found" from a repo-wide
  search that ALSO came up empty (or ambiguous) would repeat the
  false-positive problem in mirror image — confidently flagging drift
  we cannot actually confirm. Loud skipping (an `unchecked` count in
  every summary line) is the design instead of silent guessing.
  Consequence: because a resolved target is by construction a real
  file, "file not found" can no longer be produced as a finding reason
  — only "line/section exceeds bounds" can. Real drift that manifests
  as a citation with no remaining repo-wide match (e.g. a hard-cut
  directory rename with no alias) now falls into `unchecked`, not a
  finding; this is a recall-for-precision trade, documented in the
  round-2 dogfood note, not an oversight.
- `§N` anchor doc-name resolution (Task 2) uses the same fallback and
  the same three-bucket outcome.

Round 3 (2026-07-28, plan Task 3 continued): the round-2 corpus re-run
(`docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md` §Round 2)
found the remaining `section not found` findings (244) were 240/244 one
pattern: the cited target document uses named (non-numbered) headings
throughout and simply doesn't use the `## N.` convention at all — the
`§N` grammar cannot be applied to it in either direction. A resolved
target with ZERO numbered headings is now UNCHECKED, not a finding
(`check_section_anchor`); a finding may only fire when the target HAS
numbered headings but lacks the specific one cited. This is the same
"loud skip over confident wrong guess" design as the round-2 fallback
above, applied to the applicability question instead of the resolution
question. Four individually-adjudicated parser-mis-bind instances from
round 2 were re-examined and left unfixed (documented in the round-3
dogfood note instead): each is either an inherent grammar limitation
(a `§N.M` referring to a numbered list item, never a real heading) or
a same-line multi-doc-name ambiguity / cardinal-number false heading
match already declined as unsafe to special-case in round 1's "Parser
fixes considered, not made" section — fixing them would need semantic
judgment a regex heuristic cannot supply safely, the same conclusion
round 1 already reached.

Round 4 (2026-07-29, plan Task 4 final — split-half shipping): the
three-round dogfood (`docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md`)
measured the two checks apart, not just together. The path:line bounds
check finished at 0% measured false positives (8/8 confirmed true
positives, zero confirmed false positives across rounds 2-3). The §N
anchor check never produced a single confirmed true positive on the
whole 329-file corpus and still carries 4 architecturally distinct
residual false positives after two targeted fixes. Per the user's
decision, the default invocation now runs ONLY the path:line bounds
check; the §N anchor check moves behind an opt-in `--sections` flag
and is marked **experimental**: the `§N` convention it enforces was
only introduced to this corpus days before the round-1 measurement, so
its value is prospective, not yet demonstrated on real drift. Re-measure
(and reconsider default-on) once the corpus's `§N` usage has grown
materially past this run's population (401 refs, round 1 §1).

The repo-wide file list (`list_repo_files`) walks the tree once via
`os.walk`, excluding only `.git`. This over-includes untracked/ignored
files relative to `git ls-files` (e.g. `__pycache__`), but that is the
conservative direction for this design: an extra candidate can only
ever turn a would-be-unique match into an ambiguous (unchecked) one —
it never fabricates a false "resolves cleanly" result — and it avoids
adding a `git` subprocess dependency to an otherwise stdlib-only script.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Matches a backtick-quoted `path`, `path:line`, or `path:line-range` candidate.
# The path segment excludes backticks/whitespace/colons; requiring a
# `.` in the final path component (checked in `_looks_like_citation`)
# keeps this from matching unrelated `key:value`-shaped backtick spans
# that happen to end in digits. A line-less candidate is retained only
# when `extract_citations` finds its required following anchor.
_CITATION_RE = re.compile(r"`([^`\s:]+)(?::(\d+)(?:-(\d+))?)?`")

# Matches a paired double-quoted `"..."` string on the same line as a
# backtick citation. The captured group is the verbatim anchor string
# verified as a substring in the target file. A citation with no paired
# quote on its line yields `None` and the substring check does not fire
# (backward compatible — no existing citation carries a paired quote).
_ANCHOR_RE = re.compile(r'"([^"]*)"')


def _looks_like_citation(path: str) -> bool:
    """True if `path`'s final segment has a dot (an extension).

    Filters out non-path backtick spans like `` `note:123` `` that the
    regex would otherwise match.
    """
    return "." in path.rsplit("/", 1)[-1]


def extract_citations(
    text: str,
) -> list[tuple[int, str, int | None, int | None, str | None]]:
    """Return `(doc_lineno, cited_path, start_line, end_line, anchor)` per citation.

    `doc_lineno` is 1-indexed (the line in `text` the citation appears
    on). `start_line` and `end_line` are both `None` for a canonical
    line-less path+anchor citation. `end_line` is otherwise `None` for
    a single-line citation (`path:N`) and the range end for a range
    citation (`path:N-M`). `anchor` is the
    paired double-quoted `"..."` string found on the same line as the
    citation, or `None` when no such quote is present (the substring
    check then does not fire). Order matches first-seen order in `text`.
    """
    citations: list[tuple[int, str, int | None, int | None, str | None]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        matches = list(_CITATION_RE.finditer(line))
        for index, match in enumerate(matches):
            path, start_str, end_str = match.group(1), match.group(2), match.group(3)
            if not _looks_like_citation(path):
                continue
            next_citation_start = (
                matches[index + 1].start() if index + 1 < len(matches) else len(line)
            )
            anchor_match = _ANCHOR_RE.search(
                line, match.end(), next_citation_start
            )
            anchor = anchor_match.group(1) if anchor_match is not None else None
            if start_str is None and anchor is None:
                continue
            end = int(end_str) if end_str is not None else None
            start = int(start_str) if start_str is not None else None
            citations.append((lineno, path, start, end, anchor))
    return citations


# Matches a backtick-quoted citation shorthand carrying NO path segment
# — `` `:170-179` `` — the form authors use when the path is named in the
# surrounding prose. `_CITATION_RE` cannot match it (its path group needs
# at least one character), so before this it was dropped silently: a doc
# citing entirely in this form reported `checked 0 / unchecked 0` and
# exit 0, indistinguishable from a genuine all-clear.
_PATHLESS_CITATION_RE = re.compile(r"`:(\d+)(?:-(\d+))?`")


def count_pathless_citations(text: str) -> int:
    """Return how many pathless `` `:N` `` / `` `:N-M` `` spans `text` has.

    These are counted UNCHECKED rather than resolved: with no path inside
    the backticks there is no target to bounds-check.

    The governing rule is the one `check_doc_report` states for omitted
    `§N` refs — the counts must never imply a citation was checked when it
    was not — but note the TREATMENT differs and deliberately so: omitted
    `§N` refs are extracted into neither bucket (a full, documented
    omission), whereas a pathless shorthand IS a `path:line`-family span
    the reader wrote as a citation, so dropping it from both buckets is
    exactly the silent-pass this function exists to end.
    """
    return sum(1 for _ in _PATHLESS_CITATION_RE.finditer(text))


def list_repo_files(repo_root: Path) -> list[str]:
    """Return every file's path relative to `repo_root`, POSIX-style.

    Walks the tree once, skipping `.git`. See module docstring for why
    `os.walk` (not `git ls-files`) and why over-inclusion is the safe
    direction for the suffix-match fallback below.
    """
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for filename in filenames:
            rel = (Path(dirpath) / filename).relative_to(repo_root)
            files.append(rel.as_posix())
    return files


def resolve_cited_path(
    repo_root: Path, cited_path: str, repo_files: list[str]
) -> Path | None:
    """Resolve `cited_path` to a real file, or `None` if UNCHECKED.

    Tries the literal repo-root-relative path first; if that is not a
    file, falls back to a repo-wide suffix match (a real file's path
    ending with `cited_path`). Returns `None` (UNCHECKED) when the
    fallback finds zero or multiple candidates — see module docstring.
    """
    direct = repo_root / cited_path
    if direct.is_file():
        return direct
    matches = [f for f in repo_files if f.endswith("/" + cited_path)]
    if len(matches) == 1:
        return repo_root / matches[0]
    return None


def check_citation(
    repo_root: Path,
    cited_path: str,
    start: int | None,
    end: int | None,
    repo_files: list[str],
    anchor: str | None = None,
) -> tuple[bool, str | None]:
    """Return `(checked, reason)` for one `path:line` citation.

    `checked` is `False` when `cited_path` is UNCHECKED (see
    `resolve_cited_path`); `reason` is then always `None`. When
    `checked` is `True`, `reason` is a finding string for an
    out-of-range line or a missing anchor substring, or `None` for a
    clean citation. A resolved target is by construction a real file,
    so "file not found" can no longer occur here (round 2 — see module
    docstring).

    `anchor` (the paired `"..."` string from the same line, or `None`)
    is the PRIMARY check: when present and resolved as a verbatim
    substring in the target file, the citation is clean — the line
    number is optional precision, and a stale out-of-bounds line does
    not invalidate a resolved anchor (the anchor survives the change
    that writes it; the line number rots within it). The line-bounds
    check is SECONDARY and runs only when no anchor is present (backward
    compatible — citations without a paired quote rely on the line
    number alone).
    """
    target = resolve_cited_path(repo_root, cited_path, repo_files)
    if target is None:
        return False, None
    file_text = target.read_text(encoding="utf-8", errors="replace")
    # Primary check: the anchor (verbatim substring). When an anchor is
    # present and resolves in the target file, the citation is valid —
    # the line number is optional precision, and a stale out-of-bounds
    # line does not invalidate a resolved anchor (the rule this checker
    # enforces: the anchor survives the change that writes it).
    if anchor is not None:
        if not anchor:
            return True, "quoted string not found in target"
        if anchor not in file_text:
            return True, "quoted string not found in target"
        return True, None
    # Secondary check: line-bounds, when no anchor is present (backward
    # compatible — citations without a paired quote rely on the line
    # number alone).
    assert start is not None
    line_count = len(file_text.splitlines())
    check_line = end if end is not None else start
    if check_line > line_count:
        return True, f"line {check_line} exceeds file length ({line_count} lines)"
    return True, None


# Matches a backtick-quoted bare Markdown document name (no `:line`
# suffix — that shape is `_CITATION_RE`'s territory). Used to find which
# document a `§N` anchor on the same line is naming.
_DOC_NAME_RE = re.compile(r"`([^`:\s]+\.md)`")

# Matches a `§N` or `§N.M` section-anchor reference.
_SECTION_REF_RE = re.compile(r"§(\d+)(?:\.(\d+))?")

# Matches a numbered heading: `## N.` or `### N.M` (any level, optional
# `§` decoration before the digit, optional trailing `.` after the last
# digit group) — see module docstring's §N scope note.
_HEADING_RE = re.compile(r"^#{1,6}\s+§?(\d+)(?:\.(\d+))?\.?(?:\s|$)")


def extract_section_refs(
    text: str,
) -> list[tuple[int, str | None, int, int | None]]:
    """Return `(doc_lineno, target_doc_name, major, minor)` per `§N` ref.

    `target_doc_name` is the bare-Markdown-name captured from the
    nearest backtick `` `doc.md` `` citation on the same line (nearest
    preceding it, else the first one on the line); `None` if no
    document is named on that line (bare self-reference). `minor` is
    `None` for a `§N` reference and the int for `§N.M`.
    """
    refs: list[tuple[int, str | None, int, int | None]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        doc_matches = list(_DOC_NAME_RE.finditer(line))
        for match in _SECTION_REF_RE.finditer(line):
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) is not None else None
            target = _nearest_doc_name(doc_matches, match.start())
            refs.append((lineno, target, major, minor))
    return refs


def _nearest_doc_name(doc_matches: list[re.Match[str]], pos: int) -> str | None:
    """Return the doc name from the nearest preceding match, else the first."""
    if not doc_matches:
        return None
    preceding = [m for m in doc_matches if m.start() < pos]
    chosen = preceding[-1] if preceding else doc_matches[0]
    return chosen.group(1)


def parse_headings(text: str) -> set[tuple[int, int | None]]:
    """Return the set of `(major, minor)` numbered headings in `text`."""
    headings: set[tuple[int, int | None]] = set()
    for line in text.splitlines():
        match = _HEADING_RE.match(line)
        if match is None:
            continue
        major = int(match.group(1))
        minor = int(match.group(2)) if match.group(2) is not None else None
        headings.add((major, minor))
    return headings


def check_section_anchor(
    repo_root: Path,
    citing_doc_path: Path,
    target_doc_name: str | None,
    major: int,
    minor: int | None,
    repo_files: list[str],
) -> tuple[bool, str | None]:
    """Return `(checked, tail)` for one `§N` anchor.

    `target_doc_name` of `None` means the anchor refers to the citing
    document itself. Otherwise the target doc name is resolved via
    `resolve_cited_path` (same repo-wide fallback as citations);
    `checked` is `False` (UNCHECKED) when that resolution is ambiguous
    or finds nothing — round 2 replaces v1's "missing file folds into
    section not found" with this third bucket, see module docstring.

    Round 3: a resolved target with ZERO numbered headings is ALSO
    UNCHECKED, not a finding — the round-2 corpus re-run
    (`docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md`
    §Round 2) found this is the dominant remaining false-positive class
    (240/244): the `§N` grammar only exists for documents that use the
    `## N.` numbered-heading convention; a doc that uses named headings
    exclusively cannot support a "does §N exist" verdict at all, in
    either direction (self-reference or cross-doc). A finding may only
    fire when the target HAS numbered headings but lacks the specific
    one cited. `tail`, when `checked` is `True`, is a `<target>:§N
    section not found` finding tail, or `None` for a resolved section.
    """
    if target_doc_name is None:
        target_path: Path | None = citing_doc_path
        target_repr = str(citing_doc_path)
    else:
        target_path = resolve_cited_path(repo_root, target_doc_name, repo_files)
        target_repr = target_doc_name
        if target_path is None:
            return False, None

    headings = parse_headings(target_path.read_text(encoding="utf-8", errors="replace"))
    if not headings:
        return False, None

    if (major, minor) in headings:
        return True, None
    section_repr = f"{major}.{minor}" if minor is not None else str(major)
    return True, f"{target_repr}:§{section_repr} section not found"


@dataclass(frozen=True)
class DocReport:
    """Per-document result: findings plus the checked/unchecked split."""

    findings: list[str]
    checked: int
    unchecked: int


def check_doc_report(
    doc_path: Path,
    repo_root: Path,
    repo_files: list[str],
    check_sections: bool = False,
) -> DocReport:
    """Return the full report (findings + checked/unchecked counts).

    `repo_files` is caller-supplied (see `list_repo_files`) so `main()`
    can compute it once per repo root instead of walking the tree once
    per document. Finding format: `<doc>:<lineno> -> <cited-path>:
    <cited-line> <reason>` for `path:line` citations, and `<doc>:
    <lineno> -> <target>:§N section not found` for unresolvable `§N`
    anchors.

    Pathless `` `:N` ``/`` `:N-M` `` shorthands (see
    `count_pathless_citations`) add to `unchecked` regardless of
    `check_sections` — they are `path:line`-family spans with the path
    left to prose, never resolvable, and never findings.

    `check_sections` (default `False`, round 4): the `§N` anchor check
    is opt-in and experimental (see module docstring's Round 4 note).
    When `False`, `§N` refs are never even extracted from `text` — they
    contribute to neither `findings` nor `checked`/`unchecked`, a full
    omission rather than a silent pass, so the counts never imply a
    section anchor was checked when it was not.
    """
    text = doc_path.read_text(encoding="utf-8")
    findings: list[str] = []
    checked = 0
    unchecked = 0
    for lineno, cited_path, start, end, anchor in extract_citations(text):
        was_checked, reason = check_citation(
            repo_root, cited_path, start, end, repo_files, anchor
        )
        if not was_checked:
            unchecked += 1
            continue
        checked += 1
        if reason is None:
            continue
        if start is None:
            findings.append(f"{doc_path}:{lineno} -> {cited_path} {reason}")
        else:
            cited_repr = f"{start}-{end}" if end is not None else str(start)
            findings.append(
                f"{doc_path}:{lineno} -> {cited_path}:{cited_repr} {reason}"
            )
    unchecked += count_pathless_citations(text)
    if check_sections:
        for lineno, target_doc_name, major, minor in extract_section_refs(text):
            was_checked, tail = check_section_anchor(
                repo_root, doc_path, target_doc_name, major, minor, repo_files
            )
            if not was_checked:
                unchecked += 1
                continue
            checked += 1
            if tail is None:
                continue
            findings.append(f"{doc_path}:{lineno} -> {tail}")
    return DocReport(findings=findings, checked=checked, unchecked=unchecked)


def check_doc(
    doc_path: Path, repo_root: Path, check_sections: bool = False
) -> list[str]:
    """Return only the finding strings for `doc_path` (back-compat wrapper).

    Computes the repo-wide file list internally. `main()` uses
    `check_doc_report` directly with a cached `repo_files` list to
    avoid re-walking the tree once per document in a multi-doc run.
    """
    return check_doc_report(
        doc_path, repo_root, list_repo_files(repo_root), check_sections
    ).findings


def find_repo_root(doc_path: Path) -> Path:
    """Walk up from `doc_path` to the nearest `.git` dir; else cwd."""
    current = doc_path.resolve().parent
    for parent in (current, *current.parents):
        if (parent / ".git").exists():
            return parent
    return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    repo_root: Path | None = None
    check_sections = False
    doc_args: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--repo-root":
            if i + 1 >= len(args):
                print(
                    "usage error: --repo-root requires a path argument",
                    file=sys.stderr,
                )
                return 2
            repo_root = Path(args[i + 1])
            i += 2
        elif args[i] == "--sections":
            check_sections = True
            i += 1
        else:
            doc_args.append(args[i])
            i += 1

    if not doc_args:
        print(
            "usage: check_doc_citations.py <file.md> [more.md ...] "
            "[--repo-root PATH] [--sections]\n"
            "  --sections  EXPERIMENTAL, opt-in: also check §N section-anchor\n"
            "              citations (off by default — see module docstring's\n"
            "              Round 4 note for why and the re-measure trigger).",
            file=sys.stderr,
        )
        return 2

    all_findings: list[str] = []
    total_checked = 0
    total_unchecked = 0
    repo_files_by_root: dict[Path, list[str]] = {}
    for doc_str in doc_args:
        doc_path = Path(doc_str)
        if not doc_path.is_file():
            print(f"usage error: not a file: {doc_str}", file=sys.stderr)
            return 2
        root = repo_root if repo_root is not None else find_repo_root(doc_path)
        if root not in repo_files_by_root:
            repo_files_by_root[root] = list_repo_files(root)
        report = check_doc_report(
            doc_path, root, repo_files_by_root[root], check_sections
        )
        all_findings.extend(report.findings)
        total_checked += report.checked
        total_unchecked += report.unchecked

    print(
        f"checked {total_checked} / unchecked {total_unchecked} / "
        f"findings {len(all_findings)}"
    )

    if all_findings:
        for finding in all_findings:
            print(finding)
        return 1

    # The success line must never claim more than was actually verified.
    # "all citations resolve" is only unqualified when NOTHING was skipped;
    # with any unchecked citation the line states its own scope. Mixed
    # documents are the typical case, and these counts are summed across
    # every document in one invocation (requesting-docs-review runs this
    # over all changed .md files at once), so an unscoped success line
    # would let one resolvable citation vouch for a whole batch.
    # Exit stays 0 in every branch below: "unverifiable" is not "wrong",
    # and exit 1 is reserved for findings.
    if total_unchecked == 0:
        print("OK: all citations resolve.")
    elif total_checked == 0:
        print(
            "NOTE: nothing verified — every citation found was unresolvable "
            "(pathless `:N` shorthand, ambiguous path, or absent target)."
        )
    else:
        print(
            f"OK: all {total_checked} checked citations resolve "
            f"({total_unchecked} unchecked — pathless `:N` shorthand, "
            "ambiguous path, or absent target)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
