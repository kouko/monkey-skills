# Brief: copywriting-toolkit convergence modernization (knife 2)

Date: 2026-07-30 · Stage: brainstorming output → writing-plans input
Branch: `feat-copywriting-convergence-modernization` · copywriting-toolkit 1.14.2 → 1.15.0

## Design-side on-ramp

N/A — tool-shaped increment to an existing plugin (negative guard).

## Problem

The copywriting gate pipeline shares the exact problem shape loom-code solved in
0.42.0: prose review whose flag-mode verdict rule ("2+ 🟡 → NEEDS_REVISION" over
qualitative craft dimensions) has no closed blocking class and no
prior-findings verification duty — each re-run can mint fresh 🟡s, and the
existing round caps convert churn into early human escalation instead of
convergence. Worse, the pipeline's entire enforcement layer (envelope schema,
three retry counters, monotonicity, immutable fields, append-only audit_trail,
the manual-PASS ban) is a prose-only state machine the model bookkeeps about
itself — zero mechanical checks — which the repo's own lessons show dies on
weak executors. copywriting-toolkit's CLAUDE.md names the failure ("resetting
is how stall-loops hide") without being able to enforce it.

Evidence (2026-07-30 three-stream audit, this session):
- 🟡-accumulation rule: `copywriting-toolkit/skills/copywriting-form-check-stage/SKILL.md:116-119`,
  `copywriting-toolkit/agents/copywriter-evaluator.md:64-68`, rubric dims
  `.../rubrics/form-appropriate-gate.md:79-153` (qualitative: Affinity
  thickness, inter-stage flow).
- Prose-only counters + self-report oracles: `copywriting-toolkit/CLAUDE.md:146,188-190,282-283`;
  per-variant retry arithmetic a weak orchestrator will fumble:
  `copywriting-toolkit/skills/copywriting-audit-stage/SKILL.md:103-120`.
- Caps ALREADY exist (2 revise/phase, bounce ≥3 halt, total_retries ≥4 HALT —
  `CLAUDE.md:188-190`) — only the verdict semantics and the enforcement medium
  are missing; this is a semantics + mechanization port, not a redesign.

## Users

- The operator running copy jobs end-to-end (router-driven) or via direct
  stage entry.
- Orchestrator agents at any tier (weak included) doing the envelope
  bookkeeping; the evaluator agent (opus by design) rendering gate verdicts.
  Weak-tier orchestrators are the design constraint: obligations must be
  validator-checked, not prose-only.

## Smallest End State

1. **P3 — contract-class verdict semantics** (port of 0.42.0's blocking-class
   design; MUST land before P2 so the validator pins the new vocabulary):
   - Every gate finding carries `class: contract | craft` — **contract**: the
     finding cites a violated contract term (brief constraint, form spec
     limit/mandatory element, declared voice target, ethics rule — an
     objective, checkable referent); **craft**: a qualitative observation
     (affinity thickness, flow, tone nuance). Unclear → contract (fail
     closed).
   - The gate verdict aggregates over **contract-class findings only**;
     craft-class findings are recorded observations that never gate. Ethics
     checklist mode keeps FATAL semantics unchanged (already the new shape);
     FIXABLE ≈ recorded + bounded auto-fix.
   - **Round-2 duty**: a re-gate dispatch carries the prior round's findings
     verbatim; the evaluator verifies each against the current draft BEFORE
     raising anything new; re-raising a closed finding in new words is
     forbidden; a finding that resurfaces after being fix-verified ends the
     loop → surface to the operator (oscillation), whatever the counters say.
   - Surfaces: form-check SKILL + rubric, voice-quadrant/voice-tone gate
     sections, audit-stage aggregation, copywriter-evaluator agent contract,
     CLAUDE.md verdict vocabulary. (All toolkit-local: the form rubric header
     declares DIVERGED FROM domain-teams — no sync pipeline; Tier-1 lock
     applies only to third-party framework text inside standards files,
     `CLAUDE.md:34-51`.)
