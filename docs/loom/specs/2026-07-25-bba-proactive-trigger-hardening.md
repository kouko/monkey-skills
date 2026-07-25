# Brief — bba proactive-trigger hardening across the loom family

> Source: loom-code:brainstorming, 2026-07-25. Consumed by writing-plans → SDD.
> Scope confirmed by user ("全做", 6 plugins). Approach: name in place (cross-plugin).

## Problem

**JTBD**: the user wants `dev-workflow:brief-before-asking` (bba) to fire more
often. Diagnosis (`docs/harness-audit/2026-07-22-bba-trigger-baseline.md`,
re-classified 2026-07-25) shows the under-firing is **proactive**, not
reactive: of the 3 identified true misses, 3/3 are proactive-misses — the
agent was about to ask the user a non-trivial fork and did NOT invoke bba
first. (R=0 is a sampling-frame artifact — the baseline only sampled
AskUserQuestion events — not proof reactive misses are zero.)

**Root cause**: the imperative that names bba and binds it to the
ask-a-fork moment is *structurally absent* from the omnipresent SessionStart
surface. `loom-code/hooks/router-card.md:13` (rule 5) carries only a generic
paraphrase ("default to AskUserQuestion + lead with anchor+stakes") that
never names bba. The real imperative exists only in pulled skill bodies that
load *after* the agent has already entered a skill:
`loom-code/skills/brainstorming/SKILL.md:58`,
`loom-code/skills/subagent-driven-development/SKILL.md:40`,
`loom-code/skills/requesting-code-review/SKILL.md:20`, and
`loom-pipeline/skills/using-loom-pipeline/SKILL.md:158`. A plain session that
reaches a fork *before* entering any of those (exactly what happened at the
opening of this session) gets no reminder. The 4 design-side plugins
(loom-discovery / loom-interface-design / loom-product-principles / loom-spec)
name bba nowhere at all.

Evidence base for the fix mechanism: repo memory
`docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md` —
an imperative action-moment card that NAMES the skill flipped weak-model
behavior 2/2; a descriptive generic paraphrase moved behavior 0/2. The
current failing rule 5 is exactly that generic paraphrase.

## Users

- **Primary — the acting agent** (any tier) in a loom-family session, at the
  moment it is about to ask the user a non-trivial fork. It needs an
  imperative, action-moment reminder to invoke bba FIRST — not descriptive
  prose (0/2) and not a reminder gated behind already entering brainstorming/
  SDD.
- **Secondary — the human (kouko)**, who experiences under-briefing when the
  agent asks bare forks. This session's opening turn was a live proactive
  miss ("剛剛的溝通就讓我搞不清楚狀況了，這時候本來該由這 skill 幫我白話說明").

## Smallest End State

Three change classes, 6 plugin version bumps, no new skills:

1. **Proactive imperative at session-start (loom-code)** —
   `loom-code/hooks/router-card.md` rule 5 gains an imperative naming
   `dev-workflow:brief-before-asking`, reusing the canonical trigger triple
   (`≥3 trade-offs / ≥2 implementation paths / architectural blast radius`)
   already pinned lockstep across the 3 loom-code skill bodies.
2. **Reactive-signal summary in the description (dev-workflow)** —
   `dev-workflow/skills/brief-before-asking/SKILL.md` description (line 4)
   summarizes the two body-level reactive signals it currently omits: the
   check-question guard (SKILL.md:81-92) and the repeated-confusion
   meta-trigger (SKILL.md:79). This is a description-summary gap, not a
   missing mechanism.
3. **bba imperative in the 4 design-side routers** — each
   `using-*/SKILL.md` router body (loom-discovery / loom-interface-design /
   loom-product-principles / loom-spec) gains a one-line bba imperative,
   matching the existing `using-loom-pipeline/SKILL.md:158` pattern. Router
   bodies load early in design-side sessions (the user starts by invoking the
   `using-*` router), so a body line is well-positioned there.

**TDD shape (prose-contract surfaces)**: for each carrier, RED = add a
grep-based guard test asserting the bba imperative (and, where applicable,
the trigger triple) is present → fails; GREEN = add the text → passes. This
also pins the two currently-unguarded surfaces (router-card rule 5, bba
description) so future description sweeps cannot silently drop them
(`docs/loom/memory/description-sweeps-must-run-owning-plugin-suite.md`).

## Current State Evidence

- **Forward** (who calls the surface): `loom-code/hooks/session-start` injects
  `router-card.md` verbatim every loom-code session; `loom-pipeline/hooks/
  session-start:45` injects `family-reception.md` + an awk slice of
  `family-relay.md §(b)` only. Design-side plugins have NO SessionStart hook —
  their `using-*/SKILL.md` router is the earliest always-relevant surface.
