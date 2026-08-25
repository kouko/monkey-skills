"""Compaction contract for the merged loom-design entry router."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "using-loom-design" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.split())
PLAIN = FLAT.replace("**", "")


def test_entrypoint_preserves_reception_station_order_boundaries_and_host_tools_within_word_range():
    assert "<subagent-stop>" in LOW and "parent orchestrator only" in LOW
    assert "references/design-relay.md" in TEXT
    assert "references/family-relay.md §family relay discipline" in FLAT
    assert "references/family-reception.md" in TEXT and "precedence" in LOW
    assert all(station in LOW for station in (
        "discovery station", "product-principles station",
        "interface-design station", "spec station",
    ))
    assert "loom-code:using-loom-code" in TEXT
    assert "loom-workflow:brief-before-asking" in TEXT
    assert "thin entry" in LOW and "does not" in LOW
    assert "re-entrant" in LOW and "share no artifact" in FLAT and "no agent" in FLAT
    assert "principles.md" in LOW and "modality" in LOW
    assert "needs_revision" in LOW and "pass_with_notes" in LOW
    assert "draft/expand a spec from a seed" in LOW
    assert "critique/audit an existing draft for omissions" in LOW
    assert all(path in TEXT for path in (
        "references/discovery-claude-code-tools.md",
        "references/discovery-codex-tools.md",
        "references/interface-claude-code-tools.md",
        "references/interface-codex-tools.md",
        "references/spec-claude-code-tools.md",
        "references/spec-codex-tools.md",
    ))
    assert "claude code" in LOW and "codex cli" in LOW
    assert "does not auto-invoke any member" in PLAIN
    words = len(TEXT.split())
    assert 1_458 <= words <= 1_665, f"expected 1458..1665 words, got {words}"


def test_upstream_and_interface_order_remain_explicit():
    discovery = LOW.index("discovery normally comes first")
    principles = LOW.index("then product-principles", discovery)
    interface = LOW.index("then interface-design", principles)
    spec = LOW.index("then spec", interface)
    assert discovery < principles < interface < spec

    modality = LOW.index("record the modality first")
    governance = LOW.index("principles.md governs", modality)
    concerns = LOW.index("two generate skills", governance)
    assert modality < governance < concerns


def test_router_keeps_member_ownership_and_explicit_invocation_boundary():
    for owner in (
        "that is `business-value`",
        "that is `user-insights`",
        "that is `product-principles`",
        "that is `design-system` and",
        "that is `spec-expansion` and",
    ):
        assert owner in LOW
    assert "explicit invocation" in LOW
    assert "load it via the skill tool directly" in LOW
