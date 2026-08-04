"""Tests for claim_copy_sweep.py — the repair-side claim enumerator.

WHY this tool exists: docs/loom/memory/enumerate-every-copy-before-editing-a-claim
-and-name-the-leaks.md records the rule ("enumerate every copy before editing
any"), and the review-scope-resolver arc violated it twice — once by the author
who had written it hours earlier. The rule asked a repairer to hand-assemble a
grep; this makes it one command.

The load-bearing behaviour is WRAP-INSENSITIVITY. This repo's prose is hard-
wrapped (docs/loom/memory line length: median 69, p90 81), so a claim spanning
two physical lines matches no contiguous grep — and
docs/loom/memory/verbatim-phrase-guards-break-on-hard-line-wrap.md records a
live instance where exactly that made a correction silently no-op AND made its
verification grep confirm the false success. A sweep that misses wrapped copies
reproduces the defect it exists to prevent, so the wrapped-copy tests below are
the RED that matters.

Fixtures build a REAL temporary repo tree so the script's actual file walking,
classification and reporting are exercised, not a mock of them.
"""

import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "claim_copy_sweep.py"

CLAIM = "the resolver refuses when freshness cannot be established"


def run(repo_root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), *args],
        capture_output=True,
        text=True,
    )


def write(repo_root, rel, text):
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the load-bearing case: a copy split across a hard wrap ----------------


