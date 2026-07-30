"""Tests for validate_envelope.py — the file-borne envelope validator.

Each check class has at least one failing-input case AND one passing case,
plus the legitimate minimal shapes (audit alt-entry per CLAUDE.md §External
Caller Guide; fresh envelope validated without --prev). Fixtures are built
in-test under tmp_path, derived from CLAUDE.md §Handoff Envelope's canonical
example.

Exit-code contract under test (documented in the script's module docstring):
  0 valid | 2 usage/IO/parse | 3 schema | 4 counters | 5 immutable-field
  6 audit_trail append-only | 7 manual-PASS ban | 8 round-2 prior_findings

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate_envelope.py"


def canonical_envelope() -> dict:
    """CLAUDE.md §Handoff Envelope canonical example (trimmed to fields used)."""
    return {
        "phase": "phase-4-draft",
        "form": "long-form-pasona",
        "brief": {"product": "x", "target_audience": "y"},
        "message_thesis": "...",
        "draft": "...",
        "express_mode_used": True,
        "audit_trail": [
            {
                "at": "2026-07-30T02:00:00Z",
                "event": "skill-entered",
                "skill": "copywriting-intake",
                "detail": "Express Mode",
            },
            {
                "at": "2026-07-30T02:00:12Z",
                "event": "skill-exited",
                "skill": "copywriting-intake",
                "detail": "brief synthesized",
            },
        ],
        "retries": {"bounce_round": 0, "revise_round_count": 0, "total_retries": 0},
        "next_stage": "copywriting-voice-quadrant-stage",
    }


def run_validator(tmp_path, envelope, prev=None, raw_text=None):
    """Write fixture(s), invoke the CLI, return CompletedProcess."""
    assert SCRIPT.is_file(), f"validator script absent: {SCRIPT}"
    env_file = tmp_path / "envelope.json"
    if raw_text is not None:
        env_file.write_text(raw_text, encoding="utf-8")
    else:
        env_file.write_text(json.dumps(envelope), encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), str(env_file)]
    if prev is not None:
        prev_file = tmp_path / "prev.json"
        prev_file.write_text(json.dumps(prev), encoding="utf-8")
        cmd += ["--prev", str(prev_file)]
    return subprocess.run(cmd, capture_output=True, text=True)


# ---------------------------------------------------------------- valid shapes


def test_fresh_canonical_envelope_passes_without_prev(tmp_path):
    # WHY: the everyday case — a well-formed stage-boundary envelope with no
    # predecessor must validate clean, or the pipeline halts on every hop.
    r = run_validator(tmp_path, canonical_envelope())
    assert r.returncode == 0, r.stderr


def test_audit_alt_entry_minimal_shape_passes(tmp_path):
    # WHY: CLAUDE.md §External Caller Guide's audit alt-entry omits
    # express_mode_used / audit_trail / retries by design; the validator must
    # not reject the documented minimal shape.
    envelope = {
        "phase": "phase-audit-entry",
        "form": "unknown",
        "brief": {"review_focus": "all"},
        "external_copy": "Full text of the copy under review, verbatim.",
    }
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------- exit 2 usage


def test_missing_file_exits_2(tmp_path):
    assert SCRIPT.is_file(), f"validator script absent: {SCRIPT}"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "nope.json")],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2
    assert "validate_envelope:" in r.stderr


def test_unparseable_json_exits_2(tmp_path):
    r = run_validator(tmp_path, None, raw_text="{not json")
    assert r.returncode == 2
    assert "validate_envelope:" in r.stderr


# ---------------------------------------------------------------- exit 3 schema


def test_missing_express_mode_used_fails_schema(tmp_path):
    # WHY: express_mode_used is immutable-after-intake and consumed by Phase 7
    # audit; a pipeline envelope silently dropping it must fail loud.
    envelope = canonical_envelope()
    del envelope["express_mode_used"]
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "express_mode_used" in r.stderr


def test_missing_audit_trail_fails_schema(tmp_path):
    envelope = canonical_envelope()
    del envelope["audit_trail"]
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "audit_trail" in r.stderr


def test_retries_missing_counter_fails_schema(tmp_path):
    envelope = canonical_envelope()
    del envelope["retries"]["total_retries"]
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "total_retries" in r.stderr


def test_unknown_phase_fails_schema(tmp_path):
    envelope = canonical_envelope()
    envelope["phase"] = "phase-99-bogus"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "phase" in r.stderr


def test_malformed_audit_trail_entry_fails_schema(tmp_path):
    envelope = canonical_envelope()
    envelope["audit_trail"].append({"event": "skill-entered"})  # no at/skill
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3


def test_alt_entry_missing_external_copy_fails_schema(tmp_path):
    # WHY: audit-stage rejects envelopes without full external_copy text; the
    # validator enforces presence structurally at the boundary.
    envelope = {"phase": "phase-audit-entry", "form": "unknown", "brief": {}}
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "external_copy" in r.stderr


# --------------------------------------------------------------- exit 4 counters


def test_counter_decrease_fails(tmp_path):
    # WHY: resetting counters is how stall-loops hide (CLAUDE.md §Immutable
    # fields — retries are monotonic).
    prev = canonical_envelope()
    prev["retries"] = {"bounce_round": 1, "revise_round_count": 0, "total_retries": 1}
    curr = copy.deepcopy(prev)
    curr["retries"] = {"bounce_round": 0, "revise_round_count": 0, "total_retries": 0}
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 4
    assert "bounce_round" in r.stderr


def test_counter_identity_violation_fails(tmp_path):
    # WHY: total_retries is defined as the aggregate; a drifting total lets
    # the combined >=4 halt cap be bypassed.
    envelope = canonical_envelope()
    envelope["retries"] = {"bounce_round": 1, "revise_round_count": 1, "total_retries": 1}
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 4
    assert "total_retries" in r.stderr


def test_counters_monotonic_increase_passes(tmp_path):
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["retries"] = {"bounce_round": 1, "revise_round_count": 0, "total_retries": 1}
    curr["audit_trail"] = prev["audit_trail"] + [
        {
            "at": "2026-07-30T02:01:00Z",
            "event": "violation-detected",
            "skill": "using-copywriting-toolkit",
            "detail": "missing brief.product",
        }
    ]
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 0, r.stderr


# ------------------------------------------------------- exit 5 immutable fields


def test_express_mode_used_flip_fails_immutable(tmp_path):
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["express_mode_used"] = False
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 5
    assert "express_mode_used" in r.stderr


def test_brief_field_mutation_fails_immutable(tmp_path):
    # WHY: brief.* travels multiple hops; silent rewrites downstream of intake
    # are the drop class the preservation contract exists for.
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["brief"]["product"] = "something else"
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 5
    assert "brief.product" in r.stderr


def test_voice_quadrant_preserved_passes(tmp_path):
    prev = canonical_envelope()
    prev["voice_quadrant"] = {"primary": "Q2", "schwartz_alignment": "ok"}
    curr = copy.deepcopy(prev)
    curr["brief"]["channel"] = "web"  # additive brief key is allowed
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 0, r.stderr


def test_voice_quadrant_mutation_fails_immutable(tmp_path):
    prev = canonical_envelope()
    prev["voice_quadrant"] = {"primary": "Q2", "schwartz_alignment": "ok"}
    curr = copy.deepcopy(prev)
    curr["voice_quadrant"]["schwartz_alignment"] = "conflict_flagged"
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 5
    assert "voice_quadrant" in r.stderr


# ------------------------------------------------ exit 6 audit_trail append-only


def test_audit_trail_dropped_entry_fails_append_only(tmp_path):
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["audit_trail"] = curr["audit_trail"][1:]  # dropped the first entry
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 6
    assert "append-only" in r.stderr


def test_audit_trail_rewritten_entry_fails_append_only(tmp_path):
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["audit_trail"][0]["detail"] = "history, rewritten"
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 6


def test_audit_trail_appended_entries_pass(tmp_path):
    prev = canonical_envelope()
    curr = copy.deepcopy(prev)
    curr["audit_trail"] = curr["audit_trail"] + [
        {
            "at": "2026-07-30T02:02:00Z",
            "event": "skill-entered",
            "skill": "copywriting-long-form-pasona",
            "detail": "Phase 4 draft",
        }
    ]
    r = run_validator(tmp_path, curr, prev=prev)
    assert r.returncode == 0, r.stderr


# ------------------------------------------------------- exit 7 manual-PASS ban


def _gate_verdict_entry(verdict: str) -> dict:
    return {
        "at": "2026-07-30T02:03:00Z",
        "event": "gate-verdict",
        "skill": "copywriter-evaluator",
        "detail": f"{verdict} — ethics gate",
    }


def test_manual_pass_without_evaluator_entry_fails(tmp_path):
    # WHY: the acceptance case — a PASS nobody's evaluator wrote is the
    # silent-gate-bypass CLAUDE.md §What NOT to do bans; must exit non-zero.
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASS"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 7
    assert "gate-verdict" in r.stderr


def test_pass_with_matching_evaluator_entry_passes(tmp_path):
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASS"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


def test_manual_ethics_verdict_pass_without_evaluator_entry_fails(tmp_path):
    # WHY: form-check gates Phase-8 entry on ethics_verdict == "PASS" — a
    # hand-set ethics_verdict is the same silent bypass as a hand-set
    # gate_verdict and must hit the same ban (whole-branch review 🟡:
    # the ban previously pinned gate_verdict only).
    envelope = canonical_envelope()
    envelope["ethics_verdict"] = "PASS"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 7
    assert "ethics_verdict" in r.stderr


def test_manual_form_verdict_pass_without_evaluator_entry_fails(tmp_path):
    envelope = canonical_envelope()
    envelope["form_verdict"] = "PASS_WITH_NOTES"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 7
    assert "form_verdict" in r.stderr


def test_ethics_verdict_with_matching_evaluator_entry_passes(tmp_path):
    envelope = canonical_envelope()
    envelope["ethics_verdict"] = "PASS"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


def test_pass_verdict_does_not_match_pass_with_notes_entry(tmp_path):
    # WHY: substring matching would let a PASS_WITH_NOTES trail entry
    # legitimize a bare PASS field — the match must be exact-token.
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASS"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS_WITH_NOTES"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 7


def test_pass_with_notes_with_matching_entry_passes(tmp_path):
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASS_WITH_NOTES"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS_WITH_NOTES"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


def test_needs_revision_verdict_needs_no_entry(tmp_path):
    # WHY: the ban covers only the passing verdicts; NEEDS_REVISION never
    # unlocks a downstream stage, so it is not a bypass vector.
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "NEEDS_REVISION"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


# ------------------------------------------- exit 3 non-canonical verdict tokens


def test_gate_verdict_lowercase_variant_fails_schema(tmp_path):
    # WHY: T8 probe — {"gate_verdict": "Pass"} never hit the enum, so the
    # manual-PASS ban (exit 7) silently never fired on non-canonical tokens.
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "Pass"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "gate_verdict" in r.stderr


def test_gate_verdict_passed_token_fails_schema(tmp_path):
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASSED"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "gate_verdict" in r.stderr


def test_ethics_verdict_emoji_token_fails_schema(tmp_path):
    envelope = canonical_envelope()
    envelope["ethics_verdict"] = "✅ PASS"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "ethics_verdict" in r.stderr


def test_form_verdict_passed_token_fails_schema(tmp_path):
    envelope = canonical_envelope()
    envelope["form_verdict"] = "PASSED"
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3
    assert "form_verdict" in r.stderr


def test_canonical_verdict_tokens_still_pass_schema(tmp_path):
    # WHY: the enum guard must not reject the legitimate canonical tokens.
    # (The passing ethics_verdict carries its evaluator entry — the widened
    # manual-PASS ban covers all three verdict fields; NEEDS_REVISION needs
    # none, the ban only guards PASSING verdicts.)
    envelope = canonical_envelope()
    envelope["ethics_verdict"] = "PASS_WITH_NOTES"
    envelope["form_verdict"] = "NEEDS_REVISION"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS_WITH_NOTES"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


# -------------------------------- exit 7 gate-verdict entry skill authorship pin


def test_gate_verdict_entry_from_non_evaluator_skill_fails(tmp_path):
    # WHY: CLAUDE.md §Audit Trail pins copywriter-evaluator as the sole writer
    # of gate-verdict events; a router-authored entry (e.g.
    # "using-copywriting-toolkit") must not legitimize a PASS. The positive
    # direction (skill == "copywriter-evaluator" legitimizes PASS) is already
    # pinned by test_pass_with_matching_evaluator_entry_passes above.
    envelope = canonical_envelope()
    envelope["gate_verdict"] = "PASS"
    entry = _gate_verdict_entry("PASS")
    entry["skill"] = "using-copywriting-toolkit"
    envelope["audit_trail"].append(entry)
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 7
    assert "gate-verdict" in r.stderr


# ------------------------------------------ multi-class aggregation + exit pin


def test_multiple_violation_classes_all_reported_exit_is_first_class(tmp_path):
    # WHY: pins the "all violation classes printed to stderr, exit code is the
    # FIRST failing class in evaluation order" contract from the module
    # docstring — previously exercised only implicitly, never asserted.
    envelope = canonical_envelope()
    del envelope["express_mode_used"]  # schema violation (class 3)
    envelope["retries"]["total_retries"] = 99  # counters violation (class 4)
    envelope["gate_verdict"] = "PASS"  # manual-PASS violation (class 7)
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 3  # schema is first in evaluation order
    lines = [l for l in r.stderr.splitlines() if l.strip()]
    assert len(lines) >= 3, r.stderr


# ------------------------------------------------- exit 8 round-2 prior_findings


def _regate_envelope() -> dict:
    envelope = canonical_envelope()
    envelope["phase"] = "phase-7-ethics"
    envelope["retries"] = {"bounce_round": 0, "revise_round_count": 1, "total_retries": 1}
    return envelope


def test_regate_without_prior_findings_fails(tmp_path):
    # WHY: the round-2 duty (CLAUDE.md §Gate Convergence Vocabulary) requires
    # the re-gate dispatch to carry prior findings verbatim; enforcing it
    # structurally is the plan's resolved Open Q3.
    r = run_validator(tmp_path, _regate_envelope())
    assert r.returncode == 8
    assert "prior_findings" in r.stderr


def test_regate_with_empty_prior_findings_fails(tmp_path):
    envelope = _regate_envelope()
    envelope["prior_findings"] = []
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 8


def test_regate_with_prior_findings_passes(tmp_path):
    envelope = _regate_envelope()
    envelope["prior_findings"] = [
        {"class": "contract", "finding": "char limit exceeded", "status": "open"}
    ]
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr


def test_revised_envelope_outside_gate_phase_needs_no_prior_findings(tmp_path):
    # WHY: the duty binds re-GATE entry, not every envelope that ever revised;
    # a delivered envelope with revise history must not fail retroactively.
    envelope = canonical_envelope()
    envelope["phase"] = "delivered"
    envelope["retries"] = {"bounce_round": 0, "revise_round_count": 1, "total_retries": 1}
    envelope["gate_verdict"] = "PASS"
    envelope["audit_trail"].append(_gate_verdict_entry("PASS"))
    r = run_validator(tmp_path, envelope)
    assert r.returncode == 0, r.stderr
