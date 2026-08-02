"""Tests for loom_gate_markers — the gate-marker CLI the SDD orchestrator
runs so hooks/git-guard.py can enforce review/verify gates mechanically.

Each test builds a THROWAWAY git repo under tmp_path (git init + empty
commit). No dependency on the outer repo. Marker JSON is parsed and
asserted field-by-field against the frozen contract.

External-surface grounding (source a — live verification): the git
flags the CLI depends on (`rev-parse --git-dir`, `rev-parse
--abbrev-ref HEAD`, `rev-parse HEAD`, `git show <rev>:<path>`, `git
cat-file -t <rev>:<path>`) are exercised LIVE by this suite against the
throwaway repos above — every happy-path test both drives them through
the CLI and re-runs them directly via `_git()` to cross-check
branch/sha values, so a flag regression in the installed git surfaces
here, not via belief. `git show <rev>:<path>` and `git cat-file -t
<rev>:<path>` back the origin-quote verification path
(`_show_committed_file`) added in Task 2; their failure-mode shapes
(sha-unresolvable / file-absent / non-blob / undecodable-blob) are each
exercised against a real throwaway repo by the tests below, not
asserted from documentation.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from loom_gate_markers import main


def _git(repo: Path, *args: str) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "commit", "--allow-empty", "-m", "init")
    return repo


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def _marker_dir(repo: Path) -> Path:
    return repo / ".git" / "loom"


VALID_VERDICT = """\
standards_version: 2026-06
verdict: PASS
dimension_scores:
  security: 5
  correctness: 5
findings:
  - severity: yellow
    where: loom-code/scripts/foo.py:12
    dimension: correctness
    origin: none
    note: naming nit
"""


def _write_verdict(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "verdict.md"
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- review-pass


def test_review_pass_writes_marker_matching_contract(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    marker = _marker_dir(repo) / "review-pass.json"
    assert marker.is_file()
    data = json.loads(marker.read_text(encoding="utf-8"))
    # Exact field set — no extras, no omissions (frozen contract).
    assert set(data) == {"schema", "branch", "head_sha", "verdict", "written_at"}
    assert data["schema"] == 1
    assert data["branch"] == _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    assert data["head_sha"] == _head(repo)
    assert len(data["head_sha"]) == 40  # full sha, not abbreviated
    assert data["verdict"] == "PASS"
    datetime.fromisoformat(data["written_at"])  # parses as iso8601
    # Marker path printed for the orchestrator.
    assert str(marker) in capsys.readouterr().out


def test_review_pass_with_notes_accepted(tmp_path):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, VALID_VERDICT.replace("verdict: PASS", "verdict: PASS_WITH_NOTES")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "review-pass.json").read_text(encoding="utf-8")
    )
    assert data["verdict"] == "PASS_WITH_NOTES"


def test_review_needs_revision_exits_3_and_writes_nothing(tmp_path):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, VALID_VERDICT.replace("verdict: PASS", "verdict: NEEDS_REVISION")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 3
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_review_missing_keys_exits_4_listing_them(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    # Only a verdict line — standards_version + dimension_scores missing.
    verdict_file = _write_verdict(tmp_path, "verdict: PASS\n")

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "standards_version" in err
    assert "dimension_scores" in err


def test_review_invalid_verdict_value_exits_4(tmp_path):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, VALID_VERDICT.replace("verdict: PASS", "verdict: MAYBE")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_review_finding_without_where_exits_4(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    note: opaque finding, no location\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    assert "where" in capsys.readouterr().err


def test_review_empty_standards_version_exits_4(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    # Key present but value empty — must be treated as missing.
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version:\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    assert "standards_version" in capsys.readouterr().err


def test_review_finding_where_commit_sha_accepted(tmp_path):
    # Reviewer output contract allows `where: <commit SHA>` — bare hex
    # (7-40 chars) must count as a path-like token.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: yellow\n"
        "    where: 610dbc409c7e\n"
        "    dimension: correctness\n"
        "    origin: none\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_review_finding_where_without_pathlike_token_exits_4(tmp_path, capsys):
    # dimension: correctness + origin: none are present and well-formed so
    # this fixture refuses ONLY on the not-path-like where: — otherwise a
    # broken _PATHLIKE_RE would still exit 4 via the (absent) origin
    # requirement and this test would pass for the wrong reason.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: everywhere\n"
        "    dimension: correctness\n"
        "    origin: none\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert "where" in capsys.readouterr().err


# ------------------------------------------------------- origin (code-arm gate)


def _verdict_with_finding(
    *,
    where="loom-code/scripts/foo.py:12",
    severity="red",
    dimension_line=None,
    origin_line=None,
):
    """Build verdict text with one finding block. `dimension_line`/
    `origin_line` are None to omit the key entirely, "" to include the
    key with an empty value, or a string to include the key with that
    value — this distinguishes "no dimension: line" from "dimension:
    with nothing after it" for the fail-closed partition tests."""
    lines = [
        "standards_version: 2026-06",
        "verdict: PASS",
        "dimension_scores:",
        "  security: 5",
        "findings:",
        f"  - severity: {severity}",
        f"    where: {where}",
    ]
    if dimension_line is not None:
        lines.append(f"    dimension: {dimension_line}")
    if origin_line is not None:
        lines.append(f"    origin: {origin_line}")
    lines.append("    note: finding note")
    return "\n".join(lines) + "\n"


