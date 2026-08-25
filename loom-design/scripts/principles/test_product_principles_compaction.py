"""Compaction contract for product-principles' executable entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "product-principles" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.replace("*", "").split())


def test_entrypoint_preserves_elicitation_canon_artifact_and_headless_traceability_within_word_range():
    assert "own words" in LOW and "target user" in LOW
    assert "same-axis" in LOW and "same question" in LOW
    assert "docs/loom/PRINCIPLES.md" in TEXT
    assert "seed-traceability invariant" in LOW and "no silent drops" in LOW
    words = len(TEXT.split())
    assert 2_117 <= words <= 2_418, f"expected 2117..2418 words, got {words}"


def test_entrypoint_keeps_all_authoring_references_and_elicitation_rules():
    for reference in (
        "references/principles-rules.md",
        "references/question-sets.md",
        "references/canon-product.md",
        "references/canon-design-interaction.md",
        "references/canon-design-visual.md",
        "references/canon-engineering.md",
        "references/knowledge-triage.md",
    ):
        assert reference in TEXT

    assert "own words" in LOW and "target user" in LOW
    assert "propose-then-react" in LOW and "coverage self-check" in LOW
    assert "enumerate" in LOW and "cross-section answer propagation" in LOW


def test_entrypoint_keeps_canon_choice_and_visual_anchor_rules():
    assert "same-axis" in LOW and "same question" in LOW
    assert "2-3 canon candidates" in LOW and "≥2 distinct traditions" in TEXT
    assert "considered-but-rejected" in LOW and "per-round" in LOW
    assert "3-5 tone & manner adjectives" in FLAT
    assert "primary visual anchor" in LOW
    assert "single axis-a candidate round" in FLAT
    assert "downstream of the tone & manner anchor" in FLAT
    assert "never a pick-one menu" in FLAT
    assert "never overrides a principles value" in FLAT


def test_entrypoint_keeps_artifact_schema_readback_and_validation():
    for heading in (
        "## Product Principles",
        "## Design Principles",
        "## Engineering Principles",
        "## Anchors",
        "## Deviation Ledger",
        "## Open Questions",
    ):
        assert heading in TEXT
    assert "3–7" in TEXT and "1–7" in TEXT
    assert "— check:" in TEXT and "— reason:" in TEXT
    assert "— principle:" in TEXT and "re-trigger" in LOW
    assert "read-back" in LOW and "per-section" in LOW and "final total" in LOW
    assert "key term" in LOW and "docs/loom/PRINCIPLES.md" in TEXT
    assert "scripts/principles/validate_principles_output.py" in TEXT
    assert "scripts/principles/check_seed_traceability.py" in TEXT
    assert "never through a shell" in LOW and "exit 0" in LOW


def test_entrypoint_keeps_headless_inventory_traceability_and_human_ownership():
    headless = LOW.split("## headless / seeded mode", 1)[1]
    headless_flat = " ".join(headless.replace("*", "").split())
    assert "thin seed" in headless and "blocked" in headless
    assert "never fabricate" in headless_flat and "seed-inventory.md" in headless
    assert "named_anchors:" in headless and "deferred_items:" in headless
    assert "never use `negative:`" in headless and "write-only" in headless
    assert "seed-traceability invariant" in headless and "no silent drops" in headless
    assert "each individual stance" in headless_flat and "bullet granularity" in headless
    assert "out-of-jurisdiction" in headless and "never out-of-jurisdiction" in headless
    assert "version-pinned `## anchors` row" in headless
    assert "carrying principle" in headless and "open question" in headless
    assert "(agent-decided)" in headless and "same physical line" in headless
    assert "deferred-to-human" in headless and "grep" in headless


def test_entrypoint_keeps_downstream_governance_boundary():
    assert "## downstream" in LOW and "interface-design" in LOW
    assert "spec-expansion" in LOW and "code" in LOW and "headless / cli" in LOW
