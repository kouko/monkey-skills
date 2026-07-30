# Plan: copywriting-toolkit convergence modernization (knife 2)

Source brief: docs/loom/specs/2026-07-30-copywriting-convergence-modernization.md
Total tasks: 16
Critical-path depth: 5 (T1→T8→T9→T10→T14)
Execution order: parallel-where-possible (wave 1: T1∥T7∥T12; wave 2 after T1: T2∥T8∥T13 (+T9 after T8); wave 3 after T2: T3∥T4∥T5∥T6∥T11; tail: T14/T15/T16)
Plan-document-reviewer verdict: PASS (2026-07-30, round 2, 14/14; round-1 gaps = three Module-singleton splits, resolved)

## Task 1 — contract/craft vocabulary SSOT in CLAUDE.md
- Description: Define the convergence vocabulary canonically in
  copywriting-toolkit/CLAUDE.md: per-finding `class: contract | craft`
  (contract = cites a violated contract term with an objective checkable
  referent — brief constraint, form spec limit/mandatory element, declared
  voice target, ethics rule; craft = qualitative observation; unclear →
  contract, fail closed); gate verdicts aggregate over contract-class
  findings ONLY (craft recorded, never gates); round-2 duty (prior findings
  verbatim in the re-gate dispatch; evaluator verifies each against the
  current draft BEFORE new findings; re-raising a closed finding in new
  words forbidden); oscillation stop (a fix-verified finding resurfacing
  ends the loop → operator, regardless of counters). Ethics FATAL semantics
  explicitly unchanged. Replace the "2+ 🟡" vocabulary in CLAUDE.md's gate
  sections with pointers to this section.
- Module: copywriting-toolkit/CLAUDE.md
- Files touched: copywriting-toolkit/CLAUDE.md,
  copywriting-toolkit/scripts/test_convergence_vocabulary.py
- Context paths:
  - docs/loom/specs/2026-07-30-copywriting-convergence-modernization.md
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: `PYTHONDONTWRITEBYTECODE=1 pytest copywriting-toolkit/scripts/test_convergence_vocabulary.py`
    fails (vocabulary section absent from CLAUDE.md).
  - GREEN: window-scoped pins pass — class definitions + fail-closed sentence,
    contract-only aggregation, round-2 duty, re-litigation ban, oscillation
    stop, ethics-FATAL-unchanged sentence. (Local runs during the arc; CI
    wiring for copywriting-toolkit pytest lands in Task 15 per the
    runnable-capability note.)
- External surfaces: None.
- Dependencies: none
- Independent: true
- Brief item covered: "P3 — contract-class verdict semantics … Every gate
  finding carries `class: contract | craft` … aggregates over
  contract-class findings only … Round-2 duty"

## Task 2 — copywriter-evaluator contract update
- Description: Update copywriting-toolkit/agents/copywriter-evaluator.md:
  per-finding `class: contract | craft` in the finding format (definitions
  transcribed from Task 1's CLAUDE.md text — transcribe, don't re-derive);
  replace the "2+ 🟡 → NEEDS_REVISION" verdict rule (:64-68) with
  contract-class aggregation; add the round-2 `prior_findings_check` duty
  (verify each verbatim prior finding against quoted current draft text
  first; statuses fix-verified / not-fixed / resurfaced; any resurfaced →
  report oscillation) mirroring the docs-reviewer agent's shape.
- Module: copywriting-toolkit/agents
- Files touched: copywriting-toolkit/agents/copywriter-evaluator.md,
  copywriting-toolkit/scripts/test_evaluator_contract.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - loom-code/agents/docs-reviewer.md
- Acceptance:
  - RED: `pytest copywriting-toolkit/scripts/test_evaluator_contract.py`
    fails (class field + prior_findings_check absent; old 2+🟡 rule still
    present — include an absence pin on the old wording).
  - GREEN: pins pass; wording matches Task 1's CLAUDE.md text (side-by-side
    window assertions on the shared phrases).
- External surfaces: None.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Surfaces: … copywriter-evaluator agent contract" +
  "Round-2 duty: a re-gate dispatch carries the prior round's findings
  verbatim"