def test_code_arm_finding_without_origin_refuses_to_mint(tmp_path):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, _verdict_with_finding(dimension_line="correctness")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_docs_arm_finding_without_origin_still_mints(tmp_path):
    # Discriminating case against over-reach: a naive GLOBAL origin:
    # requirement satisfies every other criterion and fails only this
    # one, blocking every docs-only and mixed-branch push.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, _verdict_with_finding(dimension_line="omission")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


@pytest.mark.parametrize(
    "dimension_line",
    [None, "performance", ""],
    ids=["no-dimension-line", "unrecognized-value", "empty-value"],
)
def test_finding_with_unparseable_dimension_refuses_without_origin(
    tmp_path, dimension_line
):
    # Discriminating case against under-reach (§Pinned dimension
    # partition, fail-closed clause): a finding with no parseable
    # dimension: must refuse without origin:, not escape the check.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path, _verdict_with_finding(dimension_line=dimension_line)
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


@pytest.mark.parametrize(
    "origin_line",
    ["none", 'docs/loom/plans/x.md :: "seven call sites"'],
    ids=["none-value", "path-and-quote"],
)
def test_origin_none_and_quoted_value_validate(tmp_path, origin_line):
    repo = _init_repo(tmp_path)
    if "::" in origin_line:
        # A quoted origin now must also verify against committed content
        # (Task 2) — commit the file the quote names so this test keeps
        # asserting its original intent (a grammar-valid origin mints).
        _commit_file(repo, "docs/loom/plans/x.md", "seven call sites\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(dimension_line="correctness", origin_line=origin_line),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


@pytest.mark.parametrize(
    "origin_line",
    [
        "docs/loom/plans/x.md",
        '"seven call sites"',
        'docs/loom/plans/x.md :: ""',
        'docs/loom/plans/x.md :: "   "',
    ],
    ids=[
        "path-value-no-separator",
        "quote-value-no-separator",
        "empty-quote",
        "whitespace-only-quote",
    ],
)
def test_origin_bare_path_or_bare_quote_refuses(tmp_path, origin_line):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(dimension_line="correctness", origin_line=origin_line),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_origin_quote_containing_separator_splits_on_first_occurrence(tmp_path):
    # A path may not contain ` :: `; a quote may. Splitting on the FIRST
    # ` :: ` treats everything after it as the quote, so a quote
    # containing the separator string is accepted whole rather than
    # mis-parsed into a truncated path and an unquoted remainder.
    repo = _init_repo(tmp_path)
    # Quote verification (Task 2) now needs the quote to actually be
    # committed under this path for the finding to mint.
    _commit_file(repo, "p.md", "a :: b\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='p.md :: "a :: b"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_duplicate_dimension_lines_treated_as_unparseable_requires_origin(tmp_path):
    # Two `dimension:` lines in one block must not resolve first-wins (or
    # last-wins) into a docs-arm exemption — YAML readers disagree on
    # which value wins, so a duplicate is unparseable and, by the
    # fail-closed clause, requires origin: like any other unparseable
    # dimension.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: loom-code/scripts/foo.py:12\n"
        "    dimension: omission\n"
        "    dimension: correctness\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_duplicate_origin_lines_refuses_to_mint(tmp_path):
    # Same question as duplicate dimension:, decided the same way: two
    # origin: lines in one block is malformed input, not "first one
    # wins" — refuse rather than silently pick either value.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: loom-code/scripts/foo.py:12\n"
        "    dimension: correctness\n"
        "    origin: none\n"
        '    origin: p.md :: "quoted text"\n',
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


# --------------------------------------------- field column anchoring (nesting)


def test_dimension_nested_inside_note_does_not_grant_exemption(tmp_path):
    # A `dimension:` line quoted inside a note's YAML block-literal (e.g. a
    # pasted verdict-schema example) is NOT a sibling field of this finding
    # block — the block has no dimension: of its own, so the fail-closed
    # clause must refuse it, not read the nested line as a docs-arm grant.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: a/b.py:12\n"
        "    note: |\n"
        "      ```\n"
        "      dimension: omission\n"
        "      ```\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_origin_nested_inside_note_does_not_satisfy_requirement(tmp_path):
    # Mirror case: a code-arm finding (dimension: correctness, sibling)
    # with an `origin:` line only inside the nested note block-literal.
    # The finding has no origin: of its own and must refuse.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: a/b.py:12\n"
        "    dimension: correctness\n"
        "    note: |\n"
        "      ```\n"
        "      origin: none\n"
        "      ```\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_where_nested_inside_note_does_not_satisfy_requirement(tmp_path, capsys):
    # The pre-existing where: check carries the identical weakness — a
    # `where:` line quoted inside a nested note must not count as this
    # finding's own where:. Deliberately tightened alongside dimension:/
    # origin: rather than left as a second convention.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    dimension: correctness\n"
        "    origin: none\n"
        "    note: |\n"
        "      ```\n"
        "      where: a/b.py:12\n"
        "      ```\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    assert "where" in capsys.readouterr().err


def test_finding_fields_at_consistent_nonstandard_indent_still_mints(tmp_path):
    # The rule is same-column-as-siblings, never a hardcoded column count —
    # a well-formed finding whose fields all sit at 6 spaces (not the usual
    # 4) must still mint.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "      where: a/b.py:12\n"
        "      dimension: correctness\n"
        "      origin: none\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_finding_with_blank_line_before_first_field_still_mints(tmp_path):
    # A blank line directly after `- severity:` is ordinary formatting.
    # The old column-detection read `lines[start + 1]` literally, so a
    # blank line there set column = "" and every real field line (all
    # indented) was then skipped as "wrong column" — a false refusal
    # even though where:/dimension:/origin: are all present, correctly
    # indented, and mutually consistent.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "\n"
        "    where: a/b.py:12\n"
        "    dimension: correctness\n"
        "    origin: none\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_arm_dimension_partition_is_disjoint():
    # §Pinned dimension partition claims "verified disjoint 2026-08-02" —
    # mechanically enforced here rather than trusted as a comment, and
    # via the module's own runtime check so a future edit to either set
    # fails loud at import time, not just in this one test.
    from loom_gate_markers import (
        _CODE_ARM_DIMENSIONS,
        _DOCS_ARM_DIMENSIONS,
        _check_arm_disjoint,
    )

    assert _CODE_ARM_DIMENSIONS.isdisjoint(_DOCS_ARM_DIMENSIONS)
    _check_arm_disjoint(_CODE_ARM_DIMENSIONS, _DOCS_ARM_DIMENSIONS)  # no raise


def test_arm_dimension_partition_check_raises_on_overlap():
    from loom_gate_markers import _check_arm_disjoint

    with pytest.raises(AssertionError):
        _check_arm_disjoint({"x", "y"}, {"y", "z"})


# ------------------------------------------------- origin quote verification


def _commit_file(repo: Path, rel_path: str, content: str) -> None:
    """Write `content` to `rel_path` inside `repo` and commit it."""
    full = repo / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    _git(repo, "add", rel_path)
    _git(repo, "commit", "-q", "-m", f"add {rel_path}")


def test_origin_quote_present_only_in_worktree_refuses_to_mint(tmp_path):
    # Committed content lacks the quoted sentence; the on-disk (uncommitted)
    # file contains it. The check must read the commit, never the worktree —
    # a Path.read_text() implementation would wrongly pass this.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "Nothing quotable here.\n")
    (repo / "docs" / "note.md").write_text(
        "Nothing quotable here. The quoted sentence appears now.\n",
        encoding="utf-8",
    )
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "The quoted sentence appears now."',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_validate_dry_run_reports_quote_verification_did_not_run(tmp_path, capsys):
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "some quote"',
        ),
    )

    rc = main(["validate", "--verdict-file", str(verdict_file)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "quote verification did not run" in out.lower()


def test_origin_quote_present_in_commit_mints(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "The exact quoted sentence is here.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "The exact quoted sentence is here."',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_origin_quote_absent_at_sha_refuses_with_distinct_message(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "Nothing like the quote in here.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "a totally different sentence"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "docs/note.md" in err
    assert "a totally different sentence" in err


def test_origin_file_absent_at_sha_refuses_with_distinct_message(tmp_path, capsys):
    repo = _init_repo(tmp_path)  # docs/note.md never committed
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line=(
                'docs/note.md :: "a quote from a file that never existed"'
            ),
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "docs/note.md" in err
    assert "does not exist" in err


def test_origin_none_skips_quote_verification_entirely(tmp_path):
    repo = _init_repo(tmp_path)  # no files beyond the init commit
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(dimension_line="correctness", origin_line="none"),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_show_committed_file_sha_unresolvable_distinguished_from_absent(tmp_path):
    # Unreachable through _cmd_review_pass: the existing `if branch is None
    # or head_sha is None` guard returns 2 before quote verification runs,
    # since head_sha always comes from a live `rev-parse HEAD` on a real
    # repo. Exercised directly on the helper instead (plan Task 2 GREEN).
    from loom_gate_markers import _show_committed_file

    repo = _init_repo(tmp_path)
    bad_sha = "0" * 40  # well-formed hex, does not resolve to any commit

    content, failure_kind = _show_committed_file(repo, bad_sha, "docs/note.md")

    assert content is None
    assert failure_kind == "sha-unresolvable"


def test_show_committed_file_distinguishes_file_absent_from_sha_unresolvable(
    tmp_path,
):
    from loom_gate_markers import _show_committed_file

    repo = _init_repo(tmp_path)
    head = _head(repo)

    content, failure_kind = _show_committed_file(repo, head, "nope.md")

    assert content is None
    assert failure_kind == "file-absent"


def test_show_committed_file_classifies_gitlink_with_object_present_as_not_a_file(
    tmp_path,
):
    # A gitlink's classification is CONDITIONAL on whether the linked
    # commit object is present in this repo's local object store, not a
    # fixed property of gitlinks (see the THIRD verified quirk in
    # _show_committed_file's docstring — a prior version of this
    # docstring wrongly stated the object-absent outcome as the only
    # outcome). This test constructs the PRESENT branch: fetch the
    # linked commit into `repo`'s own object store before reading the
    # gitlink path, so `cat-file -t` finds a real object and reports
    # `commit` (non-blob) — landing in `_NOT_A_FILE`, the same branch a
    # directory takes, not `_FILE_ABSENT`.
    from loom_gate_markers import _show_committed_file

    sub = tmp_path / "subrepo"
    sub.mkdir()
    _git(sub, "init", "-q")
    _git(sub, "config", "user.email", "test@example.com")
    _git(sub, "config", "user.name", "Test User")
    _git(sub, "commit", "--allow-empty", "-m", "sub init")
    sub_sha = _git(sub, "rev-parse", "HEAD")
    sub_branch = _git(sub, "rev-parse", "--abbrev-ref", "HEAD")

    repo = _init_repo(tmp_path)
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{sub_sha},mysub")
    _git(repo, "commit", "-m", "add gitlink")
    head = _head(repo)

    # Bring the linked commit object into repo's own object store by
    # fetching the subrepo's branch tip. This is what distinguishes the
    # PRESENT branch from the ABSENT one — without this fetch, `sub_sha`
    # stays an object `repo` never learned about.
    _git(
        repo,
        "fetch",
        str(sub),
        f"{sub_branch}:refs/remotes/subrepo/{sub_branch}",
    )
    assert _git(repo, "cat-file", "-t", sub_sha) == "commit"

    content, failure_kind = _show_committed_file(repo, head, "mysub")

    assert content is None
    assert failure_kind == "not-a-file"


def test_normalized_tier_matches_across_hard_wrapped_lines_and_is_recorded(
    tmp_path, capsys
):
    # This repo hard-wraps prose, so a truthful one-line quote of a
    # multi-line passage fails byte-exact matching by construction — the
    # normalised tier (whitespace runs collapsed to one space) must still
    # mint, and the output must record that it matched only at that tier
    # (§Notes kickoff decision: the tier is the observable that separates
    # "no quotable origins" from "the matcher rejected true ones").
    repo = _init_repo(tmp_path)
    _commit_file(
        repo,
        "docs/note.md",
        "This function computes the discounted cash flow across all\n"
        "periods for the given schedule.\n",
    )
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line=(
                'docs/note.md :: "This function computes the discounted '
                'cash flow across all periods for the given schedule."'
            ),
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    out = capsys.readouterr().out
    assert "normalis" in out.lower()  # "normalised"/"normalisation"


def test_normalized_tier_folds_typographic_quotes_dashes_and_nbsp(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(
        repo,
        "docs/note.md",
        "It’s the pre–flight check — done.\n",
    )
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "It\'s the pre-flight check - done."',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_normalized_match_is_case_sensitive_and_refuses(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "Hello World, this is committed.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "hello world, this is committed."',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_normalizer_does_not_strip_markdown_emphasis_or_backticks(tmp_path):
    # The normaliser folds whitespace/typography only — it must not strip
    # `**`/backticks, or a quote of the rendered prose would wrongly match
    # markdown source that never contained that literal text.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "plain text, no markdown here.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "**plain text, no markdown here.**"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_normalizer_does_not_strip_backticks(tmp_path):
    # Sibling case to the `**` test above: backticks must survive the
    # normaliser too, or a quote of rendered prose could wrongly match
    # markdown source that never contained that literal text.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/note.md", "plain text, no markdown here.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "`plain text, no markdown here.`"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_normalizer_folds_nfd_needle_against_nfc_haystack(tmp_path):
    # NFC-normalize both sides: an NFD-decomposed quote (e.g. combining
    # accent as a separate codepoint) must still match NFC-composed
    # committed content.
    import unicodedata

    repo = _init_repo(tmp_path)
    composed = "café committed here.\n"  # NFC: e + U+00E9 (é)
    assert unicodedata.is_normalized("NFC", composed)
    _commit_file(repo, "docs/note.md", composed)
    decomposed_quote = "café committed here."  # NFD: e + combining acute
    assert not unicodedata.is_normalized("NFC", decomposed_quote)
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line=f'docs/note.md :: "{decomposed_quote}"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_normalize_for_quote_match_is_symmetric_on_typographic_marks(tmp_path):
    # The SAME normaliser must be applied to both the quote and the
    # haystack (§Notes kickoff decision) — verified directly on the
    # helper rather than through the CLI: normalising a string already
    # containing the ASCII-folded forms must be idempotent, and folding
    # each typographic mark individually must equal folding all of them
    # together (order-independence of the substitution).
    from loom_gate_markers import _normalize_for_quote_match

    marks = "It’s the pre–flight check — done. Really."
    once = _normalize_for_quote_match(marks)
    twice = _normalize_for_quote_match(once)
    assert once == twice  # idempotent
    assert once == _normalize_for_quote_match(
        "It's the pre-flight check - done. Really."
    )


def test_origin_directory_path_refuses_to_mint(tmp_path):
    # `git show <sha>:<dir>` exits 0 and prints a git-generated tree
    # listing, not repository content — a directory path must never be
    # treated as a readable origin (FATAL: this mints a quote from thin
    # air, since the listing's filenames are content the reviewer never
    # read).
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/a.md", "hello\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs :: "a.md"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_origin_directory_path_trailing_slash_refuses_to_mint(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/a.md", "hello\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/ :: "a.md"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


def test_origin_directory_tree_header_word_refuses_to_mint(tmp_path, capsys):
    # The header word `git show` prints for ANY tree object is the
    # literal string "tree" — a quote of exactly that word needs no
    # knowledge of the directory's contents to "match", which is the
    # sharpest form of the bypass.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/a.md", "hello\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs :: "tree"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "docs" in err


def test_origin_quote_undecodable_blob_refuses_without_crash(tmp_path, capsys):
    # A non-UTF-8 blob must be refused as its own explicit failure kind,
    # never an uncaught UnicodeDecodeError traceback (which would leak
    # interpreter paths and mint no marker only by accident of the crash).
    repo = _init_repo(tmp_path)
    (repo / "bin.dat").write_bytes(b"\x80\x81\x82PNGtail")
    _git(repo, "add", "bin.dat")
    _git(repo, "commit", "-q", "-m", "add binary")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='bin.dat :: "PNG"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "bin.dat" in err


def test_review_pass_marker_carries_origin_quote_tier_counts(tmp_path):
    # §Notes kickoff decision: the tier count must be collected from the
    # first finding, or the pre-registered ≥40-finding stop rule has no
    # observable separating "no quotable origins existed" from "the
    # matcher rejected true ones".
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/exact.md", "The exact quoted sentence is here.\n")
    _commit_file(repo, "docs/norm.md", "It’s the pre–flight check.\n")
    text = "\n".join(
        [
            "standards_version: 2026-06",
            "verdict: PASS",
            "dimension_scores:",
            "  security: 5",
            "findings:",
            "  - severity: red",
            "    where: loom-code/scripts/foo.py:12",
            "    dimension: correctness",
            '    origin: docs/exact.md :: "The exact quoted sentence is here."',
            "    note: exact-tier finding",
            "  - severity: yellow",
            "    where: loom-code/scripts/bar.py:5",
            "    dimension: correctness",
            "    origin: docs/norm.md :: \"It's the pre-flight check.\"",
            "    note: normalised-tier finding",
        ]
    ) + "\n"
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    marker = _marker_dir(repo) / "review-pass.json"
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert data["origin_quote_tiers"] == {"exact": 1, "normalised": 1}


# ------------------------------------------------------------------- verified

# A real command that exits 0 and prints a sentinel we assert is captured
# (proves output_tail records the ACTUAL run, not a typed string), and a
# real command that exits non-zero.
RUN_OK = "python3 -c \"print('loom-real-run-sentinel')\""
RUN_FAIL = "python3 -c \"import sys; sys.exit(1)\""


def test_verified_runs_command_and_writes_marker_recording_it(tmp_path):
    # The marker binds to a REAL run: --run executes, we mint only on
    # exit 0, and the payload records the command + its captured output
    # (was: a self-typed --suite-line string that proved no run happened).
    repo = _init_repo(tmp_path)

    rc = main(["verified", "--repo", str(repo), "--run", RUN_OK])

    assert rc == 0
    marker = _marker_dir(repo) / "verified.json"
    data = json.loads(marker.read_text(encoding="utf-8"))
    # git-guard-critical fields preserved; suite_line gone.
    assert data["schema"] == 1
    assert data["head_sha"] == _head(repo)
    assert "suite_line" not in data
    # Real run recorded: the command, its exit code, a tail of its output.
    assert data["run_cmd"] == RUN_OK
    assert data["exit_code"] == 0
    assert "loom-real-run-sentinel" in data["output_tail"]
    datetime.fromisoformat(data["written_at"])


def test_verified_failing_command_writes_no_marker_and_exits_nonzero(tmp_path):
    repo = _init_repo(tmp_path)

    rc = main(["verified", "--repo", str(repo), "--run", RUN_FAIL])

    assert rc != 0
    assert not (_marker_dir(repo) / "verified.json").exists()


def test_verified_no_longer_accepts_suite_line(tmp_path):
    # The self-typed --suite-line mint path is REMOVED: `verified` binds
    # to a real --run. Passing --suite-line must be rejected by argparse
    # (unrecognized argument), never silently accepted into a marker.
    repo = _init_repo(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main(["verified", "--repo", str(repo), "--suite-line", "999 passed"])

    assert excinfo.value.code != 0
    assert not (_marker_dir(repo) / "verified.json").exists()


# -------------------------------------------------------- patch-id relaxation


def test_review_pass_records_base_sha_and_patch_id_when_resolvable(tmp_path):
    repo = _init_repo(tmp_path)
    default_branch = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "-q", "-b", "feature/x")
    (repo / "f.txt").write_text("hello\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    _git(repo, "commit", "-m", "add f.txt")
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "review-pass.json").read_text(encoding="utf-8")
    )
    expected_base = _git(repo, "merge-base", default_branch, "HEAD")
    assert data["base_sha"] == expected_base
    assert isinstance(data["patch_id"], str) and data["patch_id"]


def test_verified_records_base_sha_and_patch_id_when_resolvable(tmp_path):
    repo = _init_repo(tmp_path)
    default_branch = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "-q", "-b", "feature/x")
    (repo / "f.txt").write_text("hello\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    _git(repo, "commit", "-m", "add f.txt")

    rc = main(["verified", "--repo", str(repo), "--run", RUN_OK])

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "verified.json").read_text(encoding="utf-8")
    )
    expected_base = _git(repo, "merge-base", default_branch, "HEAD")
    assert data["base_sha"] == expected_base
    assert isinstance(data["patch_id"], str) and data["patch_id"]


def test_review_pass_omits_patch_id_fields_when_diff_is_empty(tmp_path):
    # Single-branch throwaway repo: default-branch ref IS the current
    # branch, so merge-base(default, HEAD) == HEAD and the diff is
    # empty. The fallback fields must be omitted entirely (fail-closed:
    # no fields recorded → strict head_sha equality is the only path),
    # not written as empty strings.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "review-pass.json").read_text(encoding="utf-8")
    )
    assert "base_sha" not in data
    assert "patch_id" not in data


def test_verified_head_sha_tracks_second_commit(tmp_path):
    repo = _init_repo(tmp_path)
    first_sha = _head(repo)
    assert main(["verified", "--repo", str(repo), "--run", RUN_OK]) == 0

    _git(repo, "commit", "--allow-empty", "-m", "second")
    second_sha = _head(repo)
    assert second_sha != first_sha
    # Re-run: silent overwrite, latest wins.
    assert main(["verified", "--repo", str(repo), "--run", RUN_OK]) == 0

    data = json.loads(
        (_marker_dir(repo) / "verified.json").read_text(encoding="utf-8")
    )
    assert data["head_sha"] == second_sha
    assert data["run_cmd"] == RUN_OK


# --------------------------------------------------------------------- waiver


def test_waiver_writes_marker_and_warns_loudly(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    reason = "emergency hotfix, review gate waived per incident 42"

    rc = main(["waiver", "--repo", str(repo), "--reason", reason])

    assert rc == 0
    marker = _marker_dir(repo) / "waiver.json"
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert set(data) == {"schema", "scope", "reason", "written_at"}
    assert data["schema"] == 1
    assert data["scope"] == "push"
    assert data["reason"] == reason
    datetime.fromisoformat(data["written_at"])
    err = capsys.readouterr().err
    assert "bypass" in err.lower()
    assert "one-shot" in err.lower()


@pytest.mark.parametrize("reason", ["", "too short", "   padded  "])
def test_waiver_short_reason_exits_4(tmp_path, reason):
    repo = _init_repo(tmp_path)

    rc = main(["waiver", "--repo", str(repo), "--reason", reason])

    assert rc == 4
    assert not (_marker_dir(repo) / "waiver.json").exists()


# -------------------------------------------------------------------- validate


def test_validate_reports_all_violations_in_one_run(tmp_path, capsys):
    # Missing standards_version AND dimension_scores AND a bad suite
    # line — all three must surface together, not just the first.
    verdict_file = _write_verdict(tmp_path, "verdict: PASS\n")

    rc = main(
        ["validate", "--verdict-file", str(verdict_file),
         "--suite-line", "0 passed in 0.01s"]
    )

    assert rc == 4
    err = capsys.readouterr().err
    assert "standards_version" in err
    assert "dimension_scores" in err
    assert "passed" in err


def test_validate_clean_verdict_and_suite_line_exits_0(tmp_path, capsys):
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["validate", "--verdict-file", str(verdict_file),
         "--suite-line", "12 passed in 0.30s"]
    )

    assert rc == 0
    assert not capsys.readouterr().err


def test_validate_without_suite_line_checks_verdict_only(tmp_path):
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(["validate", "--verdict-file", str(verdict_file)])

    assert rc == 0


def test_validate_bad_suite_line_alone_exits_4(tmp_path, capsys):
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["validate", "--verdict-file", str(verdict_file),
         "--suite-line", "3 failed, 2 passed in 1.2s"]
    )

    assert rc == 4
    assert "passed" in capsys.readouterr().err


