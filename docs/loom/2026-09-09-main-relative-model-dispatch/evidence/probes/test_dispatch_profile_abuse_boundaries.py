"""Adversarial boundary probes for the shared dispatch-profile contract."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[5]
PROFILE = ROOT / "loom-code" / "references" / "dispatch-profile.md"


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
    assert any(
        verb in sentence.lower().split()
        for verb in ("must", "requires", "returns", "repair")
    )
    assert not any(
        token in sentence.lower().split()
        for token in ("not", "never", "neither", "without")
    )
    return sentence


def test_helper_affirmative_sentence_accepts_requirement() -> None:
    """The prose-pin helper accepts an affirmative requirement."""
    assert _affirmative_sentence("A successful run returns routed.", "returns routed")


def test_helper_negated_sentence_rejects_requirement() -> None:
    """The prose-pin helper rejects a negated requirement."""
    with pytest.raises(AssertionError):
        _affirmative_sentence("A successful run must not return routed.", "return routed")


def test_classification_security_mechanical_prefers_mechanical() -> None:
    """A mechanically checkable security edit cannot bypass declared precedence."""
    text = _contract()
    flat = _flat(text)

    assert "Classification precedence is `mechanical > complex > ordinary`" in flat
    assert "`mechanical` requires an exact transformation, bounded targets, and a mechanical oracle" in flat
    assert "Otherwise, `complex` requires" in flat


def test_evidence_missing_packet_routes_ordinary() -> None:
    """Irreparable missing classification evidence routes ordinary without role inference."""
    text = _contract()
    flat = _flat(text)

    _affirmative_sentence(text, "repair it before execution")
    assert "Otherwise route as `ordinary`" in flat
    assert "record `insufficient-task-evidence`" in flat
    assert "Role names and round labels are not routing evidence" in flat


def test_profile_unobservable_component_omits_both() -> None:
    """One unobservable main-profile component triggers the atomic fallback."""
    text = _contract()
    flat = _flat(text)

    assert "If either main-profile component is unavailable" in flat
    _affirmative_sentence(text, "omit both overrides")
    assert "partial profile" in flat


def test_capability_unsupported_pair_omits_both() -> None:
    """A model-specific unsupported pair cannot retain one tempting override."""
    text = _contract()
    flat = _flat(text)

    assert "unsupported model, effort, or model-effort combination is unsupported" in flat
    _affirmative_sentence(text, "omit both overrides")
    assert "keep the model override" not in flat
    assert "keep the effort override" not in flat


def test_escalation_high_xhigh_requires_sequence() -> None:
    """High and xhigh cannot be entered by skipping their completed predecessor."""
    text = _contract()
    flat = _flat(text)

    assert "Entering `high` requires a completed `frontier/medium` attempt" in flat
    assert "Entering `xhigh` requires a completed `frontier/high` attempt" in flat
    assert "`frontier/medium` → `frontier/high` → `frontier/xhigh`" in flat
    assert "transient executor failures are insufficient escalation evidence" in flat


def test_effort_max_native_remains_inherited() -> None:
    """Max and native effort values remain inheritance-only under portable arithmetic."""
    text = _contract()
    flat = _flat(text)

    _affirmative_sentence(text, "use `xhigh` as its generation ceiling")
    _affirmative_sentence(text, "remain inheritance-only values")
    _affirmative_sentence(text, "preserve an inherited host-native effort unchanged")
    assert "generate `max`" not in flat
    assert "generate `ultra`" not in flat


def test_rejection_preexecution_replacement_preserves_budget() -> None:
    """A pre-execution rejection and replacement do not consume a completed redispatch."""
    text = _contract()
    flat = _flat(text)

    assert "rejects a supposedly supported profile before task execution" in flat
    assert "retry once with both overrides omitted" in flat
    assert "This replacement occupies the same task attempt" in flat
    assert "two completed redispatches after its initial completed execution" in flat


def test_redispatch_final_success_returns_routed() -> None:
    """A successful final allowed redispatch returns routed despite budget exhaustion."""
    text = _contract()

    _affirmative_sentence(
        text,
        "successful execution returns `routed` regardless of its position in the budget",
    )
