# Brief: goal-loop harness — target-agnostic "judge the goal, iterate until met"

> Status: SUPERSEDED (2026-07-23, same day) by
> `2026-07-23-wiki-update-maintenance-loop.md` — user re-cut scope from
> "general harness + 2 adapters" to "obsidian wiki-update thin
> orchestrator + loop engine" (Rule-of-Three: generalize only when a
> third loop target is real; re-trigger recorded in BACKLOG). This
> file remains the research substrate: Axis 4 sweeps (6 total), §Design
> constraints 1-5, and §loom-* integration map are consumed by the
> successor brief by reference, not copied.

## Design-side on-ramp

Offered previously across loom arcs — user pattern is direct-to-code for
internal tooling; proceeding direct. (`docs/loom/PRINCIPLES.md` absent at
repo root; internal plugin machinery, not end-user product surface.)

## Problem

(Axis 1) The user wants agents that can take a goal, judge for themselves
whether it is met, and iterate until it is — as a GENERAL capability, not
per-target bespoke machinery. The job behind the ask: "let me hand an
agent an improvable artifact + a definition of better, walk away, and
trust that what comes back either genuinely improved or honestly reports
why it stopped." The repo has built this once (principles-improve-loop /
principles-replay-matrix) but welded to one target; every new target
today means rebuilding the loop, the brakes, and the verdict discipline
from scratch.

## Users

(Axis 2) kouko running long/AFK improvement sessions in Claude Code on
this machine (and eventually Codex hosts), over targets like: skill/rule
prose quality, doc stores, config tuning — anything with an articulable
"better". Constraint: weak-model executors must be safe inside the loop
(the repo's verified lesson: judgment-shaped prose dies on weak tiers;
verdict paths must be mechanical).

## Smallest End State

(Axis 3) One target-agnostic loop skeleton + adapter contract, proven by
exactly TWO adapters: (a) principles-improve-loop refactored to consume
the skeleton (extraction = deletion, lockstep tests keep honest), (b) one
new cheap target with a fully mechanical oracle. NOT in v1: goal-compiler
UX polish, oracle router as standalone skill, cross-family judge panels.

## Current State Evidence

- Forward: loop entry today is per-target Workflow JS —
  `.claude/workflows/principles-improve-loop.js` (860 lines) drives
  rounds; `.claude/workflows/principles-replay-matrix.js` (546) fans out
  headless replays.
- Reverse (SSOT/ownership): verdict logic lives in
  `loom-product-principles/scripts/improve_loop_verdict.py` (367) —
  compare/smoke/wordcap/plateau by CLI exit codes; already
  target-generic (consumes only seedId/pass).
- Error: brakes = plateau (`improve_loop_verdict.py:222-228`), word-cap
  (`:188-197`), one-invariant-per-round schema
  (`principles-improve-loop.js:252-273`), proposal-branch-never-push exit
  (`:613-656`).
- Data: seed inventory + held-out exclusion
  (`principles-improve-loop.js:98-110,747-752`); grade transcript
  persisted for human re-audit (`principles-replay-matrix.js:542`).
- Boundary (the trust gap): the grade courier is an LLM agent
  self-reporting script exit codes (`principles-replay-matrix.js:473-499`)
  — verdict LOGIC is LLM-free, verdict TRANSPORT is not. Known sibling:
  #595's seg2 lesson (sandbox-internal validators can't self-exec;
  the fix is a sandbox-external step).
- Extraction cost (measured): ~200-250 of ~1,400 core lines are
  target-bound; `improve_loop_verdict.py` reusable near-verbatim;
  hardest knots = replay prompt embedding skill-specific procedure
  (`principles-replay-matrix.js:334-345`), hardcoded ROOT (`:19`),
  dcg-stash revert coupling (`improve-loop.js:400`), commit scope
  (`:629`). No structural dead-ends found.
- Tests: 5 pytest files (~2,726 lines) assert on workflow text +
  `node --check` + extracted guard functions; dogfood runs at
  `docs/loom/dogfood/2026-07-11-l3-loop-smoke/` and `-run2/`.

## Alternatives Considered (Axis 4 — research-grounded)

