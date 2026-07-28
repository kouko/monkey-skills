"""Tests for check_doc_citations: path:line citation bounds checking.

`check_doc(doc_path, repo_root)` scans one Markdown file for backtick
citations of the form `` `path:line` `` or `` `path:line-range` `` and
returns one finding string per citation whose target file is missing
or whose line (or range end) exceeds the target file's length. Clean
citations produce no finding.

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

    assert rc == 0


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