## Task 3 — form-check gate semantics
- Description: Rewrite copywriting-form-check-stage's verdict rule
  (SKILL.md:116-119) to contract-class aggregation (pointer to CLAUDE.md
  vocabulary; no local restatement) and annotate the rubric's dimension
  rows (rubrics/form-appropriate-gate.md:79-153): objective form-constraint
  rows (length/char limits, mandatory elements, platform constraints) →
  contract; qualitative rows (Affinity thickness, inter-stage flow) →
  craft (recorded). Keep the loop-back mechanics + caps (:165-188)
  unchanged.
- Module: copywriting-toolkit/skills/copywriting-form-check-stage
- Files touched: copywriting-toolkit/skills/copywriting-form-check-stage/SKILL.md,
  copywriting-toolkit/skills/copywriting-form-check-stage/rubrics/form-appropriate-gate.md,
  copywriting-toolkit/scripts/test_form_check_gate_semantics.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - copywriting-toolkit/agents/copywriter-evaluator.md
- Acceptance:
  - RED: `pytest .../test_form_check_gate_semantics.py` fails (old 2+🟡 rule
    present; contract/craft row annotations absent).
  - GREEN: pins pass — old-rule ABSENT (whole-file), row annotations
    present, aggregation pointer present, caps text unchanged (anchored
    window).
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Surfaces: form-check SKILL + rubric"

## Task 4 — voice-quadrant gate semantics
- Description: Apply contract-class semantics to
  copywriting-voice-quadrant-stage's gate/verdict passages: declared-voice-
  target (quadrant) mismatches → contract; positioning nuance → craft
  (recorded). Pointer to CLAUDE.md vocabulary, no local restatement.
- Module: copywriting-toolkit/skills/copywriting-voice-quadrant-stage
- Files touched: copywriting-toolkit/skills/copywriting-voice-quadrant-stage/SKILL.md,
  copywriting-toolkit/scripts/test_voice_quadrant_gate_semantics.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - copywriting-toolkit/agents/copywriter-evaluator.md
- Acceptance:
  - RED: `pytest .../test_voice_quadrant_gate_semantics.py` fails
    (contract/craft split absent from the gate passage).
  - GREEN: pins pass — split present, old accumulation wording absent.
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Surfaces: … voice-quadrant/voice-tone gate sections"

## Task 5 — voice-tone gate semantics
- Description: Same contract-class semantics for
  copywriting-voice-tone-stage's gate/verdict passages: declared tone-target
  violations (against the SHOULD voice-consistency gate's stated target) →
  contract; tone nuance → craft (recorded).
- Module: copywriting-toolkit/skills/copywriting-voice-tone-stage
- Files touched: copywriting-toolkit/skills/copywriting-voice-tone-stage/SKILL.md,
  copywriting-toolkit/scripts/test_voice_tone_gate_semantics.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - copywriting-toolkit/agents/copywriter-evaluator.md
- Acceptance:
  - RED: `pytest .../test_voice_tone_gate_semantics.py` fails (contract/craft
    split absent).
  - GREEN: pins pass — split present, old accumulation wording absent.
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Surfaces: … voice-quadrant/voice-tone gate sections"

## Task 6 — audit-stage aggregation semantics
- Description: Rewrite copywriting-audit-stage's aggregation (:103-120
  neighborhood): per-variant verdicts aggregate contract-class findings
  only; craft observations carried into the audit report as recorded
  notes. Per-variant counter mechanics unchanged.
- Module: copywriting-toolkit/skills/copywriting-audit-stage
- Files touched: copywriting-toolkit/skills/copywriting-audit-stage/SKILL.md,
  copywriting-toolkit/scripts/test_audit_gate_semantics.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - copywriting-toolkit/agents/copywriter-evaluator.md
- Acceptance:
  - RED: `pytest .../test_audit_gate_semantics.py` fails (contract-only
    aggregation wording absent).
  - GREEN: pins pass — aggregation rewritten, counters window unchanged.
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Surfaces: … audit-stage aggregation"

## Task 7 — neta overlay example passthrough fields
- Description: Complete copywriting-neta-injection's overlay-mode output
  envelope example (:220-238): add the omitted passthrough fields
  (express_mode_used / retries etc.) consistent with the canonical
  CLAUDE.md example, matching the knife-1 alignment sweep's conventions.
- Module: copywriting-toolkit/skills/copywriting-neta-injection
- Files touched: copywriting-toolkit/skills/copywriting-neta-injection/SKILL.md,
  copywriting-toolkit/scripts/test_neta_overlay_example.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
