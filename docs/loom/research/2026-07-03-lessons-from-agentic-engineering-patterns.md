# Lessons from agentic-engineering-patterns (AEP) — borrowed vs rejected (2026-07-03)

> Comparative decision doc for loom-pipeline, in the style of AEP's own
> `lessons-from-gsd.md`. Source: github.com/memorysaver/agentic-engineering-patterns
> (v2.5.0, 2026-06-27), surveyed 2026-07-03. AEP is an independent
> convergence on the same problem space — a Claude Code plugin driving
> concept→MVP via staged agents, built on the same Workflow tool and
> `agent()/parallel()/pipeline()` primitives loom-pipeline will use.

## Independent convergences (mutual corroboration, no action)

- Generator/evaluator separation with generator-writable fields
  whitelisted — ≙ loom's writer≠judge + evaluator-never-modifies rule.
- Communication only via structured artifacts, never peer agent chat —
  ≙ loom's file-artifact handoff + verdict enums.
- Deterministic harness authored as code; multi-agent flexibility
  expressed as a fixed JS script, not free-form chat — ≙ the conductor
  design. AEP's philosophy note "every component in a harness encodes
  an assumption about what the model can't do" ≙ our
  rigidity-is-a-current-model-bet caveat (research doc, bitter-lesson).
- Small retry ceilings + human escalation triggers enumerated precisely.
- AEP killed its own "claude-team" mechanism over silent spawn
  failures and false liveness — same failure family as our F5/dogfood
  findings; validates fail-loud liveness checks.

## Borrowed into loom-pipeline v1 (brief amended same-day)

1. **Change-strategy recovery ladder** (AEP: same-fix → re-ground →
   fresh generator → decompose → escalate-to-human, capped at 5) —
   upgrades our blind per-station retry ×2 into an escalating ladder.
   Folded into G1 handling.
2. **Per-station token budgets** (AEP publishes concrete numbers:
   ~50K/story build, ~10K/eval) — one level finer than our run-level
   budget; station over-budget = fail-loud, not silent overrun.
3. **Stable-prefix dispatch convention** (AEP context assembly: shared
   cacheable prefix + story-specific payload + retrieval instructions)
   — formalizes what our dogfood already did ad hoc (append-not-prepend
   to preserve cache). Driver rule: station preambles are stable;
   per-change payload appends.
4. **Explicit driver-side behavioral prohibitions** (AEP forbids its
   orchestrator from reading worker code / merging / writing eval
   responses, even though it technically could) — loom-pipeline's entry
   skill states verbatim: the driver never edits station artifacts,
   never produces verdicts, never merges. Structural isolation (plugin
   boundary) + written prohibition, both.

## Rejected / parked (with reasons)

- **Autopilot / continuous dispatch loop** (tick state machine, story
  scoring formula, backlog-driven) — this is exactly loom-pipeline's
  parked autonomous mode. AEP proves feasibility AND fragility (their
  own claude-team removal; tick locks; liveness probes). Park stands;
  re-trigger unchanged (segmented mode stable ≥3 real runs + decision
  ledger designed).
- **1–5 dimension scoring verdicts with hard thresholds** — different
  bet than our two-valued no-bare-PASS scheme. Ours optimizes against
  unconditional-completeness claims; theirs against coarse labels.
  Not adopted; revisit only if the G4 verdict-distribution A/B shows
  our scheme inflating.
- **Executor abstraction (Claude Code/Codex/tmux)** — solves a
  portability problem we deliberately parked (Codex has no Workflow
  primitive; loom stations already run interactively on Codex).
- **Readiness-score routing** (graded 0–1 spec-quality score routes
  refine-vs-launch) — our validator exit-0 binary gate is simpler and
  already proven; graded routing is speculative for us.
- **Git-commit dispatch lock** (commit `in_progress` before workspace
  creation as a filesystem mutex) — elegant; only needed when multiple
  changes run in parallel. Backlog, re-trigger: multi-change
  parallelism lands on the roadmap.
- **CHECK/ACT split with a cheap code-blind monitor agent** — candidate
  implementation detail for the G6 watchdog, not a v1 requirement.
  Noted in backlog.

## Caveat

AEP's v2 roadmap items (Capability Map, full ORCA object modeling,
Outcome Contract) are self-marked not-yet-implemented; borrowings above
were taken only from shipped, documented mechanisms.
