# loom family connective tissue — reception, uniform entries, §Intake (brief)

> Brainstorming brief (loom-code:brainstorming), 2026-07-04. Consumed by
> writing-plans. All fork decisions made with kouko in-session; the merge
> question was re-litigated and re-rejected with new reasons (§Alternatives).

## Problem

loom-code inherited superpowers' tight interlock (one injected router, every
skill cross-referencing its pipeline neighbors, handoff contracts, red-flag
tables). When the family grew to five plugins, that connective tissue was
never built at the family level: only loom-code has a SessionStart hook, so
**goal-oriented instructions (「幫我做出 X 功能」) always land in loom-code
and nothing ever suggests running principles → design → spec first**. The
design-side stations fire only when the user already knows to name them
(the #456 fix covers direct asks, not guidance). kouko's recurring pull
toward "merge everything into one plugin" is a symptom of this missing
tissue, not a packaging need.

> **Amended 2026-07-10**: loom-discovery (problem-space station) added —
> see docs/loom/specs/2026-07-09-loom-discovery-station.md. The "five
> plugins" framing above reflects the family at brief time (2026-07-04);
> it is now five stations / six plugins.

The job to be done: make the five-plugin family operate as one system —
predictable entry points, context-driven guidance to upstream stations even
when the user never asks, station-to-station handoffs visible — without
merging plugins and without weakening the one proven trigger mechanism.

## Users

- kouko (interactive): wants one memorable rule — *"要用 loom-X,就從
  `using-loom-X` 開始"* — and wants to be told "this looks like a new
  product; consider principles/design/spec first" when he charges in
  goal-first. Recommendations must be offered ONCE and never nag;
  incremental fixes (bug/refactor/covered increments) must not be
  interrupted.
- The model (routing agent): needs the guidance to sit on surfaces it
  reliably reads — #456 established that hook-injected router text fires
  dependably while description-pull alone under-fires on advisory tasks.

## Smallest End State

Six deliverables, all prose/contract layer — no driver changes, no station
logic changes:

1. **Family reception (loom-pipeline hook)** — new `hooks/hooks.json` +
   session-start injection in loom-pipeline (mirroring loom-code's
   mechanism): a compact "loom family front door" (~≤60 lines) carrying
   (a) the family map (five entries, one per plugin), (b) the three doors
   (interactive design-side / interactive loom-code / explicit Workflow
   pipeline+batch — the Workflow door is DESCRIBED, never auto-opened),
   (c) the **on-ramp criteria table** (SSOT — all §Intake checks reference
   it): missing `docs/loom/PRINCIPLES.md` + product-shaped work →
   product-principles first; user-facing surface + no DESIGN.md/ui-flows
   covering it → interface-design first; multi-state/multi-object behavior
   + no spec/change-folder → spec-expansion first; **negative guard**: bug
   fix / refactor / test-covered increment → do not interrupt.
2. **Two new thin entry skills** — `loom-product-principles:
   using-loom-product-principles` and `loom-spec:using-loom-spec`,
   completing the `using-loom-*` convention (3 of 5 exist). Each is
   §Intake + hand-off/routing only (spec's entry also disambiguates
   expansion vs critic — the #456-documented adjacent mis-route). Their
   descriptions must NOT steal member stations' direct asks (near-miss
   harness corpus guards this).
3. **§Intake contract** — a uniformly named first section in all five
   family entries: step 1 前站檢查 (upstream-artifact check against the
   reception's criteria table; recommend-once, record the user's choice,
   proceed), step 2 對站檢查 (wrong-station redirect), step 3 domain
   routing/discovery (loom-code's full brainstorming is the thickest
   instance — it gains "Axis 0" running steps 1-2; pipeline's intake
   reaffirms explicit-invocation). A structural test asserts every family
   entry carries the §Intake section (uniformity is machine-guarded).
   > **Amended 2026-07-10**: loom-discovery (problem-space station) added —
   > see docs/loom/specs/2026-07-09-loom-discovery-station.md. "All five
   > family entries" above now means six entries across five stations.
4. **Interactive chain cross-refs** — each design-side station's output
   states its next station (principles → design or spec; design → spec;
   spec → writing-plans is already wired), superpowers-style pipeline
   diagram in family entry skills; one red-flag line in using-loom-code
   ("skipping the Axis 0 upstream check before writing a brief =
   violation").
5. **Behavioral-test harness lands in-repo** — rebuild the #456 headless
   harness (mine triggers → `claude -p … --allowedTools Skill` → parse
   fired skill → grade EXACT/FAMILY/MISS/OVER) as versioned scripts (not
   scratchpad), with the five documented method traps baked into the
   README/comments. Acceptance runs: (a) goal-oriented corpus (「幫我做一個
   記帳 app」-type) must surface the design-side recommendation, (b)
   near-miss corpus must show no over-trigger from the two new entries,
   (c) direct-ask corpus must keep #456's 2/2 on design-side stations.
6. **Naming convention documented** — `using-loom-*` = family entry
   (router/intake); artifact names (product-principles, spec-expansion,
   design-system…) = stations, tuned for direct pull; `brainstorming`
   remains loom-code's discovery skill name. No renames of any existing
   skill (rename bill rejected — §Alternatives).

## Current State Evidence

- **Forward**: entry inventory verified 2026-07-04 — `using-loom-code`
  (loom-code/skills/), `using-loom-interface-design`
  (loom-interface-design/skills/), `using-loom-pipeline`
  (loom-pipeline/skills/) exist; loom-product-principles has a single
  skill `product-principles`; loom-spec has `spec-expansion` +
  `completeness-critic` and no entry router. Only loom-code has hooks
  (`loom-code/hooks/hooks.json` + `hooks/session-start/`); the four
  sibling plugins have no `hooks/` directory.
- **Reverse (SSOT direction)**: loom-code's `standards/`, `rubrics/`,
  `checklists/` are byte-identical functional copies distributed FROM
  domain-teams via `loom-code/scripts/distribute.py` (CI
  `verify-drift.py` enforces) — the in-house pattern proving cross-plugin
  sharing needs no merge; the reception's criteria table is authored once
  in loom-pipeline's injected text and *referenced* (not copied) by
  §Intake sections.
- **Error**: the failure mode this change exists to prevent is recorded
  behavior, not speculation — #456 firing test:
  `loom-interface-design:interaction-flows` and
  `loom-product-principles:product-principles` under-fired 0/8 until
  description retuning (fix: positive specificity, NOT negation);
  `completeness-critic` mis-routed to `spec-expansion` (adjacent-family
  confusion); root cause verified structural — hook asymmetry
  (memory: project_loom_firing_test_router_asymmetry). #475's dogfood
  (loom-spec resolved a product decision inline) evidences the thin
  design-side gating this brief's §Intake partially addresses.
- **Data**: the on-ramp judgment inputs are objective — file existence
  (`docs/loom/PRINCIPLES.md`, DESIGN.md / ui-flows for the surface,
  spec/change-folder) + work shape; no keyword sentiment. Recommendation
  outcome is recorded in the brainstorming brief ("design-side offered,
  user chose direct") so downstream reviewers do not re-flag.
- **Boundary**: hooks are a Claude Code mechanism — Codex hosts run
  neither loom-code's existing hook nor the new reception (parity
  unchanged, no regression). `using-loom-pipeline`'s fire condition
  (explicit invocation + Workflow + 4 stations, N/A-loud) is NOT widened
  by hosting the reception hook — the hook injects text; the skill's own
  trigger stays narrow. The reception text degrades gracefully when a
  station plugin is missing (recommend install, never hard-fail).

> **Amended 2026-07-10**: loom-discovery (problem-space station) added —
> see docs/loom/specs/2026-07-09-loom-discovery-station.md. The
> "Workflow + 4 stations" framing above is now 5 stations.

Evidence paths appendix:
`loom-code/hooks/hooks.json`, `loom-code/skills/using-loom-code/SKILL.md`,
`loom-code/skills/brainstorming/SKILL.md`,
`loom-pipeline/skills/using-loom-pipeline/SKILL.md`,
`loom-interface-design/skills/`, `loom-spec/skills/`,
`loom-product-principles/skills/`,
`loom-code/scripts/distribute.py`,
memory: project_loom_firing_test_router_asymmetry (PR #456),
docs/loom/BACKLOG.md (loom-spec #475 parity entry),
docs/loom/research/2026-06-17-plan-frozen-auto-advance-orchestration.md.

## Decision

Build the family tissue as **reception (loom-pipeline hook) + completed
`using-loom-*` entry convention + §Intake contract + cross-refs +
in-repo behavioral harness** — packaging untouched:

- **Front door lives in loom-pipeline (P2)**: sequencing knowledge is the
  conductor's jurisdiction (its README/driver already encode the four-station
  order). loom-code's existing hook is NOT touched — the #456-proven
  mechanism carries zero regression risk, and the two injections have
  disjoint jobs (reception: where you are in the journey / which door;
  loom-code: coding discipline).
  > **Amended 2026-07-10**: loom-discovery (problem-space station) added —
  > see docs/loom/specs/2026-07-09-loom-discovery-station.md. The
  > "four-station order" above is now a five-station order.
- **Guidance without being asked** rides the strongest existing mechanism
  instead of racing it: goal-oriented utterances still land in loom-code
  (its hook wins — fine), but brainstorming is the unskippable HARD-GATE
  first station, so its new Axis 0 runs the upstream check
  deterministically. Guarantee chain: goal-first instruction → mandatory
  brainstorming → mandatory Axis 0 → missing-artifact recommendation
  surfaces. Entering via any other door hits the same check in that
  entry's §Intake. Recommend-once, user decides, choice recorded; the
  negative guard exempts incremental fixes.
- **No per-plugin hook parity, no *-brainstorming renames, no merge** —
  see Alternatives; each carries an explicit re-trigger instead of a
  standing argument.

We will NOT: touch any `driver_*.js` or the generated asset; widen
using-loom-pipeline's fire condition; auto-open the Workflow door from
context; hard-gate the design-side on-ramp; rename any existing skill;
change station generator/critic logic.

## Alternatives Considered

1. **Merge all loom-* into one plugin** (re-litigated this session,
   third time). Rejected again: the desired tightness = connective tissue
   (routing, contracts, cross-refs), demonstrably orthogonal to packaging
   (2026-06-17 research verbatim: "Auto-advance needs the gates to chain,
   which is orthogonal to packaging… crutch-class consolidation with zero
   verification benefit and real coupling cost"). New reasons this round:
   a unified brainstorming is either thin (= the reception, no merge
   needed) or a four-domain god-skill; agentType renames
   (`loom-code:implementer` is hardcoded in driver_50_seg3.js and consumed
   cross-plugin) + 5→1 CI/manifest/version rework are real bills with no
   new income. **Re-trigger**: tissue shipped AND behavioral tests still
   show the cross-plugin boundary itself leaking.
2. **Front door stays in loom-code (P3) or moves wholesale (P1)**: P3
   leaves loom-code speaking for siblings (jurisdiction leak); P1 removes
   the #456-proven coding-discipline hook and lets it depend on pipeline
   being installed (naked-discipline risk). P2 chosen.
3. **Hook parity for the three design-side plugins**: hooks are for
   mandates, not discoverability; the on-ramp is a recommendation and the
   reception is its one signpost; 3 extra injections tax every session in
   every project. **Re-trigger** (#456's own reserved fallback): a family
   still under-fires on natural asks in the post-tissue behavioral test →
   hook for that family only.
4. **Rename entries to `*-brainstorming`**: misnames routers/conductors
   (entries serve the whole journey, not just discovery); uniform naming
   of different things manufactures the adjacent mis-route failure #456
   documented; positive specificity is the proven firing lever. Rejected.
5. **Full per-family brainstorming skill files**: converged instead to
   §Intake sections (uniform contract, domain-appropriate thickness) —
   principles' generator is already elicitation-shaped; separate files =
   double questioning ceremony. **Re-trigger**: a family's §Intake proves
   too weak behaviorally → promote that one to a skill.

Industry grounding (thin for this internal design space — the primary
evidence is in-house #456 behavioral data): monorepo umbrella-entry
pattern and "keep god packages small and composable"
(toptal.com/front-end/guide-to-monorepos;
deepwiki.com/better-auth/better-auth package structure;
github.com/TanStack/router discussion #755); JA search returned no
countervailing pattern (ja.vuejs.org plugin guide closest).

## What Becomes Obsolete

- The ambiguity "loom-code's router is the de-facto family front door" —
  resolved explicitly (reception owns the family map; loom-code owns
  coding discipline).
- The #456 harness's scratchpad-only existence — its method lives in
  memory but the scripts evaporated with the session; deliverable 5 makes
  it a versioned repo asset (lesson: reusable test rigs belong in-repo,
  not scratchpads).
- Nothing deleted from any plugin; purely-additive is acknowledged — the
  tissue was never built, this is the build.

## Open Questions

1. **Reception token budget**: target ≤60 lines injected — writing-plans
   should include a structural test capping it (injected text is a
   per-session tax; the cap keeps it honest).
2. **§Intake in using-loom-pipeline**: its step 3 is "reaffirm explicit
   invocation" — exact wording must not soften the N/A-loud /
   never-hand-drive constitution. → writing-plans wording task.
3. **loom-spec #475 parity** (brief-before-asking escalation for
   interactive product forks): same-family thinness but a behavioral
   upgrade, not wiring — kept OUT of this change (scope control), stays
   in BACKLOG with its own entry.
4. **Harness home**: `loom-code/scripts/` (near its consumers' tests) vs
   a family-neutral location — writing-plans decides; must respect the
   flat skill-folder rule (scripts/ at plugin root is outside skill
   folders, fine).