- Acceptance:
  - RED: `pytest .../test_neta_overlay_example.py` fails (overlay example
    lacks the passthrough fields).
  - GREEN: pin passes — fields present in the overlay example window.
- External surfaces: None.
- Dependencies: none
- Independent: true
- Brief item covered: "fix the neta overlay example's omitted passthrough
  fields while touching it"

## Task 8 — envelope validator script + test suite
- Description: Create copywriting-toolkit/scripts/validate_envelope.py
  (stdlib-only, loom_gate_markers-style fail-loud distinct exit codes):
  validate an envelope JSON file — schema (mandatory fields incl.
  express_mode_used / audit_trail[] / retries; alt-entry minimal shape
  allowed per CLAUDE.md:290 with express_mode_used omissible), counter
  monotonicity vs `--prev <file>` (bounce_round / revise_round_count /
  total_retries never decrease; total = bounce + revise), immutable-field
  preservation vs --prev, audit_trail append-only vs --prev, manual-PASS
  ban (gate_verdict PASS/PASS_WITH_NOTES valid only with a matching
  evaluator-written gate-verdict audit_trail entry), and the round-2
  structural duty (revise_round_count > 0 entering a re-gate requires a
  non-empty prior_findings block). Pytest suite: each check has a failing
  and a passing case, plus the legitimate minimal shapes.
- Module: copywriting-toolkit/scripts
- Files touched: copywriting-toolkit/scripts/validate_envelope.py,
  copywriting-toolkit/scripts/test_validate_envelope.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - loom-code/scripts/loom_gate_markers.py
- Acceptance:
  - RED: `pytest copywriting-toolkit/scripts/test_validate_envelope.py`
    fails (script absent).
  - GREEN: suite passes — incl. the manual-PASS case proving a PASS without
    an evaluator gate-verdict entry exits non-zero. (Command-surface
    declaration + CI wiring in Task 15.)
- External surfaces: None (stdlib only).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "P2 — envelope validator … Checks: JSON schema …
  counter monotonicity … manual-PASS ban" + "the validator also enforces
  the round-2 duty structurally" (Open Q3: yes)

## Task 9 — CLAUDE.md envelope-validation section
- Description: Add §Envelope validation to copywriting-toolkit/CLAUDE.md:
  file-borne handoff (orchestrator serializes the envelope to the run's
  work file at EVERY stage boundary and runs `python3
  <plugin-root>/scripts/validate_envelope.py <file> [--prev <file>]`;
  proceed only on exit 0; non-zero = STOP and surface — never hand-repair
  the envelope silently); work-file convention
  `${TMPDIR:-/tmp}/copywriting-run-<run_id>/envelope-<seq>.json`, run_id
  minted at intake (resolves brief Open Q2); the prose counter-enforcement
  warnings (:282-283) become pointers to the validator (prose explains,
  validator enforces). Also update the :340 "sync script deferred" note to
  point at scripts/check_anchor_copies.py (Task 13's script — CLAUDE.md has
  exactly two touchers this arc, Tasks 1 and 9, so this note rides here).
- Module: copywriting-toolkit/CLAUDE.md
- Files touched: copywriting-toolkit/CLAUDE.md,
  copywriting-toolkit/scripts/test_envelope_validation_doc.py
- Context paths:
  - copywriting-toolkit/scripts/validate_envelope.py
- Acceptance:
  - RED: `pytest .../test_envelope_validation_doc.py` fails (§Envelope
    validation absent; old prose-only warnings unconverted).
  - GREEN: pins pass — MUST-validate imperative, work-file convention,
    warnings now point at the validator.
- External surfaces: None.
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: "Envelope handoff becomes file-borne … proceed only
  on exit 0" + Open Q2 resolution

## Task 10 — router validator wiring
- Description: Wire the validation step into
  using-copywriting-toolkit/SKILL.md's routing loop as an imperative at the
  acting moment (serialize → validate → proceed on exit 0 / STOP on
  non-zero), pointing at CLAUDE.md §Envelope validation for the mechanics
  (pointer, no restatement).
- Module: copywriting-toolkit/skills/using-copywriting-toolkit
- Files touched: copywriting-toolkit/skills/using-copywriting-toolkit/SKILL.md,
  copywriting-toolkit/scripts/test_router_validator_wiring.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
