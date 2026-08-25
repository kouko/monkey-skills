# Brief: loom-design skill text compaction

Date: 2026-08-25
Parent brief: docs/loom/specs/2026-08-25-loom-skill-text-compaction.md
Status: FROZEN — Part 1's dual-host pilot gate passed and the user authorized continuing the staged compaction.

## Design-side on-ramp

not fired — this is a behavior-preserving refactor of existing design contracts with regression coverage

## Problem

The nine remaining loom-design entrypoints repeat examples, rationale, schemas, and phase detail that do not all belong in the default load. Together they contain 20,142 words, making weak models spend context before reaching the activation rule, boundaries, required sequence, artifact contract, and ending gate.

## Users

- Claude Code and Codex users who need unchanged design decisions after the entrypoints become shorter.
- Loom maintainers who need per-skill essence oracles and explicit word ranges rather than subjective prose review.
- Reviewers who need weak-model evidence for activation, routing, refusal, artifact effects, human gates, and stop behavior.

## Smallest End State

All nine remaining loom-design `SKILL.md` entrypoints are 20–30% shorter while retaining their always-needed behavior inline. Each skill has a RED-first static essence and word-range test, valid references, focused and package tests green, a privacy gate, an atomic commit, and independent specification and quality review. The family then passes two baseline/candidate replicates per skill on Claude Code `haiku` and Codex `gpt-5.6-luna`, with stronger adjudication restricted to surviving `INCONCLUSIVE` results.

- BI-1 — Compact business-value while preserving exact explicit and implicit firing/skip rules, reentrancy, one-at-a-time three-axis evaluation, planning-team and user-insights boundaries, verdict logic, artifact template, and bounded validation.
- BI-2 — Compact completeness-critic while preserving spec-only writer-not-judge isolation, fresh panels, targeted reseeding, all required lenses and views, diagnostic-only overlap, ranked critic-found writeback, nonempty blind spots, verdict minting, validation, and the two-cycle cap.
- BI-3 — Compact design-critic while preserving design-artifact guards, tag/tier precheck, fresh and targeted panels, Nielsen grounding, ranked critic-found augmentation, nonempty blind spots, verdict minting, validation, and the two-cycle cap.
- BI-4 — Compact design-system while preserving principles and tone anchoring, absent-principles consent, modality routing, knowledge triage, the complete GUI contract, TUI/CLI stub, artifact paths, validation, on-disk ending gate, and visual-only boundary.
- BI-5 — Compact interaction-flows while preserving reference and principles intake, absent-principles behavior, modality choice, seven dimensions, Mermaid/ASCII rules, flag-only variants, knowledge triage, addressable artifact output, validation, ending gate, and surface/spec boundary.
- BI-6 — Compact product-principles while preserving reference intake, user-first probing and coverage, canon candidates and rejections, tone anchor, exact artifact structure, read-back, validation, headless thin-seed refusal, traceability with no silent drops, decision ownership, and downstream boundary.
- BI-7 — Compact user-insights while preserving the two distinct modes, research-versus-interrogation boundary, evidence-backed problem-space purity, job stories, explicit commitment and ratification, delegation/search thresholds, evidence chain, investment boundary, and bounded validation.
- BI-8 — Compact using-loom-design while preserving subagent stop, family reception/relay and upstream precedence, station routing, complex-fork briefing, thin-router boundary, isolated reentrant discovery, principles/interface ordering, critic resolution, draft-versus-critique distinction, host tools, and no-auto-invoke rule.
- BI-9 — Compact using-loom-pipeline while preserving subagent stop, conditional availability and Codex N/A behavior, exact driver invocation contract, three segments, four human gates, prohibitions, complete batch queue lifecycle and safety rules, dispatcher ownership, and terminal state.
- BI-10 — Record per-skill and aggregate size deltas plus static, focused, package, privacy, review, Claude, Codex, replicate, raw-evidence, and adjudication results with no confirmed regression or unexplained side effect.

## Current State Evidence

