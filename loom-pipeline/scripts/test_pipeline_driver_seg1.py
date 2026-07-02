"""Structural tests for driver_30_seg1.js — the segment-1 module of the
build-assembled Workflow driver (see
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md Task 9). Source-only:
the concat-build lands in Task 14, and driver_60_ledger.js (Task 12) is being
written concurrently, so this test only grep-asserts the required contract
surface plus `node --check` on the module in isolation — it does not execute
runSegment1 (that needs the Workflow runtime globals + the concurrently
written ledger module, neither available here).
"""
import re
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_30_seg1.js"
HEADER_PATH = Path(__file__).parent / "driver_00_header.js"


def _segment_1_phase_title():
    """Read the segment-1 phase title from driver_00_header.js's meta.phases
    array directly, instead of hardcoding it here — avoids drift if the
    header's title text changes."""
    header_source = HEADER_PATH.read_text(encoding="utf-8")
    match = re.search(r"phases:\s*\[\s*\{\s*title:\s*'([^']+)'", header_source)
    assert match, "could not locate phases[0].title in driver_00_header.js"
    return match.group(1)


def test_seg1_panel_caps_ledger():
    # @req: REQ-LOOM-PIPELINE-SEG1-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # node --check must pass (valid JS syntax, no runtime execution)
    result = subprocess.run(
        ["node", "--check", str(MODULE_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"

    # public entry point name (T13's main dispatch module routes to this)
    assert "async function runSegment1" in source, "missing runSegment1 export"

    # adopt-if-valid branch on an existing PRINCIPLES.md
    assert "PRINCIPLES.md" in source, "missing PRINCIPLES.md reference"
    assert re.search(r"adopt", source, re.IGNORECASE), (
        "missing an adopt-if-valid path for an existing PRINCIPLES.md"
    )

    # design-critic panel: >= 2 distinct critic-lens dispatches (script-layer
    # writer!=judge fan-out, NOT folded into one station's self-review)
    lens_count = len(re.findall(r"lens", source, re.IGNORECASE))
    assert lens_count >= 2, (
        f"expected >=2 distinct critic-lens references, found {lens_count}"
    )
    assert source.count("agent(") >= 2, (
        "expected >=2 separate agent() dispatch call sites for the critic panel"
    )

    # rally-cap usage (loop-back on NEEDS_REVISION, capped, from T8's constant)
    assert "RALLY_CAP" in source, "missing RALLY_CAP usage"

    # per-judge ledger push (G5) — each lens's verdict pushed individually
    assert "recordLedger(" in source, "missing recordLedger call"

    # G3: Decisions-section presence check on emitted artifacts
    assert re.search(r"Decisions", source), "missing Decisions-section check"

    # phase title must match the header's segment-1 title verbatim
    expected_title = _segment_1_phase_title()
    assert f"phase('{expected_title}')" in source or f'phase("{expected_title}")' in source, (
        f"phase() call must use the header's segment-1 title verbatim: {expected_title!r}"
    )

    # this module must NOT declare LEDGER/recordLedger itself — those are
    # DECLARED in driver_60_ledger.js (Task 12, concurrent); declaring them
    # here would collide at concat time.
    assert "const LEDGER" not in source, (
        "must not declare LEDGER — it is declared in driver_60_ledger.js"
    )
    assert "function recordLedger" not in source, (
        "must not declare recordLedger — it is declared in driver_60_ledger.js"
    )

    # no forbidden non-deterministic tokens (concat-chain rule, inherited)
    for token in ["Date.now(", "Math.random(", "new Date()"]:
        assert token not in source, f"forbidden token present: {token}"


def test_seg1_ledger_entries_carry_judge_or_role():
    # @req: REQ-LOOM-PIPELINE-SEG1-2
    source = MODULE_PATH.read_text(encoding="utf-8")

    ledger_lines = [
        line for line in source.splitlines()
        if "recordLedger(" in line and not line.strip().startswith("//")
    ]
    assert ledger_lines, "expected at least one recordLedger call site"
    for line in ledger_lines:
        assert "judge:" in line or "role:" in line, (
            f"recordLedger call site missing judge/role field (driver_60_ledger.js "
            f"throws without one): {line!r}"
        )


def test_seg1_no_naked_agent_dispatch():
    # @req: REQ-LOOM-PIPELINE-SEG1-3
    source = MODULE_PATH.read_text(encoding="utf-8")

    # Every agent() dispatch must be wrapped by runStation's watchdog / token
    # budget / recovery ladder — a naked `await agent(...)` bypasses all of
    # that and lets a hung lens hang the segment.
    assert "await agent(" not in source, (
        "found a naked `await agent(` dispatch — every station / critic-lens "
        "dispatch must go through runStation(name, thunk, opts) instead"
    )

    for station_name in ["principles", "design", "design-critic"]:
        assert re.search(rf"runStation\(\s*['\"]{re.escape(station_name)}", source), (
            f"expected a runStation(...) call site for station {station_name!r}"
        )

    runstation_count = source.count("runStation(")
    assert runstation_count >= 3, (
        "expected >=3 runStation( call sites (principles/design/design-critic), "
        f"found {runstation_count}"
    )

    # the design-critic panel loop body (over DESIGN_CRITIC_LENSES) must
    # reference runStation — dispatching each lens through it, not a naked
    # agent() call inside the loop.
    panel_fn_match = re.search(r"async function runDesignCriticPanel[\s\S]*?\n}\n", source)
    assert panel_fn_match, "could not locate runDesignCriticPanel function body"
    assert "runStation(" in panel_fn_match.group(0), (
        "runDesignCriticPanel's loop body must dispatch each lens via runStation()"
    )


def test_seg1_decisions_section_checked_against_artifact_not_self_report():
    # @req: REQ-LOOM-PIPELINE-SEG1-4
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "DECISIONS_SECTION" in source, (
        "missing the DECISIONS_SECTION machine-parsable token"
    )

    # token must appear in the design station's stable preamble — the
    # instruction telling the agent to Read artifacts back off disk and
    # report the field computed against the real file.
    design_preamble_match = re.search(r"const DESIGN_STABLE_PREAMBLE = \[[\s\S]*?\]\.join", source)
    assert design_preamble_match, "could not locate DESIGN_STABLE_PREAMBLE"
    assert "DECISIONS_SECTION" in design_preamble_match.group(0), (
        "design station preamble must instruct the agent to report "
        "DECISIONS_SECTION: present|absent computed against the real artifact"
    )

    # ...and the script must parse (not just mention) that field.
    assert "parseDecisionsSectionField" in source, (
        "missing a script-side parser for the DECISIONS_SECTION field — G3 "
        "must gate on the parsed field, not the writer's self-reported summary"
    )


def test_seg1_is_principles_structurally_valid_wired_or_absent():
    # @req: REQ-LOOM-PIPELINE-SEG1-5
    source = MODULE_PATH.read_text(encoding="utf-8")

    definition_count = len(re.findall(r"function isPrinciplesStructurallyValid", source))
    total_references = len(re.findall(r"isPrinciplesStructurallyValid\(", source))

    if definition_count == 0:
        return  # helper removed entirely — acceptable per the fix contract

    call_sites = total_references - definition_count
    assert call_sites >= 1, (
        "isPrinciplesStructurallyValid is defined but never invoked beyond its "
        "own definition — dead helper (must be wired or deleted)"
    )


def test_seg1_station_results_carry_station_field():
    # @req: REQ-LOOM-PIPELINE-SEG1-6
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert re.search(r"principlesResult\.station\s*=\s*'principles'", source), (
        "principlesResult must be tagged station: 'principles' before it is "
        "pushed onto the stations array driver_90_main.js reads"
    )
    assert re.search(r"designResult\.station\s*=\s*`design r\$\{round\}`", source), (
        "designResult must be tagged with the per-round design station label "
        "before it is pushed onto the stations array"
    )
    assert re.search(r"\.station\s*=\s*'design-critic'", source), (
        "the rally-cap-exhausted marker must be tagged station: 'design-critic'"
    )
    station_tag_count = len(re.findall(r"\.station\s*=\s*", source))
    assert station_tag_count >= 3, (
        f"expected >=3 station-tag assignment sites (principles/design/"
        f"design-critic-unresolved), found {station_tag_count}"
    )
