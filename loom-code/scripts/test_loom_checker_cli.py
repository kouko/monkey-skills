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
    "contract.requires",
    "intake.confirmed",
    "intake.confirmed-behavior",
    "intake.spec-pass",
    "intent.needs-design-reason",
    "intent.needs-design-recompute",
    "intent.product-no-identifiers",
    "intent.schema",
    "push.dismissed-by-reviewer",
    "push.open-findings-closed",
    "push.probes-adversarial",
    "push.probes-package-tests",
    "push.review-only-head",
    "push.review-schema",
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
        assert area in {"contract", "intent", "intake", "push", "standing"}, rule_id
        assert name and "." not in name, rule_id


def test_unknown_subcommand_exits_2() -> None:
    result = run_checker("teleport")
    assert result.returncode == 2
    assert "teleport" in result.stderr


def test_no_arguments_exits_2() -> None:
    result = run_checker()
    assert result.returncode == 2
    assert result.stderr.strip()


def test_hooks_probe_is_gone() -> None:
    """`--probe` in codex_scaffold.py owns the belt check; the reserved
    checker sub-command that never grew a body is deleted, not kept."""
    result = run_checker("hooks-probe")
    assert result.returncode == 2
    assert "unknown sub-command" in result.stderr
    assert "hooks-probe" not in CHECKER.read_text(encoding="utf-8").split('"""')[1]


def test_the_rule_population_is_twenty() -> None:
    assert len(run_checker("--list-rules").stdout.splitlines()) == 20


# --- contract --require (spec G) -------------------------------------------


def test_contract_require_accepts_a_met_floor() -> None:
    assert run_checker("contract", "--require", "1.0").returncode == 0


def test_contract_require_blocks_a_higher_minor() -> None:
    result = run_checker("contract", "--require", "1.99")
    assert result.returncode == 1
    assert "BLOCK contract.requires:" in result.stderr
    assert "請更新 loom-code" in result.stderr


def test_contract_require_blocks_a_different_major() -> None:
    result = run_checker("contract", "--require", "2.0")
    assert result.returncode == 1
    assert "contract.requires" in result.stderr


def test_contract_require_higher_major_still_says_update_loom_code() -> None:
    """The shipped contract (major 1) is below a higher required major (2):
    the checker itself is what's behind, so the old message direction
    ('please update loom-code') is correct and unchanged."""
    result = run_checker("contract", "--require", "2.0")
    assert result.returncode == 1
    assert "請更新 loom-code" in result.stderr


def test_contract_require_lower_major_blames_the_consuming_plugin() -> None:
    """The shipped contract (major 1) is above a lower required major (0):
    the CONSUMER declares an old contract major, not loom-code being behind
    -- the message must point at the consuming plugin, never say
    '請更新 loom-code'."""
    result = run_checker("contract", "--require", "0.5")
    assert result.returncode == 1
    assert "BLOCK contract.requires:" in result.stderr
    assert "請更新 loom-code" not in result.stderr
    assert "consuming plugin" in result.stderr
    assert "old contract major" in result.stderr


def test_contract_require_rejects_a_malformed_floor() -> None:
    assert run_checker("contract", "--require", "1").returncode == 2
    assert run_checker("contract").returncode == 2


def test_missing_operand_exits_2(tmp_path: Path) -> None:
    for argv in (["intent"], ["intake"], ["intake", "write-plan"], ["standing"]):
        result = run_checker(*argv, cwd=tmp_path)
        assert result.returncode == 2, argv
        assert result.stderr.strip(), argv


def test_internal_failure_fails_closed_with_exit_2(tmp_path: Path) -> None:
    """A path that cannot be read is an internal error, never a silent pass."""
    result = run_checker("intent", str(tmp_path / "nope.md"), cwd=tmp_path)
    assert result.returncode == 2
