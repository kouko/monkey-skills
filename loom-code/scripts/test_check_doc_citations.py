"""Tests for check_doc_citations: path+anchor and path:line verification.

`check_doc(doc_path, repo_root)` scans one Markdown file for backtick
citations of the canonical `` `path` "verbatim anchor" `` form and the
legacy `` `path:line` `` / `` `path:line-range` `` forms. It verifies
anchors when supplied and otherwise bounds-checks legacy line numbers.

Round 4 (2026-07-29, plan Task 4 final): the default invocation now
runs ONLY the path:line bounds check (see module docstring's Round 4
note). Every test below that exercises the `§N` section-anchor check
now passes `check_sections=True` explicitly — see the "Update any
test whose pinned scenario this redefines" note in each such test's
comment, and the new "--- --sections flag" section at the bottom for
tests of the default-off / opt-in-on split itself.

Stdlib only (pathlib, re, sys, argparse-free manual arg parsing to
match check-living-spec-index.py's usage-error convention).
"""
from __future__ import annotations

from pathlib import Path

from check_doc_citations import (
    check_doc,
    check_doc_report,
    find_repo_root,
    list_repo_files,
    main,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_flags_out_of_range_line(tmp_path: Path) -> None:
    # target file has 3 lines
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(
        doc,
        "See `target.py:2` (in bounds) and `target.py:10` (out of bounds).\n",
    )

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "target.py:10" in findings[0]
    assert "target.py:2" not in findings[0]


def test_clean_doc_has_no_findings(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:1` and `target.py:3`.\n")

    assert check_doc(doc, tmp_path) == []


def test_missing_file_zero_suffix_match_is_unchecked(tmp_path: Path) -> None:
    # ROUND 2 (loom-code plan 2026-07-28 Task 3, round 2): previously this
    # produced a "file not found" finding. With the repo-wide suffix-match
    # fallback (see module docstring), a citation with ZERO suffix-match
    # candidates anywhere in the repo is UNCHECKED, not a finding — a
    # confident "file not found" claim from an inconclusive repo-wide
    # search would repeat the false-positive problem in mirror image.
    doc = tmp_path / "doc.md"
    _write(doc, "See `nope.py:1`.\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_pathless_shorthand_citation_is_unchecked_not_dropped(
    tmp_path: Path,
) -> None:
    # 2026-07-31: a citation written as a bare `` `:N-M` `` shorthand (the
    # path named in surrounding prose instead of inside the backticks) did
    # not match `_CITATION_RE` at all — its path group requires at least
    # one character — so it was dropped before extraction, contributing to
    # neither `checked` nor `unchecked`. A document whose citations are ALL
    # in this form reported `checked 0 / unchecked 0 / findings 0` and
    # exit 0: a silent pass byte-identical to "all citations resolve".
    # Counting it UNCHECKED (not a finding) follows the same principle
    # `check_doc_report`'s docstring already states for omitted `§N` refs —
    # never let the counts imply a citation was checked when it was not.
    doc = tmp_path / "doc.md"
    _write(doc, "See that audit's §8 (`:170-179`).\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_pathless_regex_does_not_double_count_a_real_citation(
    tmp_path: Path,
) -> None:
    # Parity with `_CITATION_RE`'s over-match guards: a resolvable
    # `path:line` citation must register once, as `checked` — never also as
    # a pathless shorthand, which would inflate both counters off one span.
    # Structurally guaranteed (the pathless pattern requires the backtick to
    # be immediately followed by `:`), pinned so a future relaxation of
    # either pattern cannot silently break it.
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:1`.\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.checked == 1
    assert report.unchecked == 0


def test_flags_out_of_range_line_range_end(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:2-10` (end past file length).\n")

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "target.py:2-10" in findings[0]


def test_in_range_line_range_not_flagged(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:1-3`.\n")

    assert check_doc(doc, tmp_path) == []


def test_finding_format_matches_doc_lineno_and_cited_target(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "first line\nSee `target.py:99`.\n")

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    doc_repr = str(doc)
    assert findings[0].startswith(f"{doc_repr}:2 -> target.py:99 ")


def test_bare_path_line_without_backticks_is_ignored(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See target.py:99 (no backticks, ignored in v1).\n")

    assert check_doc(doc, tmp_path) == []


def test_backtick_citation_without_extension_is_filtered(tmp_path: Path) -> None:
    # KNOWN v1 limitation: extensionless file paths like `Dockerfile:10` are
    # silently filtered by _looks_like_citation() because it requires a dot
    # in the final path component. This test pins that behavior for Task 3
    # (corpus reconciliation).
    _write(tmp_path / "Dockerfile", "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `Dockerfile:10` (extensionless, filtered in v1).\n")

    assert check_doc(doc, tmp_path) == []


def test_find_repo_root_walks_up_to_git_dir(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "docs" / "loom"
    nested.mkdir(parents=True)
    doc = nested / "doc.md"
    _write(doc, "no citations here\n")

    assert find_repo_root(doc) == tmp_path


def test_main_exits_1_on_findings(tmp_path: Path, capsys) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:99`.\n")

    rc = main([str(doc), "--repo-root", str(tmp_path)])

    assert rc == 1
    out = capsys.readouterr().out
    assert "target.py:99" in out


def test_main_exits_0_on_clean_doc(tmp_path: Path, capsys) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:1`.\n")

    rc = main([str(doc), "--repo-root", str(tmp_path)])
    out = capsys.readouterr().out

    assert rc == 0
    # Positive half of the success-line contract. Before 0.42.3 this test
    # took `capsys` and never read it, so BOTH print statements could be
    # deleted with the whole suite still green (whole-branch review,
    # 2026-07-31). The unqualified wording is correct here and only here:
    # nothing was skipped, so "all" ranges over everything examined.
    assert "OK: all citations resolve." in out


def test_main_scopes_the_ok_line_when_some_citations_were_unchecked(
    tmp_path: Path, capsys
) -> None:
    # Whole-branch review, 2026-07-31 — both code-arm reviewers independently
    # landed on this: the first cut of the fix guarded only `checked == 0`,
    # but the defect is the word "all" ranging over checked ∪ unchecked.
    # Mixed documents are the TYPICAL case (68 of the 72 files carrying a
    # pathless shorthand also carry a resolvable citation), and `main` sums
    # counts across every document in one invocation — requesting-docs-review
    # runs it over all changed .md files at once — so a single resolvable
    # citation anywhere re-armed the unqualified OK line for the whole batch.
    # The success line must state its own scope instead.
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "Real `target.py:1`, plus a shorthand (`:170-179`).\n")

    rc = main([str(doc), "--repo-root", str(tmp_path)])
    out = capsys.readouterr().out

    assert rc == 0
    assert "checked 1 / unchecked 1" in out
    assert "all 1 checked citations resolve" in out
    assert "1 unchecked" in out
    # The unqualified claim must NOT appear when anything was skipped.
    assert "OK: all citations resolve." not in out


def test_main_does_not_claim_all_resolve_when_nothing_was_checked(
    tmp_path: Path, capsys
) -> None:
    # 2026-07-31, second face of the pathless-shorthand bug: a doc whose
    # citations were ALL unresolvable still printed "OK: all citations
    # resolve." on exit 0. Nothing resolved — nothing was even checked —
    # so that line asserted a verification that never ran, which is the
    # exact misread the shorthand bug caused downstream (a docs-review
    # pre-pass folding this output into a dispatch packet reads it as a
    # clean bill). Exit code deliberately stays 0: "unverifiable" is not
    # "wrong", and flipping it would break every consumer of the current
    # contract. Only the claim is withdrawn.
    doc = tmp_path / "doc.md"
    _write(doc, "See that audit's §8 (`:170-179`).\n")

    rc = main([str(doc), "--repo-root", str(tmp_path)])
    out = capsys.readouterr().out

    assert rc == 0
    assert "checked 0 / unchecked 1" in out
    assert "all citations resolve" not in out
    # Positive assertion added after whole-branch review: pinning only the
    # absence let the NOTE branch be deleted with the suite still green.
    assert "nothing verified" in out


def test_main_exits_2_on_no_args() -> None:
    assert main([]) == 2


def test_main_exits_2_on_missing_doc_file(tmp_path: Path) -> None:
    assert main([str(tmp_path / "missing.md")]) == 2


# --- §N section-anchor checks (Task 2) ---
#
# Round 4: the §N check is now opt-in behind `--sections` (see module
# docstring's Round 4 note and the dedicated flag-behavior section at
# the bottom of this file). Every test below passes `check_sections=True`
# explicitly to keep exercising the mechanism these tests were written to
# pin — without it, none of these fixtures would produce a finding at
# all, and the test would pass for the wrong reason.


def test_flags_missing_section_anchor(tmp_path: Path) -> None:
    _write(
        tmp_path / "sibling.md",
        "## 1. One\n"
        "## 2. Two\n"
        "## 3. Three\n"
        "### 3.7 SubThree\n"
        "## 4. Four\n"
        "## 5. Five\n"
        "## 6. Six\n"
        "## 7. Seven\n",
    )
    doc = tmp_path / "doc.md"
    _write(
        doc,
        "See `sibling.md` §9 (missing).\n"
        "See `sibling.md` §3.7 (valid).\n",
    )

    findings = check_doc(doc, tmp_path, check_sections=True)

    assert len(findings) == 1
    assert findings[0] == f"{doc}:1 -> sibling.md:§9 section not found"


def test_bare_section_anchor_resolves_to_self_when_valid(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    _write(doc, "## 5. Some Heading\nSee §5 above.\n")

    assert check_doc(doc, tmp_path, check_sections=True) == []


def test_bare_section_anchor_self_ref_with_no_numbered_headings_is_unchecked(
    tmp_path: Path,
) -> None:
    # ROUND 3: redefines this scenario from round 2 (which expected a
    # "section not found" finding here). The citing doc itself has ZERO
    # numbered headings at all, so the §N grammar cannot be applied to it
    # in either direction — UNCHECKED, not a finding (see module docstring
    # §N applicability rule and test_flags_missing_section_anchor for the
    # contrasting case where a finding IS still correct).
    # ROUND 4: redefined again to pass check_sections=True — without it
    # the §N ref is never even extracted (default mode), which would make
    # this assertion trivially true for the wrong reason.
    doc = tmp_path / "doc.md"
    _write(doc, "See §9 above but no such heading exists.\n")

    report = check_doc_report(
        doc, tmp_path, list_repo_files(tmp_path), check_sections=True
    )

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_section_anchor_minor_does_not_match_major_only_heading(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "sibling2.md", "## 3. Three\n")
    doc = tmp_path / "doc2.md"
    _write(doc, "See `sibling2.md` §3.7 (no such subsection).\n")

    findings = check_doc(doc, tmp_path, check_sections=True)

    assert len(findings) == 1
    assert findings[0] == f"{doc}:1 -> sibling2.md:§3.7 section not found"


def test_date_style_heading_parses_as_section_number(tmp_path: Path) -> None:
    # KNOWN v1 false-resolve class: date-like headings without internal punctuation
    # (e.g. `## 2026 Release Notes`) parse as section 2026, so a citation like
    # `§2026` coincidentally resolves even though the heading looks like a date/title.
    _write(
        tmp_path / "target.md",
        "## 2026 Release Notes\nSome content here.\n",
    )
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.md` §2026 (year parses as section number).\n")

    findings = check_doc(doc, tmp_path, check_sections=True)

    # Should resolve without finding — the year (2026) gets parsed as section 2026,
    # so the citation coincidentally succeeds (false-resolve).
    assert len(findings) == 0

    # Discrimination: flip the assertion to show the test catches the opposite
    # (if we expected a finding, this would fail)
    assert check_doc(doc, tmp_path, check_sections=True) == []


def test_missing_target_doc_zero_suffix_match_is_unchecked(tmp_path: Path) -> None:
    # ROUND 2: v1 "folded" a missing target doc into a "section not found"
    # finding (treating "no such file" as "no headings"). With the suffix
    # fallback, a target doc name with ZERO repo-wide matches is UNCHECKED
    # instead — same reasoning as test_missing_file_zero_suffix_match_is_unchecked.
    doc = tmp_path / "doc.md"
    _write(doc, "See `absent.md` §3 (file missing).\n")

    report = check_doc_report(
        doc, tmp_path, list_repo_files(tmp_path), check_sections=True
    )

    assert report.findings == []
    assert report.unchecked == 1


def test_section_anchor_target_with_no_numbered_headings_is_unchecked(
    tmp_path: Path,
) -> None:
    # ROUND 3 (loom-code plan, round 3): the round-2 dogfood
    # (docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md, §Round 2)
    # measured 240/244 remaining findings as targets that use named
    # (non-numbered) headings only -- the §N grammar simply does not apply
    # to them. A resolved target with ZERO numbered headings can no longer
    # support a "does §N exist" adjudication at all -- UNCHECKED, not a
    # finding. Contrast test_flags_missing_section_anchor, where the target
    # DOES have numbered headings and a finding is still correct.
    _write(tmp_path / "named.md", "# Title\n## Problem\n## Users\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `named.md` §3 (target uses named headings only).\n")

    report = check_doc_report(
        doc, tmp_path, list_repo_files(tmp_path), check_sections=True
    )

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_multiple_anchors_bind_to_nearest_preceding_doc(tmp_path: Path) -> None:
    # When multiple document citations appear on one line, each section anchor
    # binds to the nearest preceding document (from _nearest_doc_name logic).
    _write(tmp_path / "one.md", "## 1. One\n## 2. Two\n")
    _write(tmp_path / "two.md", "## 1. One\n")
    doc = tmp_path / "doc.md"
    _write(
        doc,
        "See `one.md` §1 and `two.md` §2 (missing in two.md).\n",
    )

    findings = check_doc(doc, tmp_path, check_sections=True)

    # Should have exactly one finding: §2 is missing in two.md. §1 binds to
    # one.md (which has it), §2 binds to two.md (which lacks it).
    assert len(findings) == 1
    assert "two.md" in findings[0]

    # Discrimination: flip to one.md to show the error binds to the nearest
    # document, not a different one
    assert findings[0] == f"{doc}:1 -> two.md:§2 section not found"


# --- repo-wide suffix-match fallback (Task 3 round 2) ---
#
# Round-1 dogfood (docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md)
# measured a 79.7% false-positive rate, 95% of it one pattern: docs cite
# files by bare name or partial path, which the literal repo-root resolver
# can't follow. When the direct repo-root lookup fails, fall back to a
# repo-wide suffix match; a UNIQUE match resolves and bounds-checks
# normally, but ZERO or MULTIPLE matches are UNCHECKED — not a finding
# (see module docstring and the two updated tests above this section).
#
# The path:line-only tests in this section are unaffected by Round 4's
# `--sections` split — they never touch §N — so they keep the default
# `check_sections=False` call shape.


def test_suffix_fallback_resolves_unique_bare_name_in_bounds(tmp_path: Path) -> None:
    _write(tmp_path / "pkg" / "foo.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `foo.py:2` (bare name, lives under pkg/).\n")

    assert check_doc(doc, tmp_path) == []


def test_suffix_fallback_flags_out_of_range_on_resolved_target(tmp_path: Path) -> None:
    _write(tmp_path / "pkg" / "foo.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `foo.py:10` (bare name, out of range once resolved).\n")

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "foo.py:10" in findings[0]
    assert "exceeds file length" in findings[0]


def test_suffix_fallback_ambiguous_basename_is_unchecked_not_finding(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "a" / "dup.py", "line1\n")
    _write(tmp_path / "b" / "dup.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `dup.py:1` (ambiguous - two real targets).\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_suffix_fallback_zero_match_is_unchecked_not_finding(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    _write(doc, "See `totally_missing_file.py:1` (matches nothing anywhere).\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.unchecked == 1
    assert report.checked == 0


def test_section_anchor_doc_name_suffix_fallback_resolves(tmp_path: Path) -> None:
    _write(tmp_path / "nested" / "sibling.md", "## 1. One\n## 2. Two\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §2 (bare name, lives under nested/).\n")

    assert check_doc(doc, tmp_path, check_sections=True) == []


def test_section_anchor_doc_name_ambiguous_is_unchecked(tmp_path: Path) -> None:
    _write(tmp_path / "a" / "sibling.md", "## 1. One\n")
    _write(tmp_path / "b" / "sibling.md", "## 1. One\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §1 (ambiguous - two real targets).\n")

    report = check_doc_report(
        doc, tmp_path, list_repo_files(tmp_path), check_sections=True
    )

    assert report.findings == []
    assert report.unchecked == 1


def test_check_doc_report_counts_checked_and_unchecked(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(
        doc,
        "See `target.py:2` (checked, clean) and `totally_missing.py:1` "
        "(unchecked, zero match).\n",
    )

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.checked == 1
    assert report.unchecked == 1
    assert report.findings == []


def test_main_prints_checked_unchecked_findings_summary(
    tmp_path: Path, capsys
) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(
        doc,
        "See `target.py:1` (checked, clean) and `target.py:99` (checked, "
        "out of range) and `nope.py:1` (unchecked, zero match).\n",
    )

    rc = main([str(doc), "--repo-root", str(tmp_path)])

    out = capsys.readouterr().out
    assert rc == 1
    assert "checked 2 / unchecked 1 / findings 1" in out


# --- --sections flag: default off / opt-in on (Task 4 round 4) ---
#
# Split-half shipping decision (per the user, after 3 measured rounds --
# see docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md's Round 4
# disposition): the path:line bounds check measured 0% FP (8/8 confirmed
# true positives); the §N anchor check produced zero true positives on
# the whole corpus. Default invocation now runs ONLY the path:line check;
# §N moves behind an opt-in, experimental `--sections` flag.


def test_default_mode_emits_no_section_anchor_findings(tmp_path: Path) -> None:
    # This exact fixture is test_flags_missing_section_anchor's fixture,
    # which WOULD produce one §N finding under check_sections=True (see
    # that test above). In default mode the §N ref is never even
    # extracted, so it contributes to neither findings nor checked/
    # unchecked -- full omission, not a silent "checked and passed".
    _write(
        tmp_path / "sibling.md",
        "## 1. One\n## 2. Two\n## 3. Three\n",
    )
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §9 (missing, but only under --sections).\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.checked == 0
    assert report.unchecked == 0


def test_check_sections_true_restores_finding_on_same_fixture(
    tmp_path: Path,
) -> None:
    # Same fixture as the test above; check_sections=True must still catch
    # it, proving the flag -- not some other change -- gates the behavior.
    _write(
        tmp_path / "sibling.md",
        "## 1. One\n## 2. Two\n## 3. Three\n",
    )
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §9 (missing, but only under --sections).\n")

    report = check_doc_report(
        doc, tmp_path, list_repo_files(tmp_path), check_sections=True
    )

    assert len(report.findings) == 1
    assert report.findings[0] == f"{doc}:1 -> sibling.md:§9 section not found"


def test_main_default_mode_does_not_wire_sections_flag(
    tmp_path: Path, capsys
) -> None:
    _write(tmp_path / "sibling.md", "## 1. One\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §9 (missing, but default mode).\n")

    rc = main([str(doc), "--repo-root", str(tmp_path)])

    out = capsys.readouterr().out
    assert rc == 0
    assert "checked 0 / unchecked 0 / findings 0" in out
    assert "§" not in out


def test_main_sections_flag_enables_section_anchor_check(
    tmp_path: Path, capsys
) -> None:
    _write(tmp_path / "sibling.md", "## 1. One\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `sibling.md` §9 (missing, --sections enables this).\n")

    rc = main([str(doc), "--repo-root", str(tmp_path), "--sections"])

    out = capsys.readouterr().out
    assert rc == 1
    assert "sibling.md:§9 section not found" in out


# --- anchor substring verification (paired `"..."` on same line) ---


def test_line_less_citation_whose_anchor_is_absent_is_flagged(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "target.md", "different text\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.md` "missing anchor".\n')

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "quoted string not found in target" in findings[0]


def test_line_less_citation_whose_anchor_is_present_is_clean(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "target.md", "the stable anchor survives\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.md` "stable anchor".\n')

    assert check_doc(doc, tmp_path) == []


def test_line_less_inline_code_without_anchor_is_not_a_citation(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "target.md", "content\n")
    doc = tmp_path / "doc.md"
    _write(doc, "Use `target.md` as the input file.\n")

    report = check_doc_report(doc, tmp_path, list_repo_files(tmp_path))

    assert report.findings == []
    assert report.checked == 0
    assert report.unchecked == 0


def test_mixed_line_less_and_legacy_citations_pair_with_their_own_anchors(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "a.md", "alpha\n")
    _write(tmp_path / "b.md", "beta\n")
    doc = tmp_path / "doc.md"
    _write(doc, '`a.md` "alpha" and `b.md:1` "not beta"\n')

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "b.md:1" in findings[0]


def test_a_citation_whose_quoted_string_is_absent_from_the_target_is_flagged(
    tmp_path: Path,
) -> None:
    # A backtick `path:line` citation carrying a paired `"..."` quote whose
    # string does NOT occur in the target file is flagged. The substring
    # (anchor) check is the new primary verification; the line-bounds check
    # remains as a secondary check.
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.py:1` "this string is not in the file".\n')

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "target.py" in findings[0]


def test_a_citation_whose_quoted_string_is_present_in_the_target_is_clean(
    tmp_path: Path,
) -> None:
    # The paired `"..."` string DOES occur in the target file — no finding.
    _write(tmp_path / "target.py", "the verbatim string is here\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.py:1` "the verbatim string".\n')

    assert check_doc(doc, tmp_path) == []


def test_a_citation_whose_anchor_resolves_but_line_is_out_of_bounds_is_clean(
    tmp_path: Path,
) -> None:
    # The anchor (paired `"..."` string) is the PRIMARY check; the line
    # number is optional precision. When the anchor resolves as a verbatim
    # substring in the target file, the citation is clean — a stale
    # out-of-bounds line does NOT invalidate a resolved anchor (the rule
    # this checker enforces: the anchor survives the change that writes
    # it, the line number rots within it). Pre-fix this returned the
    # "line ... exceeds file length" finding because line-bounds ran first
    # and short-circuited before the anchor check.
    _write(tmp_path / "target.py", "the verbatim string is here\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.py:999` "the verbatim string".\n')

    assert check_doc(doc, tmp_path) == []


def test_citation_without_paired_quote_is_unaffected(tmp_path: Path) -> None:
    # Backward compatibility: a citation with NO paired `"..."` quote on the
    # same line is unaffected — the substring check does not fire.
    _write(tmp_path / "target.py", "line1\nline2\nline3\n")
    doc = tmp_path / "doc.md"
    _write(doc, "See `target.py:1` (no paired quote, unaffected).\n")

    assert check_doc(doc, tmp_path) == []


def test_citation_with_empty_paired_quote_is_flagged(tmp_path: Path) -> None:
    _write(tmp_path / "target.py", "line1\n")
    doc = tmp_path / "doc.md"
    _write(doc, 'See `target.py:1` "".\n')

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "quoted string not found in target" in findings[0]


def test_multiple_citations_each_use_their_adjacent_quote(tmp_path: Path) -> None:
    _write(tmp_path / "a.py", "alpha\n")
    _write(tmp_path / "b.py", "beta\n")
    doc = tmp_path / "doc.md"
    _write(doc, '`a.py:1` "alpha" and `b.py:1` "beta"\n')

    assert check_doc(doc, tmp_path) == []
