# Brief — loom-pipeline: the conductor plugin (2026-07-03)

> Brainstorming output (loom-code:brainstorming, 5-axis). Consumed by
> `writing-plans`. Inputs: F5 dispatch spike (this session), G1–G7 from
> `docs/loom/research/2026-07-03-pipeline-driver-industry-research.md`,
> F1–F5 from `docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md`,
> cross-plugin delegation contract (CLAUDE.md).

## Problem

When kouko wants a feature built end-to-end by the loom pipeline
(principles → design → spec → code), the only automated way is a
hand-written, session-local Workflow script that dies with the session
— every run means re-deriving the driver, re-learning its hardening
(F1–F5), and re-baking paths. The job to be done: **"run the proven
7-station pipeline against any consumer project, repeatably, without
babysitting each station, and without the driver improvising when
something is missing."** Reliability (no silent derail, no cost
blowup, honest verdicts) is the product; orchestration is the
mechanism.

## Users

kouko, solo dev, Claude Code on macOS, working in consumer repos where
the loom-* plugins are installed (marketplace source = this repo).
Invocation: interactive session (`/using-loom-pipeline` style entry) or
background job. NOT (v1): other-team distribution, Codex hosts (no
Workflow primitive — N/A-loud), fully-unattended autonomous runs.

## Smallest End State

A 5th thin plugin shipping exactly:

1. **One entry skill** (router + contract): collects run inputs
   (change-id, target project path, model/cost policy), resolves the
   driver script's absolute path from the skill's base path, and
   invokes `Workflow({scriptPath})` — one workflow invocation **per
   pipeline segment**, with human gates between segments.
2. **One driver script asset** — the dogfood driver's descendant with
   F1–F5 + the v1 gap subset baked in (see Decision). **Assembled, not
   hand-monolithic** (decision 2026-07-03, plan-review round-2
   escalation, user-approved): flat per-concern source modules under
   `loom-pipeline/scripts/` (header/guard/runStation/segments/ledger)
   concatenated by `scripts/build_driver.py` into the self-contained
   asset (Workflow scripts cannot import), with a rebuild-and-diff
   drift test — the same SSOT-and-functional-copy mechanism as
   loom-code's `distribute.py`. Atomic tasks per module; the built
   asset is generated-and-committed.
3. **Structural tests** for the script + skill prose (repo CI).

No agents of its own, no standards of its own, no gates of its own —
judgment stays in the four station plugins (delegation contract rule:
orchestration in pipeline, judgment in stations).

## Current State Evidence

- **Forward** (what will invoke this): user via entry skill; the
  Workflow tool accepts arbitrary `scriptPath` (F5 spike run
  `wf_667ec006-ec2` proved script-layer `agent()` + `agentType`
  dispatch works; plugin-native `workflows/` component does NOT exist —
  official plugin components exclude it, verified against
  code.claude.com/docs plugins-reference 2026-07-03).
- **Reverse** (what this calls): station skills
  `loom-product-principles:product-principles`,
  `loom-interface-design:{design-system,interaction-flows,design-critic}`,
  `loom-spec:{spec-expansion,completeness-critic}`, loom-code SDD roles
  as workflow `agentType` (`loom-code/agents/implementer.md`,
  `spec-reviewer.md`, `code-quality-reviewer.md`, `code-reviewer.md` —
  output contracts at code-reviewer.md §Output contract). SSOT
  direction: verdict enums + change-folder layout owned by stations;
  conductor consumes, never copies (CLAUDE.md §Cross-Plugin Delegation
  禁止 rules).
- **Error** (failure modes to design against): F1 prose-vs-structured
  output (pin StructuredOutput in dispatch), F2 transient API errors
  (per-station retry), F3 usage-limit freeze (journal resume), F4
  args-undefined silent derail (bake paths; input-contract guard:
  missing input → FAIL, never improvise), F5 no station sub-dispatch
  (panels/triads at script layer) — all from
  `docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md`. Plus
  G1–G7 (research doc §Seven gaps).
- **Data**: per-change folder `docs/loom/<change-id>/` (loom-spec
  owns layout); STATION result schema {verdict, artifacts,
  validator_exit, interventions[], summary} (dogfood driver, session
  `3f8c7086` `workflows/scripts/loom-pipeline-dogfood-wf_9e99b055-eb8.js`);
  workflow journal.jsonl for resume.
- **Boundary**: Workflow permission gate is separate from skill opt-in
  (docs); workflow `model` param limited to Claude family (G5
  cross-vendor judging out of reach); Codex has no Workflow primitive;
  station agents have Skill tool but no Agent tool (F5 spike).

## Alternatives Considered (settled earlier this session; cited, not reopened)

1. **Merge 4 plugins into one** — REJECTED 2026-07-02 (decision
   history: merge buys governance, ~zero capability; contracts decay
   into implicit coupling).
2. **Driver inside loom-code** — rejected in-session: conductor≠station;
   plugin boundary forces the conductor through public contracts (F4
   lesson: contracts must be structural, not self-discipline).
