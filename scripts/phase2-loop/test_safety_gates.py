"""Pre-flight safety gates for the nightly Phase 2 loop (Task 2).

These are the deterministic checks the unattended routine runs BEFORE it
touches anything: kill switch, scope guard, branch guard. They are pure
logic with no side effects so they can be exhaustively unit-tested.
"""

import pytest

import safety_gates
from safety_gates import (
    is_nightly_paused,
    requires_real_agent_surface,
)


# --- kill switch: is_nightly_paused ---------------------------------------


def test_paused_when_sentinel_file_exists(tmp_path):
    sentinel = tmp_path / "NIGHTLY_PAUSED"
    sentinel.write_text("paused by kouko\n")
    assert is_nightly_paused(sentinel) is True


def test_not_paused_when_sentinel_file_absent(tmp_path):
    sentinel = tmp_path / "NIGHTLY_PAUSED"
    assert is_nightly_paused(sentinel) is False


def test_kill_switch_never_writes_sentinel(tmp_path):
    # The routine only ever READS this file; checking must not create it.
    sentinel = tmp_path / "NIGHTLY_PAUSED"
    is_nightly_paused(sentinel)
    assert not sentinel.exists()


# --- scope guard: requires_real_agent_surface -----------------------------


@pytest.mark.parametrize(
    "description",
    [
        "run claude -p to validate the harness",
        "needs a headless agent eval pass",
        "kick off the real-headless-agent eval loop",
        "requires an e2e run against a live model",
    ],
)
def test_requires_surface_for_real_agent_language(description):
    assert requires_real_agent_surface(description) is True


def test_no_surface_for_plain_mechanical_b1():
    # B1's actual text from docs/dbt-wiki-quality-campaign.md — a purely
    # mechanical fix the nightly loop is allowed to pick up.
    b1 = "B1: rescan ~450 lines inline pseudocode -> shipped TDD'd scripts"
    assert requires_real_agent_surface(b1) is False


def test_does_not_false_positive_on_retrieval():
    # "eval" is a substring of "retrieval" -- must not fire on in-domain
    # prose that merely contains the word, only on standalone agent/eval.
    assert requires_real_agent_surface("optimize tiered retrieval") is False


def test_fail_closed_on_ambiguous_description():
    # Deliberately ambiguous: gestures at an agent/eval invocation without
    # clearly being mechanical. Fail closed -> refuse rather than guess.
    ambiguous = "re-run the eval loop and reconcile the agent output"
    assert requires_real_agent_surface(ambiguous) is True


# --- branch guard removed: assert_safe_target_branch ----------------------


def test_assert_safe_target_branch_removed():
    # Retired dead code: batch_queue.py's ensure_worktree already isolates
    # every queue entry into its own branch/worktree, superseding this
    # module's own branch-collision check.
    assert hasattr(safety_gates, "assert_safe_target_branch") is False
