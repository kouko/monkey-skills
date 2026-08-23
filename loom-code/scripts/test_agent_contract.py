"""Focused structural contracts for loom-code's implementation agent."""

from pathlib import Path


AGENT = Path(__file__).resolve().parent.parent / "agents" / "implementer.md"


def _requirement_contract() -> str:
    text = AGENT.read_text(encoding="utf-8")
    start = text.index("11. **`@req` Definition-of-Done")
    end = text.index("12. **Prose-contract placement guard", start)
    return " ".join(text[start:end].split())


def test_implementer_uses_packaged_requirement_identifier_contract():
    contract = _requirement_contract()

    assert (
        "[packaged requirement-identifier contract]"
        "(../skills/writing-plans/references/requirement-identifiers.md)"
        in contract
    )
    assert "Do not invoke `loom-design:spec-expansion` to interpret identifiers" in contract
    assert "optional upstream spec-authoring handoff" in contract
    assert "only when that public skill is available" in contract
    assert (
        "design-authored spec artifact is likewise optional upstream input, "
        "not a runtime dependency of this agent"
        in contract
    )

    # Mutation guard: restoring the old mandatory grammar handoff must fail even
    # if the local link and the new optional-handoff sentence remain present.
    assert "invoke `loom-design:spec-expansion` for the full" not in contract
    assert "repository source:" not in contract
