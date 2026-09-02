"""Executable contract for `loom_checker.py`'s CLI surface (plan W0-02).

The rule-id table this asserts is a mechanism population: `--list-rules`
is the recomputable face of the checker for `docs/loom/evidence/
mechanisms.yaml` (concept-model §11), so the ids are pinned here and a
rename is a deliberate, visible edit rather than silent drift.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")

EXPECTED_RULE_IDS = [
    "intake.confirmed",
    "intake.confirmed-behavior",
    "intake.spec-pass",
    "intent.needs-design-reason",
    "intent.needs-design-recompute",
    "intent.product-no-identifiers",
    "intent.schema",
    "push.open-findings-closed",
    "push.probes-package-tests",
    "push.review-only-head",
    "push.reviewed-sha",
    "push.reviewer-ne-implementer",
    "push.verdicts-ge-2",
    "standing.product-principles-reject",
    "standing.silence",
    "standing.warn",
]


def run_checker(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def test_list_rules_exits_zero() -> None:
    assert run_checker("--list-rules").returncode == 0


def test_list_rules_emits_id_tab_description() -> None:
    lines = run_checker("--list-rules").stdout.splitlines()
    assert lines
    for line in lines:
        assert line.count("\t") == 1, line
        rule_id, description = line.split("\t")
        assert rule_id.strip() == rule_id
        assert description.strip() == description
        assert len(description.split()) >= 3, line


def test_list_rules_covers_exactly_the_planned_population() -> None:
    ids = [line.split("\t")[0] for line in run_checker("--list-rules").stdout.splitlines()]
    assert ids == EXPECTED_RULE_IDS


def test_list_rules_is_sorted_and_stable() -> None:
    first = run_checker("--list-rules").stdout
    second = run_checker("--list-rules").stdout
    assert first == second
    ids = [line.split("\t")[0] for line in first.splitlines()]
    assert ids == sorted(ids)


def test_every_rule_id_is_area_dot_name() -> None:
    for line in run_checker("--list-rules").stdout.splitlines():
        rule_id = line.split("\t")[0]
        area, _, name = rule_id.partition(".")
        assert area in {"intent", "intake", "push", "standing"}, rule_id
        assert name and "." not in name, rule_id


def test_unknown_subcommand_exits_2() -> None:
    result = run_checker("teleport")
    assert result.returncode == 2
    assert "teleport" in result.stderr


def test_no_arguments_exits_2() -> None:
    result = run_checker()
    assert result.returncode == 2
    assert result.stderr.strip()


def test_hooks_probe_is_reserved_and_exits_2() -> None:
    result = run_checker("hooks-probe")
    assert result.returncode == 2
    assert "not implemented" in result.stderr


def test_missing_operand_exits_2(tmp_path: Path) -> None:
    for argv in (["intent"], ["intake"], ["intake", "write-plan"], ["standing"]):
        result = run_checker(*argv, cwd=tmp_path)
        assert result.returncode == 2, argv
        assert result.stderr.strip(), argv


def test_internal_failure_fails_closed_with_exit_2(tmp_path: Path) -> None:
    """A path that cannot be read is an internal error, never a silent pass."""
    result = run_checker("intent", str(tmp_path / "nope.md"), cwd=tmp_path)
    assert result.returncode == 2
