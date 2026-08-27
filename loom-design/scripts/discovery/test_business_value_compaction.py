"""Compaction contract for the business-value entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "business-value" / "SKILL.md"


def test_entrypoint_preserves_firing_axes_verdict_and_validation():
    text = SKILL.read_text(encoding="utf-8")
    low = text.lower()

    # Decidable firing and silent negative guards.
    assert "fire when any" in low.replace("*", "")
    for marker in ("**(a)**", "**(b)**", "**(c)**"):
        assert marker in low
    assert "personal tool" in low
    assert "go is already decided" in low
    assert "incremental feature" in low
    assert "skip silently" in low
    assert "implicit go" in low
    assert "no artifact" in low

    # Re-entrant interrogation and jurisdiction.
    assert "re-entrant" in low
    assert "not a one-way gate" in low
    assert "one question at a time" in low
    for axis in ("why now", "why me", "opportunity cost"):
        assert axis in low
    assert "domain-teams:planning-team" in text
    assert "user-insights" in low
    assert "never inline" in low

    # Executor, ratification, verdict policy, and artifact contract.
    assert "you (the agent running this skill) are the executor" in low
    assert "user's call to ratify" in low
    for verdict in ("GO", "NO-GO", "NEEDS-MORE-RESEARCH"):
        assert verdict in text
    assert "one" in low and "weak axis" in low and "two or more" in low
    assert "assets/business-value-template.md" in text
    assert "docs/loom/discovery/<date>-<slug>/business-value.md" in text

    # Validator invocation is direct argv, bounded, and terminal boundary stays clear.
    assert "validate_discovery_artifacts.py" in text
    assert "argv:" in low
    assert "never through a shell" in low
    assert "2 attempts" in low
    assert "stop at the worth-it one-pager" in low