def test_validate_missing_verdict_file_exits_4(tmp_path, capsys):
    rc = main(["validate", "--verdict-file", str(tmp_path / "nope.md")])

    assert rc == 4
    assert capsys.readouterr().err.strip()


def test_validate_does_not_require_a_git_repo(tmp_path):
    # validate is a dry-run text check — no --repo, no marker write, no
    # git resolution needed. Running from a plain (non-repo) directory
    # must not exit 2 the way the marker-writing subcommands do.
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(["validate", "--verdict-file", str(verdict_file)])

    assert rc == 0


# ---------------------------------------------------------------- --repo flag


def test_repo_flag_post_subcommand_honored_from_different_cwd(
    tmp_path, monkeypatch
):
    repo = _init_repo(tmp_path)
    elsewhere = tmp_path / "elsewhere"  # NOT a git repo
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    rc = main(["verified", "--repo", str(repo), "--run", RUN_OK])

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "verified.json").read_text(encoding="utf-8")
    )
    assert data["head_sha"] == _head(repo)


def test_repo_flag_pre_subcommand_is_rejected_loudly(tmp_path):
    # argparse subparser defaults clobber parent-parser values, so a
    # pre-subcommand --repo would silently fall back to cwd. The flag
    # therefore only exists post-subcommand; the pre-subcommand form
    # must fail loudly (argparse: unrecognized argument), never
    # silently use the wrong repo.
    repo = _init_repo(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main(["--repo", str(repo), "verified", "--run", RUN_OK])

    assert excinfo.value.code != 0
    assert not (_marker_dir(repo) / "verified.json").exists()


# ------------------------------------------------------------------ non-repo


def test_not_a_git_repo_exits_2_for_every_subcommand(tmp_path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    argvs = [
        ["review-pass", "--repo", str(plain), "--verdict-file", str(verdict_file)],
        ["verified", "--repo", str(plain), "--run", RUN_OK],
        ["waiver", "--repo", str(plain), "--reason", "a perfectly long reason"],
    ]
    for argv in argvs:
        assert main(argv) == 2, argv
    assert "git" in capsys.readouterr().err.lower()
