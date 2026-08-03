#!/usr/bin/env python3
"""Enumerate every copy of a claim across the repo's Markdown prose.

The rule this executes lives in
`docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`:
before editing a claim that may exist in more than one place, enumerate the
population first. That rule asked a repairer to hand-assemble a grep, and the
review-scope-resolver arc violated it twice — once by the author who had
written it hours earlier. This makes the enumeration one command.

WHY whitespace normalization is the load-bearing part: this repo's prose is
hard-wrapped, so a claim spanning two physical lines matches no contiguous
grep. `docs/loom/memory/verbatim-phrase-guards-break-on-hard-line-wrap.md`
records a live instance where that made a correction silently no-op AND made
its verification grep confirm the false success. Both the haystack and the
needle are collapsed to single spaces (and lowercased) before matching, so a
wrap cannot hide a copy in either direction.

WHY there is exactly ONE normalization implementation, and why it folds rather
than lowercases: there were two implementations and they disagreed. `normalize`
used a whole-string `str.lower()` (which applies the Greek final-sigma rule:
`ΟΔΟΣ` → `οδος`) while the haystack was built character by character
(`Σ` → `σ`), so a document containing the claim verbatim returned NO hits —
the tool's own core failure mode, in the tool. Deriving `normalize` from
`normalize_with_lines` closed that, but **symmetry of function is not symmetry
of input**: the needle is typed by a human and the haystack is on disk, so a
non-folding rule still splits one word into two needles. `str.lower()` is a
case MAPPING; the mirror case (`ΟΔΟΣ` typed against `οδος` on disk) still
missed. The rule is now `str.casefold()`, a case FOLDING, which maps `ς` and
`σ` to the same character. Verified context-free (per-character == whole-string
across ΟΔΟΣ / οδος / Straße / STRASSE / İstanbul / ﬁle / ǅ / ẞ / Ὀδυσσεύς), so
the per-emitted-character loop below stays valid — and it already absorbs the
1→2 expansions casefold introduces (`ß` → `ss`).

WHY this reports and never edits: `docs/loom/memory/big-rename-operative-frozen-sweep.md`
records an automated sweep rewriting prose ABOUT the sweep into
self-contradiction — a CHANGELOG line stating the docs archive was NOT renamed
got itself renamed. Enumeration is the job; the edit stays with a human or an
agent that can read what each copy is for. Hits are partitioned into operative
(an edit must cover these) and frozen (editing these falsifies the record),
and the partition is printed rather than applied.

WHY the leaks are always printed: the memory entry is named for them. A sweep
that hides what it cannot see ships as reliable and misses silently. That
includes files this run could not read — they are listed, not skipped in
silence.

Read-only. Stdlib only (`os`, `pathlib`, `re`, `sys`).

Exit codes: 0 = the sweep ran (any number of hits, including none);
2 = usage error. There is deliberately no "found too many" failure code — this
is a reporter, not a gate.
"""

import os
import re
import sys
from pathlib import Path

DEFAULT_FROZEN_PREFIXES = (
    "docs/loom/archive/",
    "docs/loom/dogfood/",
)
DEFAULT_FROZEN_BASENAMES = frozenset({"CHANGELOG.md"})

_WHITESPACE_RUN = re.compile(r"\s+")


def normalize_with_lines(text: str) -> tuple[str, list[int]]:
    """Normalize `text` and return the 1-based source line of each output char.

    Whitespace runs collapse to one space. A run containing a newline carries
    the line the run STARTED on, so a match spanning a hard wrap anchors to its
    first physical line — the place a reader should open.

    The map gains one entry per EMITTED character, not per source character:
    `"İ".casefold()` is two characters (as is `"ß".casefold()`), and one entry
    per source character desynchronized the map for everything after it —
    surfacing as an uncaught IndexError that took down the whole sweep, not as
    a merely wrong line.
    """
    out: list[str] = []
    lines: list[int] = []
    line = 1
    in_run = False
    for ch in text:
        if ch.isspace():
            if not in_run:
                out.append(" ")
                lines.append(line)
                in_run = True
            if ch == "\n":
                line += 1
        else:
            for folded_ch in ch.casefold():
                out.append(folded_ch)
                lines.append(line)
            in_run = False
    start = 0
    end = len(out)
    while start < end and out[start] == " ":
        start += 1
    while end > start and out[end - 1] == " ":
        end -= 1
    return "".join(out[start:end]), lines[start:end]


def normalize(text: str) -> str:
    """The needle's normalization — derived from the haystack's, never parallel
    to it. See the module docstring's ONE-implementation note."""
    return normalize_with_lines(text)[0]


def fence_state_by_line(text: str) -> list[bool]:
    """Return, per 1-based source line, whether that line sits inside a fence.

    Both delimiter lines count as outside. Fences are tracked rather than
    skipped: `check_doc_citations.py` cannot tell a fenced example from a live
    one and ate false positives on its own dogfood note, while silently
    skipping fences would hide copies that ARE the thing being edited (a rule
    quoted verbatim inside a fence is still a copy). Reporting both and marking
    which is which leaves the judgement with the reader.

    Known limit, stated: only ``` fences are tracked, not `~~~`, and a ``` in
    an indented block toggles the state.
    """
    states = [False]  # index 0 unused; lines are 1-based
    inside = False
    for raw in text.split("\n"):
        is_delimiter = raw.strip().startswith("```")
        states.append(inside and not is_delimiter)
        if is_delimiter:
            inside = not inside
    return states


def iter_markdown_files(repo_root: Path):
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield Path(dirpath) / name


