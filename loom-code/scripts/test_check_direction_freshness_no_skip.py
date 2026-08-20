"""Anti-cheat probe for check_direction_freshness.py — Task 5 of
docs/loom/plans/2026-08-20-direction-queue-gate.md.

Why this file exists: docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md
documents that a mechanical check can go green not because things are
clean but because a regex or a path lookup matched nothing. A probe
that merely runs `check_direction_freshness.py` and sees it pass
proves nothing — it must show each check FIRES on input engineered to
violate it.

Three probes:
  - the unlanded-change check reports a finding for a scratch git repo
    it should flag (a branch that still carries a governing-file
    change the base branch does not have);
  - the queue-relation check rejects a brief with no '## Queue
    relation' section at all, rather than treating the absence as
    satisfied;
  - the '## Now' entry parser's em-dash separator actually recovers a
    name from a correctly formatted line and that name resolves an
    `in-queue:` declaration — covering the coupling Task 4 left in
    place (a strict em-dash separator, kept on purpose): if that
    regex were ever broken to match nothing, every downstream
    in-queue/displaces lookup would go blind, and this is the test
    that would catch it.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parent / "check_direction_freshness.py"

_spec = importlib.util.spec_from_file_location(
    "check_direction_freshness", _SCRIPT
)
check_direction_freshness = importlib.util.module_from_spec(_spec)
sys.modules["check_direction_freshness"] = check_direction_freshness
_spec.loader.exec_module(check_direction_freshness)

find_unlanded_direction_changes = check_direction_freshness.find_unlanded_direction_changes
resolve_queue_relation = check_direction_freshness.resolve_queue_relation
_parse_now_entry_names = check_direction_freshness._parse_now_entry_names


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )


def _init_scratch_repo(tmp_path: Path) -> Path:
    """A tiny real git repo with a `main` branch and a `feature` branch
    that still carries an unlanded change to a governing file — the
    input the unlanded-change check is supposed to flag."""
    repo = tmp_path / "scratch-repo"
    repo.mkdir()
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.email", "t@example.com")
    _run_git(repo, "config", "user.name", "T")
    (repo / "docs" / "loom" / "backlog").mkdir(parents=True)
    (repo / "docs" / "loom" / "DIRECTION.md").write_text(
        "## Now\n\n- widget — ship the widget\n"
    )
    (repo / "docs" / "loom" / "backlog" / "widget.md").write_text("original body\n")
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-q", "-m", "init")
    _run_git(repo, "checkout", "-q", "-b", "feature")
    (repo / "docs" / "loom" / "backlog" / "widget.md").write_text("changed body\n")
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-q", "-m", "touch widget backlog")
    _run_git(repo, "checkout", "-q", "main")
    return repo


def test_unmerged_check_cannot_pass_by_matching_nothing(tmp_path):
    repo = _init_scratch_repo(tmp_path)
    findings = find_unlanded_direction_changes(repo, base_branch="main")
    assert any(
        "feature" in f and "docs/loom/backlog/widget.md" in f for f in findings
    ), (
        "find_unlanded_direction_changes reported nothing for a branch "
        "that demonstrably still carries an unlanded governing-file "
        "change relative to main — the check has gone blind, not "
        "clean: " + repr(findings)
    )


def test_queue_relation_rejects_absent_section_not_silently_satisfied():
    result = resolve_queue_relation("", now_names=[])
    assert result.status == "unresolved", (
        "resolve_queue_relation treated a brief with no '## Queue "
        "relation' section at all as satisfied — an absent section "
        "must not silently pass: " + repr(result)
    )


def test_em_dash_separator_actually_parses_and_resolves():
    direction_text = "## Now\n\n- widget — ship the widget\n"
    now_names = _parse_now_entry_names(direction_text)
    assert now_names == ["widget"], (
        "the '## Now' entry parser did not recover 'widget' from a "
        "correctly em-dash-separated line — if that separator regex "
        "ever matches nothing, every downstream in-queue/displaces "
        "lookup goes blind: " + repr(now_names)
    )
    brief_text = "## Queue relation\nin-queue: widget\n"
    result = resolve_queue_relation(brief_text, now_names)
    assert result.status == "resolved", (
        "in-queue: widget failed to resolve against a now_names list "
        "that legitimately contains 'widget': " + repr(result)
    )