Sweep A — shipped iteration architectures (EN+JA):
- Evaluator-optimizer (Anthropic pattern; Spring AI ships it) — judge =
  separate LLM call with explicit criteria; precondition "criteria clear,
  ideally machine-checkable". EN: anthropic.com/engineering/building-effective-agents
- AlphaEvolve / FunSearch (DeepMind, production) — judge = pure
  mechanical execution scoring; explicitly limited to auto-scorable
  domains. EN: deepmind.google/blog/alphaevolve-…
- DSPy GEPA (ICLR 2026; Shopify/Decagon production) — judge = metric fn
  + trace-reading diagnosis; small-model + GEPA ≈75x cheaper / ≈2x more
  reliable than single-prompt frontier. EN: dspy.ai/api/optimizers/GEPA/…,
  decagon.ai/blog/optimizing-gepa-for-production
- SWE-agent/OpenHands patch-verify — judge = tests re-run in a CLEAN
  environment; fail→pass only. EN: arxiv.org/pdf/2603.00575
- Producer-critic / クロスリフレクション (JA) — separated critic role,
  different model family recommended. JA: zenn.dev/loglass/articles/c7f4499ec8320b
Convergent principles: externalize the evaluation signal (mechanical
first); writer≠judge; stopping lives OUTSIDE the loop and reads progress
signals, not round counts. Known failures: intrinsic self-correction
degrades accuracy without external signal (Huang et al.); models read
consecutive failure as "try harder" not "wrong direction"; judges
themselves biased. EN/JA delta: JA contributes ops guardrails (triple
stop conditions, org-side kill responsibility), few original
architectures — a finding, echoed in sweeps below.

Sweep B — judge reliability:
- Self-preference bias is real, large (-38%..+90% swing on ArenaHard),
  and PERPLEXITY-rooted → fresh-context SAME-model judging cures
  anchoring but NOT self-preference; same-family judging inherits
  family-bias. EN: arXiv:2410.21819, arXiv:2508.06709; JA replication:
  tech.revcomm.co.jp (GPT-4o/Claude self-inflate; family-bias observed).
- Mitigation ranking: deterministic checks first > cross-family
  writer≠judge > small human calibration set (κ≥0.6 gate, JA) > PoLL
  panel of 3 diverse small judges (beats single frontier judge, ~7x
  cheaper; arXiv:2404.18796) > rubric anchoring > position-swap.
- Never: same-model self-grading; trusting judge scores with no human
  calibration ("reliability without validity", arXiv:2606.19544).

Sweep C — goal→criteria compilation & freezing:
- Shipped spec-first flows: GitHub Spec-Kit (spec.md as SSOT,
  [NEEDS CLARIFICATION] markers), AWS Kiro (EARS-syntax requirements →
  tasks with per-requirement traceback), eval-driven development
  (golden set + graders before build). EN: github.com/github/spec-kit,
  kiro.dev/docs/specs; JA original: 受け入れ駆動開発 (qiita/autotaker) —
  acceptance-scope.md per component.
- Criteria quality bar: executable / binary / independent; rubric rules:
  behavioral specificity + non-overlapping dimensions.
- Freezing (ImpossibleBench, arXiv:2510.20270): read-only test files
  REDUCE but do not eliminate gaming (agents shift to special-casing);
  HIDING criteria from the agent → near zero. Strong freeze = criteria
  outside the executor's visible domain. JA has no original literature
  on this axis (EN-only; itself a finding).

Sweep D — brakes & escalation:
- Shipped brake types: hard round caps (Ralph Wiggum, LangGraph
  recursion_limit=25); OpenHands Stuck Detector (same action+result
  4x / same action errors 3x / monologue 3+ / ping-pong 6+ →
  auto-terminate); tool-call fingerprint sliding window (MD5(tool+args)
  3+ in last 20 → warn+skip, arXiv:2603.05344); token budget gates the
  agent "cannot talk its way past" (Oracle); one-task-per-iteration with
  per-round commits (Ralph origin).
- Converge-vs-spin discriminator: "did the next attempt carry NEW
  information"; repeated failure 2-3x = change-course signal (industry
  threshold HARSHER than judgment-rubrics §4's prose); regression is
  also a change-course signal.
