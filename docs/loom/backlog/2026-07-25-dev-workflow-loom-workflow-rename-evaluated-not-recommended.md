---
name: 2026-07-25-dev-workflow-loom-workflow-rename-evaluated-not-recommended
description: dev-workflow → loom-workflow rename — evaluated, NOT recommended
status: PARKED
origin: bba proactive-trigger-hardening arc (2026-07-25) side-discussion. User asked whether dev-workflow, since loom-* is its dominant citer (loom-code 23 + loom-pipeline 2 prose refs vs ~3 non-loom), should be renamed `loom-workflow`.
start: only if dev-workflow becomes genuinely loom-only — i.e. `dbt-model-style` has moved out AND no non-loom caller remains (git-memory no longer gates non-loom commits). Not today's reality.
---

- Start: only if dev-workflow becomes genuinely loom-only — i.e. `dbt-model-style`
  has moved out AND no non-loom caller remains (git-memory no longer gates
  non-loom commits). Not today's reality.
- Origin: bba proactive-trigger-hardening arc (2026-07-25) side-discussion.
  User asked whether dev-workflow, since loom-* is its dominant citer
  (loom-code 23 + loom-pipeline 2 prose refs vs ~3 non-loom), should be
  renamed `loom-workflow`.
- Verdict: **NOT recommended now.** (1) Asserts a false loom-exclusivity —
  `dev-workflow:git-memory` gates EVERY commit in any repo, loom or not; the
  prose-reference count misses harness/user invocation. (2) `dbt-model-style`
  is dbt-specific, not loom — the plugin is a general dev toolkit. (3) Inverts
  the placement principle (below): the health test is "does the skill stand
  alone", not "who cites it most". (4) Breaking rename blast radius reaches the
  user's OWN global rules (`~/.claude/rules/institution-maintenance.md` cites
  `dev-workflow:git-memory`; `judgment-rubrics.md` cites
  `dev-workflow:brief-before-asking`), marketplace.json, 25+ repo refs, and all
  guard tests pinning `dev-workflow:` strings. (5) Name by function, not by
  dominant caller (callers change; function doesn't).
- Better path if the goal is family-membership clarity: document dev-workflow's
  dual role (loom shared foundation + standalone dev tools) in loom-memory /
  family reception — no rename.
- **Placement principle (reusable, worth recording separately)**: a skill
  belongs in the shared general layer (dev-workflow) iff it stands alone
  outside loom; the citation-count metric will always favor loom and is the
  wrong test. Same error class as "move bba into loom" — mis-scoping a general
  tool into the loom namespace.
