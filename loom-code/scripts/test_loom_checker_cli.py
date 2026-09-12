"""Executable contract for `loom_checker.py`'s CLI surface (plan W0-02).

The rule-id table this asserts is a mechanism population: `--list-rules`
is the recomputable face of the checker for `docs/loom/evidence/
mechanisms.yaml` (concept-model §11), so the ids are pinned here and a
rename is a deliberate, visible edit rather than silent drift.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")

EXPECTED_RULE_IDS = [
    "contract.charter-complete",
    "contract.requires",
    "intake.confirmed",
    "intake.confirmed-behavior",
    "intake.spec-ready",
    "intake.test-case-pair",
    "intent.kind-recompute",
    "intent.needs-design-reason",
    "intent.needs-design-recompute",
    "intent.product-no-identifiers",
    "intent.schema",
    "plan.field-caps",
    "push.attestation",
    "push.contextual-body",
    "spec.req-grammar",
    "spec.ui-flows-recompute",
    "standing.product-principles-reject",
    "standing.second-vendor-valid",
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


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def make_intent_state_repo(tmp_path: Path, *, delivered: bool) -> tuple[Path, str]:
    repo = tmp_path / "intent-state-repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    intent = repo / "docs/loom/intent/2026-09-09-example.md"
    intent.parent.mkdir(parents=True)
    intent.write_text(
        """# Example
originator: tester
kind: engineering
needs-design: no — fixture
status: confirmed 2026-09-09

## Problem
Fixture.

## Proposed outcome
Fixture.

## Acceptance
1. Fixture passes.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
""",
        encoding="utf-8",
    )
    git(repo, "add", str(intent.relative_to(repo)))
    git(repo, "commit", "-q", "-m", "confirmed intent")
    if delivered:
        attestation = repo / "docs/loom/2026-09-09-example/attestation.json"
        attestation.parent.mkdir(parents=True)
        attestation.write_text(
            json.dumps(
                {
                    "schema": "loom-attestation/v1",
                    "change_id": "2026-09-09-example",
                    "content_digest": "historical",
                    "executions": [{
                        "kind": "package-tests", "command": "pytest", "artifact": "",
                        "result": "pass", "command_digest": "0" * 64,
                    }],
                    "verdicts": [{
                        "reviewer": "fixture", "vendor": "test", "model": "test",
                        "lens": "code", "verdict": "PASS", "findings": [],
                    }],
                    "findings": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        git(repo, "add", str(attestation.relative_to(repo)))
        git(repo, "commit", "-q", "-m", "deliver example (#123)")
    remote_head = git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/origin/trunk", remote_head)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    git(repo, "checkout", "-q", "-b", "work")
    return repo, remote_head


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


def test_list_rules_describes_the_closed_status_alternative() -> None:
    lines = run_checker("--list-rules").stdout.splitlines()
    confirmed_line = next(line for line in lines if line.startswith("intake.confirmed\t"))
    assert "closed" in confirmed_line
    assert "PR #" in confirmed_line
    assert "remote-default" in confirmed_line
    assert "indeterminate" in confirmed_line


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
        assert area in {"contract", "intent", "intake", "plan", "push", "review", "spec", "standing"}, rule_id
        assert name and "." not in name, rule_id


def test_unknown_subcommand_exits_2() -> None:
    result = run_checker("teleport")
    assert result.returncode == 2
    assert "teleport" in result.stderr


def test_no_arguments_exits_2() -> None:
    result = run_checker()
    assert result.returncode == 2
    assert result.stderr.strip()


def test_publish_is_a_declared_cli_command() -> None:
    import loom_checker

    assert loom_checker.COMMANDS["publish"] is loom_checker.cmd_publish
    assert "loom_checker.py publish --confirm-authorized" in loom_checker.__doc__


def test_intents_is_a_declared_cli_command() -> None:
    import loom_checker

    assert loom_checker.COMMANDS["intents"] is loom_checker.cmd_intents
    assert "loom_checker.py intents" in loom_checker.__doc__


def test_intents_lists_only_active_confirmed_intents_by_default(tmp_path: Path) -> None:
    active_repo, _ = make_intent_state_repo(tmp_path / "active", delivered=False)
    delivered_repo, _ = make_intent_state_repo(tmp_path / "delivered", delivered=True)

    active = run_checker("intents", cwd=active_repo)
    delivered = run_checker("intents", cwd=delivered_repo)

    assert active.returncode == 0
    assert active.stdout == "2026-09-09-example\tactive\n"
    assert delivered.returncode == 0
    assert delivered.stdout == ""


def test_intents_reports_one_delivered_intent_with_optional_metadata(tmp_path: Path) -> None:
    repo, remote_head = make_intent_state_repo(tmp_path, delivered=True)

    result = run_checker("intents", "2026-09-09-example", "--metadata", cwd=repo)

    assert result.returncode == 0
    assert result.stdout.startswith("2026-09-09-example\tdelivered")
    assert f"commit={remote_head}" in result.stdout
    assert "pr=#123" in result.stdout
    assert "committed_at=" in result.stdout
    assert "merged_at=" not in result.stdout


def test_intents_explains_why_one_intent_is_active(tmp_path: Path) -> None:
    repo, _ = make_intent_state_repo(tmp_path, delivered=False)

    result = run_checker("intents", "2026-09-09-example", cwd=repo)

    assert result.returncode == 0
    assert result.stdout.startswith("2026-09-09-example\tactive\t")
    assert "attestation is absent" in result.stdout


def test_intents_reports_indeterminate_without_remote_default(tmp_path: Path) -> None:
    repo, _ = make_intent_state_repo(tmp_path, delivered=False)
    git(repo, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")

    result = run_checker("intents", "2026-09-09-example", cwd=repo)

    assert result.returncode == 1
    assert "2026-09-09-example\tindeterminate" in result.stdout
    assert "refresh the selected remote-default ref" in result.stdout


def test_intents_rejects_an_unsafe_remote_name(tmp_path: Path) -> None:
    repo, _ = make_intent_state_repo(tmp_path, delivered=False)

    result = run_checker("intents", "--remote", "../origin", cwd=repo)

    assert result.returncode == 2
    assert "safe literal" in result.stderr


def test_hooks_probe_is_gone() -> None:
    """`--self-test` in codex_scaffold.py owns the copy check; the reserved
    checker sub-command that never grew a body is deleted, not kept."""
    result = run_checker("hooks-probe")
    assert result.returncode == 2
    assert "unknown sub-command" in result.stderr
    assert "hooks-probe" not in CHECKER.read_text(encoding="utf-8").split('"""')[1]