- Escalation: escape hatch written into the prompt CONTRACT (N rounds →
  blockers report, then stop; Ralph README); LangGraph interrupt()/
  resume; stop conditions must be judgeable by a CONTEXT-FREE external
  process (MindStudio). JA: kill-switch belongs to orchestration layer,
  not agent logic; multi-agent ping-pong real-world case (4 Discord
  agents, 50 posts/38min) fixed by 3-layer defense.

Rejected alternatives for v1:
- Adopt DSPy/GEPA wholesale — optimizes prompts against metrics, not
  arbitrary artifacts; Python-ecosystem harness alien to the
  skill/Workflow substrate; keep as inspiration (trace-reading feedback).
- Build on loom-pipeline — jurisdiction inversion: pipeline is a
  CLIENT of a general loop, not its home.
- LangGraph-style external framework — violates zero-infra/plugin-native
  substrate; the Workflow tool already provides deterministic
  orchestration with resume.

## Decision

Build ONE target-agnostic loop harness as (v1) a generic Workflow
skeleton + adapter contract + the four research-mandated disciplines
baked in:

1. **Adapter contract** (per target): executor (prompt+model), grader
   (command array + pass rule, exit-code only), seed/case source, edit
   surface (dir + allow-list), budget caps. Extracted from
   principles-improve-loop; that workflow becomes adapter #1 (extraction
   = deletion; its 5 pytest suites keep the refactor honest). Adapter #2
   = a new mechanical-oracle target proving generality.
2. **Criteria freeze**: goal compiled to a frozen criteria file BEFORE
   round 1 (Spec-Kit-style, executable/binary/independent bar);
   held-out/hidden checks stay harness-side per ImpossibleBench;
   criteria edits mid-loop require human ratification.
3. **Verdict trust**: keep verdict logic mechanical (exit codes); close
   the courier transport gap where cheap (grade transcript persisted —
   already done; sandbox-external re-exec where the host allows, same
   lane as #595's deferred CI-side arc — do NOT block v1 on it, disclose
   instead).
4. **Brakes as contract**: plateau + word-cap (existing) + port
   OpenHands-style stuck rules (same-grader-failure 3x, no-new-info
   rounds) into the generic verdict CLI + escape-hatch clause in the
   executor prompt (N rounds → blockers report). Stopping decisions
   readable by a context-free process (the verdict CLI itself).

NOT building in v1: standalone oracle-router skill (a selection table
inside the criteria-compiler step suffices); cross-family judge panel
(host Agent tool is single-family; note codex CLI as a conditional
upgrade path); LLM-judged rubric lanes beyond what adapter targets need.

## Out of Scope

- loom-pipeline integration (it may later consume the skeleton as a
  client; nothing in v1 depends on it).
- verify-before-ship / issue-first general skills (siblings from the
  general-workflow gap analysis; separate arcs).
- Cross-host (Codex) port of the Workflow substrate.
- Any auto-merge/auto-push exit — proposal branch + human gate stays.

## Open Questions

1. **Adapter #2 target — RESOLVED (user, 2026-07-23)**: wiki-lint
   auto-fix loop over the obsidian vault's `wiki/` — executor edits
   wiki pages, oracle = `obsidian:wiki-lint`'s 15 mechanical checks,
   convergence = violations → 0 or plateau; proposal-branch discipline
   applies since the edit surface is vault content. Fills wiki-lint's
   documented check-only gap.
2. **Judge-family diversity for future LLM-judged lanes** — DEFERRED to
   the first target that needs an LLM judge (v1 is mechanical-only):
   choose then between same-family multi-tier panel (in-host) vs codex
   CLI as a second family.

## Design constraints from supplementary research (2026-07-23 round 2)

Two additional bilingual sweeps (proposal-exit/review-gate products;
Goodhart/content-conservation in edit loops) yielded five binding
constraints:

1. **Structural scorecard, not prose** — the proposal's evidence leads
   with structural metrics (diff lines/files, touched-test-or-CI-files
   flag, grader exit status); agent narrative is decoration, not
   evidence (33,707-PR study: structure predicts review effort AUC
   0.957, PR prose ≈0.52). EN: arxiv.org/html/2601.00753v1