def is_frozen(rel_path: str, extra_prefixes: tuple[str, ...]) -> bool:
    """Frozen = a record editing would falsify. Basename match, not a path
    suffix — `endswith("CHANGELOG.md")` also swallowed RELEASE-CHANGELOG.md,
    and misfiling an operative file as frozen hides a copy the reader's edit
    must cover, which is this tool's own failure mode.

    `--frozen` prefixes are matched raw, so `--frozen vendor` also captures
    `vendorlib/`. That is the caller's choice and the report echoes every
    prefix in effect so it is visible; an EMPTY prefix is refused at intake
    because it would match everything and print a confident `operative
    locations (0)` all-clear."""
    if Path(rel_path).name in DEFAULT_FROZEN_BASENAMES:
        return True
    prefixes = DEFAULT_FROZEN_PREFIXES + extra_prefixes
    return any(rel_path.startswith(prefix) for prefix in prefixes)


def find_in_text(needle: str, text: str) -> list[tuple[int, bool]]:
    """Return (line, inside_fence) for every occurrence of `needle` in `text`."""
    if not needle:
        return []
    haystack, line_of = normalize_with_lines(text)
    fences = fence_state_by_line(text)
    hits: list[tuple[int, bool]] = []
    pos = haystack.find(needle)
    while pos != -1:
        line = line_of[pos]
        inside = fences[line] if line < len(fences) else False
        hits.append((line, inside))
        pos = haystack.find(needle, pos + 1)
    return hits


def sweep(repo_root: Path, needles: list[str], extra_prefixes: tuple[str, ...]):
    operative: list[tuple[str, int, bool]] = []
    frozen: list[tuple[str, int, bool]] = []
    unreadable: list[str] = []
    swept = 0
    for path in iter_markdown_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            unreadable.append(f"{rel} ({type(exc).__name__})")
            continue
        swept += 1
        seen: set[int] = set()
        for needle in needles:
            for line, inside in find_in_text(needle, text):
                if line in seen:
                    continue
                seen.add(line)
                bucket = frozen if is_frozen(rel, extra_prefixes) else operative
                bucket.append((rel, line, inside))
    operative.sort()
    frozen.sort()
    unreadable.sort()
    return operative, frozen, unreadable, swept


LEAKS = """what this sweep CANNOT see (named here rather than hidden):
  - a synonym: the same proposition restated in different words matches no
    string search at all. Declare each phrasing you know about with --also;
    the ones you do not know about stay invisible, and no flag changes that.
  - a self-referential count: a number describing the document it sits in
    changes when the sentence stating it changes, so no fixed string can find
    its next value.
  - anything outside `.md` files — a copy living in a code comment, a test
    fixture, or a commit message is out of scope by construction."""


def render(claim, alternates, operative, frozen, unreadable, swept, extra_prefixes=()) -> str:
    frozen_rule = ", ".join(
        sorted(DEFAULT_FROZEN_BASENAMES) + list(DEFAULT_FROZEN_PREFIXES) + list(extra_prefixes)
    )
    lines = [
        f'claim: "{claim}"',
        f"swept {swept} markdown files; alternate phrasings declared: {len(alternates)}",
        f"frozen rule in effect: {frozen_rule}",
        "",
        f"operative locations ({len(operative)}) — an edit to this claim must "
        "cover these (one entry per source line):",
    ]
    lines.extend(_render_hits(operative))
    lines.append("")
    lines.append(
        f"frozen locations ({len(frozen)}) — history; editing these falsifies the record:"
    )
    lines.extend(_render_hits(frozen))
    lines.append("")
    if unreadable:
        lines.append(
            f"files this run could not read ({len(unreadable)}) — NOT searched, "
            "so any copy in them is unaccounted for:"
        )
        lines.extend(f"  {entry}" for entry in unreadable)
        lines.append("")
    lines.append(LEAKS)
    return "\n".join(lines)


def _render_hits(hits) -> list[str]:
    if not hits:
        return ["  (none)"]
    return [
        f"  {rel}:{line}" + ("  [inside fence]" if inside else "")
        for rel, line, inside in hits
    ]


def usage(message: str) -> int:
    print(f"usage error: {message}", file=sys.stderr)
    print(
        "usage: claim_copy_sweep.py --claim TEXT [--also TEXT ...] "
        "[--frozen PREFIX ...] [--repo-root PATH]",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    repo_root = Path(__file__).resolve().parents[1]
    claim: str | None = None
    alternates: list[str] = []
    extra_prefixes: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--claim", "--also", "--frozen", "--repo-root"):
            if i + 1 >= len(args):
                return usage(f"{arg} requires a value")
            value = args[i + 1]
            if arg == "--claim":
                claim = value
            elif arg == "--also":
                alternates.append(value)
            elif arg == "--frozen":
                if not value.strip():
                    return usage(
                        "--frozen requires a non-empty prefix; an empty one "
                        "matches every path and would report a false "
                        "'operative locations (0)' all-clear"
                    )
                extra_prefixes.append(value)
            else:
                repo_root = Path(value).resolve()
            i += 2
            continue
        return usage(f"unknown argument: {arg}")

    if claim is None:
        return usage("--claim is required")
    if not normalize(claim):
        return usage("--claim must contain non-whitespace text")
    if not repo_root.is_dir():
        return usage(f"not a directory: {repo_root}")

    needles = [normalize(claim)]
    for alternate in alternates:
        normalized = normalize(alternate)
        if normalized and normalized not in needles:
            needles.append(normalized)

    operative, frozen, unreadable, swept = sweep(
        repo_root, needles, tuple(extra_prefixes)
    )
    print(
        render(
            claim,
            alternates,
            operative,
            frozen,
            unreadable,
            swept,
            tuple(extra_prefixes),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
