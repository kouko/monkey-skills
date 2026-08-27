"""Compaction contract for design-critic's executable entrypoint."""

import re
from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "design-critic" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.split())


def test_entrypoint_preserves_artifact_guard_panel_nielsen_and_bounded_verdict():
    assert "design.md" in LOW and "ui-flows.md" in LOW
    assert "wrong-artifact guard" in LOW and "spec" in LOW and "code" in LOW
    assert "surface" in LOW and "writer≠judge" in LOW
    assert "fresh context" in LOW and "general reasoning agent" in LOW
    assert "nielsen" in LOW
    assert set(re.findall(r"`(NEEDS_REVISION|PASS_WITH_NOTES)`", TEXT)) == {
        "NEEDS_REVISION", "PASS_WITH_NOTES"
    }


def test_precheck_preserves_enum_tiers_and_panel_after_precheck():
    for term in ("craft", "domain-convention", "project-local"):
        assert term in LOW
    assert "out-of-enum" in LOW
    assert "shaping" in LOW and "deferrable" in LOW and "deferred: <reason>" in LOW
    assert "pre-check" in LOW and "panel still runs" in LOW


def test_targeted_loop_and_fixed_lenses_remain_grounded():
    assert "targeted re-seed" in LOW and "k = 2" in LOW and "consecutive" in LOW
    assert "round-1" in LOW and "dryness" in LOW
    assert "5 load-bearing lenses" in LOW
    for term in (
        "render-state completeness", "dead-end & exit / user control",
        "navigation reachability & entry", "error prevention & recovery",
        "modality fit & accessibility",
    ):
        assert term in LOW
    assert "principles lens: n/a" in LOW
    assert "references/design-heuristics.md" in TEXT and "in full" in LOW
    assert "distinct persona" in LOW
    assert "do not load" in LOW and "completeness-critic" in LOW
    for filename in ("interface-claude-code-tools.md", "interface-codex-tools.md"):
        assert filename in TEXT
        assert (SKILL.parent.parent / "using-loom-design" / "references" / filename).is_file()


def test_overlap_consolidation_and_evidence_contracts_remain_narrow():
    assert "qualitative overlap" in LOW and "redundancy" in LOW
    assert "never" in LOW and "completeness signal" in LOW
    assert "dedup semantically" in LOW
    assert "severity × number-of-lenses" in LOW
    assert "evidence_needed" in LOW and "flags" in LOW
    assert "never runs websearch" in LOW


def test_writeback_honesty_summary_and_direct_process_contracts_remain():
    assert "augmentation only" in LOW and "critic-found" in LOW
    assert "validate_design_output.py" in TEXT
    assert "## blind spots — needs human/field input" in LOW and "non-empty" in LOW
    assert "do not claim \"complete\"" in LOW
    assert "surface-coverage relative to n lenses" in LOW
    assert "round summary" in LOW
    assert "capped at 2" in LOW and "after minting" in LOW and "hand back" in LOW
    assert 'mint_critic_verdict.py", "mint"' in TEXT
    assert FLAT.count("argv: [") >= 2
    assert "never through a shell" in LOW
    assert "no unqualified `pass`" in LOW
