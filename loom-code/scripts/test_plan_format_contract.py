"""Contract pins for the packaged writing-plans schema."""

from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
PLAN_FORMAT = PLUGIN_ROOT / "skills/writing-plans/references/plan-format.md"
IDENTIFIER_CONTRACT = (
    PLUGIN_ROOT / "skills/writing-plans/references/requirement-identifiers.md"
)


def test_plan_format_uses_packaged_requirement_identifier_contract():
    """The plan schema must resolve REQ semantics inside loom-code alone."""
    assert IDENTIFIER_CONTRACT.is_file(), (
        "loom-code must package its own requirement-identifier contract"
    )
    text = PLAN_FORMAT.read_text(encoding="utf-8")

    local_pointer = "[`requirement-identifiers.md`](requirement-identifiers.md)"
    assert text.count(local_pointer) == 2, (
        "both REQ referent definitions must point at writing-plans' packaged "
        "requirement-identifiers.md contract"
    )
    assert "`loom-design:spec-expansion`" not in text, (
        "plan-format must not require loom-design to interpret REQ identifiers"
    )

    # Keep the task/scenario join semantics beside the local pointer. These
    # assertions make replacing the old dependency with a vague filename
    # mention insufficient.
    assert "<change-id> / REQ-<n> / Scenario: <name>" in text
    assert "A bare `REQ-<n>` (no `/ Scenario:` suffix)" in text
    assert "covers every scenario under that requirement" in text
