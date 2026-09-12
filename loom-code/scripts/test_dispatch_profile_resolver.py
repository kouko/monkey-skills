"""Executable examples for the host-neutral dispatch-profile resolver."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import dispatch_profile  # noqa: E402


CAPABILITIES = {
    "economy": ["low", "medium"],
    "standard": ["low", "medium", "high"],
    "frontier": ["low", "medium", "high", "xhigh", "max", "ultra"],
}


def initial(model: str, effort: str, **evidence: bool) -> dict[str, object]:
    return {
        "event": "initial",
        "main_profile": {"model": model, "effort": effort},
        "task_evidence": evidence,
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }


@pytest.mark.parametrize(
    ("model", "expected"),
    [("economy", "economy"), ("standard", "economy"), ("frontier", "standard")],
)
def test_mechanical_route_computes_each_model_tier(model: str, expected: str) -> None:
    result = dispatch_profile.resolve(
        initial(
            model,
            "low",
            exact_transformation=True,
            bounded_targets=True,
            mechanical_oracle=True,
        )
    )

    assert result["task_class"] == "mechanical"
    assert result["requested_profile"] == {"model": expected, "effort": "low"}
    assert result["outcome"] == "dispatch"


def test_irreparable_insufficient_evidence_routes_ordinary() -> None:
    payload = initial("standard", "medium")
    payload["task_evidence"] = None

    result = dispatch_profile.resolve(payload)

    assert result["task_class"] == "ordinary"
    assert result["uncertainty"] == "insufficient-task-evidence"
    assert result["requested_profile"] == {"model": "standard", "effort": "medium"}


@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_all_five_portable_efforts_can_be_inherited(effort: str) -> None:
    result = dispatch_profile.resolve(initial("frontier", effort))
    assert result["requested_profile"] == {"model": "frontier", "effort": effort}


def test_host_native_effort_is_inherited_but_never_generated() -> None:
    inherited = dispatch_profile.resolve(initial("frontier", "ultra"))
    assert inherited["requested_profile"] == {"model": "frontier", "effort": "ultra"}

    generated = dispatch_profile.resolve(
        initial("frontier", "max", changed_consumed_interface=True)
    )
    assert generated["requested_profile"] == {"model": "frontier", "effort": "max"}


def test_selected_model_pair_is_checked_atomically() -> None:
    payload = initial("standard", "high")
    payload["capabilities"] = {"standard": ["low", "medium"]}

    result = dispatch_profile.resolve(payload)

    assert result["requested_profile"] == {"model": "standard", "effort": "high"}
    assert result["overrides"] is None
    assert result["effective_profile"] == "inherited"
    assert result["reason"] == "unsupported-profile"


def test_unknown_main_component_uses_atomic_unverified_fallback() -> None:
    payload = initial("standard", "medium")
    payload["main_profile"]["effort"] = "mystery"
    payload["inheritance_guaranteed"] = False

    result = dispatch_profile.resolve(payload)

    assert result["requested_profile"] is None
    assert result["overrides"] is None
    assert result["effective_profile"] == "host-default/unverified"


def test_preexecution_host_rejection_gets_one_override_free_replacement() -> None:
    payload = initial("standard", "medium")
    payload.update({"event": "host-rejection", "rejection_retried": False})

    result = dispatch_profile.resolve(payload)

    assert result["overrides"] is None
    assert result["outcome"] == "dispatch"
    assert result["completed_redispatches"] == 0
    assert result["reason"] == "host-rejection-replacement"

    payload["rejection_retried"] = True
    repeated = dispatch_profile.resolve(payload)
    assert repeated["outcome"] == "execution-failed"
    assert repeated["effective_profile"] == "host-default/unverified"


def test_host_rejection_needs_only_rejection_state_and_fallback_context() -> None:
    result = dispatch_profile.resolve(
        {
            "event": "host-rejection",
            "rejection_retried": False,
            "inheritance_guaranteed": False,
            "completed_redispatches": 0,
        }
    )

    assert result["overrides"] is None
    assert result["effective_profile"] == "host-default/unverified"


def test_reasoning_escalation_is_sequential_and_uses_shared_budget() -> None:
    high = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": True,
            "profile": {"model": "frontier", "effort": "medium"},
            "failure_kind": "reasoning-depth",
            "failure_trigger": "high-risk-decision-unsettled",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }
    high_result = dispatch_profile.resolve(high)
    assert high_result["requested_profile"] == {"model": "frontier", "effort": "high"}
    assert high_result["completed_redispatches"] == 0
    assert high_result["next_redispatch"] == 1

    xhigh = dict(high)
    xhigh["last_attempt"] = {
        **high["last_attempt"],
        "profile": {"model": "frontier", "effort": "high"},
        "failure_trigger": "same-high-risk-blocker-with-artifact",
    }
    xhigh["completed_redispatches"] = 1
    xhigh_result = dispatch_profile.resolve(xhigh)
    assert xhigh_result["requested_profile"] == {"model": "frontier", "effort": "xhigh"}
    assert xhigh_result["completed_redispatches"] == 1
    assert xhigh_result["next_redispatch"] == 2


def test_reasoning_depth_below_frontier_raises_effort_without_skipping_tiers() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": True,
            "profile": {"model": "standard", "effort": "low"},
            "failure_kind": "reasoning-depth",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["requested_profile"] == {"model": "standard", "effort": "medium"}
    assert result["reason"] == "reasoning-depth-redispatch"
    assert result["next_redispatch"] == 1


def test_capability_quality_at_frontier_low_falls_through_to_medium() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": True,
            "profile": {"model": "frontier", "effort": "low"},
            "failure_kind": "capability-quality",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["requested_profile"] == {"model": "frontier", "effort": "medium"}
    assert result["reason"] == "capability-quality-redispatch"
    assert result["next_redispatch"] == 1


def test_host_rejection_is_not_capability_quality_escalation() -> None:
    payload = initial("standard", "medium")
    payload.update({"event": "host-rejection", "failure_kind": "capability-quality"})
    result = dispatch_profile.resolve(payload)
    assert result["requested_profile"] is None
    assert result["reason"] == "host-rejection-replacement"


def test_final_allowed_execution_success_is_routed() -> None:
    result = dispatch_profile.resolve(
        {
            "event": "after-execution",
            "last_attempt": {
                "completed": True,
                "success": True,
                "conforming": True,
                "profile": {"model": "frontier", "effort": "xhigh"},
            },
            "capabilities": CAPABILITIES,
            "inheritance_guaranteed": True,
            "completed_redispatches": 2,
        }
    )
    assert result["outcome"] == "routed"
    assert result["effective_profile"] == {"model": "frontier", "effort": "xhigh"}


def test_completed_nonconforming_output_retries_same_profile() -> None:
    profile = {"model": "frontier", "effort": "medium"}

    result = dispatch_profile.resolve(
        {
            "event": "after-execution",
            "last_attempt": {
                "completed": True,
                "success": False,
                "conforming": False,
                "profile": profile,
                "failure_kind": "malformed-response",
            },
            "capabilities": CAPABILITIES,
            "inheritance_guaranteed": True,
            "completed_redispatches": 0,
        }
    )

    assert result["outcome"] == "dispatch"
    assert result["reason"] == "nonconforming-output-redispatch"
    assert result["requested_profile"] == profile
    assert result["overrides"] == profile
    assert result["effective_profile"] == profile
    assert result["next_redispatch"] == 1


def test_nonconforming_output_at_redispatch_limit_fails_closed() -> None:
    result = dispatch_profile.resolve(
        {
            "event": "after-execution",
            "last_attempt": {
                "completed": True,
                "success": False,
                "conforming": False,
                "profile": {"model": "frontier", "effort": "medium"},
                "failure_kind": "malformed-response",
            },
            "capabilities": CAPABILITIES,
            "inheritance_guaranteed": True,
            "completed_redispatches": 2,
        }
    )

    assert result["outcome"] == "execution-failed"
    assert result["reason"] == "no-legal-redispatch"


def test_nonconforming_output_with_unknown_failure_kind_is_rejected() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": False,
            "profile": {"model": "frontier", "effort": "medium"},
            "failure_kind": "invented-upgrade-reason",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    with pytest.raises(dispatch_profile.InputError):
        dispatch_profile.resolve(payload)


@pytest.mark.parametrize(
    ("completed", "completed_redispatches"),
    [(False, 0), (True, 2)],
)
def test_unknown_failure_kind_is_rejected_before_terminal_guards(
    completed: bool, completed_redispatches: int,
) -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": completed,
            "success": False,
            "conforming": False,
            "profile": {"model": "frontier", "effort": "medium"},
            "failure_kind": "invented-upgrade-reason",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": completed_redispatches,
    }

    with pytest.raises(dispatch_profile.InputError):
        dispatch_profile.resolve(payload)


def test_nonconforming_known_nonrouting_failure_is_terminal() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": False,
            "profile": {"model": "frontier", "effort": "medium"},
            "failure_kind": "timeout",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["outcome"] == "execution-failed"
    assert result["reason"] == "non-routing-failure"


def test_nonconforming_output_without_failure_kind_is_terminal() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": False,
            "profile": {"model": "frontier", "effort": "medium"},
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["outcome"] == "execution-failed"
    assert result["reason"] == "no-legal-redispatch"


def test_incomplete_attempt_fails_closed() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": False,
            "success": False,
            "conforming": False,
            "profile": {"model": "frontier", "effort": "medium"},
            "failure_kind": "timeout",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["outcome"] == "execution-failed"
    assert result["reason"] == "no-legal-redispatch"


def test_nonconforming_malformed_output_never_escalates() -> None:
    profile = {"model": "frontier", "effort": "medium"}
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": False,
            "profile": profile,
            "failure_kind": "malformed-response",
            "failure_trigger": "high-risk-decision-unsettled",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }

    result = dispatch_profile.resolve(payload)

    assert result["effective_profile"] == profile
    assert result["reason"] == "nonconforming-output-redispatch"


def test_cli_is_deterministic_json_and_rejects_malformed_input() -> None:
    script = SCRIPTS / "dispatch_profile.py"
    payload = initial("standard", "medium")
    run = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode == 0
    assert json.loads(run.stdout) == dispatch_profile.resolve(payload)

    bad = subprocess.run(
        [sys.executable, str(script)],
        input="not-json",
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad.returncode == 2
    assert bad.stdout == ""


def test_unknown_failure_kind_fails_closed() -> None:
    payload = {
        "event": "after-execution",
        "last_attempt": {
            "completed": True,
            "success": False,
            "conforming": True,
            "profile": {"model": "standard", "effort": "medium"},
            "failure_kind": "invented-upgrade-reason",
        },
        "capabilities": CAPABILITIES,
        "inheritance_guaranteed": True,
        "completed_redispatches": 0,
    }
    with pytest.raises(dispatch_profile.InputError):
        dispatch_profile.resolve(payload)


def test_contract_defines_the_executable_json_boundary() -> None:
    text = (PLUGIN / "references" / "dispatch-profile.md").read_text(encoding="utf-8")
    assert "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch_profile.py" in text
    assert "python3 <injected loom-code plugin root>/scripts/dispatch_profile.py" in text
    assert '"event": "initial"' in text
    assert '"event": "after-execution"' in text
    assert '"event": "host-rejection"' in text
    assert "capabilities" in text
    assert "completed_redispatches" in text


@pytest.mark.parametrize("station", ["build", "review"])
def test_stations_invoke_the_executable_resolver_before_spawn(station: str) -> None:
    text = (PLUGIN / "skills" / station / "SKILL.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch_profile.py" in text
    assert "python3 <injected loom-code plugin root>/scripts/dispatch_profile.py" in text
    assert "Pass its deterministic JSON result to the host-native spawn" in flat
    assert "post-execution capability-quality failure" in flat
    assert "pre-execution host rejection" in flat
