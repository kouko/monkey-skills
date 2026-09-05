"""Executable contract for `declared_lane()` and the `lane:`/`default-lane:`
grammar (plan W1-01).

`declared_lane` is a pure function -- no subprocess needed, unlike the
`intent`-subcommand cases below which exercise the CLI the way
`test_loom_checker_intent.py` does. Fixtures reuse that module's
`make_repo`/`run_checker`/`git`/`blocked_rules` helpers rather than
re-deriving them (loom-code convention: one helper set per shape).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import loom_checker
from test_loom_checker_intent import (  # noqa: E402
    blocked_rules,
    git,
    make_repo,
    run_checker,
)

CHECKER = Path(__file__).with_name("loom_checker.py")


def _write_intent(repo: Path, change_id: str, *, lane_lines: tuple[str, ...] = ()) -> Path:
    """A schema-complete intent (every required field/section) with zero or
    more `lane:` lines inserted after `needs-design:` -- the LAST one wins,
    per `parse_document`'s frontmatter dict (it overwrites on each match),
    so declared_lane needs no extra "last wins" logic of its own."""
    lines = [
        f"# {change_id}",
        "originator: kouko",
        "kind: engineering",
        "needs-design: no — no interface surface touched",
        *lane_lines,
        "",
        "## Problem",
        "People doing this work want less verification for a light change.",
        "",
        "## Proposed outcome",
        "A declared lane.",
        "",
        "## Acceptance",
        "1. The declared lane is honoured.",
        "",
        "## Constraints",
        "- none",
        "",
        "## Out of scope",
        "- none",
        "",
        "## Open questions",
        "- none",
        "",
    ]
    path = repo / f"docs/loom/intent/{change_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_kickoff(repo: Path, *, default_lane: str | None = None) -> None:
    lines = ["# Kickoff Defaults", ""]
    if default_lane is not None:
        lines.append(f"- default-lane: {default_lane} — a repo default (2026-09-05)")
    (repo / "docs/loom/KICKOFF-DEFAULTS.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/loom/KICKOFF-DEFAULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# =============================================================================
# declared_lane() -- pure function, no subprocess.
# =============================================================================


def test_declared_lane_plain_intent_value(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x1"
    _write_intent(repo, change_id, lane_lines=("lane: express",))
    assert loom_checker.declared_lane(repo, change_id) == ("express", "intent", None)


def test_declared_lane_switch_from_round(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x2"
    _write_intent(
        repo, change_id,
        lane_lines=("lane: express — switched 2026-09-05 by kouko, from round 2",),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("express", "intent", 2)


def test_declared_lane_switch_from_wave_has_no_round_number(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x3"
    _write_intent(
        repo, change_id,
        lane_lines=("lane: gate-only — switched 2026-09-05 by kouko, from wave 1",),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "intent", None)


def test_declared_lane_last_line_wins(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x4"
    _write_intent(
        repo, change_id,
        lane_lines=(
            "lane: express",
            "lane: gate-only — switched 2026-09-05 by kouko, from round 3",
        ),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "intent", 3)


def test_declared_lane_falls_back_to_kickoff_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x5"
    _write_intent(repo, change_id, lane_lines=())
    _write_kickoff(repo, default_lane="gate-only")
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "kickoff", None)


def test_declared_lane_falls_back_to_full_with_nothing_declared(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x6"
    _write_intent(repo, change_id, lane_lines=())
    assert loom_checker.declared_lane(repo, change_id) == ("full", "default", None)


def test_declared_lane_no_intent_file_falls_back_to_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    assert loom_checker.declared_lane(repo, "2026-09-05-nonexistent") == (
        "full", "default", None,
    )


# =============================================================================
# `intent` subcommand: schema and switch-line-verbatim-in-message rules.
# =============================================================================


def test_intent_lane_switch_missing_by_name_blocks_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y1"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    lane_line = "lane: express — switched 2026-09-05, from round 2"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{lane_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0
    assert "intent.schema" in blocked_rules(result)


def test_intent_lane_line_missing_from_commit_message_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y2"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write_intent(repo, change_id, lane_lines=("lane: express",))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0
    assert "intent.needs-design-reason" in blocked_rules(result)


def test_intent_lane_switch_with_by_name_and_verbatim_message_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y3"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    lane_line = "lane: express — switched 2026-09-05 by kouko, from round 2"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{lane_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_intent_no_lane_line_is_unaffected(tmp_path: Path) -> None:
    """No `lane:` line at all must never trip either new rule."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y4"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write_intent(repo, change_id, lane_lines=())
    git(repo, "add", intent_rel)
    message = "docs(loom): add an intent\n\nneeds-design: no — no interface surface touched"
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, result.stderr


# =============================================================================
# Rule count pin.
# =============================================================================


def test_list_rules_count_stays_twenty_seven() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rules, saw {len(lines)}:\n{result.stdout}"