2. **Size circuit-breaker + proposal expiry** — oversized proposals
   auto-request splitting (Intercom: rejecting big PRs to force small
   ones is what made auto-approval safe); stale proposals expire
   (agent-ghosting is real, 0.9-10%). EN: intercom.com/blog/ai-is-
   approving-our-pull-requests…
3. **Safe/unsafe action tiering, fixed at design time** — port Ruff/
   ESLint's autofix doctrine: each repair action class is pre-classified
   (wiki case: retarget wikilink / add alias = safe, auto-run; delete
   line/section/entry = unsafe, proposal-only, never auto). Tiering
   hangs on the ACTION TYPE at loop-design time, never on the agent's
   runtime judgment (repo memory: judgment-prose dies on weak models).
   EN: docs.astral.sh/ruff/linter/
4. **Conservation ratchet + dual oracle** — per-round grader (visible
   subset) ≠ acceptance grader (full mechanical set + ratchet:
   content quantity/link count/heading count may not net-decrease
   without a flagged justification). Visible-only oracles are gamed
   (SpecBench: visible 97% / held-out 0%). EN: arxiv.org/html/2605.21384v1
5. **Reviewer-triggered evidence** — final verification runs are
   triggered by the review side, not self-attached by the proposer
   (Copilot's human-approved workflow runs; consistent with the
   courier-transport deferral in Decision 3). Output language of
   proposal summaries configurable (JA adoption evidence: unreadable
   evidence = no evidence).

Noted for honesty: a diff-budget mechanism (deletion lines ∝ repair
count) has NO mature public precedent in either language — if adopted
it is self-invented, flagged as such.

## What Becomes Obsolete

- `principles-improve-loop.js` / `principles-replay-matrix.js` current
  monolithic forms — refactored onto the skeleton in the same arc
  (extraction = deletion; tests updated in lockstep, not duplicated).
- The "L3 loop is principles-only" framing in their SKILL descriptions.

## loom-* integration map

goal-loop is general-workflow machinery; every loom plugin is a CLIENT
via adapters or shared discipline — never the other way around:

- **loom-product-principles**: adapter #1 (this arc, T5/T8) — its
  improve-loop becomes config + thin wrappers on the skeleton.
- **loom-spec**: natural adapter #3 candidate (post-v1) — mechanical
  oracle already exists (`validate_spec_output.py` + mint_critic
  freshness gate); a spec-draft quality loop is config-only work once
  v1 ships.
- **loom-code**: NOT a client for building new code — SDD's plan-driven
  task triads + TDD remain the lane for new features. Routing rule
  (goes in T4 SKILL.md): build-new = loom-code SDD; converge-existing-
  artifact-against-frozen-mechanical-criteria = goal-loop. Shared
  discipline both ways: gate markers' verified-by-real-run = the same
  evidence philosophy as reviewer-triggered verification.
- **loom-pipeline**: future client — batch mode may invoke goal-loop
  workflows as segments; STUCK blockers reports route to
  `docs/loom/BACKLOG.md` entries (its existing entry format).
- **loom-memory**: run lessons (adapter gotchas, threshold tunings)
  record via `loom-pipeline:loom-memory` per its jurisdiction table.
- **family-relay**: goal-loop's close-out report follows §(a)'s
  Close-out card; proposal-summary output language is adapter-
  configurable (JA adoption evidence: unreadable evidence = none).
- **Built-in `/goal`**: routing line in T4 SKILL.md — in-session,
  one-sentence goal, human present → `/goal`; AFK, artifact-set,
  mechanical oracle exists → goal-loop.

## Evidence appendix

Research transcripts: 4 web sweeps + 1 dissection, this session
(2026-07-23). Source URLs inline above; internal citations:
`.claude/workflows/principles-improve-loop.js`,
`.claude/workflows/principles-replay-matrix.js`,
`loom-product-principles/scripts/improve_loop_verdict.py`,
`loom-product-principles/scripts/check_seed_traceability.py`,
`loom-product-principles/scripts/validate_principles_output.py`,
`docs/loom/dogfood/2026-07-11-l3-loop-smoke/`, `-run2/loop-report.md`.
