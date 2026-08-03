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

import errno
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

import loom_gate_markers
from loom_gate_markers import _origin_path_quote, main


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
    "origin_line,expected_reason",
    [
        ("docs/loom/plans/x.md", "is not 'none' or"),
        ('"seven call sites"', "is not 'none' or"),
        ('docs/loom/plans/x.md :: ""', "quote is empty or blank"),
        ('docs/loom/plans/x.md :: "   "', "quote is empty or blank"),
    ],
    ids=[
        "path-value-no-separator",
        "quote-value-no-separator",
        "empty-quote",
        "whitespace-only-quote",
    ],
)
def test_origin_bare_path_or_bare_quote_refuses(
    tmp_path, capsys, origin_line, expected_reason
):
    # `expected_reason` pins WHY this refuses (a grammar failure raised
    # during schema validation, before HEAD is even resolved) rather
    # than just asserting the final rc — the target path is never
    # committed in this repo, so an rc-only assertion would pass just
    # as well if the grammar check silently let the value through and
    # a later, unrelated file-absent check caught it instead. That
    # masking is exactly how the blank-check and quoted-check mutants
    # inside the shared origin parser would otherwise survive.
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
    err = capsys.readouterr().err
    assert "verdict text failed schema validation" in err
    assert expected_reason in err


# ------------------------------------- origin (docs-arm grammar-when-present)
#
# Task 1's docs-arm exemption excuses a docs-arm finding from CARRYING an
# origin: line — it does not excuse one it DOES carry from being
# well-formed. Before this fix, `_finding_problems` only ran
# `_origin_grammar_problem` inside the `_origin_required(...)` branch, so
# a docs-arm finding with a malformed origin: (bare path, unterminated
# quote, blank quote) skipped grammar validation entirely and minted
# clean — the docs-arm silent-accept bug found in review.


@pytest.mark.parametrize(
    "origin_line,expected_reason",
    [
        ("docs/loom/plans/x.md", "is not 'none' or"),
        ('docs/loom/plans/x.md :: "abc', "quote is not fully quoted"),
        ('docs/loom/plans/x.md :: "   "', "quote is empty or blank"),
    ],
    ids=["bare-path", "unterminated-quote", "blank-quote"],
)
def test_docs_arm_finding_with_malformed_origin_refuses_to_mint(
    tmp_path, capsys, origin_line, expected_reason
):
    # `expected_reason` pins the grammar-check failure text (see the
    # comment on test_origin_bare_path_or_bare_quote_refuses for why
    # rc alone is not enough — the target path is never committed here
    # either, so a masked quoted-check/blank-check mutant would still
    # produce rc==4 via file-absence).
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(dimension_line="omission", origin_line=origin_line),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    err = capsys.readouterr().err
    assert "verdict text failed schema validation" in err
    assert expected_reason in err


def test_docs_arm_finding_with_duplicate_origin_refuses_to_mint(tmp_path):
    # Mirrors test_duplicate_origin_lines_refuses_to_mint (code-arm) on the
    # docs arm — duplicate handling was already arm-agnostic before this
    # fix; pinned here so it stays that way.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: docs/x.md:1\n"
        "    dimension: omission\n"
        "    origin: none\n"
        '    origin: p.md :: "quoted text"\n',
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()


@pytest.mark.parametrize(
    "origin_line,expected_reason",
    [
        ("loom-code/scripts/foo.py:12", "is not 'none' or"),
        ('loom-code/scripts/foo.py:12 :: "abc', "quote is not fully quoted"),
        ('loom-code/scripts/foo.py:12 :: "   "', "quote is empty or blank"),
    ],
    ids=["bare-path", "unterminated-quote", "blank-quote"],
)
def test_code_arm_finding_with_malformed_origin_refuses_to_mint(
    tmp_path, capsys, origin_line, expected_reason
):
    # Sibling to the docs-arm parametrization above — pins that the same
    # malformed shapes refuse identically on the arm whose requirement
    # check already forced grammar validation, so both arms are pinned
    # side by side. `expected_reason` pins the grammar-check failure
    # text for the same masking reason documented there.
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
    err = capsys.readouterr().err
    assert "verdict text failed schema validation" in err
    assert expected_reason in err


# ------------------------------------------- origin (no length/width floor)
#
# Amendment 2026-08-02, user decision: the grammar rule is exactly
# split-on-first-` :: `-then-require-a-non-blank-quoted-interior. Five
# review rounds tried four length/width-shaped floors on top of that and
# each one either excluded whole scripts (CJK) or, at display width >= 4,
# bought 2.1 percentage points of refusal while accepting 97.7% of this
# repo's committed .md files. The floor is deleted outright, not
# replaced — the successor (corpus selectivity) is a separate backlog
# item, not a sixth patch here.


def test_origin_quote_no_length_or_width_floor(tmp_path):
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/loom/plans/x.md :: "e"',
        ),
    )

    rc = main(["validate", "--verdict-file", str(verdict_file)])

    assert rc == 0


def test_origin_quote_short_but_non_blank_mints_end_to_end(tmp_path):
    # The reviewer's own repro (§Notes History): "e" is exactly the
    # quote the display-width floor used to refuse. It now mints like any
    # other grammatically valid, verified origin.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/l.md", "some prose containing the letter e.\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/l.md :: "e"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


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


