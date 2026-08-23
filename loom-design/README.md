# loom-design

The **design-side** plugin of the loom suite: discovery → product
principles → interface design → spec, plus the pipeline conductor that
sequences them.

Its stations (`business-value`, `user-insights`, `product-principles`,
`design-system`, `interaction-flows`, `design-critic`, `spec-expansion`,
`completeness-critic`) author the artifacts; `using-loom-design` is the
one entry router over all four stations. The conductor half —
`using-loom-pipeline` — never authors an artifact and never produces a
verdict; it only sequences the design stations and `loom-code` through
the principles→design→spec→code pipeline, one deterministic `Workflow`
invocation per segment, stopping for the human at 4 fixed gates in
between. The discovery station (the problem-space entry, upstream of
principles) is v0.1 **interactive-only** — the conductor
does not drive it as a Workflow segment; pipeline runs still start at
principles.

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

Judgment stays in the four Workflow-driven stations and in the
discovery station, the fifth, interactive-only one; the conductor half
only orchestrates and records.

## Execution flow

Three `Workflow` invocations — one per segment, never one call for the
whole run — carry four of the five stations in order (principles →
interface-design → spec → code); the discovery station
sits upstream of principles and is v0.1 interactive-only, not a Workflow
segment. The human gates (a)–(d) sit around the three Workflow-driven
segments:

```mermaid
flowchart TD
    RH["SessionStart reception hook<br/>packaged family-reception contract"] -.->|awareness only, never auto-opens| CON
    INV["Explicit invocation<br/>'run the loom pipeline'"] --> CON
    CON["using-loom-pipeline conductor<br/>collects the 6-field run-input contract"]
    CON --> GAC["Gate (a) change-id minting<br/>Gate (c) cost policy"]
    GAC --> SEG1
    subgraph SEG1["Workflow segment 1 - Principles + Design"]
        PP["product-principles<br/>PRINCIPLES.md"] --> IXD["design-system + interaction-flows<br/>DESIGN.md + ui-flows.md + design-critic"]
    end
    SEG1 --> GC2["Gate (c) cost policy"] --> SEG2
    subgraph SEG2["Workflow segment 2 - Spec"]
        SPC["spec station<br/>spec-expansion + completeness-critic + validator gate"]
    end
    SEG2 --> GC3["Gate (c) cost policy"] --> SEG3
    subgraph SEG3["Workflow segment 3 - Code"]
        CODE["loom-code<br/>SDD build + whole-branch review + ui-verification"]
    end
    SEG3 --> GD["Gate (d) final merge<br/>output: PR branches + run ledger, human merges"]
    GB["Gate (b) product forks<br/>any segment, briefed to the human"] -.- SEG1 & SEG2 & SEG3
```

Each segment delegates all judgment (drafts, critic panels, verdicts,
validator/review gates) to its station; the on-ramp criteria the
reception hook injects live in the packaged
[`family-reception` contract](skills/using-loom-design/references/family-reception.md),
not here.

## Running the tests

Run each station's suite as its OWN pytest invocation:

```
python3 -m pytest loom-design/scripts/pipeline/
python3 -m pytest loom-design/scripts/interface/
python3 -m pytest loom-design/scripts/discovery/
python3 -m pytest loom-design/scripts/spec/
python3 -m pytest loom-design/scripts/principles/
```

`python3 -m pytest loom-design/scripts/` — the obvious whole-plugin form —
fails at collection with "import file mismatch". The station dirs ship
same-named test files (`test_marketplace_entry.py`, `test_plugin_manifest.py`,
`test_knowledge_triage.py`, `test_mint_critic_verdict.py`) and carry no
`__init__.py`, so pytest cannot tell the modules apart. `.github/workflows/
loom-siblings-ci.yml` runs them as separate jobs for the same reason.

## Install + requirements

Install from the monkey-skills marketplace like any other plugin.
`loom-design` and `loom-code` are independently installable: every design
station works interactively without `loom-code`. The full
`using-loom-pipeline` conductor is an optional composition feature and checks
for both plugins at entry; if `loom-code` is absent, it reports
`loom-design: N/A` with the reason and stops the whole conductor before any
segment runs.

When both plugins are installed, they compose only through public,
plugin-qualified skill names such as `loom-code:using-loom-code` and
project-owned `docs/loom/` artifacts. Neither plugin reads the other's
private `hooks/`, `skills/`, or `scripts/` paths.

Conductor requirements, checked before that entry skill fires:

- Both station plugins are installed: `loom-design` and `loom-code`. The
  conductor uses `loom-code`'s public plugin-qualified agents and skills — for
  example `loom-code:implementer`, `loom-code:spec-reviewer`,
  `loom-code:requesting-code-review`, and `loom-code:ui-verification`. Their
  independent installation guarantee applies to interactive stations, not to
  a partial conductor run. (The discovery station, inside `loom-design`, sits
  upstream of principles and is v0.1 interactive-only — not required by the
  conductor and never driven as a Workflow segment.)
