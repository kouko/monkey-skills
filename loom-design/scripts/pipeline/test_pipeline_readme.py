"""Structural test: loom-pipeline/README.md and CHANGELOG.md exist and carry
the required sections — Codex N/A note, G4 comparison-protocol section, the
v1.1 batch-mode note, and all 5 parked items each with a re-trigger.

"""
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[1]
README = PLUGIN_ROOT / "README.md"
CHANGELOG = PLUGIN_ROOT / "CHANGELOG.md"


def test_readme_parks_and_codex_note():
    assert README.exists(), f"missing {README}"
    text = README.read_text()

    # Codex N/A note
    assert "Codex" in text and "N/A" in text, "missing Codex N/A note"
    assert "Workflow primitive" in text, "missing 'no Workflow primitive' reason"

    # G4 section — Sonnet-vs-Fable gate A/B comparison protocol
    assert "G4" in text, "missing G4 section heading"
    assert "Sonnet-vs-Fable" in text, "missing Sonnet-vs-Fable naming"
    assert "verdict-distribution comparison" in text, (
        "missing verdict-distribution comparison protocol phrase"
    )

    # v1.1 batch-mode section
    assert "v1.1" in text, "missing v1.1 marker"
    assert "batch" in text.lower(), "missing batch-mode mention"
    assert "time-agnostic" in text, "missing time-agnostic framing (no scheduler required)"

    # All 5 parked items, each with its re-trigger phrase
    parked_items = [
        ("full autopilot", "segmented mode stable across"),
        ("codex exec", "real need to run the full pipeline on Codex"),
        ("git-commit dispatch lock", "multi-change parallelism"),
        ("watchdog", "G6 watchdog proves insufficient"),
        ("mutation-testing", "post-v1 backlog"),
    ]
    for item_phrase, retrigger_phrase in parked_items:
        assert item_phrase.lower() in text.lower(), f"missing parked item: {item_phrase}"
        assert retrigger_phrase in text, f"missing re-trigger for {item_phrase}: {retrigger_phrase}"

    assert CHANGELOG.exists(), f"missing {CHANGELOG}"
    changelog_text = CHANGELOG.read_text()
    assert "[0.1.0]" in changelog_text, "missing [0.1.0] entry in CHANGELOG"


def test_readme_batch_mode_documented_not_committed_next():
    """v1.1 shipped — README flips from the 'Committed next' promise to
    documenting the batch_queue.py CLI that actually exists now (plan
    Task 12, docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md).
    """
    text = README.read_text()

    assert "Batch mode" in text, "missing §Batch mode heading"
    assert "Committed next (v1.1)" not in text, (
        "stale 'Committed next (v1.1)' heading — batch mode has shipped"
    )


def test_readme_family_naming_convention():
    """README documents the loom family's naming convention (Task A3,
    docs/loom/plans/2026-07-04-loom-family-connective-tissue.md): a
    §Family entries & naming convention section carrying the one-sentence
    rule, the entry-vs-station distinction, brainstorming called out as
    loom-code's discovery skill, the WHY behind using-loom-code's missing
    duplicate §Intake heading (plan note 5), and a reception paragraph
    pointing at the SessionStart hook.
    """
    text = README.read_text()

    assert "Family entries" in text and "naming convention" in text, (
        "missing §Family entries & naming convention section"
    )

    # The one-sentence rule, verbatim from hooks/family-reception.md
    assert "要用 loom-X" in text and "using-loom-X" in text, (
        "missing the one-sentence naming rule (要用 loom-X, 就從 using-loom-X 開始)"
    )

    # Entry vs station convention table content
    assert "using-loom-*" in text, "missing using-loom-* entry naming convention"
    assert "product-principles" in text and "spec-expansion" in text, (
        "missing station artifact-name examples (product-principles / spec-expansion)"
    )

    # brainstorming called out as loom-code's discovery skill
    assert "brainstorming" in text and "discovery" in text, (
        "missing brainstorming = loom-code's discovery skill callout"
    )

    # WHY using-loom-code carries no duplicate §Intake heading (plan note 5)
    assert "Axis 0" in text, (
        "missing WHY using-loom-code has no duplicate §Intake heading "
        "(brainstorming's Axis 0 IS its family-entry intake)"
    )

    # Reception paragraph: SessionStart hook injects the family map
    assert "SessionStart" in text, "missing reception paragraph naming the SessionStart hook"
    assert "family-reception.md" in text, "missing pointer to hooks/family-reception.md"
    assert "explicit" in text.lower() and "Workflow" in text, (
        "missing 'Workflow door remains explicit-invocation only' framing"
    )
