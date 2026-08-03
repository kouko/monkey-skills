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
missed. The rule is now the canonical caseless match of UAX#15 D145 —
**NFC → casefold → NFC**. The second normalization is not decoration:
`casefold` EXPANDS some precomposed characters back into a decomposed sequence
(the Greek dialytika+tonos set), so folding without re-normalizing leaves a
precomposed copy on disk and a decomposed needle sitting on different
codepoints — another silent `operative locations (0)`, found by review after
the first normalization pass had already shipped. The per-emitted-character map
absorbs every length change either pass introduces, expansions (`ß` → `ss`) and
compositions alike.

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

Read-only. Stdlib only (`os`, `pathlib`, `sys`, `unicodedata`).

Exit codes: 0 = the sweep ran (any number of hits, including none);
2 = usage error. There is deliberately no "found too many" failure code — this
is a reporter, not a gate.
"""

import os
import sys
import unicodedata
from pathlib import Path

DEFAULT_FROZEN_PREFIXES = (
    "docs/loom/archive/",
    "docs/loom/dogfood/",
)
DEFAULT_FROZEN_BASENAMES = frozenset({"CHANGELOG.md"})


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
    in_run = False
    # NFC -> casefold -> NFC, per line. The canonical caseless match of
    # UAX#15 D145: casefold is NOT a normalization, and it EXPANDS some
    # precomposed characters back into a decomposed sequence, so folding
    # without re-normalizing leaves the two sides on different codepoints
    # (observed on the Greek dialytika+tonos set). Running it per line keeps
    # one map entry per EMITTED character while letting each pass see a whole
    # line: NFC never alters newline count or position, so line numbers are
    # unaffected and `fence_state_by_line` still indexes the same lines.
    for lineno, raw_line in enumerate(
        unicodedata.normalize("NFC", text).split("\n"), start=1
    ):
        for ch in unicodedata.normalize("NFC", raw_line.casefold()):
            if ch.isspace():
                if not in_run:
                    out.append(" ")
                    lines.append(lineno)
                    in_run = True
            else:
                out.append(ch)
                lines.append(lineno)
                in_run = False
        # The newline that ended this line is whitespace too, and a run
        # spanning a hard wrap carries the line it STARTED on.
        if not in_run:
            out.append(" ")
            lines.append(lineno)
            in_run = True
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


def iter_markdown_files(repo_root: Path, unreadable: list[str]):
    """Walk for `.md` files, recording directories the walk could not enter.

    `os.walk` defaults to `onerror=None`, which SWALLOWS a directory-level
    error: every `.md` inside an unreadable directory vanishes with no trace,
    no entry in the could-not-read list, and an exit 0. That is the same
    silent-miss the file-level handler exists to prevent, one level up, and it
    under-reports — the dangerous direction.
    """

    def on_error(exc: OSError) -> None:
        unreadable.append(f"{exc.filename} ({type(exc).__name__}, directory)")

    for dirpath, dirnames, filenames in os.walk(repo_root, onerror=on_error):
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


def _find_prepared(needle, haystack, line_of, fences) -> list[tuple[int, bool]]:
    """The matching core, over an already-prepared haystack."""
    if not needle:
        return []
    hits: list[tuple[int, bool]] = []
    pos = haystack.find(needle)
    while pos != -1:
        line = line_of[pos]
        inside = fences[line] if line < len(fences) else False
        hits.append((line, inside))
        pos = haystack.find(needle, pos + 1)
    return hits


def find_in_text(needle: str, text: str) -> list[tuple[int, bool]]:
    """Return (line, inside_fence) for every occurrence of `needle` in `text`.

    Convenience wrapper for a single needle; `sweep` prepares the haystack once
    per file and calls `_find_prepared` directly.
    """
    haystack, line_of = normalize_with_lines(text)
    return _find_prepared(needle, haystack, line_of, fence_state_by_line(text))


def sweep(repo_root: Path, needles: list[str], extra_prefixes: tuple[str, ...]):
    operative: list[tuple[str, int, bool]] = []
    frozen: list[tuple[str, int, bool]] = []
    unreadable: list[str] = []
    swept = 0
    for path in iter_markdown_files(repo_root, unreadable):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            unreadable.append(f"{rel} ({type(exc).__name__})")
            continue
        swept += 1
        # Hoisted out of the needle loop: both are needle-independent, and
        # recomputing them per needle made cost linear in --also count on a
        # flag that is the tool's own answer to its named synonym leak.
        haystack, line_of = normalize_with_lines(text)
        fences = fence_state_by_line(text)
        seen: set[int] = set()
        for needle in needles:
            for line, inside in _find_prepared(needle, haystack, line_of, fences):
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
  - markup INTERIOR to the claim: `the resolver **refuses** when …` is the same
    words, not a synonym, and the emphasis markers sit inside the phrase, so
    the match fails. Links, code spans and emphasis are ordinary in this prose.
    Sweep a fragment that avoids the markup, or sweep both forms with --also.
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
