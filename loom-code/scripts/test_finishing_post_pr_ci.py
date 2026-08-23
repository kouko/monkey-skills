"""Structural contracts for the bounded post-PR CI phase (plan Tasks 2–3)."""

import json
from pathlib import Path


SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"
CONTINUOUS = (
    Path(__file__).parents[1] / "skills" / "using-loom-code" / "references"
    / "continuous-mode.md"
)
SDD = Path(__file__).parents[1] / "skills" / "subagent-driven-development" / "SKILL.md"
PLUGIN = Path(__file__).parents[1]
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CHANGELOG = PLUGIN / "CHANGELOG.md"


def _step_11() -> str:
    text = SKILL.read_text(encoding="utf-8")
    return text[text.index("11. Open the PR"):text.index("12. ASK user")]


def _step_13() -> str:
    text = SKILL.read_text(encoding="utf-8")
    return text[text.index("13. Report final state"):]


def test_finishing_waits_repairs_and_rechecks_current_head():
    """Step 11 owns post-create CI: bounded repair always waits on new HEAD."""
    step = _step_11()
    required_in_order = [
        "gh pr create",
        'gh pr view "$PR_NUMBER" --json headRefOid',
        "post_pr_ci.py",
        "--pr",
        "--expected-head",
        '"pass"',
        '"fail"',
        "systematic-debugging",
        "requesting-code-review",
        "verification-before-completion",
        "loom-workflow:git-memory",
        "privacy",
        "git commit",
        "loom_gate_markers.py",
        "git push",
        "new HEAD",
        "at most two",
    ]
    positions = []
    cursor = 0
    for phrase in required_in_order:
        cursor = step.index(phrase, cursor)
        positions.append(cursor)
        cursor += len(phrase)

    assert positions == sorted(positions)
    for stop in ("timeout", "no_checks", "operational_error", "head_drift", "cancelled", "budget exhaustion"):
        assert stop in step
    assert "STOP" in step
    assert "never auto-merge" in step


def test_finishing_captures_created_pr_identity_before_ci_waiting():
    step = _step_11()
    create = step.index('PR_URL="$(gh pr create')
    resolve = step.index('PR_NUMBER="$(gh pr view "$PR_URL" --json number --jq .number)"', create)
    helper = step.index('--pr "$PR_NUMBER"', resolve)

    assert create < resolve < helper
    assert "$PR_NUMBER" in step[resolve:helper]


def test_finishing_validates_pr_body_before_creation_and_commits_ci_repairs():
    step = _step_11()
    create = step.index('PR_URL="$(gh pr create')
    carrier = step.index("PR-carrier check")
    repair = step.index('On status `"fail"`')
    commit = step.index("git commit", repair)
    marker = step.index("loom_gate_markers.py", repair)

    assert carrier < create
    assert repair < commit < marker


def test_phase_overview_and_cross_skill_table_name_post_pr_ci_delegation():
    text = SKILL.read_text(encoding="utf-8")
    overview = text[text.index("finishing-a-development-branch"):text.index("## When NOT")]
    table = text[text.index("## Cross-skill contract"):text.index("## Default flow")]

    assert "Post-PR CI" in overview
    assert "post_pr_ci.py" in overview
    assert "systematic-debugging" in table
    assert "Post-PR CI" in table


def test_final_report_includes_ci_evidence():
    assert "CI evidence" in _step_13()


def test_continuous_mode_stops_only_after_ci_verified_pr_without_duplication():
    text = CONTINUOUS.read_text(encoding="utf-8")
    terminal_row = next(line for line in text.splitlines() if "PR-open reached" in line)

    assert "CI-verified" in terminal_row
    assert "never auto-merge" in terminal_row
    assert "finishing-a-development-branch" in terminal_row


def test_sdd_automatically_enters_finishing_after_an_approved_plan_completes():
    text = SDD.read_text(encoding="utf-8")
    completion = text[text.index("## Continuous execution"):text.index("## Asking the user")]

    assert "automatically invokes" in completion
    assert "finishing-a-development-branch" in completion
    assert "一站一站來" in completion
    assert "after a task DONE" not in text


def test_plugin_version_and_changelog_ship_the_ci_loop():
    assert json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))["version"] == "0.97.8"
    assert json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))["version"] == "0.97.8"
    changelog = CHANGELOG.read_text(encoding="utf-8")
    release = changelog.split("## [0.97.8]", 1)[1].split("\n## [", 1)[0]
    assert "post-PR CI" in release
