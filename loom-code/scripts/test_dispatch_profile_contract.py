"""Executable pins for Loom's shared, host-neutral dispatch profile."""

from __future__ import annotations

import shutil
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
PROFILE = PLUGIN / "references" / "dispatch-profile.md"
MECHANISMS = PLUGIN.parent / "docs" / "loom" / "evidence" / "mechanisms.yaml"
PILOT_REPORT = (
    PLUGIN.parent
    / "docs"
    / "skill-dogfood"
    / "2026-09-09-model-effort-cost-pilot"
    / "report.md"
)
STATIONS = (
    PLUGIN / "skills" / "build" / "SKILL.md",
    PLUGIN / "skills" / "review" / "SKILL.md",
)


def _contract() -> str:
    return PROFILE.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _affirmative_sentence(text: str, anchor: str) -> str:
    sentence = next(
        part.strip()
        for part in text.replace("\n", " ").split(".")
        if anchor in part
    )
    assert "must" in sentence.lower()
    assert not any(
        token in sentence.lower().split()
        for token in ("not", "never", "neither", "without")
    )
    return sentence


def test_affirmative_sentence_helper_accepts_requirement() -> None:
    assert _affirmative_sentence("The dispatcher must preserve effort.", "preserve effort")


def test_affirmative_sentence_helper_rejects_negated_requirement() -> None:
    try:
        _affirmative_sentence("The dispatcher must not preserve effort.", "preserve effort")
    except AssertionError:
        pass
    else:
        raise AssertionError("negated prose must not satisfy an affirmative contract pin")


def test_class_relative_route_and_insufficient_evidence_boundary() -> None:
    text = _contract()
    flat = _flat(text)

    assert "mechanical > complex > ordinary" in flat
    _affirmative_sentence(text, "lower the model by one tier and preserve effort")
    _affirmative_sentence(text, "raise the model by one tier and preserve effort")
    _affirmative_sentence(text, "preserve both model and effort")
    assert "exact transformation, bounded targets, and a mechanical oracle" in flat
    assert "insufficient-task-evidence" in flat
    assert "route as `ordinary`" in flat
    assert "Role names and round labels are not routing evidence" in flat


def test_five_portable_effort_tiers_and_native_values_are_inheritance_only() -> None:
    text = _contract()
    flat = _flat(text)

    assert "`economy < standard < frontier`" in flat
    assert "`low < medium < high < xhigh < max`" in flat
    assert "host-native effort" in flat
    _affirmative_sentence(text, "preserve an inherited host-native effort unchanged")
    _affirmative_sentence(text, "use `xhigh` as its generation ceiling")
    _affirmative_sentence(text, "remain inheritance-only values")
    assert "Portable arithmetic generates `ultra`" not in flat


def test_atomic_fallback_forbids_partial_profiles() -> None:
    text = _contract()
    flat = _flat(text)

    _affirmative_sentence(text, "verify the selected model accepts the requested effort")
    _affirmative_sentence(text, "omit both overrides")
    assert "retry once with both overrides omitted" in flat
    assert "partial profile" in flat
    assert "keep the supported override" not in flat
    assert "ask the user to choose" not in flat


def test_high_and_xhigh_are_sequential_and_max_is_inherited_only() -> None:
    text = _contract()
    flat = _flat(text)

    assert "completed `frontier/medium` attempt" in flat
    assert "completed `frontier/high` attempt" in flat
    assert "`frontier/medium` → `frontier/high` → `frontier/xhigh`" in flat
    _affirmative_sentence(text, "retain the matching failure trigger")
    _affirmative_sentence(text, "use `xhigh` as its generation ceiling")
    _affirmative_sentence(text, "remain inheritance-only values")
    assert "An inherited `max`" in flat
    assert "initial dispatch may newly enter only `low` or `medium`" in flat


def test_capability_quality_transition_is_complete_at_the_model_ceiling() -> None:
    text = _contract()
    flat = _flat(text)

    assert "Below `frontier`, a capability-quality failure raises the model one tier" in flat
    assert "At `frontier`, capability-quality uses the same effort handling" in flat
    assert "`low` raises to `medium`" in flat
    assert "does not bypass the `high` or `xhigh` evidence gates" in flat