- **Reverse** (SSOT / who owns bba): bba is owned by dev-workflow's shared
  utility layer (siblings: git-memory, complexity-critique, proposal-critique,
  handoff, recap-state — all consumed cross-family). Dependency direction is
  one-way loom-* → dev-workflow; no `dependencies` field exists in any
  `plugin.json` (co-shipped marketplace). The cross-plugin reference is the
  sanctioned pattern (CLAUDE.md:71; already 6 `dev-workflow:brief-before-asking`
  refs, 10 `git-memory`, 9 `complexity-critique`).
- **Error / degradation**: existing bba references are unconditional +
  test-pinned (`loom-code/scripts/test_asking_user_briefing_escalation.py`
  pins the triple + "brief-before-asking" across 3 skills;
  `loom-pipeline/scripts/test_pipeline_skill_gates.py:51-52` pins
  "brief-before-asking" + "#475" in the pipeline router). The family already
  treats dev-workflow as a required sibling.
- **Data** (guard-test facts): `router-card.md` is UNGUARDED (no test file
  references it). bba SKILL.md description field is UNGUARDED. bba body has
  two ordering markers pinned at `loom-pipeline/scripts/test_family_relay.py:
  193-194` ("never bury a briefing and an AskUserQuestion", "explicit user
  request for a visual is always honored") — must be preserved.
  `family-reception.md` is hard-capped ≤60 lines and sits at 60/60 (why the
  shared-card route is out of scope).
- **Boundary**: the 4 design-side routers' own guard tests are NOT yet
  enumerated — RESOLVE IN PLAN TASK 1 (grep each plugin's `scripts/test_*.py`
  for the router filename before editing).

Evidence paths:
- `docs/harness-audit/2026-07-22-bba-trigger-baseline.md`
- `loom-code/hooks/router-card.md`, `loom-code/hooks/session-start`
- `dev-workflow/skills/brief-before-asking/SKILL.md`
- `loom-pipeline/hooks/family-relay.md`, `family-reception.md`, `session-start`
- `loom-{code,pipeline}/scripts/test_*.py`
- `docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md`
- `docs/loom/memory/skill-triggering-diagnose-listing-before-text.md`
- `docs/loom/memory/description-sweeps-must-run-owning-plugin-suite.md`

## Decision

Name bba in place (cross-plugin, sanctioned) across all 6 carriers; reuse the
canonical trigger triple for cross-carrier consistency; add guard tests to
pin every new imperative (including the two previously-unguarded surfaces).
Do NOT move bba into loom (two consumers → doesn't eliminate cross-plugin
refs, degrades bba's shared-layer placement, breaking rename) and do NOT keep
rule 5 generic (that IS the current failing text; 0/2 by memory).

## Out of Scope

- **family-reception shared-card surgery** — the 60/60 line cap + awk-slice
  widening + 6 marker guards make it high-friction for marginal gain (router
  bodies + loom-code card already cover the sessions). Parked.
- **Compressed/lightweight briefing template ("Cut 3" 3a)** — dropped by user
  ("只用 6-block 樣式就好").
- **family-relay message-class ordering table** — dropped with Cut 3.
- **Delivery-blemish fixes** — 5/8 organic triggers fired but delivered a
  malformed/buried/skipped briefing. Real, but a *delivery* problem, not a
  *trigger* problem. Separate arc.
- **Live firing-harness A/B** — deferred to the already-planned 07-28
  telemetry (P3). Static guard tests are the pre-merge proof; behavioral A/B
  is a post-merge step (marketplace pulls GitHub main —
  `docs/loom/memory/deploy-surface-ab-legs-run-post-merge.md`).

## Alternatives Considered

- **Move bba into a loom plugin** — rejected: loom-code AND loom-pipeline both
  consume it, so no single loom home makes all refs intra-plugin; degrades a
  general tool into loom-specific; breaking ID rename across 6+ test-pinned
  refs. Would only be reconsidered if the loom family were to ship
  independently of dev-workflow (user confirmed no such intent).
- **Keep rule 5 generic (don't name bba)** — rejected: it is the current
  failing text; generic descriptive prose moved behavior 0/2 (memory).

## What Becomes Obsolete

Nothing is removed. The generic rule-5 paraphrase is strengthened in place
(the anchor+stakes floor stays; the bba imperative is added above it). No
runbook or duplicate mechanism is retired.

## Open Questions

- The 4 design-side routers' guard-test coverage (Boundary above) — resolve
  in plan Task 1 before editing those files.
- Exact one-line wording per carrier is an implementation detail for SDD;
  must reuse the canonical triple verbatim to satisfy consistency + any
  lockstep guard.
