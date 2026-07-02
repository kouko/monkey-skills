# loom-pipeline

The **conductor** plugin for the loom suite. It never authors an
artifact and never produces a verdict — it only sequences the four
station plugins (`loom-product-principles`, `loom-interface-design`,
`loom-spec`, `loom-code`) through the principles→design→spec→code
pipeline, one deterministic `Workflow` invocation per segment, and
stops for the human at 4 fixed gates in between.

## What it is — the human, plus a 3-layer execution stack

```
 Human — decision authority: between-segment gates (a-d);
         each gate is a stop, not a notification
   |
   v
+------------------------------------------------------------+
| Main session  supervisor — collects the run-input          |
|               contract, resolves the driver asset path,    |
|               reports segment results and gate prompts     |
+------------------------------------------------------------+
| Workflow      deterministic skeleton — one invocation      |
| script        per segment (assets/loom-pipeline.js);       |
|               never edits artifacts, never verdicts,       |
|               never merges                                 |
+------------------------------------------------------------+
| Station       judgment — principles / design / spec / code |
| agents        + their critics and reviewers, each owning   |
|               its own standards and gates                  |
+------------------------------------------------------------+
```

Judgment stays in the four station plugins (cross-plugin delegation
contract, repo `CLAUDE.md`); this plugin only orchestrates and
records.

## Install + requirements

Install from the monkey-skills marketplace like any other plugin.
Requirements, checked before the entry skill fires:

- All four station plugins installed: `loom-product-principles`,
  `loom-interface-design`, `loom-spec`, `loom-code`.
- A Claude Code host that exposes the **Workflow** primitive (a tool
  accepting an arbitrary `scriptPath`). No Workflow tool → the skill
  reports `loom-pipeline: N/A` with the reason and stops; it never
  fakes the orchestration by hand-driving the stations one call at a
  time.

## Run inputs

The driver takes a 6-field run-input contract: **change-id**, **target
project path**, **token budgets** (`{ run: <number>, perStation: {
<stationName>: <number>, ... } }`), **model policy**, **skillsRoot**
(required once a run includes segment 2), and an optional
**resumeRunId** to resume a checkpointed run instead of starting over.

`skills/using-loom-pipeline/SKILL.md` §Run inputs is the authoritative
definition (field names, defaults, fail-loud rules) — this README only
summarizes it; do not let this section drift from that table.

## Human gates

Exactly 4 stops between segments — each waits for the human's answer
before the next `Workflow` call:

(a) **Change-id minting** — before Segment 1; the human names the
    per-change folder, the conductor never invents one.
(b) **Product forks** — whenever a station surfaces a genuine product
    decision; briefed per the #475 complex-fork escalation instead of
    letting the station improvise a default.
(c) **Cost policy** — before each segment; the human confirms or
    revises the token budgets and model-tier policy for the segment
    about to run.
(d) **Final merge** — after Segment 3; the pipeline never merges — its
    output is PR branches + the run ledger, and a human takes it from
    there.

## Codex hosts: N/A

The driver requires the Workflow primitive, which Codex does not
expose. On Codex this plugin is **N/A by definition** — report
`loom-pipeline: N/A (no Workflow primitive on this host)` and stop; do
not attempt an inline substitute. The four station plugins remain
usable on Codex — run them interactively, one station at a time,
instead of through this conductor.

## G4 — Sonnet-vs-Fable gate A/B (open question)

v1 **records, not solves** G4: a documented **verdict-distribution comparison**
protocol, not an automated gate. Before trusting a cheaper judge tier
(e.g. Fable) as the default reviewer/critic model for a station, run
the same branch's review or critique through both model tiers and
compare:

1. **Verdict tokens** — do the two tiers land on the same
   PASS / PASS_WITH_NOTES / NEEDS_REVISION (or equivalent) verdict for
   the same artifact?
2. **Finding severity distributions** — do the two tiers surface
   findings at comparable severity (fatal / should-fix / nit) rates,
   or does the cheaper tier systematically under- or over-flag?
3. **A human review baseline** — compare both tiers' output against a
   human's own review of the same branch, not just against each
   other, since two cheap judges can agree and both be wrong.

Run this comparison before switching a station's default judge model
to a cheaper tier; a single anecdotal run is not sufficient evidence.

## Committed next (v1.1): batch implementation mode

Not in v1. A queue of **FROZEN** change-folders (validator exit-0 +
plan written) feeds a batch entry mode that iterates Segment 3 per
queued item — each its own worktree/branch, its own pre-authorized
budget, and a failure isolates to its own item rather than stalling
the queue. Output is N ledgers + N PR branches; merge stays human.
Explicitly **time-agnostic** — no scheduler required; it runs whenever
invoked, foreground or background. This is distinct from the parked
full-autopilot mode below: batch mode's human gates move to
spec-freeze time, they do not disappear.

## Parked items (with re-triggers)

- **Full autopilot** (agent-selected work, continuous ticks, no human
  gates) — parked. Re-trigger: segmented mode stable across ≥3 real
  runs AND a decision-ledger mechanism designed.
- **Codex shell driver via `codex exec`** — parked. Re-trigger: a real need to run the full pipeline on Codex arises.
- **git-commit dispatch lock** (for multi-change parallelism) —
  parked. Re-trigger: multi-change parallelism lands on the roadmap.
- **CHECK/ACT cheap-monitor watchdog implementation** (an optional
  richer alternative to the baked-in wall-clock watchdog) — parked.
  Re-trigger: the G6 watchdog proves insufficient in live runs.
- **G7 mutation-testing spot-check gate** — parked. Re-trigger: post-v1 backlog pickup.

## License

MIT.
