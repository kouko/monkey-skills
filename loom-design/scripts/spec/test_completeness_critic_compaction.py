"""Compaction contract for completeness-critic's executable entrypoint."""

import re
from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "completeness-critic" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.split())


def test_entrypoint_preserves_panel_lenses_synthesis_and_bounded_verdict_within_word_range():
    assert "omissions" in LOW and "spec" in LOW
    assert "fresh context" in LOW and "general reasoning agent" in LOW
    assert "writer" in LOW and "judge" in LOW
    assert "review code" in LOW and "run tdd" in LOW and "hard boundary" in LOW
    words = len(TEXT.split())
    assert 2_803 <= words <= 3_203, f"expected 2803..3203 words, got {words}"


def test_targeted_loop_preserves_dry_and_no_skip_semantics():
    assert "targeted re-seed" in LOW
    assert "new" in LOW and "defect" in LOW and "class" in LOW
    assert "k = 2" in LOW and "consecutive" in LOW
    assert "dry" in LOW and "by definition" in LOW
    assert "silently skip the loop" in LOW


def test_panel_preserves_all_lenses_views_and_host_references():
    assert "five" in LOW and "fixed" in LOW
    for term in (
        "nfr / security", "policy / legal / permissions",
        "missing object / actor", "state completeness",
        "cross-object & system-layer failures", "principles-entailed omission",
    ):
        assert term in LOW
    assert "original-requirements-only" in LOW
    assert "spec-claude-code-tools.md" in TEXT
    assert "spec-codex-tools.md" in TEXT
    assert "references/claude-code-tools.md" not in TEXT
    assert "references/codex-tools.md" not in TEXT
    for term in ("security", "permission", "data-boundary"):
        assert term in LOW


def test_honesty_rails_preserve_overlap_blind_spots_and_no_estimate():
    assert "qualitatively" in LOW
    assert "high overlap" in LOW and "redundancy" in LOW
    assert "not near-completeness" in LOW or "not near completeness" in LOW
    assert "never claim" in LOW and "complete" in LOW
    assert "capture-recapture" in LOW and "percentage" in LOW
    assert "coverage relative to seed + n lenses" in LOW
    assert "## blind spots — needs human/field input" in LOW
    assert "non-empty" in LOW and "source" in LOW


def test_consolidation_preserves_consistency_ranked_writeback_and_augmentation():
    assert "references/consistency-lens.md" in TEXT
    assert "mandatory" in LOW and "consistency" in LOW
    assert "dedup semantically" in LOW
    assert "severity × number-of-lenses" in LOW
    assert "ranked" in LOW and "load-bearing" in LOW and "critic-found" in LOW
    assert "given/when/then" in LOW
    assert "never overwrite" in LOW and "augmentation" in LOW


def test_verdict_and_process_contracts_remain_bounded_and_direct():
    assert set(re.findall(r"`(NEEDS_REVISION|PASS_WITH_NOTES)`", TEXT)) == {
        "NEEDS_REVISION", "PASS_WITH_NOTES"
    }
    assert "capped at 2" in LOW
    assert "after minting" in LOW and "hand back" in LOW
    assert FLAT.count("argv: [") >= 3
    assert "validate_spec_output.py" in TEXT
    assert 'mint_critic_verdict.py", "mint"' in TEXT
    assert 'mint_critic_verdict.py", "validate"' in TEXT
    assert "never through a shell" in LOW
