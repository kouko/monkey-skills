# Phase 2 loop — execution-only redesign (compose loom-pipeline batch mode)

Supersedes `docs/loom/specs/2026-07-11-u1-nightly-phase2-loop.md` (never
committed — deleted as part of this brief; see Current State Evidence).

## Problem

The dbt-wiki quality campaign's Phase 2 backlog
(`docs/dbt-wiki-quality-campaign.md`, items B1-B14) is a queue of low-risk,
mechanical engineering fixes. The job to be done: let this class of backlog
work get executed on a schedule, without kouko driving each item by hand,
**without duplicating queue/state/circuit-breaker/branch-isolation machinery
that `loom-pipeline`'s batch mode (`loom-pipeline/scripts/batch_queue.py`)
already builds and actively maintains**, and without letting an unattended
run brainstorm or plan on its own — only execute work a human has already
reviewed.

This reframes the original U1 brief in two ways this session settled:

1. **Compose, don't duplicate.** U1's own Decision said "compose existing
   primitives," but its Alternatives Considered only researched external
   industry sources — it missed that `loom-pipeline` v1.1 batch mode
   (`docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md`, shipped
   2026-07-03, **before** U1's own spec date) already solves the queue,
   state-tracking, circuit-breaker, and branch-isolation pieces U1 was
   building bespoke — and has since been hardened twice more (0.9.0
   2026-07-18 `reconcile`/`mark-running`/`SUSPECT` recovery; 0.10.0
   2026-07-21 terminal-mark precursor guard) specifically against the
   failure mode U1's own risk assessment named: "reviewer subagents
   silently getting stuck or dying mid-run... an unattended loop has no
   human to catch that."
2. **Split by review status, not by clock time.** The original U1 framing
   ("nightly") conflated two independent things: whether a plan has been
   human-reviewed (frozen), and what triggers the automated run (a nightly
   schedule was one example trigger, not a requirement). This brief
   separates them into a **regulatory/planning stage** (brainstorming →
   writing-plans → reviewer PASS — interactive, any time, unchanged from
   how kouko already works) and an **execution stage** (scheduled/
   unattended — `loom-pipeline` batch mode's `segment 3`, only ever
   dispatched against an already-frozen plan). Naming and file paths drop
   "nightly" accordingly (see Decision).

## Users

kouko, sole maintainer. Planning-stage work stays synchronous/interactive
(unchanged habit — brainstorm + plan a Phase 2 item in a normal session,
same as W1/G1 this session). Execution-stage work runs via the platform's
scheduling capability (`CronCreate` / `/schedule`), triggered independent of
whether kouko is present — kouko's own firm constraint carried from U1
still holds: an unattended run must never silently ship something broken,
drain unbounded budget, or expand its own scope beyond what was explicitly
approved.

## Smallest End State

Compose `loom-pipeline/scripts/batch_queue.py` directly; add only the
project-specific pieces it doesn't provide (kill switch, scope guard,
campaign-doc queue-entry authoring, campaign-doc journal narration).

- **Queue of record for planning** stays
  `docs/dbt-wiki-quality-campaign.md`'s Phase 2 checklist — kouko keeps
  checking off `- [ ] B<n>: ...` by hand as items get planned, same habit
  as today.
- **Queue of record for execution** is `docs/loom/QUEUE.toml` +
  `docs/loom/queue-state.json` (batch mode's own convention — neither file
  exists yet in this repo; this is the first real consumer). A Phase 2
  item only enters `QUEUE.toml` once its plan has been written and passed
  `Plan-document-reviewer verdict: PASS` (batch mode's Form A/B freeze
  predicate, `check_frozen` at `loom-pipeline/scripts/batch_queue.py:241`
  — unchanged, still the hard gate).
- **Planning-stage helper**: `propose_queue_entry(item_id, plan_path,
  campaign_doc_path) -> QueueEntryDraft` — repurposed from the existing
  `backlog_parser.py`'s `parse_next_backlog_item`. Validates the target
  plan file already carries the `Plan-document-reviewer verdict: PASS`
  line (fail loud, mirroring `batch_queue.py`'s own no-improvised-defaults
  stance, if not) and drafts the `[[change]]` TOML block (`id`, `plan`,
  `budgets.run`). Run by hand or by an agent during the planning-stage
  session — never by the unattended execution stage.
