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


def _prose_self_sweep_rule() -> str:
    text = AGENT.read_text(encoding="utf-8")
    start = text.index("14. **Prose-edit self-sweep")
    end = text.index("<!-- BEGIN baseline-v1", start)
    return text[start:end]


def test_implementer_has_prose_edit_self_sweep_rule():
    rule = _prose_self_sweep_rule()

    for marker in ("(a)", "(b)", "(c)", "(d)", "(e)"):
        assert marker in rule

    for phrase in ("Do not emit", "self-score", "PASS claim"):
        assert phrase in rule

    # Mutation guard: the rule must stay silent — no checklist output verb.
    assert "output the checklist" not in rule
    assert "emit a checklist" not in rule

    # Out-link guard: the firing condition's referents (`Files touched`,
    # `Review-weight`) must resolve to plan-format.md for a cold reader.
    assert "plan-format.md" in rule
    assert "Review-weight" in rule

    # Position guard: rule 14 must live before the managed baseline block,
    # in the hand-written section distribute.py never overwrites.
    text = AGENT.read_text(encoding="utf-8")
    assert text.index("14. **Prose-edit self-sweep") < text.index(
        "<!-- BEGIN baseline-v1"
    )