- Acceptance:
  - RED: `pytest .../test_router_validator_wiring.py` fails (routing loop
    lacks the validation imperative).
  - GREEN: pins pass — imperative present at the routing loop's acting
    moment, pointer resolves to the real CLAUDE.md heading.
- External surfaces: None.
- Dependencies: Task 9 completes first
- Independent: false
- Brief item covered: "router + CLAUDE.md instruct this as a MUST at the
  acting moment"

## Task 11 — FIXABLE auto-revise worker≠judge seam
- Description: In copywriting-ethics-check-stage (auto-revise clause ~:163
  neighborhood): FIXABLE fixes are applied by a copywriter (worker)
  dispatch — never by the orchestrating context — and the gate re-verifies
  the affected checklist items after the fix; the evaluator's re-check, not
  the fixer's claim, closes the finding.
- Module: copywriting-toolkit/skills/copywriting-ethics-check-stage
- Files touched: copywriting-toolkit/skills/copywriting-ethics-check-stage/SKILL.md,
  copywriting-toolkit/scripts/test_fixable_worker_seam.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - copywriting-toolkit/agents/copywriter.md
- Acceptance:
  - RED: `pytest .../test_fixable_worker_seam.py` fails (worker-dispatch +
    re-verify wording absent; polarity pin: text must NOT permit
    orchestrator-applied fixes to self-close).
  - GREEN: pins pass.
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "FIXABLE auto-revise worker≠judge seam"

## Task 12 — intake BLOCKED becomes a verifiable action
- Description: Replace copywriting-intake's judgment-shaped halt ("user
  cannot decide after one probe round → BLOCKED", ~:69/:171-199) with a
  mechanical condition: after the bounded probe round, BLOCKED is emitted
  with the NAMED list of still-empty required intake fields.
- Module: copywriting-toolkit/skills/copywriting-intake
- Files touched: copywriting-toolkit/skills/copywriting-intake/SKILL.md,
  copywriting-toolkit/scripts/test_intake_blocked_verifiable.py
- Context paths:
  - docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md
- Acceptance:
  - RED: `pytest .../test_intake_blocked_verifiable.py` fails
    (named-empty-fields requirement absent; old judgment-only wording
    present).
  - GREEN: pins pass.
- External surfaces: None.
- Dependencies: none
- Independent: true
- Brief item covered: "Intake's judgment-shaped halt → verifiable action"

## Task 13 — psychology-anchor copy sync check script
- Description: Create copywriting-toolkit/scripts/check_anchor_copies.py
  (stdlib): verifies the 5 copies of persuasion-psychology-anchor.md and
  the 2 copies of sns-evolution-aisas-ulssas.md are byte-identical
  (canonical choices documented in the docstring); non-zero exit with a
  diff summary on drift. Pytest suite incl. a synthetic-drift case.
  (CLAUDE.md:340's deferred-note flip is Task 9's edit — this task touches
  no CLAUDE.md file.)
- Module: copywriting-toolkit/scripts
- Files touched: copywriting-toolkit/scripts/check_anchor_copies.py,
  copywriting-toolkit/scripts/test_check_anchor_copies.py
- Context paths:
  - copywriting-toolkit/CLAUDE.md
  - loom-code/scripts/verify-drift.py
- Acceptance:
  - RED: `pytest .../test_check_anchor_copies.py` fails (script absent).
  - GREEN: suite passes incl. synthetic-drift detection; live run exits 0
    (copies currently identical). (CI wiring in Task 15.)
- External surfaces: None.
- Dependencies: none
- Independent: true
- Brief item covered: "Psychology-anchor 5× copies: build the deferred sync
  script … per CLAUDE.md:340's own pre-authorization"

## Task 14 — release: version bump + CHANGELOG + codex sync
- Description: Bump copywriting-toolkit 1.14.2→1.15.0 in
  .claude-plugin/plugin.json; CHANGELOG entry covering P3 semantics,
  validator + wiring, and the three ride-alongs; run
  `python3 scripts/sync_codex_manifests.py copywriting-toolkit` (mirrors
  .codex-plugin/plugin.json).
- Module: copywriting-toolkit
- Files touched: copywriting-toolkit/.claude-plugin/plugin.json,
  copywriting-toolkit/.codex-plugin/plugin.json,
  copywriting-toolkit/CHANGELOG.md
- Context paths:
  - scripts/sync_codex_manifests.py
  - copywriting-toolkit/CHANGELOG.md
