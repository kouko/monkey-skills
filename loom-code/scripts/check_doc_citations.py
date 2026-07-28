#!/usr/bin/env python3
"""Bounds-check `path:line` / `path:line-range` citations in Markdown docs.

Reimplements, as a durable script, the mid-loop ad-hoc check described in
`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` §5: every
backtick-quoted citation like `` `loom-code/scripts/foo.py:123` `` or
`` `docs/loom/BACKLOG.md:10-25` `` is parsed out of a doc, resolved
against the repo root, and checked that the target file exists and that
its line (or, for a range, the range end) does not exceed the file's
line count.

Scope (v1 — Task 1 + Task 2 only):
- ONLY backtick-wrapped `path:line` citations are parsed. A bare,
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
  No quoted-string verification, no other semantic check.

Read-only: this script never writes to any file it inspects.

Stdlib only (`pathlib`, `re`, `sys`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Matches a backtick-quoted `path:line` or `path:line-range` citation.
# The path segment excludes backticks/whitespace/colons; requiring a
# `.` in the final path component (checked in `_looks_like_citation`)
# keeps this from matching unrelated `key:value`-shaped backtick spans
# that happen to end in digits.
_CITATION_RE = re.compile(r"`([^`\s:]+):(\d+)(?:-(\d+))?`")


def _looks_like_citation(path: str) -> bool:
    """True if `path`'s final segment has a dot (an extension).

    Filters out non-path backtick spans like `` `note:123` `` that the
    regex would otherwise match.
    """
    return "." in path.rsplit("/", 1)[-1]


def extract_citations(text: str) -> list[tuple[int, str, int, int | None]]:
    """Return `(doc_lineno, cited_path, start_line, end_line)` per citation.

    `doc_lineno` is 1-indexed (the line in `text` the citation appears
    on). `end_line` is `None` for a single-line citation (`path:N`) and
    the range end for a range citation (`path:N-M`). Order matches
    first-seen order in `text`.
    """
    citations: list[tuple[int, str, int, int | None]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _CITATION_RE.finditer(line):
            path, start_str, end_str = match.group(1), match.group(2), match.group(3)
            if not _looks_like_citation(path):
                continue
            end = int(end_str) if end_str is not None else None
            citations.append((lineno, path, int(start_str), end))
    return citations


def check_citation(
    repo_root: Path, cited_path: str, start: int, end: int | None
) -> str | None:
    """Return a reason string if the citation is invalid, else `None`.

    Distinguishes "file not found" from "line out of range" per the
    task's scope guard.
    """
    target = repo_root / cited_path
    if not target.is_file():
        return "file not found"
    line_count = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
    check_line = end if end is not None else start
    if check_line > line_count:
        return f"line {check_line} exceeds file length ({line_count} lines)"
    return None


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
) -> str | None:
    """Return a `<target>:§N section not found` finding tail, else `None`.

    `target_doc_name` of `None` means the anchor refers to the citing
    document itself. A missing target file is treated as having no
    headings (folds into the same "section not found" finding — v1
    does not distinguish it from an out-of-range section number).
    """
    if target_doc_name is None:
        target_path = citing_doc_path
        target_repr = str(citing_doc_path)
    else:
        target_path = repo_root / target_doc_name
        target_repr = target_doc_name

    headings: set[tuple[int, int | None]] = set()
    if target_path.is_file():
        headings = parse_headings(
            target_path.read_text(encoding="utf-8", errors="replace")
        )

    if (major, minor) in headings:
        return None
    section_repr = f"{major}.{minor}" if minor is not None else str(major)
    return f"{target_repr}:§{section_repr} section not found"


def check_doc(doc_path: Path, repo_root: Path) -> list[str]:
    """Return one finding string per invalid citation in `doc_path`.

    Finding format: `<doc>:<lineno> -> <cited-path>:<cited-line> <reason>`
    for `path:line` citations, and `<doc>:<lineno> -> <target>:§N
    section not found` for unresolvable `§N` anchors. Empty list means
    every citation in the doc resolves cleanly.
    """
    text = doc_path.read_text(encoding="utf-8")
    findings: list[str] = []
    for lineno, cited_path, start, end in extract_citations(text):
        reason = check_citation(repo_root, cited_path, start, end)
        if reason is None:
            continue
        cited_repr = f"{start}-{end}" if end is not None else str(start)
        findings.append(f"{doc_path}:{lineno} -> {cited_path}:{cited_repr} {reason}")
    for lineno, target_doc_name, major, minor in extract_section_refs(text):
        tail = check_section_anchor(repo_root, doc_path, target_doc_name, major, minor)
        if tail is None:
            continue
        findings.append(f"{doc_path}:{lineno} -> {tail}")
    return findings


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
        else:
            doc_args.append(args[i])
            i += 1

    if not doc_args:
        print(
            "usage: check_doc_citations.py <file.md> [more.md ...] "
            "[--repo-root PATH]",
            file=sys.stderr,
        )
        return 2

    all_findings: list[str] = []
    for doc_str in doc_args:
        doc_path = Path(doc_str)
        if not doc_path.is_file():
            print(f"usage error: not a file: {doc_str}", file=sys.stderr)
            return 2
        root = repo_root if repo_root is not None else find_repo_root(doc_path)
        all_findings.extend(check_doc(doc_path, root))

    if all_findings:
        for finding in all_findings:
            print(finding)
        return 1

    print("OK: all citations resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