def test_failure_observations_define_conformance_and_trigger_requirements() -> None:
    text = _contract()
    flat = _flat(text)

    assert "`success: false` and `conforming: true`" in flat
    assert "`conforming: false` means the output cannot be graded" in flat
    assert "`failure_trigger` is required only for a transition into `high` or `xhigh`" in flat


def test_final_allowed_redispatch_success_returns_routed() -> None:
    text = _contract()

    _affirmative_sentence(
        text,
        "successful execution returns `routed` regardless of its position in the budget",
    )


def test_build_and_review_resolve_the_shared_profile_before_every_dispatch() -> None:
    for station in STATIONS:
        text = station.read_text(encoding="utf-8")
        flat = _flat(text)
        link = "../../references/dispatch-profile.md"

        assert f"]({link})" in text, f"{station.name} must link the packaged contract"
        _affirmative_sentence(text, "Before every host-native dispatch")
        assert "classify the task from its evidence" in flat
        assert "resolve the atomic model-and-effort profile" in flat
        assert "active task context only" in flat
        assert "static model or effort pin" in flat


def test_claude_reviewer_dispatch_is_atomic_and_retry_budgets_do_not_stack() -> None:
    review = (PLUGIN / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    flat = _flat(review)

    assert "--model <model> --effort <effort>" in flat
    assert "invoke the runner with neither flag" in flat
    assert "rejects a partial pair before starting Claude" in flat
    assert "must not enter the generic transient-executor retry" in flat
    assert "`rejection_retried: true`" in flat
    assert "`[claude-code:unrecognized_model]`" in flat
    assert "Every other non-zero exit" in flat
    assert "consumes the one same-digest transient-retry slot" in flat
    assert "no further Claude invocation occurs for that digest" in flat
    assert "stderr JSON `kind`" in flat
    assert "plain-text exit 2" in flat


def test_atomic_claude_dispatch_gate_is_registered_with_executable_eval() -> None:
    gate_id = "review.atomic-claude-dispatch"
    review = (PLUGIN / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    mechanisms = MECHANISMS.read_text(encoding="utf-8")

    assert review.count(f"<!-- gate: {gate_id} -->") == 1
    assert review.count("<!-- /gate -->", review.find(f"<!-- gate: {gate_id} -->")) >= 1
    assert f'- id: "{gate_id}"' in mechanisms
    assert (
        "eval: loom-code/scripts/test_dispatch_profile_contract.py::"
        "test_claude_reviewer_dispatch_is_atomic_and_retry_budgets_do_not_stack"
    ) in mechanisms


def test_packaged_station_reference_resolves_after_isolated_install(tmp_path: Path) -> None:
    isolated = tmp_path / "standalone-loom-code"
    shutil.copytree(PLUGIN, isolated)

    for relative in (Path("skills/build/SKILL.md"), Path("skills/review/SKILL.md")):
        station = isolated / relative
        target = (station.parent / "../../references/dispatch-profile.md").resolve()
        assert target.is_relative_to(isolated.resolve())
        assert target.is_file()


def test_shared_routing_gate_is_registered_once_with_executable_eval() -> None:
    gate_id = "dispatch-profile.relative-routing"
    marker = f"<!-- gate: {gate_id} -->"
    profile = _contract()
    mechanisms = MECHANISMS.read_text(encoding="utf-8")

    assert profile.count(marker) == 1
    assert f'- id: "{gate_id}"' in mechanisms
    assert (
        "eval: loom-code/scripts/test_dispatch_profile_contract.py::"
        "test_class_relative_route_and_insufficient_evidence_boundary"
    ) in mechanisms


def test_cost_pilot_sparse_ladder_is_historical_not_normative_routing() -> None:
    report = _flat(PILOT_REPORT.read_text(encoding="utf-8"))

    assert "historical experiment design" in report
    assert "final routing" in report
    assert "`standard/medium` → `frontier/medium`" in report
    assert "comparison and calibration evidence" in report