def test_origin_quote_containing_separator_records_unverified_when_absent(
    tmp_path,
):
    # Same shape as the test above, but the committed file does NOT
    # contain the quote. Pins the exact consequence a split-position
    # divergence between the grammar check and the extraction path would
    # cause: if `_origin_path_quote` ever split on a DIFFERENT ` :: `
    # occurrence than the grammar check (e.g. last instead of first), the
    # quoted-check would fail on this value, `_origin_path_quote` would
    # return None, and `_finding_quote_status` would record `"malformed"`
    # instead of a real quote-absent verdict — treating an unverifiable
    # quote as if it had nothing to verify. Both parses now run through
    # the same single site, so this must always record the real
    # verification failure (Task 8: it no longer refuses to mint either
    # way, but which label lands is still load-bearing).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "p.md", "nothing matching here\n")
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
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


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


def test_duplicate_dimension_lines_refuses_to_mint_even_with_origin_satisfied(
    tmp_path,
):
    # Whole-branch review finding 3: the existing duplicate-dimension test
    # above only exercises the case where origin: is ALSO absent, so the
    # "no origin: line" problem masks whether duplicate dimension: is
    # itself checked at all. Here origin: is present and grammar-valid
    # ("none") — with no dedicated duplicate-dimension check in
    # `_finding_problems`, this used to mint clean at exit 0, recording
    # byte-identical to a finding with NO dimension: line at all (arm
    # "code", dimension null) and silently contaminating the population
    # partition the ledger exists to keep clean.
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
        "    dimension: correctness\n"
        "    origin: none\n",
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


def test_origin_quote_present_only_in_worktree_records_unverified(tmp_path):
    # Committed content lacks the quoted sentence; the on-disk (uncommitted)
    # file contains it. The check must read the commit, never the worktree —
    # a Path.read_text() implementation would wrongly report this quote
    # verified. Task 8: the mint no longer refuses either way, but the
    # ledger must still say "unverified", not "verified" — that is the
    # only observable proof the worktree copy was never consulted.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


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


def test_unverifiable_quote_records_and_still_mints(tmp_path):
    # Task 8 RED: a well-formed origin: whose quote is absent from the
    # cited file must exit 0, write the marker, and leave a ledger entry
    # with quote_status: unverified-quote-absent — quote verification is
    # demoted from a mint refusal to a recorded fact. Fails today (rc 4,
    # no marker written).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


def test_origin_file_absent_at_sha_records_unverified_and_mints(tmp_path):
    repo = _init_repo(tmp_path)  # docs/note.md never committed
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-file-absent"


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


def test_ledger_finding_entries_sha_unresolvable_recorded_distinctly(tmp_path):
    # Fifth of the five unverifiable reasons (Task 8). Same unreachable-
    # through-the-CLI reasoning as the test above — `head_sha` inside
    # `_cmd_review_pass` always comes from a live `rev-parse HEAD` on a
    # real repo, so it is never a well-formed-but-unresolvable sha —
    # exercised directly on `_ledger_finding_entries` instead.
    from loom_gate_markers import _ledger_finding_entries

    repo = _init_repo(tmp_path)
    bad_sha = "0" * 40  # well-formed hex, does not resolve to any commit
    text = _verdict_with_finding(
        dimension_line="correctness",
        origin_line='docs/note.md :: "anything"',
    )

    entries = _ledger_finding_entries(text, repo, bad_sha)

    assert entries[0]["quote_status"] == "unverified-sha-unresolvable"


def test_ledger_finding_entries_head_sha_none_records_unverified_without_crash(
    tmp_path, monkeypatch
):
    # Defensive guard (Task 8): `_append_origin_ledger` is only invoked
    # when `branch` resolved, and in every observed git state `branch`
    # and `head_sha` resolve or fail together (both fail on an unborn
    # HEAD — see test_review_pass_unborn_head_exits_2_and_writes_nothing
    # below) — so this state should be unreachable through the CLI. The
    # guard must never call `_show_committed_file` with a `None` sha —
    # asserting only the final `quote_status` is NOT enough to pin this:
    # `_show_committed_file(repo, None, path)` happens to ALSO resolve to
    # `sha-unresolvable` (git fails to verify the literal revision string
    # "None"), so a mutant that deletes the guard produces the identical
    # output and would survive an output-only assertion. Monkeypatching
    # `_show_committed_file` to raise if called is what actually proves
    # the short-circuit runs before any git subprocess is invoked.
    import loom_gate_markers
    from loom_gate_markers import _ledger_finding_entries

    def _boom(*_args, **_kwargs):
        raise AssertionError("_show_committed_file must not be called")

    monkeypatch.setattr(loom_gate_markers, "_show_committed_file", _boom)

    repo = _init_repo(tmp_path)
    text = _verdict_with_finding(
        dimension_line="correctness",
        origin_line='docs/note.md :: "anything"',
    )

    entries = _ledger_finding_entries(text, repo, None)

    assert entries[0]["quote_status"] == "unverified-sha-unresolvable"


