"""Tests for loom_gate_markers — the gate-marker CLI the SDD orchestrator
runs so hooks/git-guard.py can enforce review/verify gates mechanically.

Each test builds a THROWAWAY git repo under tmp_path (git init + empty
commit). No dependency on the outer repo. Marker JSON is parsed and
asserted field-by-field against the frozen contract.

External-surface grounding (source a — live verification): the git
flags the CLI depends on (`rev-parse --git-dir`, `rev-parse
--abbrev-ref HEAD`, `rev-parse HEAD`) are exercised LIVE by this suite
against the throwaway repos above — every happy-path test both drives
them through the CLI and re-runs them directly via `_git()` to
cross-check branch/sha values, so a flag regression in the installed
git surfaces here, not via belief.
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
        "    where: 610dbc409c7e\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 0
    assert (_marker_dir(repo) / "review-pass.json").is_file()


def test_review_finding_where_without_pathlike_token_exits_4(tmp_path):
    repo = _init_repo(tmp_path)
    verdict_file = _write_verdict(
        tmp_path,
        "standards_version: 2026-06\n"
        "verdict: PASS\n"
        "dimension_scores:\n"
        "  security: 5\n"
        "findings:\n"
        "  - severity: red\n"
        "    where: everywhere\n",
    )

    rc = main(
        ["review-pass", "--repo", str(repo), "--verdict-file", str(verdict_file)]
    )

    assert rc == 4


# ------------------------------------------------------------------- verified


def test_verified_writes_marker_matching_contract(tmp_path):
    repo = _init_repo(tmp_path)
    suite_line = "12 passed in 0.34s"

    rc = main(["verified", "--repo", str(repo), "--suite-line", suite_line])

    assert rc == 0
    marker = _marker_dir(repo) / "verified.json"
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert set(data) == {"schema", "head_sha", "suite_line", "written_at"}
    assert data["schema"] == 1
    assert data["head_sha"] == _head(repo)
    assert data["suite_line"] == suite_line
    datetime.fromisoformat(data["written_at"])


@pytest.mark.parametrize(
    "bad_line",
    [
        "0 passed in 0.01s",
        "3 failed, 2 passed in 1.2s",
        "3 passed, 1 error in 1.2s",
        "no tests ran",
    ],
)
def test_verified_rejects_nonconforming_suite_line(tmp_path, bad_line):
    repo = _init_repo(tmp_path)

    rc = main(["verified", "--repo", str(repo), "--suite-line", bad_line])

    assert rc == 4
    assert not (_marker_dir(repo) / "verified.json").exists()


def test_verified_accepts_green_summary_with_xfails(tmp_path):
    # "xfailed" is a green outcome — the "failed" substring inside it
    # must not trip the reject filter ("3 failed" still rejects, see
    # the nonconforming parametrize above).
    repo = _init_repo(tmp_path)
    suite_line = "10 passed, 2 xfailed in 1.2s"

    rc = main(["verified", "--repo", str(repo), "--suite-line", suite_line])

    assert rc == 0
    data = json.loads(
        (_marker_dir(repo) / "verified.json").read_text(encoding="utf-8")
    )
    assert data["suite_line"] == suite_line


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

    rc = main(["verified", "--repo", str(repo), "--suite-line", "1 passed"])

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
    assert main(["verified", "--repo", str(repo), "--suite-line", "1 passed"]) == 0

    _git(repo, "commit", "--allow-empty", "-m", "second")
    second_sha = _head(repo)
    assert second_sha != first_sha
    # Re-run: silent overwrite, latest wins.
    assert main(["verified", "--repo", str(repo), "--suite-line", "2 passed"]) == 0

    data = json.loads(
        (_marker_dir(repo) / "verified.json").read_text(encoding="utf-8")
    )
    assert data["head_sha"] == second_sha
    assert data["suite_line"] == "2 passed"


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

    rc = main(["verified", "--repo", str(repo), "--suite-line", "1 passed"])

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
        main(["--repo", str(repo), "verified", "--suite-line", "1 passed"])

    assert excinfo.value.code != 0
    assert not (_marker_dir(repo) / "verified.json").exists()


# ------------------------------------------------------------------ non-repo


def test_not_a_git_repo_exits_2_for_every_subcommand(tmp_path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    verdict_file = _write_verdict(tmp_path, VALID_VERDICT)

    argvs = [
        ["review-pass", "--repo", str(plain), "--verdict-file", str(verdict_file)],
        ["verified", "--repo", str(plain), "--suite-line", "1 passed"],
        ["waiver", "--repo", str(plain), "--reason", "a perfectly long reason"],
    ]
    for argv in argvs:
        assert main(argv) == 2, argv
    assert "git" in capsys.readouterr().err.lower()
