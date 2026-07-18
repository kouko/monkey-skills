"""Guard for the design-station knowledge-triage doctrine (plan task 9,
docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md).

Covers three artifacts:
  1. Two new references/knowledge-triage.md files (interaction-flows,
     design-system) — each must open with the pin block transcribed
     VERBATIM from the plan's §Pinned bucket vocabulary fenced block,
     then carry the station's HIGH-bar two-tier doctrine, the
     never-WebSearch restatement (closed-world drafting skill), and the
     cross-severing guard restating design-critic's verdict vocabulary is
     unchanged.
  2. One imperative mount line in each drafting SKILL.md, naming its own
     references/knowledge-triage.md.
  3. One findings-schema addition in design-critic/SKILL.md: the optional
     `evidence_needed` tag, flag-never-search, verdict enum untouched.

Per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md, assertions
are scoped to the knowledge-triage neighborhood (the new files entirely, or
an anchor-bounded window in the pre-existing SKILL.md files) rather than
whole-file substring checks, since generic terms ("state", "flag", "verdict")
already recur elsewhere in these files.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = Path(__file__).resolve().parents[1]

PLAN_PATH = (
    REPO_ROOT / "docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md"
)

IF_SKILL = PLUGIN_ROOT / "skills" / "interaction-flows" / "SKILL.md"
DS_SKILL = PLUGIN_ROOT / "skills" / "design-system" / "SKILL.md"
DC_SKILL = PLUGIN_ROOT / "skills" / "design-critic" / "SKILL.md"

IF_TRIAGE = PLUGIN_ROOT / "skills" / "interaction-flows" / "references" / "knowledge-triage.md"
DS_TRIAGE = PLUGIN_ROOT / "skills" / "design-system" / "references" / "knowledge-triage.md"

TRIAGE_FILES = {"interaction-flows": IF_TRIAGE, "design-system": DS_TRIAGE}

PIN_ANCHOR = "Three buckets"


def _fenced_block(text: str):
    for match in re.finditer(r"```\n(.*?)\n```", text, re.DOTALL):
        if match.group(1).lstrip().startswith(PIN_ANCHOR):
            return match.group(1)
    return None


def _plan_pin_block() -> str:
    text = PLAN_PATH.read_text(encoding="utf-8")
    fence = _fenced_block(text)
    assert fence, "plan's pinned bucket vocabulary fenced block not found"
    return fence


def _text(path: Path) -> str:
    assert path.is_file(), f"expected file missing: {path}"
    return path.read_text(encoding="utf-8")


# --- 1. both references/knowledge-triage.md exist, carry the pin verbatim --


def test_both_knowledge_triage_files_exist():
    for label, path in TRIAGE_FILES.items():
        assert path.is_file(), f"{label} is missing references/knowledge-triage.md"


def test_pin_block_transcribed_verbatim_in_both_files():
    plan_pin = _plan_pin_block()
    for label, path in TRIAGE_FILES.items():
        text = _text(path)
        fence = _fenced_block(text)
        assert fence is not None, f"{label} knowledge-triage.md has no pin fenced block"
        assert fence == plan_pin, (
            f"{label} knowledge-triage.md pin block is not byte-identical to "
            "the plan's §Pinned bucket vocabulary block"
        )


def test_pin_precedes_station_doctrine_in_both_files():
    """Pin block VERBATIM first, then design-station doctrine after."""
    for label, path in TRIAGE_FILES.items():
        text = _text(path)
        fence_match = re.search(r"```\n.*?\n```", text, re.DOTALL)
        assert fence_match, f"{label} knowledge-triage.md missing fenced pin block"
        after = text[fence_match.end():]
        assert len(after.strip()) > 200, (
            f"{label} knowledge-triage.md has no station doctrine after the pin"
        )


# --- 2. HIGH-bar two-tier wording in both references files -----------------


def test_high_bar_shaping_criteria_present_in_both_files():
    for label, path in TRIAGE_FILES.items():
        low = _text(path).lower()
        assert "shaping" in low, f"{label} knowledge-triage.md missing SHAPING tier"
        assert "deferrable" in low, f"{label} knowledge-triage.md missing DEFERRABLE tier"
        assert "flow structure" in low, f"{label} missing 'flow structure' shaping criterion"
        assert "state machine" in low, f"{label} missing 'state machine' shaping criterion"
        assert "semantic display convention" in low, (
            f"{label} missing 'semantic display convention' shaping criterion"
        )
        # concrete worked examples from the plan's shaping bar
        assert "color semantic" in low, f"{label} missing color-semantics example"
        assert "sign convention" in low, f"{label} missing sign-convention example"
        assert "period definition" in low, f"{label} missing period-definition example"


def test_rationale_bar_higher_than_spec_present_in_both_files():
    for label, path in TRIAGE_FILES.items():
        low = _text(path).lower()
        assert "spec" in low and "gate" in low, (
            f"{label} must reference spec's gate in the rationale"
        )
        assert "higher" in low or "narrower" in low, (
            f"{label} must state the bar is higher/narrower than spec's"
        )


# --- 3. SHAPING route: routed research BEFORE design-critic's verdict ------


def test_shaping_route_cites_design_critic_verdict_timing():
    for label, path in TRIAGE_FILES.items():
        low = _text(path).lower()
        assert "design-critic" in low, f"{label} must name design-critic"
        assert "before" in low and "verdict" in low, (
            f"{label} must state resolution happens BEFORE design-critic's verdict"
        )
        assert "routed research" in low or "routed" in low, (
            f"{label} must name the research as ROUTED (orchestrator/user), not self-run"
        )


def test_never_websearch_restated_in_both_files():
    """Cross-ref severing guard (extraction-severing-cross-ref-needs-weak-model-test):
    the drafting skill's closed-world constraint must be restated in the
    extracted file, not merely assumed from the SKILL.md body."""
    for label, path in TRIAGE_FILES.items():
        low = _text(path).lower()
        assert "never" in low and "websearch" in low, (
            f"{label} must restate that the drafting skill itself never runs WebSearch"
        )
        assert "closed-world" in low, (
            f"{label} must restate the closed-world drafting-skill framing"
        )


# --- 4. DEFERRABLE route: tagged open question, loom-spec named, no path ---


def test_deferrable_route_names_loom_spec_without_cross_plugin_path():
    for label, path in TRIAGE_FILES.items():
        text = _text(path)
        low = text.lower()
        assert "evidence_needed: domain-convention" in text, (
            f"{label} must give the tagged-open-question format"
        )
        assert "loom-spec" in low and "spec-expansion" in low, (
            f"{label} must name loom-spec's spec-expansion by name (prose mention)"
        )
        # no cross-plugin filesystem path (the plan forbids this)
        assert "loom-spec/skills" not in text, (
            f"{label} must NOT embed a cross-plugin file path to loom-spec"
        )


def test_deferrable_target_artifact_matches_station():
    # interaction-flows defers into ui-flows.md; design-system into DESIGN.md
    assert "ui-flows.md" in _text(IF_TRIAGE)
    assert "DESIGN.md" in _text(DS_TRIAGE)


# --- 5. cross-severing guard: critic verdict vocabulary unchanged ----------


def test_cross_severing_guard_restates_critic_verdict_vocabulary():
    for label, path in TRIAGE_FILES.items():
        text = _text(path)
        assert "PASS_WITH_NOTES" in text and "NEEDS_REVISION" in text, (
            f"{label} must restate design-critic's verdict enum"
        )
        low = text.lower()
        assert "unchanged" in low, (
            f"{label} must state the verdict vocabulary is unchanged by this addition"
        )


# --- 6. mount lines in the drafting SKILL.md files --------------------------


def test_interaction_flows_skill_mounts_its_own_reference():
    text = _text(IF_SKILL)
    assert "references/knowledge-triage.md" in text, (
        "interaction-flows SKILL.md must mount references/knowledge-triage.md"
    )
    idx = text.index("references/knowledge-triage.md")
    window = text[max(0, idx - 400): idx + 150]
    low = window.lower()
    assert "before" in low, (
        "the mount must be an imperative anchored to the drafting moment "
        "('before X -> do Y FIRST' shape)"
    )
    assert "first" in low, "the mount must say to run the reference FIRST"


def test_design_system_skill_mounts_its_own_reference():
    text = _text(DS_SKILL)
    assert "references/knowledge-triage.md" in text, (
        "design-system SKILL.md must mount references/knowledge-triage.md"
    )
    idx = text.index("references/knowledge-triage.md")
    window = text[max(0, idx - 400): idx + 150]
    low = window.lower()
    assert "before" in low, (
        "the mount must be an imperative anchored to the drafting moment "
        "('before X -> do Y FIRST' shape)"
    )
    assert "first" in low, "the mount must say to run the reference FIRST"


def test_skill_files_do_not_mount_each_others_reference():
    # no-shared-files: each skill's mount must point at ITS OWN copy only
    assert "design-system/references/knowledge-triage.md" not in _text(IF_SKILL)
    assert "interaction-flows/references/knowledge-triage.md" not in _text(DS_SKILL)


# --- 7. design-critic findings schema addition ------------------------------


def test_design_critic_findings_schema_carries_evidence_needed_tag():
    text = _text(DC_SKILL)
    assert "evidence_needed: craft | domain-convention | project-local" in text, (
        "design-critic SKILL.md must add the evidence_needed tag to the findings schema"
    )
    idx = text.index("evidence_needed: craft | domain-convention | project-local")
    window = text[idx: idx + 500].lower()
    assert "flag" in window, (
        "must state the critic FLAGS the tag"
    )
    assert "never" in window and "search" in window, (
        "must state the critic never searches to resolve the tag"
    )


def test_design_critic_verdict_enum_untouched_by_schema_addition():
    """The addition must not introduce a third verdict value or otherwise
    disturb the two-valued PASS_WITH_NOTES / NEEDS_REVISION enum."""
    text = _text(DC_SKILL)
    assert text.count("PASS_WITH_NOTES") >= 1
    assert text.count("NEEDS_REVISION") >= 1
    # the schema-addition paragraph itself must not mint a bare/new PASS
    # token (a third verdict state) — only reference the existing enum.
    idx = text.index("evidence_needed: craft | domain-convention | project-local")
    paragraph_end = text.index("\n\n", idx)
    paragraph = text[idx:paragraph_end]
    bare_pass = re.sub(r"PASS_WITH_NOTES|NEEDS_REVISION", "", paragraph)
    assert "PASS" not in bare_pass, (
        "the schema-addition paragraph must not introduce a new verdict token"
    )


# --- 8. flat-skill structure (repo hook enforces) ---------------------------


def test_new_references_dirs_stay_flat():
    for label, path in TRIAGE_FILES.items():
        refs_dir = path.parent
        for child in refs_dir.iterdir():
            assert not child.is_dir(), (
                f"flat-skill violation: nested subdir under {label}'s references/"
            )
