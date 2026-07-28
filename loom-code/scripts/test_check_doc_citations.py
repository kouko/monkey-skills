"""Tests for check_doc_citations: path:line citation bounds checking.

`check_doc(doc_path, repo_root)` scans one Markdown file for backtick
citations of the form `` `path:line` `` or `` `path:line-range` `` and
returns one finding string per citation whose target file is missing
or whose line (or range end) exceeds the target file's length. Clean
citations produce no finding.

Stdlib only (pathlib, re, sys, argparse-free manual arg parsing to
match check-living-spec-index.py's usage-error convention).
"""
from __future__ import annotations

from pathlib import Path

from check_doc_citations import check_doc, find_repo_root, main


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


def test_flags_missing_file(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    _write(doc, "See `nope.py:1`.\n")

    findings = check_doc(doc, tmp_path)

    assert len(findings) == 1
    assert "nope.py:1" in findings[0]
    assert "not found" in findings[0]


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