- A Claude Code host that exposes the **Workflow** primitive (a tool
  accepting an arbitrary `scriptPath`). No Workflow tool → the skill
  reports `loom-design: N/A` with the reason and stops; it never
  fakes the orchestration by hand-driving the stations one call at a
  time.

The shared family-policy source lives at
`scripts/canonical/loom-family/` in this repository. Regenerate the packaged
copies with `python3 scripts/sync_loom_family_contracts.py`; use `--check` in
CI. Verify independent installs and their optional composition with
`python3 -m pytest scripts/test_loom_plugin_install_layout.py
scripts/test_loom_plugin_composition.py -q`.

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
`loom-design: N/A (no Workflow primitive on this host)` and stop; do
not attempt an inline substitute. Every loom station (including
discovery) remains usable on Codex — run them interactively, one
station at a time, instead of through this conductor.

## Family entries & naming convention

> **要用 loom-X, 就從 using-loom-X 開始.** Each family entry point is a
> `using-loom-*` skill — start there, it routes you the rest of the way.
> (`loom-design` carries two: `using-loom-design` for the design stations,
> `using-loom-pipeline` for the conductor.)

| Name pattern | Role | Examples |
|---|---|---|
| `using-loom-*` | **Entry** — a family-routing skill. Fires on vague/goal-shaped asks, checks the on-ramp criteria, hands off to the right station. | `using-loom-design`, `using-loom-code`, `using-loom-pipeline` |
| plain artifact names | **Stations** — tuned to fire on direct, specific asks for their own artifact, without needing the entry skill first. | `business-value`, `user-insights`, `product-principles`, `design-system`, `interaction-flows`, `design-critic`, `spec-expansion`, `completeness-critic` |

`brainstorming` is loom-code's **discovery** skill, not an artifact
station — it explores intent before a brief exists, which is why
`using-loom-code` carries no duplicate `§Intake` heading of its own:
loom-code's family-entry intake work (steps 1–2, upstream/station
checks) already lives inside brainstorming as its **Axis 0**, run
before Axis 1. Giving `using-loom-code` a second, parallel `§Intake`
section would duplicate that check rather than reuse it, so the five
other entries carry `§Intake` and `using-loom-code` instead points into
brainstorming's Axis 0.

**Reception**: a `SessionStart` hook
([`family-reception`](skills/using-loom-design/references/family-reception.md)) injects the family map and
the on-ramp criteria table (the SSOT every `§Intake`/Axis 0 references)
at the start of every session. The **Workflow door remains
explicit-invocation only** — reception only describes it for awareness,
it never auto-opens the full pipeline run.

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

## Batch mode (v1.1)

A queue of **FROZEN** changes (change-folder form: spec-station validator
exit-0; or brief+plan form: reviewer-PASSed plan — plan committed
either way) feeds an unattended segment-3 loop, one queued item at a
time, each in its own worktree/branch with its own pre-authorized
budget. Explicitly **time-agnostic** — no scheduler required; it runs
whenever invoked, foreground or background. Human gates move to
spec-freeze time (queue-entry authoring), they do not disappear —
merge stays human, and this is distinct from the parked full-autopilot
mode below.

**Intent/state separation**: the human-edited queue file
(`docs/loom/QUEUE.toml` in the target project, array-of-tables
`[[change]]` — `id` / `plan` / `budgets.run` / optional
`budgets.perStation` / optional `models`) is never written by the
tooling. Machine-owned state (`docs/loom/queue-state.json`) records
each entry's status (`QUEUED` / `RUNNING` / `DONE` / `FAILED` /
`SKIPPED`) and is written only by `batch_queue.py`.

**The loop** — `loom-design/scripts/pipeline/batch_queue.py`, pure stdlib,
sequential-only:

1. `batch_queue.py next --project <path> --skills-root <path>` picks
   the first `QUEUED` entry, checks the freeze predicate (change-folder
   form: validator exit-0; or brief+plan form: the plan carries a
   reviewer PASS line — plan committed either way), creates its
   worktree/branch, records
   `RUNNING`, and prints one JSON object with ready-to-use `Workflow`
   args (`{segment: 3, changeId, projectPath, planPath, budgets,
   models, skillsRoot, branch}`). Empty/exhausted queue prints
   `{"done": true}` and exits 0.
2. The main agent calls `Workflow(segment: 3, ...)` with exactly that
   JSON — it never parses the queue file, never composes git commands,
   never diagnoses failures mid-batch.
3. `batch_queue.py mark <change-id> done|failed --project <path>
   [--run-id <id>] [--reason <text>]` writes the outcome back to state.
4. Repeat from step 1.

**Failure isolation**: an ineligible entry (freeze predicate fails, or
its plan never got committed to the worktree) is marked `SKIPPED` with
a reason and the loop advances — one bad entry never stalls the queue.
2 consecutive `FAILED` entries trip a circuit breaker: `next` exits 3
with a HALT message naming both ids (`--override-halt` bypasses).
`batch_queue.py status --project <path>` prints a one-screen overview
(id, effective status, runId, reason) — the first thing a fresh
session reads to take over a batch.

Output is N ledgers + N `loom/<id>` PR branches; merge stays human.

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