- **Execution-stage routine** (`scripts/phase2-loop/ROUTINE.md`,
  renamed from the drafted `NIGHTLY-ROUTINE.md`): kill switch → `batch_queue.py
  reconcile` → `batch_queue.py next` (freeze predicate + circuit breaker
  both enforced inside `next`) → scope guard on the picked item → dispatch
  `Workflow()` for segment 3 (loom-code SDD only — no brainstorm/plan at
  this stage) → `batch_queue.py mark-running` immediately after `Workflow()`
  returns → on completion, `batch_queue.py mark done|failed` → one
  campaign-journal line. **Unattended-context escalation ceiling**: reuse
  `loom-code/skills/using-loom-code/references/continuous-mode.md`'s
  existing "no human pumping → hand back slack one round earlier" halt
  discipline (added 0.34.0, 2026-07-18) rather than inventing a new
  threshold — this repo has no `docs/loom/PRINCIPLES.md` `escalation
  appetite` entry, so the pipeline's default ask-threshold still applies;
  continuous-mode's earlier-halt precedent is the existing, documented
  answer for "runs without a human present," not a gap to fill bespoke.
- **Kill switch**: unchanged mechanism, renamed sentinel —
  `docs/loom/PHASE2_LOOP_PAUSED` (was `docs/loom/NIGHTLY_PAUSED`). Routine
  only ever reads it.
- **Scope guard**: unchanged (`requires_real_agent_surface`) — still refuses
  any item that mentions the real-headless-agent eval surface, fail-closed
  toward a human on ambiguity.
- **Branch/worktree isolation**: no longer a project concern —
  `batch_queue.py`'s `ensure_worktree` already isolates every queue entry
  into its own `loom/<change_id>` branch + worktree. The original U1
  `assert_safe_target_branch` and its "shared rolling branch" design (and
  its own unresolved Open Question about rolling-vs-dated branches)
  become dead code — see What Becomes Obsolete.
- **Budget breaker**: batch mode's own per-entry `budgets.run` TOML field
  (set explicitly when authoring the `QUEUE.toml` entry, never left at a
  platform default) plus the existing circuit breaker (`next` HALTs after
  2 consecutive FAILED terminal entries) — no custom cross-run tracker.

## Current State Evidence

- **Forward** (already committed on this branch, `feat/u1-nightly-phase2-loop`):
  `scripts/nightly-phase2-loop/backlog_parser.py` (`parse_next_backlog_item`,
  commit `ea6b5326`), `scripts/nightly-phase2-loop/safety_gates.py`
  (`is_nightly_paused` / `requires_real_agent_surface` /
  `assert_safe_target_branch`, commit `4c5e7d86`),
  `scripts/nightly-phase2-loop/journal_writer.py` (`append_journal_line`,
  commit `4aa596c6`). Drafted but uncommitted (untracked, deleted by this
  brief): `scripts/nightly-phase2-loop/NIGHTLY-ROUTINE.md`,
  `scripts/nightly-phase2-loop/test_nightly_routine_doc.py`.