def test_review_pass_unborn_head_exits_2_and_writes_nothing(tmp_path):
    # Watch item from the Task 8 plan: moving quote verification earlier
    # (into the ledger, computed ahead of every early return) must not
    # disturb the pre-existing "cannot resolve HEAD" exit-2 path. A git
    # repo with no commits yet resolves neither `--abbrev-ref HEAD` nor
    # `HEAD` itself (both fail with the same "ambiguous argument HEAD"
    # error) — `resolve_marker_dir` still succeeds (`rev-parse --git-dir`
    # needs no commit), so `_cmd_review_pass` is reached and must hit its
    # own `branch is None or head_sha is None` guard, not crash inside
    # quote verification and not write a ledger entry (guarded on
    # `branch is not None`, which is also None here).
    repo = tmp_path / "unborn"
    repo.mkdir()
    _git(repo, "init", "-q")
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 2
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    assert not (_marker_dir(repo) / "origin-ledger.json").exists()


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


def test_normalised_advisory_aggregates_across_findings(tmp_path, capsys):
    # Whole-branch review finding: two normalised-tier findings in one
    # round used to print the identical advisory line twice with nothing
    # distinguishing which finding either line referred to. Aggregate into
    # one line naming the count instead.
    repo = _init_repo(tmp_path)
    _commit_file(repo, "docs/a.md", "It’s the pre–flight check.\n")
    _commit_file(repo, "docs/b.md", "Another em—dash sentence here.\n")
    text = "\n".join(
        [
            "standards_version: 2026-06",
            "verdict: PASS",
            "dimension_scores:",
            "  security: 5",
            "findings:",
            "  - severity: yellow",
            "    where: a.py:1",
            "    dimension: correctness",
            "    origin: docs/a.md :: \"It's the pre-flight check.\"",
            "  - severity: yellow",
            "    where: b.py:2",
            "    dimension: correctness",
            "    origin: docs/b.md :: \"Another em-dash sentence here.\"",
        ]
    ) + "\n"
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    out = capsys.readouterr().out
    # Filter on the advisory's own fixed phrase, not a bare "normalis"
    # substring — the marker path line pytest prints also contains that
    # substring here, since this test's own name/tmp_path does.
    advisory_lines = [
        line for line in out.splitlines() if "matched only after" in line.lower()
    ]
    assert len(advisory_lines) == 1
    assert "2" in advisory_lines[0]


def test_normalised_advisory_prints_resolved_ledger_path(tmp_path, capsys):
    # Whole-branch review finding 4: the advisory used to print the bare
    # string "origin-ledger.json" right after the review-pass.json path,
    # implying the same directory — false from a worktree, where the
    # ledger lives under the MAIN checkout's git-common-dir while
    # review-pass.json lives under the worktree's own private git-dir.
    # Print the resolved path so a reader can actually find the file.
    repo = _init_repo(tmp_path)
    # Commit BEFORE branching the worktree: the worktree's own HEAD is
    # whatever commit it was created from, so the quoted file must
    # already be committed on `repo`'s branch first, or the worktree's
    # HEAD would predate it and quote verification would (correctly)
    # report file-absent instead of a normalised match.
    _commit_file(repo, "docs/a.md", "It's the pre-flight check.\n")
    worktree = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", "-b", "wt-branch", str(worktree))
    text = "\n".join(
        [
            "standards_version: 2026-06",
            "verdict: PASS",
            "dimension_scores:",
            "  security: 5",
            "findings:",
            "  - severity: yellow",
            "    where: a.py:1",
            "    dimension: correctness",
            "    origin: docs/a.md :: \"It's the pre–flight check.\"",
        ]
    ) + "\n"
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(worktree), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    out = capsys.readouterr().out
    advisory_lines = [
        line for line in out.splitlines() if "matched only after" in line.lower()
    ]
    assert len(advisory_lines) == 1
    expected_ledger_path = _ledger_path(repo)
    assert str(expected_ledger_path) in advisory_lines[0]
    # The old bare-filename advisory implied the WORKTREE's own private
    # git-dir (right next to review-pass.json, printed just above) — assert
    # that directory is NOT what's named now.
    worktree_git_dir = Path(_git(worktree, "rev-parse", "--git-dir"))
    if not worktree_git_dir.is_absolute():
        worktree_git_dir = worktree / worktree_git_dir
    assert str(worktree_git_dir) not in advisory_lines[0]


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


def test_normalized_match_is_case_sensitive_and_records_unverified(tmp_path):
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


def test_normalizer_does_not_strip_markdown_emphasis_or_backticks(tmp_path):
    # The normaliser folds whitespace/typography only — it must not strip
    # `**`/backticks, or a quote of the rendered prose would wrongly match
    # markdown source that never contained that literal text.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


def test_normalizer_does_not_strip_backticks(tmp_path):
    # Sibling case to the `**` test above: backticks must survive the
    # normaliser too, or a quote of rendered prose could wrongly match
    # markdown source that never contained that literal text.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


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


# ---------------------------------------------- CJK coverage (not a floor)
#
# The nine tests that used to pin the deleted length/width floor's CJK
# carve-out were removed with the floor itself — correctly, since they
# pinned a rule that no longer exists. But `_normalize_for_quote_match`
# (NFC + typographic fold + whitespace collapse) is still live code, and
# without these it would be exercised only by the Latin `café` case above.
# These pin, end-to-end through `review-pass`, that a CJK quote mints, a
# CJK quote absent from the file refuses, and NFD/NFC composition
# differences on CJK content are normalised away — NOT any length, width,
# or token rule (§Notes kickoff decision: not being a language filter is
# the property five review rounds bought; see the plan's §Notes).


