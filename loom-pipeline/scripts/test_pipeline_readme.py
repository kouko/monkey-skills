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