- Acceptance:
  - RED: `python3 scripts/sync_codex_manifests.py --check --all` reports
    drift after the plugin.json bump alone (deterministic failing check,
    before the sync run).
  - GREEN: sync check clean; CHANGELOG entry present in house style;
    versions match across both manifests.
- External surfaces: None.
- Dependencies: Tasks 3, 4, 5, 6, 7, 10, 11, 12 complete first
- Independent: false
- Brief item covered: "Version 1.15.0 (minor — new validator surface +
  semantics change), CHANGELOG, codex sync"

## Task 15 — CI wiring for the new runnable verbs
- Description: In .github/workflows/skill-structure.yml: add a
  copywriting-toolkit pytest step (runs
  `PYTHONDONTWRITEBYTECODE=1 pytest copywriting-toolkit/scripts/`) and a
  check_anchor_copies.py step (own step or inside the anchor-lint job) —
  declaring the arc's new runnable verbs in the CI command surface per the
  runnable-capability note.
- Module: .github/workflows/skill-structure.yml
- Files touched: .github/workflows/skill-structure.yml
- Context paths:
  - .github/workflows/skill-structure.yml
  - copywriting-toolkit/scripts/check_anchor_copies.py
- Acceptance:
  - RED: `grep -q "pytest copywriting-toolkit/scripts" .github/workflows/skill-structure.yml`
    exits 1 (step absent) — deterministic failing diagnostic.
  - GREEN: grep exits 0 for both new steps; workflow YAML parses
    (`python3 -c "import yaml;yaml.safe_load(open(...))"`); local dry-run of
    both commands green.
- External surfaces: None (repo-internal CI).
- Dependencies: Tasks 8, 13 complete first
- Independent: false
- Brief item covered: "Ships with pytest coverage (the plugin's first test
  suite) + a CI job addition (no pytest job exists for this plugin today)"

## Task 16 — BACKLOG flip
- Description: Flip docs/loom/BACKLOG.md §"copywriting-toolkit
  modernization arc" from COMMITTED-NEXT to SHIPPED (this arc, 1.15.0),
  keep history, point at brief + plan paths.
- Module: docs/loom/BACKLOG.md
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/BACKLOG.md
- Acceptance:
  - RED: `grep -q "modernization arc — port the 0.42.0 convergence lessons (COMMITTED-NEXT)"
    docs/loom/BACKLOG.md` exits 0 pre-edit (old status present) —
    deterministic pre-state diagnostic; post-edit the same grep exits 1.
  - GREEN: entry reads SHIPPED with brief/plan pointers; history preserved.
- External surfaces: None.
- Dependencies: none
- Independent: true
- Brief item covered: Decision — "Port, don't redesign … in that order"
  (arc completion record; BACKLOG entry is this arc's committed tracker)

## Notes

- Kickoff decision: work-file convention →
  `${TMPDIR:-/tmp}/copywriting-run-<run_id>/envelope-<seq>.json`, run_id
  minted at intake (brief Open Q2; arm-1 design default, recorded unbriefed —
  reversible by editing the convention doc).
- Kickoff decision: validator DOES structurally enforce the round-2
  prior-findings block (brief Open Q3; marginal cost inside Task 8).
- Brief Open Q1 (per-gate taxonomy wording) resolves inside Tasks 3/4/5/6 by
  transcription from each rubric's existing objective rows — the principle is
  pinned in Task 1's CLAUDE.md text.
- CLAUDE.md is touched by Tasks 1 and 9 only — sequential via T9's
  dependency chain (T1→T8→T9); Task 9 also updates the :340 sync-script
  deferred note to point at Task 13's script (T9 runs after T8; T13 has no
  CLAUDE.md file in its Files touched to avoid a third toucher — the note
  text lives in T9's edit).
- Honest limitation: the round-2 duty's BEHAVIORAL half (evaluator actually
  verifying before raising new findings) is prose+agent-contract enforced;
  the validator only checks the structural precondition. Mitigation: the
  close-out dogfood reuses the 2026-07-30 evidence-class trap recipe adapted
  to a cold copywriter-evaluator (contract/craft version), per the brief.
- Suite baseline at branch time: `pytest scripts/ loom-code/scripts/ -q` =
  522; copywriting-toolkit/scripts/ has no tests yet (first suite lands in
  this arc).