def test_the_rule_population_is_twenty() -> None:
    assert len(run_checker("--list-rules").stdout.splitlines()) == 20


# --- contract --require (spec G) -------------------------------------------


def test_contract_require_accepts_a_met_floor() -> None:
    assert run_checker("contract", "--require", "2.0").returncode == 0


def test_contract_require_blocks_a_higher_minor() -> None:
    result = run_checker("contract", "--require", "2.99")
    assert result.returncode == 1
    assert "BLOCK contract.requires:" in result.stderr
    assert "請更新 loom-code" in result.stderr


def test_contract_require_blocks_a_different_major() -> None:
    result = run_checker("contract", "--require", "1.0")
    assert result.returncode == 1
    assert "contract.requires" in result.stderr


def test_contract_require_higher_major_still_says_update_loom_code() -> None:
    """The shipped contract (major 2) is below a higher required major (3):
    the checker itself is what's behind, so the old message direction
    ('please update loom-code') is correct and unchanged."""
    result = run_checker("contract", "--require", "3.0")
    assert result.returncode == 1
    assert "請更新 loom-code" in result.stderr


def test_contract_require_lower_major_blames_the_consuming_plugin() -> None:
    """The shipped contract (major 2) is above a lower required major (0):
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


# --- descriptions carry the load-bearing condition (W2 re-review) ---------
#
# `--list-rules` is what a reader consults to learn what a rule actually
# recomputes. A description that stops short of the condition that blocks
# is how a reader forms the wrong model of the gate, so each one is pinned
# to the words that name its own mechanism.

LOAD_BEARING_WORDS = {
    "push.attestation": ["content digest", "without replaying"],
    "intake.spec-ready": ["pre-build-review", "not persisted", "ledger"],
    "intake.test-case-pair": ["Acceptance", "positive", "negative or boundary"],
    "contract.requires": ["same major", "minor"],
    "spec.ui-flows-recompute": ["visible characters", "reviewer"],
}


def test_descriptions_name_their_load_bearing_condition() -> None:
    described = dict(
        line.split("\t", 1)
        for line in run_checker("--list-rules").stdout.splitlines()
        if "\t" in line
    )
    for rule_id, words in LOAD_BEARING_WORDS.items():
        description = described[rule_id]
        missing = [word for word in words if word not in description]
        assert not missing, f"{rule_id} description omits {missing}: {description!r}"