2. **P2 — envelope validator** (`copywriting-toolkit/scripts/validate_envelope.py`,
   stdlib-only, loom_gate_markers-style):
   - Envelope handoff becomes file-borne: at every stage boundary the
     orchestrator serializes the envelope to the run's work file and runs the
     validator; proceed only on exit 0 (router + CLAUDE.md instruct this as a
     MUST at the acting moment).
   - Checks: JSON schema (mandatory fields incl. `express_mode_used`,
     `audit_trail[]`, `retries`; alt-entry minimal shape allowed per
     `CLAUDE.md:290` — express_mode_used omissible there), counter
     monotonicity vs the previous envelope file (`--prev`), immutable-field
     preservation, audit_trail append-only, and the manual-PASS ban: a
     `gate_verdict: PASS`/`PASS_WITH_NOTES` is valid ONLY when the
     audit_trail carries a matching evaluator-written `gate-verdict` entry.
   - Ships with pytest coverage (the plugin's first test suite) + a CI job
     addition (no pytest job exists for this plugin today).
3. **Ride-alongs** (small, from the audit + knife 1):
   - FIXABLE auto-revise worker≠judge seam: auto-revise fixes are applied by
     the copywriter (worker) dispatch, and the gate re-verifies the affected
     checklist items — never orchestrator-applies-then-self-passes.
   - Intake's judgment-shaped halt → verifiable action: BLOCKED must name the
     concrete still-empty intake fields after the bounded probe round.
   - Psychology-anchor 5× copies: build the deferred sync script
     (`diff`-check style, CI-runnable) per `CLAUDE.md:340`'s own
     pre-authorization; fix the neta overlay example's omitted passthrough
     fields while touching it.
4. Version 1.15.0 (minor — new validator surface + semantics change),
   CHANGELOG, codex sync.

## Current State Evidence

- **Forward**: router phase machine `using-copywriting-toolkit/SKILL.md:40-99`;
  gate loop-backs + caps `copywriting-form-check-stage/SKILL.md:165-188`,
  ethics stop-rule `copywriting-ethics-check-stage/SKILL.md:160-193`; envelope
  canonical `CLAUDE.md:108-150` (post-#632: SSOT named, all examples aligned).
- **Reverse (SSOT)**: form rubric header "DIVERGED FROM domain-teams:copywriting-team"
  (`rubrics/form-appropriate-gate.md:2-3`) — deliberate fork, no distribute
  pipeline; Tier-1 byte-identity scoped to third-party framework text in
  standards only (`CLAUDE.md:34-51`); evaluator agent is toolkit-native (no
  lineage marker). Toolkit-side edits are self-contained.
- **Error/guards**: the ONLY mechanical check today is
  `scripts/lint-anchor-library.py` (anchor schema; CI job exists). No pytest,
  no envelope validation, no counter enforcement. Nested-dispatch guard just
  shipped in #632 (`CLAUDE.md` evaluator section).
- **Data/tests**: zero test files in the plugin (audit ①); CI jobs touching it:
  skill-structure scan (added in #632) + anchor lint. loom-code's
  `loom_gate_markers.py:201-273` is the pattern donor for the validator's
  fail-loud exits.
- **Boundary**: two agents `copywriter.md` (sonnet worker) /
  `copywriter-evaluator.md` (opus judge, verdict-only, anti-patterns stated);
  caps and counters defined `CLAUDE.md:146,188-190`; alt-entry minimal shape
  `CLAUDE.md:290`; deferred sync-script pre-authorization `CLAUDE.md:340`.
- Evidence appendix: audits ①②③ 2026-07-30 (in-session), knife-1 diff PR #632.

## Decision

Port, don't redesign: keep flag mode's qualitative dimensions but gate only a
closed contract class (0.42.0's proven shape), add the round-2
verification/re-litigation/oscillation duties, then mechanize the envelope
state machine as a file-borne validator gate that pins the post-P3 vocabulary
— in that order. Ethics checklist semantics stay. The domain-teams
copywriting-team twin is deliberately NOT updated (diverged fork, no sync
pipeline — recorded, not hidden). We do NOT restructure the 14-skill shape,
diet descriptions, or touch anchor content.

## Alternatives Considered (Axis 4)

Research basis: the 0.42.0 arc's same-day EN+JA industry research on review
convergence (`docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md`
§Alternatives — caps 2-3 rounds EN/JA consensus, severity-tiered blocking,
re-litigation bans/ledgers [JA], advisory demotion precedent [NTT Docomo]).
Same problem shape, reused with attribution rather than re-searched.

| Alternative | Why rejected |
|---|---|
| Checklist-only (delete flag mode) | loses the qualitative dimensions' diagnostic value; 0.42.0 showed you can keep dimensions and gate a class — smaller change, same convergence |
| Advisory demotion of gates (Docomo pattern) | ethics/FTC gates must block; kept as the recorded fallback if contract-class FP proves high in practice |
| Validator-only, no semantics change | mechanizes the churn: counters would be enforced around a verdict rule that still doesn't converge on prose |
| Full envelope-as-file rearchitecture (stages read/write files directly) | bigger blast radius than needed; the orchestrator-serializes-at-boundaries shape gets the enforcement without rewriting stage I/O |

## What Becomes Obsolete (Axis 5)

- The "2+ 🟡 → NEEDS_REVISION"-over-craft-dims wording in form-check SKILL,
  evaluator agent, and rubric — replaced by contract-class aggregation.
- CLAUDE.md's prose-only counter-enforcement warnings (`:282-283`) — become
  pointers to the validator (prose stays as explanation, not enforcement).
- CLAUDE.md `:340`'s "sync script deferred, acceptable if drift observed" —
  superseded by the shipped sync script.

## Out of Scope

- Skill-count restructuring / stage demotion (deliberate dual-entry design).
- Description edits (all at house norm; eviction economics say irrelevant).
- Anchor library content, Tier-1 framework text, domain-teams twin.
- Any change to loom-code; the pattern donor is read-only reference.

## Open Questions

1. Exact contract-class taxonomy wording per gate (form/voice/audit) — plan
   stage transcribes from each rubric's existing objective rows; the
   principle (objective checkable referent → contract) is settled here.
2. Envelope work-file location convention (run-scoped temp vs repo-side
   `.copywriting-run/`) — plan decides with git-hygiene in view (must not
   pollute user repos; lean: OS temp dir keyed by run id).
3. Whether the validator also enforces the round-2 duty structurally
   (prior-findings block present in re-gate dispatches) or that stays
   prose+dogfood — plan decides by cost.