- **Reverse** (the SSOT this composes): `loom-pipeline/scripts/batch_queue.py`
  — `check_frozen` (freeze predicate, line 241), `_classify_running_entry`
  (reconcile's stuck/dead-run classification, lines 643-702),
  `_read_wf_terminal_status` (opportunistic wf-record reader, line 575),
  `_describe_non_terminal_entry` (line 1060). Design docs:
  `docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md` (original
  decision), `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md`
  §4c (0.9.0 reconcile design). `loom-pipeline/CHANGELOG.md` 0.9.0
  (2026-07-18) / 0.10.0 (2026-07-21).
- **Error/Boundary**: `loom-code/skills/subagent-driven-development/SKILL.md`
  lines 34/128 — the escalation-appetite read from a target repo's
  `docs/loom/PRINCIPLES.md` `## Engineering Principles` section; absent in
  this repo (confirmed: no `docs/loom/PRINCIPLES.md` file exists), so the
  default ask-threshold applies. `loom-code/hooks/ask-triage.py` — advisory
  only, never blocks an `AskUserQuestion` call, confirmed by reading the
  hook body (always exits 0/allow).
  `loom-code/skills/using-loom-code/references/continuous-mode.md` — the
  existing "earlier halt, no human pumping" precedent (0.34.0, 2026-07-18)
  this brief points the execution-stage routine at instead of inventing a
  new threshold.
- **Data**: `docs/dbt-wiki-quality-campaign.md`'s Phase 2 checklist +
  `## Journal` section (existing read/write site, unchanged). Confirmed
  absent in this repo: `docs/loom/QUEUE.toml`, `docs/loom/queue-state.json`,
  `docs/loom/PRINCIPLES.md` — this is the first real consumer of batch mode
  in this repo; `QUEUE.toml` needs to be created (empty `[[change]]` array
  is valid) as part of this work, not assumed pre-existing.

## Decision

Repurpose the two still-useful pieces already committed
(`safety_gates.py`'s kill switch + scope guard; a narrowed
`journal_writer.py` invoked as a post-`mark` narration step), retire the
dead-weight piece (`assert_safe_target_branch` — worktree isolation
supersedes it), turn `backlog_parser.py` into a planning-stage
`propose_queue_entry` helper, and fully rewrite the routine doc around
`batch_queue.py`'s `reconcile → next → mark-running → mark` cycle instead
of an unattended brainstorm→plan→SDD cycle. Rename away from "nightly"
throughout (folder, routine doc, sentinel file) since the clock-time
framing was never the actual design constraint.

We will NOT build: a custom queue/state file, a custom circuit breaker, a
custom worktree/branch-isolation scheme, or a custom escalation-appetite
override — all four already exist and are actively maintained upstream.

## Out of Scope

- The real-headless-agent eval loop (W1/G1/G2/G3's `claude -p` real
  validation runs) — stays manual/session-driven; the scope guard still
  refuses any backlog item that would require it.
- G1's remaining dimensions (dialect, scale) and G2/G3 — unrelated.
- Auto-merge / auto-PR — `batch_queue.py`'s own model stops at a commit on
  the isolated branch; a human merges, per the campaign doc's existing
  weekly-batch rhythm. `git-guard.py` 0.36.0's disguised-push detection is
  an existing defense-in-depth layer here, not something this brief adds.
- Any change to Phase 2's own backlog CONTENT (B1-B14's descriptions).
- Writing a `docs/loom/PRINCIPLES.md` `escalation appetite` entry for this
  repo generally — out of scope for this specific loop; the execution
  routine instead points at `continuous-mode.md`'s existing precedent
  (see Smallest End State).
- Cross-run dollar aggregation beyond `batch_queue.py`'s own per-entry
  `budgets.run` field — still speculative infrastructure for a
  mechanical-fix-only loop.

## What Becomes Obsolete

- `docs/loom/specs/2026-07-11-u1-nightly-phase2-loop.md` and
  `docs/loom/plans/2026-07-11-u1-nightly-phase2-loop.md` — never committed;
  deleted by this brief (fully superseded, not left as a stale parallel
  spec).
- `scripts/nightly-phase2-loop/NIGHTLY-ROUTINE.md` and
  `scripts/nightly-phase2-loop/test_nightly_routine_doc.py` — drafted,
  never committed; deleted (replaced by `scripts/phase2-loop/ROUTINE.md`
  and its test, written fresh by `writing-plans`/SDD against this brief).
- `safety_gates.py`'s `assert_safe_target_branch` (+ its test) — dead code
  once execution moves to `batch_queue.py`'s per-item worktree isolation;
  remove in the same change that repurposes the rest of the module.
- The "shared rolling `nightly/phase2-burndown` branch" design and its
  associated Open Question from the U1 spec — resolved by batch mode's
  `loom/<change_id>` per-item branch/worktree convention; nothing to decide.
- The "nightly" naming across the surface (`scripts/nightly-phase2-loop/`
  → `scripts/phase2-loop/`, `NIGHTLY-ROUTINE.md` → `ROUTINE.md`,
  `docs/loom/NIGHTLY_PAUSED` → `docs/loom/PHASE2_LOOP_PAUSED`) — the
  clock-time framing this replaces.

## Open Questions

- `propose_queue_entry`'s exact validation strictness (fail loud on a
  missing `Plan-document-reviewer verdict: PASS` line, mirroring
  `batch_queue.py`'s own house style) vs. trusting the caller — leaning
  fail-loud; `writing-plans`/the implementer should confirm against
  `batch_queue.py`'s existing `_fail`/`QueueError` conventions rather than
  inventing a different error shape for the same class of problem.
- Whether `docs/loom/QUEUE.toml` should be seeded with a first real entry
  as part of this change (proving the wire-up end-to-end against a real
  Phase 2 item) or left empty and proven separately in a follow-up session
  — recommend proving it end-to-end in the same change, since an
  unexercised integration is the exact kind of thing this whole
  re-evaluation was trying to avoid; `writing-plans` should scope one task
  to pick the current first-unchecked Phase 2 item, run it through
  planning stage for real, and seed `QUEUE.toml` with that one entry.
