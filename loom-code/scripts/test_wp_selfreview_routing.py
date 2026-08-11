"""Pointer-pin pytest for writing-plans SKILL.md's routing-substitution-proofing
(docs/loom/backlog/2026-08-10-plan-document-reviewer-misrouted-as-agent-type.md).

A cold operator in an external consumer repo looked up plan-document-reviewer
in the agent registry, found nothing (it is a prompt file, not a registered
agent type), and substituted docs-reviewer with the wrong checklist for 3
rounds ending in a fiat PASS. This pin locks two disambiguation surfaces:
§Self-review states the prompt-file/no-substitution/model-default facts
explicitly, and the SUBAGENT-STOP block marks plan-document-reviewer as a
prompt-file role distinct from the registered agent roles it is listed
alongside.
"""
import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parents[1] / "skills" / "writing-plans" / "SKILL.md"
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def test_prompt_file_never_registry_never_substitute():
    norm = _norm(_skill_text())

    # §Self-review: explicit prompt-file identity, tied to its actual path.
    assert "PROMPT FILE" in norm
    assert "references/plan-document-reviewer-prompt.md" in norm
    assert "dispatched via a generic subagent" in norm

    # §Self-review: never an agent-registry lookup.
    assert "NEVER an agent-registry lookup" in norm

    # §Self-review: no other reviewer agent (docs-reviewer included) may substitute.
    assert "no other reviewer agent" in norm
    assert "docs-reviewer included" in norm
    assert "may substitute" in norm

    # §Self-review: dispatch model default + dispatch-time upward override.
    assert "model: sonnet" in norm
    assert "dispatch-time upward override" in norm

    # SUBAGENT-STOP: plan-document-reviewer disambiguated as a prompt-file
    # role, not a registered agent type, distinct from the roles it is
    # listed alongside.
    stop_match = re.search(
        r"<SUBAGENT-STOP>(.*?)</SUBAGENT-STOP>", _skill_text(), re.DOTALL
    )
    assert stop_match, "SUBAGENT-STOP block not found"
    stop_norm = _norm(stop_match.group(1))
    assert "plan-document-reviewer" in stop_norm
    assert "prompt-file role, not a registered agent type" in stop_norm
