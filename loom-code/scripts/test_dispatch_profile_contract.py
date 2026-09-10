"""Executable pins for Loom's shared, host-neutral dispatch profile."""

from __future__ import annotations

from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
PROFILE = PLUGIN / "references" / "dispatch-profile.md"


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