def test_origin_quote_traditional_chinese_present_mints(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(
        repo, "docs/note.md", "這份文件說明如何重新設計資料匯入流程。\n"
    )
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "重新設計資料匯入流程"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_origin_quote_japanese_present_mints(tmp_path):
    repo = _init_repo(tmp_path)
    _commit_file(
        repo, "docs/note.md", "このスクリプトは正規化処理が必要になる場合を扱う。\n"
    )
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "正規化処理が必要になる場合"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_origin_quote_cjk_absent_from_committed_file_records_unverified(tmp_path):
    # Discriminating case for the two mint tests above: same shape, but
    # the committed file does not contain the quoted text. Manually
    # verified during development that pointing this fixture's content at
    # text which DOES contain the quote flips the ledger status to
    # verified-exact — i.e. the unverified status asserted below is the
    # matcher actually rejecting an absent quote, not an unrelated
    # failure (grammar, sha resolution, file-not-found).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "docs/note.md", "這份文件與引用的字句完全無關。\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/note.md :: "完全不存在於檔案中的字句"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-quote-absent"


def test_origin_quote_nfd_kana_needle_matches_nfc_haystack_mints(tmp_path):
    # Mirrors test_normalizer_folds_nfd_needle_against_nfc_haystack (the
    # café case) on CJK content: proves NFC normalisation runs on BOTH
    # sides, not just the Latin one. が (U+304C, NFC) decomposes to か
    # (U+304B) + the combining voiced-sound mark (U+3099) under NFD — the
    # haystack is committed in composed (NFC) form, the quote is the
    # decomposed (NFD) spelling of the same text.
    import unicodedata

    repo = _init_repo(tmp_path)
    composed = "これは合成された「が」を含む文です。\n"  # NFC が
    assert unicodedata.is_normalized("NFC", composed)
    _commit_file(repo, "docs/note.md", composed)
    # NFD spelling built from separate codepoints (\u304b + \u3099)
    # rather than typed as one literal character, per the composed-vs-
    # decomposed distinction this test exists to pin.
    decomposed_quote = "合成された「が」を含む文"
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


def test_origin_directory_path_records_not_a_file_and_mints(tmp_path):
    # `git show <sha>:<dir>` exits 0 and prints a git-generated tree
    # listing, not repository content — a directory path must never be
    # treated as a readable origin (FATAL if it were: this would mint a
    # quote from thin air, since the listing's filenames are content the
    # reviewer never read). Two committed files so the listing has two
    # entries, quoted as "a.md b.md" — a non-blank quote, so this test
    # still reaches the directory-type check it names rather than being
    # shadowed by the grammar refusal. This quote is also not arbitrary
    # filler: the listing's two lines normalise (newline -> space) to
    # exactly this string, so if the type check that classifies this
    # finding were ever bypassed, this quote would go on to match at the
    # normalised tier and record verified-normalised instead of the
    # unverified-not-a-file asserted below.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "docs/a.md", "hello\n")
    _commit_file(repo, "docs/b.md", "world\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs :: "a.md b.md"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-not-a-file"


def test_origin_directory_path_trailing_slash_records_not_a_file_and_mints(tmp_path):
    # Same construction as the sibling test above (two committed files,
    # quote = the normalised listing) for the same reason: an arbitrary
    # filler quote would be non-blank but never actually exercise a
    # bypass, so it would not prove this test still reaches the
    # directory-type check when the path carries a trailing slash.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "docs/a.md", "hello\n")
    _commit_file(repo, "docs/b.md", "world\n")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='docs/ :: "a.md b.md"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-not-a-file"


def test_origin_directory_tree_header_word_records_not_a_file_and_mints(tmp_path):
    # The header `git show` prints for ANY tree object is literally
    # "tree <hash>:<dir>" — a quote of "tree <hash>" needs no knowledge
    # of the directory's actual contents, only the header's fixed format
    # plus the commit's own sha (already known to whoever writes the
    # verdict), which is the sharpest form of the bypass. "tree " plus
    # the hex sha is a non-blank quote, so this test still reaches the
    # directory-type check it names, rather than being shadowed by the
    # grammar refusal. This quote is also an
    # EXACT substring of the real `git show` output (verified live
    # below) — if the type check that classifies this finding were ever
    # bypassed, THIS quote would go on to match and record
    # verified-exact instead of the unverified-not-a-file asserted below.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "docs/a.md", "hello\n")
    head_sha = _head(repo)
    tree_header = _git(repo, "show", f"{head_sha}:docs")
    assert tree_header.startswith(f"tree {head_sha}")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line=f'docs :: "tree {head_sha}"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-not-a-file"


def test_origin_quote_undecodable_blob_records_unverified_without_crash(tmp_path):
    # A non-UTF-8 blob must record its own explicit failure reason, never
    # an uncaught UnicodeDecodeError traceback (which would leak
    # interpreter paths and mint no marker only by accident of the crash —
    # Task 8: the mint never depended on this outcome anyway, but "does
    # not crash" is still the load-bearing property). "PNG tail" is a
    # non-blank quote, so this test still reaches the decode-failure path
    # it names, rather than being shadowed by the grammar refusal (the
    # decode never runs far enough to check quote content anyway —
    # decoding fails before any match attempt — so the quote's actual
    # words are immaterial).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    (repo / "bin.dat").write_bytes(b"\x80\x81\x82PNGtail")
    _git(repo, "add", "bin.dat")
    _git(repo, "commit", "-q", "-m", "add binary")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line='bin.dat :: "PNG tail"',
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "unverified-undecodable-blob"


def test_review_pass_marker_no_longer_carries_origin_quote_tier_counts(tmp_path):
    # Task 8: `origin_quote_tiers` is REMOVED from review-pass.json — the
    # origin ledger supersedes it (see the finding-level `quote_status`
    # values asserted below), and leaving both would restate the
    # per-run-snapshot population-mismatch defect the ledger exists to
    # fix (docs/loom/backlog/2026-08-02-origin-quote-tier-counts-have-no-
    # durable-ledger.md).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
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
    assert "origin_quote_tiers" not in data
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert [f["quote_status"] for f in entry["findings"]] == [
        "verified-exact",
        "verified-normalised",
    ]


# -------------------------------------------------------------- origin ledger


def _ledger_path(repo: Path) -> Path:
    return _marker_dir(repo) / "origin-ledger.json"


def test_origin_ledger_appends_on_a_needs_revision_round(tmp_path):
    # RED (Task 7): NEEDS_REVISION returns 3 and writes no review-pass.json
    # today, but the ledger's whole point is recording rounds that FAIL —
    # that path must still get one entry.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    verdict_file = _write_verdict(
        tmp_path, VALID_VERDICT.replace("verdict: PASS", "verdict: NEEDS_REVISION")
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 3
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    rounds = ledger["branches"][branch]
    assert len(rounds) == 1
    entry = rounds[0]
    assert entry["round"] == 1
    assert entry["verdict"] == "NEEDS_REVISION"
    assert entry["head_sha"] == _head(repo)
    datetime.fromisoformat(entry["written_at"])
    assert entry["findings"] == [
        {
            "arm": "code",
            "dimension": "correctness",
            "origin_raw": "none",
            "quote_status": "none",
        }
    ]


def test_origin_ledger_needs_revision_round_carries_real_quote_verification(
    tmp_path,
):
    # Task 8: verification is no longer only reachable on a round that
    # already made it past the mint gate — a NEEDS_REVISION round (exit
    # 3, no marker) must still carry a REAL verified/unverified result
    # into the ledger, not Task 7's placeholder. Measured on this repo:
    # 0 of 24 severity-🔴 findings ever reached the old mint-time-only
    # verification call, because every one of them forced NEEDS_REVISION
    # first.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _commit_file(repo, "docs/note.md", "The exact quoted sentence is here.\n")
    text = (
        "standards_version: 2026-06\n"
        "verdict: NEEDS_REVISION\n"
        "dimension_scores:\n"
        "  security: 1\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: loom-code/scripts/foo.py:12\n"
        "    dimension: correctness\n"
        '    origin: docs/note.md :: "The exact quoted sentence is here."\n'
        "    note: real finding\n"
    )
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 3
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["verdict"] == "NEEDS_REVISION"
    assert entry["findings"][0]["quote_status"] == "verified-exact"


def test_origin_ledger_appends_second_round_without_rewriting_first(tmp_path):
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    main(["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)])
    main(["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)])

    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    rounds = ledger["branches"][branch]
    assert [r["round"] for r in rounds] == [1, 2]
    assert rounds[0]["verdict"] == "PASS"
    assert rounds[1]["verdict"] == "PASS"


def test_origin_ledger_keys_separate_branches_independently(tmp_path):
    repo = _init_repo(tmp_path)
    first_branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    main(["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)])

    _git(repo, "checkout", "-b", "feat-other")
    main(["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)])

    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert set(ledger["branches"]) == {first_branch, "feat-other"}
    assert [r["round"] for r in ledger["branches"][first_branch]] == [1]
    assert [r["round"] for r in ledger["branches"]["feat-other"]] == [1]


def test_origin_ledger_shared_across_worktrees_via_git_common_dir(tmp_path):
    # Whole-branch review finding: `resolve_marker_dir` (`--git-dir`) is
    # correct for review-pass.json/verified.json (per-checkout, must die
    # with the checkout) but WRONG for the ledger — a round run from a
    # `git worktree` checkout (the normal case; this plugin ships a
    # `using-git-worktrees` skill for exactly this) must land in the SAME
    # ledger the main checkout reads, not a private copy under
    # `<main>/.git/worktrees/<name>/loom/` that `git worktree remove`
    # deletes outright.
    repo = _init_repo(tmp_path)
    worktree = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", "-b", "wt-branch", str(worktree))
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(worktree), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    # review-pass.json is unaffected: still per-checkout, under the
    # WORKTREE's own private git-dir.
    worktree_git_dir = Path(_git(worktree, "rev-parse", "--git-dir"))
    if not worktree_git_dir.is_absolute():
        worktree_git_dir = worktree / worktree_git_dir
    assert (worktree_git_dir / "loom" / "review-pass.json").is_file()
    # The ledger must land under the MAIN checkout's .git/loom (keyed by
    # the worktree's branch), and must NOT exist at the worktree's own
    # private location.
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert "wt-branch" in ledger["branches"]
    assert not (worktree_git_dir / "loom" / "origin-ledger.json").exists()


def test_concurrent_review_pass_rounds_all_survive_the_shared_ledger(tmp_path):
    # Whole-branch review finding 1: `_append_origin_ledger` was an
    # unlocked read-modify-write. Reproduced with real OS PROCESSES (not
    # threads — the GIL would mask the race) hammering the SAME ledger
    # file concurrently, mirroring the reviewer's own four-worktree
    # repro (only one of four rounds survived). Confirmed pre-fix on this
    # exact fixture: 8 concurrent invocations recorded only 2 of 8
    # rounds, all exiting 0 with nothing on stderr. Every round must
    # survive after the fix.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    script = tmp_path / "run_one.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(Path(__file__).parent)!r})\n"
        "from loom_gate_markers import main\n"
        "raise SystemExit(main(['review-pass', '--repo', "
        f"{str(repo)!r}, '--verdict-file', {str(verdict_file)!r}]))\n",
        encoding="utf-8",
    )
    n = 8

    procs = [subprocess.Popen([sys.executable, str(script)]) for _ in range(n)]
    rcs = [p.wait() for p in procs]

    assert rcs == [0] * n
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    rounds = ledger["branches"][branch]
    assert len(rounds) == n, (
        f"expected {n} recorded rounds, got {len(rounds)}: "
        f"{[r['round'] for r in rounds]}"
    )
    assert sorted(r["round"] for r in rounds) == list(range(1, n + 1))


def test_origin_ledger_unparseable_dimension_records_null_dimension_arm_code(
    tmp_path,
):
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    text = "\n".join(
        [
            "standards_version: 2026-06",
            "verdict: PASS",
            "dimension_scores:",
            "  security: 5",
            "findings:",
            "  - severity: yellow",
            "    where: loom-code/scripts/foo.py:12",
            "    origin: none",
            "    note: no dimension: line at all",
        ]
    ) + "\n"
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"] == [
        {
            "arm": "code",
            "dimension": None,
            "origin_raw": "none",
            "quote_status": "none",
        }
    ]


def test_origin_ledger_records_origin_raw_null_when_absent_on_docs_arm(tmp_path):
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    text = "\n".join(
        [
            "standards_version: 2026-06",
            "verdict: PASS",
            "dimension_scores:",
            "  security: 5",
            "findings:",
            "  - severity: yellow",
            "    where: docs/foo.md:12",
            "    dimension: omission",
            "    note: docs-arm finding, no origin: line",
        ]
    ) + "\n"
    verdict_file = _write_verdict(tmp_path, text)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"] == [
        {
            "arm": "docs",
            "dimension": "omission",
            "origin_raw": None,
            "quote_status": "absent",
        }
    ]


def test_origin_ledger_records_malformed_quote_status_on_grammar_failure(tmp_path):
    # A grammar-invalid origin: (Task 8's "malformed" label) still
    # refuses the round (exit 4, deterministically — this bare-path
    # shape is unambiguously malformed; the grammar checker is NOT
    # false-positive-free in general, see the column-anchoring gap
    # tracked in docs/loom/backlog/) — but the ledger docstring (Task 7)
    # promises an entry on EVERY
    # invocation, schema-failure paths included, so this needs its own
    # distinct quote_status rather than colliding with "none" or one of
    # the five real unverified-<reason> values, none of which apply when
    # there was never a valid path/quote pair to check.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    verdict_file = _write_verdict(
        tmp_path,
        _verdict_with_finding(
            dimension_line="correctness",
            origin_line="docs/loom/plans/x.md",  # bare path, no ` :: `
        ),
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    assert not (_marker_dir(repo) / "review-pass.json").exists()
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    assert entry["findings"][0]["quote_status"] == "malformed"


def test_origin_ledger_duplicate_origin_not_recorded_as_absent(tmp_path):
    # Whole-branch review finding: two `origin:` lines in one block is
    # malformed (refuses to mint, exit 4) — but before this fix the ledger
    # recorded it byte-identical to a finding that carried NO origin: line
    # at all (`origin_raw: null, quote_status: "absent"`), silently
    # discarding both quotes the reviewer actually wrote under a label
    # that means, per the module docstring and `_finding_quote_status`,
    # "no origin: line exists at all" — affirmatively false here. The
    # reviewer's own reproduction (two real quotes on one finding).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: yellow\n"
        "    dimension: correctness\n"
        "    where: doc.md:1\n"
        '    origin: doc.md :: "names the upstream document"\n'
        '    origin: doc.md :: "A second line of prose"\n',
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    entry = ledger["branches"][branch][0]
    # Not "absent" (that would falsely claim no origin: line existed) and
    # not silently dropped — its own honest label, with both discarded
    # quotes reflected by a null origin_raw (which of the two is intended
    # is genuinely ambiguous; neither is kept).
    assert entry["findings"][0]["quote_status"] == "duplicate"
    assert entry["findings"][0]["origin_raw"] is None


def test_origin_ledger_corrupt_json_recovered_not_permanently_dropped(
    tmp_path, capsys
):
    # Whole-branch review finding: `json.loads` throwing into the blanket
    # `except Exception` means one corrupted ledger file permanently ends
    # every future append — loudly on stderr, but forever, contradicting
    # the module docstring's promise that the sample "is never biased".
    # Recovery: move the corrupt file aside and start a fresh ledger, and
    # prove a SECOND round afterward still lands (not merely masked once).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    marker_dir = _marker_dir(repo)
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "origin-ledger.json").write_text(
        "{not valid json", encoding="utf-8"
    )
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert ledger["branches"][branch][0]["round"] == 1
    err = capsys.readouterr().err
    assert "corrupt" in err.lower()
    corrupt_siblings = [
        p
        for p in marker_dir.iterdir()
        if p.name.startswith("origin-ledger.json.corrupt")
    ]
    assert len(corrupt_siblings) == 1

    rc2 = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc2 == 0
    ledger2 = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert [r["round"] for r in ledger2["branches"][branch]] == [1, 2]


def test_origin_ledger_lock_directory_falls_back_to_unlocked_append(
    tmp_path, capsys
):
    # Round-3 review finding A: a directory sitting at the lock path is a
    # STRUCTURAL reason locking is impossible here (not contention) —
    # `open(lock_path, "a+")` raises `IsADirectoryError` before `flock` is
    # ever attempted, and this state never self-heals. The OLD behavior
    # swallowed the round forever on every future invocation too (reproduced
    # live: 4 consecutive runs, no ledger ever created) — a lossy-under-
    # concurrency ledger regressing to total loss always, worse than no
    # lock. The fix: fall back to an unlocked append with a loud stderr
    # line instead of losing the record.
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    marker_dir = _marker_dir(repo)
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "origin-ledger.json.lock").mkdir()
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    marker = marker_dir / "review-pass.json"
    assert marker.is_file()
    err = capsys.readouterr().err
    assert "lock" in err.lower()
    assert "could not record origin ledger entry" not in err
    ledger = json.loads(
        (marker_dir / "origin-ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["branches"][branch][0]["round"] == 1


def test_origin_ledger_lock_permission_denied_falls_back_to_unlocked_append(
    tmp_path, capsys
):
    # Round-3 review finding A, second environment: a lock file the caller
    # cannot write (e.g. another user's umask in a shared checkout) raises
    # `PermissionError` at `open()`, same permanence as the directory shape
    # above. Same fallback applies.
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root bypasses filesystem permission checks")
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    marker_dir = _marker_dir(repo)
    marker_dir.mkdir(parents=True, exist_ok=True)
    lock_path = marker_dir / "origin-ledger.json.lock"
    lock_path.touch()
    lock_path.chmod(0o000)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    try:
        rc = main(
            ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
        )
    finally:
        lock_path.chmod(0o644)

    assert rc == 0
    marker = marker_dir / "review-pass.json"
    assert marker.is_file()
    err = capsys.readouterr().err
    assert "lock" in err.lower()
    ledger = json.loads(
        (marker_dir / "origin-ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["branches"][branch][0]["round"] == 1


def test_origin_ledger_lock_flock_unsupported_falls_back_immediately(
    tmp_path, capsys, monkeypatch
):
    # Round-3 review finding A, third environment: a filesystem where
    # `flock` is unsupported (NFS/CIFS/some FUSE mounts return
    # ENOLCK/ENOSYS/EOPNOTSUPP). Before the fix, EVERY OSError from
    # flock() — structural or genuinely contended — was treated as
    # contention and retried until the 10s timeout, so this shape stalled
    # every single invocation for the full timeout AND still lost the
    # round. The fix recognizes the errno as structural and falls back
    # immediately, without waiting out the timeout.
    def _always_enolck(*args, **kwargs):
        raise OSError(errno.ENOLCK, "No locks available")

    monkeypatch.setattr(fcntl, "flock", _always_enolck)
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    start = time.monotonic()
    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )
    elapsed = time.monotonic() - start

    assert rc == 0
    assert elapsed < 2.0, (
        f"a structural flock failure must not wait out the contention "
        f"timeout, took {elapsed}s"
    )
    marker = _marker_dir(repo) / "review-pass.json"
    assert marker.is_file()
    err = capsys.readouterr().err
    assert "lock" in err.lower()
    ledger = json.loads(
        (_marker_dir(repo) / "origin-ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["branches"][branch][0]["round"] == 1


def test_origin_ledger_lock_fcntl_module_unavailable_falls_back(
    tmp_path, capsys, monkeypatch
):
    # 🟢: `import fcntl` at module scope would take `validate`/`waiver`/
    # `verified` down on a host without it (none of which touch the
    # ledger). Simulated here by monkeypatching the module's own `fcntl`
    # binding to None — the degrade path finding A already needs covers
    # this too.
    monkeypatch.setattr(loom_gate_markers, "fcntl", None)
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    marker = _marker_dir(repo) / "review-pass.json"
    assert marker.is_file()
    err = capsys.readouterr().err
    assert "fcntl" in err.lower()
    ledger = json.loads(
        (_marker_dir(repo) / "origin-ledger.json").read_text(encoding="utf-8")
    )
    assert ledger["branches"][branch][0]["round"] == 1


def test_ledger_lock_raises_timeout_when_genuinely_contended(
    tmp_path, monkeypatch, capsys
):
    # Round-3 review finding B: the timeout path (`_LedgerLockTimeout`,
    # `_LEDGER_LOCK_TIMEOUT_SECONDS`, `_ledger_lock`'s poll loop) had zero
    # coverage — a reviewer deleted the whole branch and the suite stayed
    # green. Genuine contention (a REAL separate process holding the
    # exclusive flock, not a simulated structural errno) must still wait
    # then raise after the timeout elapses.
    ledger_dir = tmp_path / "loom"
    ledger_dir.mkdir()
    lock_path = ledger_dir / "origin-ledger.json.lock"
    ready_path = tmp_path / "ready"
    release_path = tmp_path / "release"
    holder_script = tmp_path / "hold_lock.py"
    holder_script.write_text(
        "import fcntl, pathlib, time\n"
        f"lock_path = pathlib.Path({str(lock_path)!r})\n"
        f"ready_path = pathlib.Path({str(ready_path)!r})\n"
        f"release_path = pathlib.Path({str(release_path)!r})\n"
        "f = open(lock_path, 'a+')\n"
        "fcntl.flock(f.fileno(), fcntl.LOCK_EX)\n"
        "ready_path.write_text('1')\n"
        "while not release_path.exists():\n"
        "    time.sleep(0.02)\n",
        encoding="utf-8",
    )
    proc = subprocess.Popen([sys.executable, str(holder_script)])
    try:
        deadline = time.monotonic() + 5
        while not ready_path.exists():
            if time.monotonic() > deadline:
                pytest.fail("holder subprocess never acquired the lock")
            time.sleep(0.02)

        monkeypatch.setattr(loom_gate_markers, "_LEDGER_LOCK_TIMEOUT_SECONDS", 0.2)
        monkeypatch.setattr(loom_gate_markers, "_LEDGER_LOCK_POLL_SECONDS", 0.02)

        with pytest.raises(loom_gate_markers._LedgerLockTimeout):
            with loom_gate_markers._ledger_lock(ledger_dir):
                pass
    finally:
        release_path.write_text("1")
        proc.wait(timeout=5)

    err = capsys.readouterr().err
    assert "held by another process" in err.lower() or "waiting" in err.lower()


@pytest.mark.parametrize(
    "corrupt_contents",
    [
        "[]",
        "null",
        '{"schema": 1, "branches": []}',
        '{"schema": 1, "branches": {"main": {}}}',
    ],
    ids=["top-level-list", "top-level-null", "branches-list", "branch-value-dict"],
)
def test_origin_ledger_wrong_shape_json_recovered_not_permanently_dropped(
    tmp_path, capsys, corrupt_contents
):
    # Whole-branch review finding 2: the recovery caught `json.JSONDecodeError`
    # only, missing four VALID-JSON-but-wrong-shape variants. Each used to
    # raise deep inside `.setdefault`/`.append` (AttributeError) and fall
    # through to the blanket swallow-and-report, permanently dropping every
    # future round exactly like the pre-recovery JSONDecodeError bug this
    # test's sibling (test_origin_ledger_corrupt_json_recovered_not_permanently_dropped)
    # already fixed — contrary to the docstring's "a single corruption cannot
    # bias every future round to empty" claim, which was false for these
    # shapes. Recovery must move the file aside and start fresh, then prove a
    # SECOND round afterward still lands (not merely masked once).
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    marker_dir = _marker_dir(repo)
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "origin-ledger.json").write_text(corrupt_contents, encoding="utf-8")
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert ledger["branches"][branch][0]["round"] == 1
    err = capsys.readouterr().err
    assert "corrupt" in err.lower()
    corrupt_siblings = [
        p
        for p in marker_dir.iterdir()
        if p.name.startswith("origin-ledger.json.corrupt")
    ]
    assert len(corrupt_siblings) == 1

    rc2 = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc2 == 0
    ledger2 = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert [r["round"] for r in ledger2["branches"][branch]] == [1, 2]


def test_origin_ledger_directory_at_path_recovered_not_permanently_dropped(
    tmp_path, capsys
):
    # Fifth shape from finding 2's table: a directory sitting at the ledger
    # path raises IsADirectoryError from the read itself (before json.loads
    # ever runs) — must recover exactly like corrupt JSON, not swallow-and-
    # report forever.
    repo = _init_repo(tmp_path)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    marker_dir = _marker_dir(repo)
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "origin-ledger.json").mkdir()
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    ledger = json.loads(_ledger_path(repo).read_text(encoding="utf-8"))
    assert ledger["branches"][branch][0]["round"] == 1
    err = capsys.readouterr().err
    assert "corrupt" in err.lower()


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


# ------------------------------------------------------------------ public surface


def test_default_branch_ref_is_importable_as_a_public_name():
    # review_scope.py (a sibling production module) needs to depend on
    # this helper's return semantics without importing a private name —
    # the existing cross-module precedent (check-living-spec-index.py)
    # only imports public symbols.
    from loom_gate_markers import default_branch_ref

    assert callable(default_branch_ref)