3. **`.claude/workflows/` repo-level** — rejected: does not travel to
   consumer repos; `~/.claude/workflows/` — personal, unversioned.
4. **Thin 5th plugin (chosen)** — asset + skill wrapper; industry
   analogue: Microsoft Conductor (deterministic orchestration as its
   own layer over agent stations).

## Decision

Build `loom-pipeline` (name pending sign-off; the keyword tag
`loom-pipeline` already groups the 4 station plugins — collision is
deliberate-or-renamed, see Open Questions) as the thin conductor
plugin. **Segmented execution with human gates is committed**: the
entry skill runs the pipeline as N sequential Workflow invocations
(segments), surfacing between segments exactly the human gates the
dogfood proved load-bearing — change-id minting, product decisions
(brief-per-#475 when a station surfaces a fork), cost policy, final
merge. Autonomous single-shot end-to-end mode is parked (re-trigger:
segmented mode stable across ≥3 real runs AND a decision-ledger
mechanism designed).

v1 bakes: F1–F5 (proven), G1 (run-level token budget via `budget`
primitive + **per-station token budgets, over-budget = fail-loud** +
wall-clock watchdog per station + rally cap ≤2 on critic↔writer
loop-backs + **change-strategy recovery ladder**: retry same →
re-ground with error context → fresh-context re-dispatch → escalate to
human — never blind same-strategy retries), G3 (every station's
artifact carries a validator-checked Decisions section), G6
(idempotent adopt-if-valid re-runs; journal resume; honest
"checkpointed, not durable" naming). Two dispatch conventions borrowed
from AEP (see
`docs/loom/research/2026-07-03-lessons-from-agentic-engineering-patterns.md`):
**stable-prefix dispatch** (station preambles stable/cacheable;
per-change payload appended, never prepended) and **driver-side
behavioral prohibitions stated verbatim in the entry skill** (the
driver never edits station artifacts, never produces verdicts, never
merges). v1 records-not-solves: G2 (critic false-positive rate as
ledger metric), G4 (verdict-distribution comparison protocol
documented for the Sonnet-vs-Fable A/B), G5 (per-judge verdicts in
ledger, aggregate in code). G7 (mutation-testing spot check) →
backlog, alongside AEP-sourced parks (git-commit dispatch lock for
multi-change parallelism; CHECK/ACT cheap-monitor as optional G6
watchdog implementation).

We will NOT build: our own review/verdict logic (stations own it), a
Codex driver variant, cross-vendor judging, an agents/ directory.

## Committed next (v1.1 — deliberately NOT in this plan)

**Batch implementation mode** (user requirement 2026-07-03, stated as
the metaphor 「白天討論規格、晚上自動實作」 — the capability wanted is
the general one, NOT time-of-day scheduling): after the user has
interactively discussed and FROZEN multiple changes (validator exit-0
+ plan written), a batch entry mode iterates segment 3 per queued
change (own worktree/branch, per-change pre-authorized budget, failure
isolates to its item) unattended — whenever invoked, foreground or
background. Interface afterwards = N ledgers + N PR branches; merge
stays human. Distinct from the parked full autopilot (agent-selected
work, continuous ticks) — human gates move to spec-freeze time, they
do not disappear. v1's segment-3-standalone design (`args.segment`,
no-merge prohibition, per-run budgets) is the enabling interface; v1.1
adds only the queue convention + the batch loop.

## Out of Scope

- Codex execution of the driver (N/A-loud note in README; parked
  re-trigger: real need to run full pipeline on Codex → shell variant
  over `codex exec`).
- Autonomous no-human-gate mode (parked, re-trigger above).
- Mutation-testing gate (G7) — backlog after v1.
- Cross-vendor judge panels (G5 full mitigation) — harness-gated.
- Any change to the four station plugins' contracts (consume as-is;
  gaps found during build route back as separate station PRs).

## What Becomes Obsolete

- The session-local dogfood driver script (session `3f8c7086`) — its
  learnings land in the asset; the script itself was never in-repo, so
  nothing to delete. The dogfood report's "driver requirements F1–F5"
  section flips from wishlist to implemented-reference (update its
  header note in the same change).
- Nothing else: purely-additive is acknowledged and justified — the
  driver was proven needed by dogfood ① before this plugin existed.

## Open Questions

1. **Name**: `loom-pipeline` collides with the existing family keyword
   tag (all 4 station plugin.jsons carry `"loom-pipeline"` in
   keywords). Options: keep (the conductor IS the pipeline; tag and
   plugin converge) vs `loom-conductor` (no collision, role-precise).
   → user sign-off.
2. **README languages**: loom-code ships 3 (en/ja/zh-TW); the other 3
   loom plugins ship 1. Follow the 3-sibling convention (1 README) for
   the new thin plugin unless told otherwise.
3. **Segment boundaries** (how many Workflow invocations per run):
   default 3 segments — [principles+design+critic] / [spec+critic] /
   [SDD+review+ui-verify] — mirrors where the dogfood's human
   interventions actually clustered; writing-plans may refine.
