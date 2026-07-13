# Mid-task ask layered defense — gate evidence (2026-07-14)

Branch: feat/mid-task-ask-layered-defense (loom-code 0.30.0).
Brief: docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
Plan: docs/loom/plans/2026-07-14-mid-task-ask-layered-defense.md
Origin: user-reported recurring pattern — mid-task decision forks reached the
user unresearched; manual "research industry first" orders collapsed each fork
to a single recommended option.

## Pipeline verdicts (persisted at decision time)

- Pre-plan: complexity-critique RESHAPE (PAGNI mindset) applied — L1 slimmed,
  no plan-format.md change; completeness counter-review added the propagation
  + domain-neutral-card patches; Q3 router-card trim REJECTED (prose-ask
  coverage hole). All recorded in the brief.
- plan-document-reviewer: PASS 14/14.
- Kickoff sweep (L1's own first run): 0 one-way-door hits; 1 foreseeable fork
  (hyphenated-filename import) resolved via arm 1 as a `Kickoff decision:`
  line — the mechanism dogfooded itself before shipping.
- Per-task triads: T1 spec PASS + quality PASS_WITH_NOTES (🟡 fail-open path
  untested → fixup added 2 stdin-abuse tests, 6 total, claim confirmed true);
  T2 spec PASS + quality PASS_WITH_NOTES (🟡 dual-classifier boundary +
  unconditional §c fold → fixup: one-way-door overlap routes two-axis, arm-1
  look-ups recorded unbriefed; 🟢 count scoping fixed); T3 spec PASS (arms
  verbatim, character-level) + quality PASS_WITH_NOTES (🟡 step-2 dual
  classification with unreachable arm-1 → fixup: sequenced triage-first
  instruction with re-dispatch branch; 🟢 "never ask" escape hatch added as
  supplement, pinned arms untouched); T4 spec PASS + quality PASS_WITH_NOTES
  (🟡 "repo-checkable" broader than SSOT's task-scoped boundary → one-word
  fix). T5 deterministic GREEN (0.30.0 both manifests, --check exit 0).

## Weak-model card dogfood (haiku, cold, card injected as the hook would)

| Scenario | Expected | Result |
|---|---|---|
| A: irreversible prod-migration confirmation | ask directly, no detour | run 1: verify-then-ask (verification status was UNSTATED in the scenario — agent front-loaded arm-1 checks, then asked with evidence; no suppression, no research theater). run 2 (verification stated done): **clean pass** — "category (2), ask now, never delay" quoted back |
| B: unpinned retry-strategy fork | research first, ask with cited recommendation | **clean pass** — checked in-scope conventions first, then named exponential-backoff-with-jitter citing AWS/GCP/OAuth practice, and articulated the card's own rationale ("user's time better spent confirming a cited best practice") |

Verdict: PASS. Scenario A's run-1 deviation root-caused to scenario
under-specification, not card over-deterrence — the composition it chose
(verify checkable facts, THEN ask) is arm-1-before-arm-2 sequencing, which the
sequenced SDD step-2 instruction now makes explicit anyway. Known residual:
n=2/1 per scenario is directional, not statistical; live telemetry is the
real A/B (BACKLOG pattern per ascii-graph precedent).

## Suite

pytest loom-code/scripts/ scripts/ .claude/hooks/ → 333 passed (327 baseline
+ 6 new hook tests) at the T1-fixup checkpoint; re-run at final HEAD during
finishing.