- **Data** — current `wc -w` baselines are 1,291 business-value, 4,004 completeness-critic, 2,323 design-critic, 1,982 design-system, 1,445 interaction-flows, 3,023 product-principles, 1,321 user-insights, 2,082 using-loom-design, and 2,671 using-loom-pipeline; total 20,142 words.
- **Forward** — `loom-code/scripts/loom_firing_harness.py` exposes dual-host baseline/candidate comparison, pinned models, retained raw JSONL, and replicate control; Part 1 already validated the runner.
- **Forward** — `docs/loom/dogfood/2026-08-25-loom-skill-compaction-dual-host-ab.md` records the successful Claude `haiku` and Codex `gpt-5.6-luna` pilot method.
- **Reverse** — the nine current `SKILL.md` files are the behavioral sources under test; `spec-expansion` is excluded because Part 1 already compacted and validated it.
- **Error** — static pins can prove that contract language remains, but only grounded live probes can reveal changed activation, routing, refusal, human gates, disk effects, or stopping behavior.
- **Boundary** — movement to a reference is not deletion: size accounting reports both the `SKILL.md` delta and any added/moved reference words, and only the net reduction excluding moved text counts toward the family result.
- **Evidence paths**:
  - `loom-design/skills/business-value/SKILL.md` — firing rules, three axes, verdict, and validation sections
  - `loom-design/skills/completeness-critic/SKILL.md` — panel, lenses, synthesis, verdict, and improve-loop sections
  - `loom-design/skills/design-critic/SKILL.md` — artifact precheck, panel, Nielsen lens, synthesis, and verdict sections
  - `loom-design/skills/design-system/SKILL.md` — intake, modality, GUI/TUI/CLI, output, and ending-gate sections
  - `loom-design/skills/interaction-flows/SKILL.md` — intake, modality, dimensions, diagram, output, and ending-gate sections
  - `loom-design/skills/product-principles/SKILL.md` — intake, elicitation, canon, artifact, validation, and headless sections
  - `loom-design/skills/user-insights/SKILL.md` — modes, evidence, commitment, delegation, artifact, and validation sections
  - `loom-design/skills/using-loom-design/SKILL.md` — reception, station routing, ordering, boundaries, and host-tool sections
  - `loom-design/skills/using-loom-pipeline/SKILL.md` — availability, driver, segments, gates, batch queue, and end-state sections

## Alternatives Considered

| Alternative | Evidence | Why rejected |
|---|---|---|
| Apply one fixed final word ceiling to every skill | Baselines range from 1,291 to 4,004 words and operative density differs | A shared absolute ceiling would over-compress dense contracts and under-challenge repetitive ones. |
| Count text moved into references as deleted | The parent arc distinguishes default-load reduction from real deletion | It would overstate simplification and could merely relocate the same runtime cost. |
| Use static essence checks without live probes | Part 1 dual-host dogfood | Static presence cannot prove a weak model still fires, refuses, asks, writes, or stops correctly. |
| Use a per-skill 20–30% net range plus dual-host replay | Current baselines and the proven Part 1 harness | Chosen: it sets a bounded compaction goal while making observable behavior the release gate. |

## Decision

Implement nine independent RED-first tasks, one per remaining skill. For each task, first add a static test that fails on the untouched entrypoint because it is outside the allowed 70–80% remaining-word range, then compact only that skill's `SKILL.md`. Delete repetition before considering extraction; any text moved to a reference is reported separately and does not count as deletion.

Each task must pass its named essence/range test, relevant focused tests, the full loom-design package suite, and a privacy review before an atomic commit. The committed task is then checked by a specification reviewer and a quality reviewer; any finding is repaired and the same gates are rerun before the task is accepted.

After all nine tasks pass, compare immutable full-plugin baseline and candidate roots on Claude Code `haiku` and Codex `gpt-5.6-luna`, two replicates per skill and host. Prompts must ground activation in real task context, exercise the essence contract, and forbid external or persistent side effects. Only replicated results that remain `INCONCLUSIVE` after mechanical comparison go to a stronger-model evidence adjudicator. A confirmed regression returns to the owning skill for repair and complete retest.

## What Becomes Obsolete

Repeated examples, historical rationale, duplicated phase explanations, and restated schemas become obsolete when removing them leaves the complete always-needed behavioral contract inline. No new comparison harness or alternate artifact schema is introduced.

## Out of Scope

- Compacting `spec-expansion`, already completed in Part 1.
- Changing any trigger, authorization boundary, verdict vocabulary, lens population, human gate, artifact schema, validator, side effect, or stopping behavior.
- Treating moved reference text as deleted words.
- Editing loom-code or loom-workflow skills in this family part.
- Making paid live evaluation an unconditional CI job.

## Queue relation

unqueued — this is the next sequential family part of the user-authorized compaction arc

## Open Questions

N/A — no unresolved question: the parent arc fixes the reduction range, host matrix, model tiers, replicate count, and adjudication rule

## Diagrams

N/A — no flow/state/architecture-shaped content: the implementation plan carries the nine-way fan-out and final join