def test_finds_a_copy_split_across_a_hard_wrap(tmp_path):
    """A claim wrapped mid-phrase is a copy. A contiguous grep misses it."""
    write(
        tmp_path,
        "docs/loom/specs/wrapped.md",
        "Intro line.\n\nWe decided that the resolver refuses when freshness\n"
        "cannot be established, which is the whole point.\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/wrapped.md:3" in result.stdout, result.stdout


def test_reports_the_line_where_the_match_starts_not_where_it_ends(tmp_path):
    """A wrapped match anchors to its first physical line, so the reader opens
    the right place."""
    write(
        tmp_path,
        "docs/loom/specs/anchor.md",
        "one\ntwo\nthree\nthe resolver refuses when freshness\ncannot be established\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert "docs/loom/specs/anchor.md:4" in result.stdout, result.stdout
    assert "anchor.md:5" not in result.stdout, result.stdout


def test_finds_an_unwrapped_copy_too(tmp_path):
    write(tmp_path, "docs/loom/plans/flat.md", f"Body. {CLAIM}. Tail.\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert "docs/loom/plans/flat.md:1" in result.stdout, result.stdout


def test_reports_every_copy_not_just_the_first(tmp_path):
    write(tmp_path, "docs/loom/specs/a.md", f"{CLAIM}\n")
    write(tmp_path, "docs/loom/plans/b.md", f"x\n{CLAIM}\n")
    write(tmp_path, "docs/loom/audits/c.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    for expected in ("specs/a.md:1", "plans/b.md:2", "audits/c.md:1"):
        assert expected in result.stdout, (expected, result.stdout)


def test_two_copies_in_one_file_are_both_reported(tmp_path):
    write(tmp_path, "docs/loom/specs/twice.md", f"{CLAIM}\n\nfiller\n\n{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert "twice.md:1" in result.stdout, result.stdout
    assert "twice.md:5" in result.stdout, result.stdout


# --- operative vs frozen ---------------------------------------------------


def test_changelog_copy_is_classified_frozen(tmp_path):
    """Rewriting a CHANGELOG falsifies history — big-rename-operative-frozen-sweep
    records a live instance of a sweep doing exactly that."""
    write(tmp_path, "loom-code/CHANGELOG.md", f"- {CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    frozen_section = result.stdout.split("frozen locations")[-1]
    assert "loom-code/CHANGELOG.md:1" in frozen_section, result.stdout


def test_archive_and_dogfood_copies_are_frozen(tmp_path):
    write(tmp_path, "docs/loom/archive/old.md", f"{CLAIM}\n")
    write(tmp_path, "docs/loom/dogfood/run.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    frozen_section = result.stdout.split("frozen locations")[-1]
    assert "docs/loom/archive/old.md:1" in frozen_section, result.stdout
    assert "docs/loom/dogfood/run.md:1" in frozen_section, result.stdout


def test_spec_copy_is_classified_operative(tmp_path):
    write(tmp_path, "docs/loom/specs/live.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    operative_section = result.stdout.split("frozen locations")[0]
    assert "docs/loom/specs/live.md:1" in operative_section, result.stdout


def test_extra_frozen_prefix_can_be_declared(tmp_path):
    write(tmp_path, "vendor/notes.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM, "--frozen", "vendor/")
    frozen_section = result.stdout.split("frozen locations")[-1]
    assert "vendor/notes.md:1" in frozen_section, result.stdout


# --- declared alternate phrasings (the prh-shaped answer to the synonym leak)


def test_also_flag_sweeps_a_declared_alternate_phrasing(tmp_path):
    write(tmp_path, "docs/loom/specs/synonym.md", "a stale base makes the review refuse\n")
    result = run(
        tmp_path, "--claim", CLAIM, "--also", "a stale base makes the review refuse"
    )
    assert "docs/loom/specs/synonym.md:1" in result.stdout, result.stdout


def test_also_flag_is_repeatable(tmp_path):
    write(tmp_path, "docs/loom/specs/one.md", "phrasing one here\n")
    write(tmp_path, "docs/loom/specs/two.md", "phrasing two here\n")
    result = run(
        tmp_path,
        "--claim",
        CLAIM,
        "--also",
        "phrasing one here",
        "--also",
        "phrasing two here",
    )
    assert "docs/loom/specs/one.md:1" in result.stdout, result.stdout
    assert "docs/loom/specs/two.md:1" in result.stdout, result.stdout


# --- fenced code blocks: reported, and marked -----------------------------


def test_copy_inside_a_fence_is_reported_and_marked(tmp_path):
    """check_doc_citations.py cannot tell a fenced example from a live citation
    and ate 2/2 false positives on its own dogfood note. This tool reports the
    hit either way and marks it, so the judgement stays with the reader."""
    write(
        tmp_path,
        "docs/loom/specs/fenced.md",
        f"Prose.\n\n```\n{CLAIM}\n```\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert "docs/loom/specs/fenced.md:4" in result.stdout, result.stdout
    assert "fence" in result.stdout.lower(), result.stdout


def test_unfenced_hit_is_not_marked_as_fenced(tmp_path):
    write(tmp_path, "docs/loom/specs/plain.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    hit_line = [ln for ln in result.stdout.splitlines() if "plain.md:1" in ln][0]
    assert "fence" not in hit_line.lower(), hit_line


# --- the named leaks are never silent -------------------------------------


def test_named_leaks_are_always_printed(tmp_path):
    """A rule that hides what it misses ships as reliable and misses silently —
    the memory entry is named for this."""
    write(tmp_path, "docs/loom/specs/a.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    lowered = result.stdout.lower()
    assert "synonym" in lowered, result.stdout
    assert "self-referential" in lowered or "self referential" in lowered, result.stdout


def test_leaks_are_printed_even_when_nothing_matched(tmp_path):
    write(tmp_path, "docs/loom/specs/a.md", "unrelated prose\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "synonym" in result.stdout.lower(), result.stdout


def test_zero_hits_says_so_rather_than_printing_an_empty_list(tmp_path):
    """`"0" in stdout` would pass unconditionally — every run prints
    "alternate phrasings declared: 0". Pin the sentinel the name claims."""
    write(tmp_path, "docs/loom/specs/a.md", "unrelated prose\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert "(none)" in result.stdout, result.stdout
    assert "operative locations (0)" in result.stdout, result.stdout


# --- one normalization rule, one implementation -----------------------------


def test_needle_and_haystack_normalize_identically_on_final_sigma(tmp_path):
    """Whole-string `.lower()` applies Greek final-sigma; per-character
    `.lower()` does not. Two implementations of one rule let a copy hide from
    the sweep — the tool's own core failure mode."""
    write(tmp_path, "docs/loom/specs/greek.md", "we say ΟΔΟΣ here\n")
    result = run(tmp_path, "--claim", "we say ΟΔΟΣ here")
    assert "docs/loom/specs/greek.md:1" in result.stdout, result.stdout


def test_expanding_lowercase_does_not_crash_the_sweep(tmp_path):
    """U+0130 lowercases to two characters. One map entry per SOURCE character
    instead of per EMITTED character desynchronizes the index-to-line map, and
    a long enough run indexes past its end — an uncaught IndexError that takes
    down the whole sweep, not just one file."""
    write(
        tmp_path,
        "docs/loom/specs/dotted.md",
        "İ" * 40 + "\nfiller line\n" + CLAIM + "\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    assert "docs/loom/specs/dotted.md:3" in result.stdout, result.stdout


# --- direct unit tests of the load-bearing helpers -------------------------
#
# Every test above drives the CLI through a subprocess, which is why the
# defects these pin were all invisible to a green suite: nothing called the
# tricky functions directly.

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claim_copy_sweep  # noqa: E402  (not `as sweep` — the module has a sweep())


@pytest.mark.parametrize(
    "text",
    [
        "we say ΟΔΟΣ here",
        "İ" * 5 + "\nclaim\n",
        "plain ascii text",
        "  leading and trailing  ",
        "hard\nwrapped\tprose",
    ],
)
def test_normalize_agrees_with_normalize_with_lines(text):
    """One rule, one implementation. The needle comes from `normalize` and the
    haystack from `normalize_with_lines`; any divergence is a silent miss."""
    assert claim_copy_sweep.normalize(text) == claim_copy_sweep.normalize_with_lines(text)[0]


@pytest.mark.parametrize("text", ["İ" * 5 + "\nclaim\n", "ΟΔΟΣ\nclaim\n", "a\nb\n"])
def test_line_map_has_one_entry_per_normalized_character(text):
    normalized, line_of = claim_copy_sweep.normalize_with_lines(text)
    assert len(normalized) == len(line_of), (len(normalized), len(line_of))


def test_find_in_text_never_indexes_past_the_line_map():
    """The desync surfaced as an uncaught IndexError, not a wrong line."""
    assert claim_copy_sweep.find_in_text("claim", "İ" * 5 + "\nclaim\n") == [(2, False)]


def test_fence_delimiter_lines_count_as_outside():
    """Both delimiters, per the docstring — the opening one already did."""
    states = claim_copy_sweep.fence_state_by_line("a\n```\nX\n```\nb\n")
    assert states[2] is False, states  # opening ```
    assert states[3] is True, states  # the fenced content
    assert states[4] is False, states  # closing ``` — was True


# --- case FOLDING, not case mapping ----------------------------------------


def test_uppercase_claim_matches_naturally_lowercased_prose(tmp_path):
    """`str.lower()` is a case MAPPING and leaves ς and σ distinct, so the
    mirror of the sigma case still missed: a human types ΟΔΟΣ, the document on
    disk carries the natural lowercase οδος. Symmetry of function is not
    symmetry of input — only a case FOLDING closes it."""
    write(tmp_path, "docs/loom/specs/sigma.md", "The street sign reads οδος here.\n")
    result = run(tmp_path, "--claim", "The street sign reads ΟΔΟΣ here.")
    assert "docs/loom/specs/sigma.md:1" in result.stdout, result.stdout


def test_nfd_copy_on_disk_matches_an_nfc_claim(tmp_path):
    """casefold is not a Unicode normalization. macOS copy-paste yields NFD, and
    this repo carries 中/日 prose, so an NFD copy against an NFC needle is an
    ordinary way to get a confident `operative locations (0)`."""
    nfd = unicodedata.normalize("NFD", "分支が古いと審査は résumé を拒否する")
    nfc = unicodedata.normalize("NFC", "分支が古いと審査は résumé を拒否する")
    assert nfd != nfc, "fixture must actually differ, or the test proves nothing"
    write(tmp_path, "docs/loom/specs/nfd.md", nfd + "\n")
    result = run(tmp_path, "--claim", nfc)
    assert "docs/loom/specs/nfd.md:1" in result.stdout, result.stdout


def test_a_directory_it_cannot_enter_is_named_not_skipped(tmp_path):
    """File-level read errors are already named. A directory the walk cannot
    enter takes its .md files with it and, before this, left no trace at all."""
    write(tmp_path, "docs/loom/specs/ok.md", f"{CLAIM}\n")
    locked = tmp_path / "docs" / "loom" / "locked"
    locked.mkdir(parents=True)
    (locked / "hidden.md").write_text(f"{CLAIM}\n", encoding="utf-8")
    locked.chmod(0o000)
    try:
        result = run(tmp_path, "--claim", CLAIM)
    finally:
        locked.chmod(0o755)
    assert result.returncode == 0, result.stderr
    assert "could not read" in result.stdout.lower(), result.stdout
    assert "locked" in result.stdout, result.stdout


def test_markup_interior_to_the_claim_is_a_named_leak(tmp_path):
    """`the resolver **refuses** when …` is the same words, so the synonym leak
    does not cover it. Deliberately NOT fixed — named, per this module's own
    contract. Both halves are pinned: the miss must still happen, and LEAKS must
    still name it. A substring check on LEAKS alone cannot fail when the
    behaviour changes, which is the prose-drifts-from-behaviour shape this
    module's own docstring warns about."""
    write(
        tmp_path,
        "docs/loom/specs/markup.md",
        "the resolver **refuses** when freshness cannot be established\n",
    )
    write(tmp_path, "docs/loom/specs/sentinel.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert "docs/loom/specs/sentinel.md:1" in result.stdout, result.stdout
    assert "docs/loom/specs/markup.md" not in result.stdout, result.stdout
    assert "markup" in claim_copy_sweep.LEAKS.lower(), claim_copy_sweep.LEAKS


def test_canonical_caseless_match_survives_precomposed_vs_decomposed(tmp_path):
    """Folding without re-normalizing is not a canonical caseless match
    (UAX#15 D145 normalizes AFTER folding). `casefold` expands some precomposed
    characters back into a decomposed sequence; without a final NFC the two
    sides land on different codepoints and the sweep reports a clean all-clear
    on a document that carries the claim."""
    on_disk = "ΐς"  # ΐς — precomposed iota with dialytika and tonos
    typed = "Ϊ́Σ"  # the uppercase form, decomposed
    write(tmp_path, "docs/loom/specs/greek2.md", f"reads {on_disk} here\n")
    result = run(tmp_path, "--claim", f"reads {typed} here")
    assert "docs/loom/specs/greek2.md:1" in result.stdout, result.stdout


def test_normalization_is_idempotent():
    """A non-idempotent fold means the two sides can never be relied on to meet."""
    for text in ["ΐ", "Ϊ́", "Straße", "İstanbul", "ΟΔΟΣ"]:
        once = claim_copy_sweep.normalize(text)
        assert claim_copy_sweep.normalize(once) == once, text


@pytest.mark.parametrize(
    "text",
    [
        "ΟΔΟΣ",
        "οδος",
        "ΣΣΣ",
        "Straße",
        "STRASSE",
        "İstanbul",
        "ﬁle",
        "ǅ",
        "ẞ",
        # U+0345 iota subscript with a second combining mark: the classic
        # casefold non-invariance trap, and the ONLY case that pins the FIRST
        # NFC pass. Without it, deleting `normalize("NFC", text)` leaves the
        # whole suite green — found by mutation, not by reading.
        # Written as escapes deliberately: the two combining marks must stay
        # in THIS order (U+0345 then U+0301); reversed, the mutant survives,
        # and a literal here is one editor away from being silently reordered.
        "\u0428\u0345\u0301",
    ],
)
def test_normalization_is_canonical_caseless_match(text):
    """The pipeline is NFC → casefold → NFC, the canonical caseless match of
    UAX#15 D145. Pinning it against an independently computed reference fails
    immediately on a revert to `.lower()` (`"ΟΔΟΣ".lower()` is `οδος` while
    `.casefold()` is `οδοσ`) and on dropping either normalization pass."""
    reference = unicodedata.normalize(
        "NFC", unicodedata.normalize("NFC", text).casefold()
    )
    assert claim_copy_sweep.normalize(text) == reference


# --- --frozen is a declaration, and it is visible --------------------------


def test_empty_frozen_prefix_is_refused(tmp_path):
    """An empty prefix matches every path, so every hit lands in the frozen
    bucket and the report prints `operative locations (0)` — this tool's own
    worst output, a confident all-clear."""
    write(tmp_path, "docs/loom/specs/live.md", f"{CLAIM}\n")
    assert_usage_error(run(tmp_path, "--claim", CLAIM, "--frozen", ""))
    assert_usage_error(run(tmp_path, "--claim", CLAIM, "--frozen", "   "))


def test_report_echoes_the_frozen_rule_in_effect(tmp_path):
    """The brief's words: the classification is written into the report so the
    user can see what they are relying on."""
    write(tmp_path, "docs/loom/specs/live.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM, "--frozen", "vendorlib/")
    assert "frozen rule in effect:" in result.stdout, result.stdout
    assert "vendorlib/" in result.stdout, result.stdout
    assert "CHANGELOG.md" in result.stdout, result.stdout


@pytest.mark.parametrize(
    "rel_path,extra,expected",
    [
        ("loom-code/CHANGELOG.md", (), True),
        ("docs/RELEASE-CHANGELOG.md", (), False),
        ("docs/loom/archive/old.md", (), True),
        ("docs/loom/dogfood/run.md", (), True),
        ("docs/loom/specs/live.md", (), False),
        ("vendor/notes.md", ("vendor/",), True),
        ("vendorlib/live.md", ("vendor",), True),  # raw prefix: documented, echoed
        ("vendorlib/live.md", ("vendor/",), False),
    ],
)
def test_is_frozen_classification(rel_path, extra, expected):
    """`is_frozen` was the one load-bearing helper reachable only through a
    subprocess, and it is the one that shipped a defect."""
    assert claim_copy_sweep.is_frozen(rel_path, extra) is expected


# --- frozen classification is by basename, not path suffix -----------------


def test_a_file_merely_ending_in_changelog_md_is_not_frozen(tmp_path):
    """`endswith("CHANGELOG.md")` also matches RELEASE-CHANGELOG.md. Misfiling
    an operative file as history means the reader's edit misses that copy."""
    write(tmp_path, "docs/RELEASE-CHANGELOG.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    operative_section = result.stdout.split("frozen locations")[0]
    assert "docs/RELEASE-CHANGELOG.md:1" in operative_section, result.stdout


# --- an unreadable file is a named leak, never a silent skip ---------------


def test_an_undecodable_file_is_reported_not_silently_skipped(tmp_path):
    """The module's stated contract is that what it cannot see gets named. A
    file it could not read is exactly that."""
    write(tmp_path, "docs/loom/specs/ok.md", f"{CLAIM}\n")
    bad = tmp_path / "docs" / "loom" / "specs" / "bad.md"
    bad.write_bytes(b"\xff\xfe\x00broken\xff")
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/bad.md" in result.stdout, result.stdout
    assert "could not read" in result.stdout.lower(), result.stdout


# --- fence delimiters are outside the fence, as the docstring says ---------


def test_closing_fence_delimiter_is_not_marked_inside(tmp_path):
    write(
        tmp_path,
        "docs/loom/specs/delim.md",
        f"prose\n```\nfenced\n```\n{CLAIM}\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    hit_line = [ln for ln in result.stdout.splitlines() if "delim.md:5" in ln][0]
    assert "fence" not in hit_line.lower(), hit_line


# --- scope and hygiene -----------------------------------------------------


def test_non_markdown_files_are_not_swept(tmp_path):
    """Absence assertions must prove the sweep RAN — otherwise they pass for a
    missing script, a crashed run, or an empty walk (see
    docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md)."""
    write(tmp_path, "scripts/thing.py", f"# {CLAIM}\n")
    write(tmp_path, "docs/loom/specs/sentinel.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/sentinel.md:1" in result.stdout, result.stdout
    assert "thing.py" not in result.stdout, result.stdout


def test_py_module_docstring_copy_is_reported(tmp_path):
    """`.py` MODULE docstrings are in scope now (Decision 2); function/class
    docstrings and other string literals stay out by construction. The
    module-docstring claim is hard-wrapped across a line break to exercise
    normalize, and its reported line must be the ACTUAL file line."""
    write(tmp_path, "docs/loom/specs/md_copy.md", f"{CLAIM}\n")
    write(
        tmp_path,
        "scripts/module_docstring.py",
        '"""We decided that the resolver refuses when freshness\n'
        'cannot be established, which is the whole point."""\n',
    )
    write(
        tmp_path,
        "scripts/function_docstring_only.py",
        '"""Unrelated module docstring."""\n'
        "\n\n"
        "def foo():\n"
        f'    """{CLAIM}"""\n'
        "    pass\n",
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/md_copy.md:1" in result.stdout, result.stdout
    assert "scripts/module_docstring.py:1" in result.stdout, result.stdout
    assert "function_docstring_only.py" not in result.stdout, result.stdout


def test_output_names_python_docstring_scope(tmp_path):
    """The self-describing output must name the extended scope (Decision 2):
    the summary line counts scanned `.py` module docstrings, and the LEAKS
    block's absolute `.md`-only claim is replaced by one that also carves out
    `.py` module docstrings and names the newly-adjacent non-leaks (function/
    class docstrings, other string literals) that stay out of scope."""
    write(tmp_path, "docs/loom/specs/sentinel.md", f"{CLAIM}\n")
    write(
        tmp_path,
        "scripts/module_docstring.py",
        '"""We decided that the resolver refuses when freshness\n'
        'cannot be established, which is the whole point."""\n',
    )
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "python module docstrings" in result.stdout, result.stdout

    normalized = claim_copy_sweep.normalize(result.stdout)
    new_leak = claim_copy_sweep.normalize(
        "anything outside `.md` files and `.py` module docstrings — a copy "
        "living in a code comment, a function or class docstring, a "
        "non-docstring string literal, a test fixture, or a commit message "
        "is out of scope by construction."
    )
    assert new_leak in normalized, result.stdout

    old_leak = claim_copy_sweep.normalize("anything outside `.md` files —")
    assert old_leak not in normalized, result.stdout


def test_git_directory_is_skipped(tmp_path):
    write(tmp_path, ".git/notes.md", f"{CLAIM}\n")
    write(tmp_path, "docs/loom/specs/sentinel.md", f"{CLAIM}\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/sentinel.md:1" in result.stdout, result.stdout
    assert ".git" not in result.stdout, result.stdout


def test_case_differences_do_not_hide_a_copy(tmp_path):
    write(tmp_path, "docs/loom/specs/case.md", CLAIM.capitalize() + "\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert "docs/loom/specs/case.md:1" in result.stdout, result.stdout


# --- usage errors ----------------------------------------------------------


def assert_usage_error(result):
    """Exit 2 alone is not enough — the interpreter also exits 2 when the script
    file is absent, so a bare returncode check passes before any code exists."""
    assert result.returncode == 2, (result.returncode, result.stdout, result.stderr)
    assert "usage" in result.stderr.lower(), result.stderr


def test_unparseable_py_lands_on_unreadable_list(tmp_path):
    """A `.py` the parser rejects must be LISTED, not skipped in silence —
    the module contract's fail-loud promise, extended to the python scope
    (whole-branch review finding: the SyntaxError→unreadable route shipped
    untested). Paired positive: the `.md` copy still reports, proving the
    sweep itself ran."""
    write(tmp_path, "docs/loom/specs/md_copy.md", f"{CLAIM}\n")
    write(tmp_path, "scripts/broken.py", "def broken(:\n")
    result = run(tmp_path, "--claim", CLAIM)
    assert result.returncode == 0, result.stderr
    assert "docs/loom/specs/md_copy.md:1" in result.stdout, result.stdout
    assert "files this run could not read" in result.stdout, result.stdout
    assert "scripts/broken.py (SyntaxError)" in result.stdout, result.stdout


def test_missing_claim_is_a_usage_error(tmp_path):
    assert_usage_error(run(tmp_path))


def test_empty_claim_is_a_usage_error(tmp_path):
    assert_usage_error(run(tmp_path, "--claim", "   "))


def test_claim_flag_without_a_value_is_a_usage_error(tmp_path):
    assert_usage_error(run(tmp_path, "--claim"))
