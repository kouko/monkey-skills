"""Guard for the design-station knowledge-triage doctrine (plan task 9,
docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md) plus the v2.1
cut (b) mechanization (plan task 15).

Loom 1.0 cut this doctrine's surface from three artifacts to one. It used to
cover two `references/knowledge-triage.md` files (interaction-flows and
design-system) plus a findings-schema addition and a mechanical pre-check
inside `design-critic/SKILL.md`. `interaction-flows` and `design-critic` are
deleted; `design-system` is the only station that still mounts the doctrine,
so every twin-file check below collapsed to a single-file check and the
critic-side checks went with the skill they described.

What is deliberately NOT weakened by that collapse:

  1. The pin block is still compared byte-for-byte against the plan's fenced
     vocabulary AND against its own HEAD copy — the two assertions that keep
     a transcribed pin from drifting.
  2. Every wording assertion that had a subject in the surviving file is
     kept verbatim, only re-aimed from a loop over two files to the one.
  3. The supplement sentences are still required to appear exactly once,
     after the pin, in that order. Only the "byte-identical across both
     files" pair is gone, because there is no second file to differ from.

Section 11 below is inherited, not new. `scripts/test_bucket_vocabulary_
consistency.py` was the repo-root guard on the bucket vocabulary "across the
plugins that carry it"; loom 1.0 left exactly one carrier — this file — so a
cross-file drift guard had nothing left to compare and was deleted. Its one
assertion that was not already made here (no variant spelling of a bucket
name inside a tag/value context) moved in with it, scoping helper included.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = Path(__file__).resolve().parents[2]

PLAN_PATH = (
    REPO_ROOT / "docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md"
)

DS_SKILL = PLUGIN_ROOT / "skills" / "design-system" / "SKILL.md"
DS_TRIAGE = PLUGIN_ROOT / "skills" / "design-system" / "references" / "knowledge-triage.md"

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


# --- 1. references/knowledge-triage.md exists, carries the pin verbatim -----


def test_knowledge_triage_file_exists():
    assert DS_TRIAGE.is_file(), f"expected file missing: {DS_TRIAGE}"


def test_pin_block_transcribed_verbatim():
    expected = _plan_pin_block()
    fence = _fenced_block(_text(DS_TRIAGE))
    assert fence is not None, "design-system knowledge-triage.md missing pin fence"
    assert fence == expected, (
        "design-system knowledge-triage.md pin block is not byte-identical to "
        "the plan's pinned bucket vocabulary"
    )


def test_pin_precedes_station_doctrine():
    text = _text(DS_TRIAGE)
    fence_match = re.search(r"```\n.*?\n```", text, re.DOTALL)
    assert fence_match, "design-system knowledge-triage.md missing fenced pin block"
    doctrine_idx = text.lower().find("## station mount doctrine")
    assert doctrine_idx > fence_match.end(), (
        "the station mount doctrine must come AFTER the transcribed pin block"
    )


# --- 2. HIGH-bar two-tier wording -------------------------------------------


def test_high_bar_shaping_criteria_present():
    low = _text(DS_TRIAGE).lower()
    assert "shaping" in low, "knowledge-triage.md missing SHAPING tier"
    assert "deferrable" in low, "knowledge-triage.md missing DEFERRABLE tier"
    assert "flow structure" in low, "missing 'flow structure' shaping criterion"
    assert "state machine" in low, "missing 'state machine' shaping criterion"
    assert "semantic display convention" in low, (
        "missing 'semantic display convention' shaping criterion"
    )
    # concrete worked examples from the plan's shaping bar
    assert "color semantic" in low, "missing color-semantics example"
    assert "sign convention" in low, "missing sign-convention example"
    assert "period definition" in low, "missing period-definition example"


def test_rationale_bar_higher_than_spec_present():
    low = _text(DS_TRIAGE).lower()
    assert "spec" in low and "gate" in low, (
        "must reference the spec station's gate in the rationale"
    )
    assert "higher" in low or "narrower" in low, (
        "must state the bar is higher/narrower than spec's"
    )


# --- 3. SHAPING route: routed research BEFORE the design-conformance verdict -


def test_shaping_route_cites_the_review_verdict_timing():
    """Was `design-critic`'s verdict; loom 1.0 moved that verdict into
    loom-code's review station under the design-conformance lens. The
    assertion is the same one: resolution happens BEFORE the verdict, and the
    research is ROUTED, never self-run."""
    low = _text(DS_TRIAGE).lower()
    assert "design-conformance" in low, (
        "must name the design-conformance lens that renders the verdict"
    )
    assert "before" in low and "verdict" in low, (
        "must state resolution happens BEFORE the design-conformance verdict"
    )
    assert "routed research" in low or "routed" in low, (
        "must name the research as ROUTED (orchestrator/user), not self-run"
    )


def test_never_websearch_restated():
    """Cross-ref severing guard (extraction-severing-cross-ref-needs-weak-model-test):
    the drafting skill's closed-world constraint must be restated in the
    extracted file, not merely assumed from the SKILL.md body."""
    low = _text(DS_TRIAGE).lower()
    assert "never" in low and "websearch" in low, (
        "must restate that the drafting skill itself never runs WebSearch"
    )
    assert "closed-world" in low, (
        "must restate the closed-world drafting-skill framing"
    )


# --- 4. DEFERRABLE route: tagged open question, loom-design named, no path ---


def test_deferrable_route_names_loom_design_without_cross_plugin_path():
    text = _text(DS_TRIAGE)
    low = text.lower()
    assert "evidence_needed: domain-convention" in text, (
        "must give the tagged-open-question format"
    )
    assert "loom-design" in low and "write-spec" in low, (
        "must name loom-design's write-spec by name (prose mention)"
    )
    # no cross-plugin filesystem path (the plan forbids this)
    assert "loom-design/skills" not in text, (
        "must NOT embed a cross-plugin file path to loom-design"
    )


def test_deferrable_target_artifact_matches_station():
    # design-system defers into DESIGN.md (interaction-flows, which deferred
    # into ui-flows.md, is deleted).
    assert "DESIGN.md" in _text(DS_TRIAGE)


# --- 5. cross-severing guard: review verdict vocabulary unchanged -----------


def test_cross_severing_guard_restates_review_verdict_vocabulary():
    text = _text(DS_TRIAGE)
    assert "PASS_WITH_NOTES" in text and "NEEDS_REVISION" in text, (
        "must restate the review station's verdict enum"
    )
    low = text.lower()
    assert "unchanged" in low, (
        "must state the verdict vocabulary is unchanged by this addition"
    )


# --- 6. mount line in the drafting SKILL.md ---------------------------------


def test_design_system_skill_mounts_its_own_reference():
    text = _text(DS_SKILL)
    assert "references/knowledge-triage.md" in text, (
        "design-system SKILL.md must mount references/knowledge-triage.md"
    )


def test_skill_does_not_mount_a_deleted_sibling_reference():
    assert "interaction-flows/references/knowledge-triage.md" not in _text(DS_SKILL)


# --- 7. flat-skill structure (repo hook enforces) ---------------------------


def test_references_dir_stays_flat():
    for child in DS_TRIAGE.parent.iterdir():
        assert not child.is_dir(), (
            "flat-skill violation: nested subdir under design-system's references/"
        )


# --- 8. the SHAPING consequence supplement ----------------------------------

SHAPING_SUPPLEMENT = (
    "SHAPING never ships as non-blocking: it either resolves before this "
    "station's gate or carries `deferred: <reason>`."
)


def test_shaping_supplement_present_verbatim():
    text = _text(DS_TRIAGE)
    assert text.count(SHAPING_SUPPLEMENT) == 1, (
        "knowledge-triage.md must carry the SHAPING supplement sentence "
        "exactly once, verbatim"
    )


def test_shaping_supplement_after_pin_never_inside():
    text = _text(DS_TRIAGE)
    fence_match = re.search(r"```\n.*?\n```", text, re.DOTALL)
    assert fence_match, "knowledge-triage.md missing fenced pin block"
    supplement_idx = text.index(SHAPING_SUPPLEMENT)
    assert supplement_idx >= fence_match.end(), (
        "SHAPING supplement must come AFTER the pin block closes"
    )
    assert not (fence_match.start() <= supplement_idx < fence_match.end()), (
        "SHAPING supplement must not be inside the pin fence"
    )


# --- 9. pin block stays byte-untouched vs HEAD ------------------------------


def _git_show_head(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel.as_posix()}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_pin_block_byte_untouched_vs_head():
    head_fence = _fenced_block(_git_show_head(DS_TRIAGE))
    assert head_fence is not None, "HEAD copy missing pin fence"
    current_fence = _fenced_block(_text(DS_TRIAGE))
    assert current_fence is not None, "current copy missing pin fence"
    assert current_fence == head_fence, (
        "pin block must stay byte-identical to the HEAD version "
        "— edits belong AFTER the pin, never inside it"
    )


# --- 10. the literal tier-label supplement ----------------------------------
# Code-quality-reviewer finding (round 1): the pre-check's grep target
# ("SHAPING") had no artifact obligation requiring it to literally exist.
# This supplement makes the tier label a literal artifact obligation. The
# pre-check it mechanized lived in design-critic and is gone; the obligation
# it created on the artifact is not, so the supplement stays required.

TIER_LABEL_SUPPLEMENT = (
    "Every tagged open question written into DESIGN.md must "
    "carry a literal `SHAPING` or `DEFERRABLE` label alongside its "
    "`evidence_needed:` tag."
)


def test_tier_label_supplement_present_verbatim():
    text = _text(DS_TRIAGE)
    assert text.count(TIER_LABEL_SUPPLEMENT) == 1, (
        "knowledge-triage.md must carry the tier-label supplement sentence "
        "exactly once, verbatim"
    )


def test_tier_label_supplement_after_first_supplement():
    """The second supplement lands AFTER the pin AND after the existing
    SHAPING consequence supplement — never before or inside either."""
    text = _text(DS_TRIAGE)
    first_idx = text.index(SHAPING_SUPPLEMENT)
    second_idx = text.index(TIER_LABEL_SUPPLEMENT)
    assert second_idx > first_idx + len(SHAPING_SUPPLEMENT), (
        "tier-label supplement must come AFTER the existing SHAPING-consequence "
        "supplement sentence"
    )


# --- 11. bucket-name spellings, inherited from the repo-root drift guard ----

BUCKET_NAMES = ("craft", "domain-convention", "project-local")

# Variant spellings that must never appear in a TAG/VALUE context. Prose like
# "the business domain's rule" is fine — these are only checked inside the
# scoped tag/value neighbourhood computed by `_scoped_tag_text` (see
# docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md: whole-file
# substring checks go false-green when the phrase pre-exists in unrelated
# prose).
VARIANT_SPELLINGS = ("domain_convention", "project_local", "domain convention")


def _scoped_tag_text(text: str) -> str:
    """Text narrowed to tag/value contexts: the fenced pin block, and any
    line naming the `evidence_needed` tag."""
    parts = []
    fence = _fenced_block(text)
    if fence:
        parts.append(fence)
    for line in text.splitlines():
        if "evidence_needed" in line:
            parts.append(line)
    return "\n".join(parts)


def test_carrier_contains_all_three_bucket_names():
    text = _text(DS_TRIAGE)
    for name in BUCKET_NAMES:
        assert name in text, f"knowledge-triage.md missing bucket name {name!r}"


def test_carrier_has_no_variant_spelling_in_tag_context():
    scoped = _scoped_tag_text(_text(DS_TRIAGE))
    for variant in VARIANT_SPELLINGS:
        assert variant not in scoped, (
            f"knowledge-triage.md uses variant spelling {variant!r} in a "
            "tag/value context"
        )
