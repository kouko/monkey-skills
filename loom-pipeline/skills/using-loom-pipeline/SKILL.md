---
name: using-loom-pipeline
description: |
  Drives the loom principles→design→spec→code pipeline end-to-end via
  deterministic Claude Code Workflow segments — one Workflow invocation per
  pipeline segment, never an inline hand-rolled orchestration. It is a thin
  conductor: judgment (verdicts, standards, gates) stays in the four station
  plugins (loom-product-principles, loom-interface-design, loom-spec,
  loom-code); this skill only sequences them and enforces the run-input
  contract. CONDITIONAL: fires only when both the Workflow tool is available
  in the host AND the four station plugins are installed — otherwise
  `loom-pipeline: N/A` with the reason, loudly. Codex hosts are N/A (Codex
  has no Workflow primitive; do not fake orchestration inline there).
  Triggers: "run the loom pipeline", "全管線", "全流程跑一遍",
  自動實作 this change, "drive principles through code", "run the conductor".
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher
already decided whether the pipeline conductor applies. Follow your dispatched
prompt directly — do not re-derive fire conditions or re-invoke Workflow
yourself.
</SUBAGENT-STOP>

# using-loom-pipeline — the thin conductor over the 4 station plugins

This skill is orchestration only. It never authors PRINCIPLES.md, DESIGN.md,
ui-flows.md, a spec draft, or code, and it never produces a verdict — those
stay with `loom-product-principles`, `loom-interface-design`, `loom-spec`,
and `loom-code`. Its entire job is: collect the run-input contract, resolve
the driver asset's absolute path, and invoke `Workflow({scriptPath})` once
per pipeline segment.

## §When it fires — BOTH conditions, checked first

1. **The Workflow tool is available** in this host (Claude Code exposes a
   `Workflow` primitive that accepts an arbitrary `scriptPath`).
2. **The four station plugins are installed**: `loom-product-principles`,
   `loom-interface-design`, `loom-spec`, `loom-code`.

Either condition false → emit **`loom-pipeline: N/A`** with the specific
reason (which condition failed) and stop. N/A is a first-class honest
outcome — **never silently skip, and never fake the orchestration inline**
(e.g. by hand-driving the four stations one Task/Skill call at a time and
presenting it as if the conductor ran). A faked run here reproduces exactly
the babysitting problem this plugin exists to remove.

**Codex hosts: N/A by definition.** Codex has no Workflow primitive (verified
against the plugin-components reference); this skill has no fallback path
for it. Report `loom-pipeline: N/A (no Workflow primitive on this host)` and
stop — do not attempt a shell-script substitute here (that is a parked,
separate re-trigger, not this skill's job).

## §Run inputs — the 6-field contract

Before invoking Workflow, collect exactly these fields. A missing required
field is a fail-loud stop, never an improvised default (except where a
default is explicitly stated below):

| Field | Required | Default | Notes |
|---|---|---|---|
| **change-id** | yes | none | Identifies the per-change folder (`docs/loom/<change-id>/`); loom-spec owns that layout — this skill only threads the id through. |
| **target project path** | yes | none | Absolute path to the consumer project the pipeline runs against. |
| **token budgets** | yes | run-level: host default budget cap; per-station: the driver's documented per-station defaults (`STATION_TOKEN_BUDGETS` in `driver_20_runstation.js`) | Canonical shape: `{ run: <number>, perStation: { <stationName>: <number>, ... } }`. `perStation` keys are station names (`principles`, `design`, `design-critic`, `spec`, `critic`, `validator`, `code`, `review`, `probe`) — omit a station's key to fall back to the driver's documented default for that station. Over-budget at either level is fail-loud inside the driver, never a silent continue. |
| **model policy** | yes | Claude default model tier for all stations | Which model tier each station runs on (Workflow's `model` param is Claude-family only — no cross-vendor judging in v1). |
| **resumeRunId** | no | none (fresh run) | Optional. Maps directly to Workflow's native `resumeFromRunId` — passing it resumes a previously checkpointed run instead of starting over. (Grounding: `scriptPath`/`resumeFromRunId` parameter names verified live — 2026-07-03 F5 dispatch spike run `wf_667ec006-ec2` and the same-day pipeline dogfood both exercised them against the real Workflow tool.) |
| **skillsRoot** | yes for runs that include segment 2 | none | Absolute path to the monkey-skills checkout / plugin source root — the orchestrator resolves it (e.g. the repo root of the loom plugins install/checkout). Segment 2 uses it to locate the loom-spec validator script; missing it is a fail-loud stop inside the driver, never a guessed path. |

## §Invocation — resolve the driver asset, one call per segment

The driver ships as a single self-contained asset at
`assets/loom-pipeline.js`, relative to this skill's own directory. Resolve
its **absolute** path from the base directory the host gives this skill (the
host provides "Base directory for this skill" — join it with
`skills/using-loom-pipeline/assets/loom-pipeline.js` if that base is the
plugin root, or `assets/loom-pipeline.js` if the base is already this
skill's own directory). Never hardcode a path guessed from the current
working directory — the asset must resolve correctly regardless of which
project the pipeline is driving.

Once resolved, invoke Workflow once per pipeline segment — never once for
the whole run:

```
Workflow({
  scriptPath: "<resolved absolute path to assets/loom-pipeline.js>",
  args: {
    segment: <1 | 2 | 3>,
    changeId: "<change-id>",
    projectPath: "<target project absolute path>",
    budgets: { run: <run-level cap>, perStation: { principles: <cap>, design: <cap>, "design-critic": <cap>, spec: <cap>, critic: <cap>, validator: <cap>, code: <cap>, review: <cap>, probe: <cap> } },
    models: { /* per-station or blanket model policy */ },
    skillsRoot: "<absolute path to the monkey-skills checkout — required for segment 2>",
    resumeRunId: "<optional — omit for a fresh run>"
  }
})
```

## §Segments — the 3-segment execution map

One `Workflow` invocation per segment, never one call for the whole run.
Segment names match the driver meta's phases (Principles + Design / Spec /
Code) — same vocabulary end to end so a paused run's segment number always
maps back to a station-plugin phase.

1. **Segment 1 — Principles + Design.** `loom-product-principles` drafts
   PRINCIPLES.md, then `loom-interface-design` drafts DESIGN.md +
   ui-flows.md, then the **design-critic panel**
   (`loom-interface-design:design-critic`) adversarially reviews the draft
   for surface omissions before the segment closes.
2. **Segment 2 — Spec.** `loom-spec:spec-expansion` fans the seed out into
   an OpenSpec-shape draft, the **completeness-critic** panel
   (`loom-spec:completeness-critic`) hunts omissions, then the **validator
   gate** (loom-spec's exit-0 binary validator) must pass before the
   segment closes.
3. **Segment 3 — Code.** `loom-code:subagent-driven-development` implements
   the spec task-by-task under the TDD iron law, then a **whole-branch
   review** (`loom-code:requesting-code-review`) covers the cumulative
   diff, then **ui-verify** (`loom-code:ui-verification`) exercises the
   running surface before the segment closes.

## §Human gates (between segments)

Exactly 4 gates. Each is a stop, not a notification — the conductor waits
for the human's answer before the next Workflow call.

(a) **Change-id minting** — before Segment 1. The human names the
    per-change folder (`docs/loom/<change-id>/`); the conductor never
    invents a change-id.

(b) **Product forks** — during any segment, whenever a station surfaces a
    genuine product decision (not an implementation detail). The
    conductor briefs it per the **#475 complex-fork escalation**
    (`dev-workflow:brief-before-asking`) instead of letting the station
    improvise a default — the same discipline #475 established for
    complex forks inside SDD applies here at the pipeline level.

(c) **Cost policy** — before each segment. The human confirms (or
    revises) the token budgets and model-tier policy for the segment
    about to run; a stale budget/model confirmation from a prior segment
    is never silently reused across a segment boundary.

(d) **Final merge** — after Segment 3. The pipeline **never merges**. The
    conductor's output is PR branches + the run ledger; a human takes it
    from there. This mirrors gate (b)'s stance: judgment-bearing actions
    are never automated inside the conductor.

## §Driver prohibitions

- The driver never edits station artifacts.
- The driver never produces verdicts.
- The driver never merges.

Judgment stays in the four station plugins (cross-plugin delegation contract)
— the conductor only orchestrates and records.

**Stable-prefix dispatch convention**: station preambles are
stable/cacheable; the per-change payload is appended, never prepended —
prepending would invalidate the cache on every dispatch.

## §Batch mode — freeze many changes, run the queue unattended

Batch mode moves every per-change human decision (gates (a) and (c)) to
**freeze time**, so a whole queue of changes runs Segment 3 unattended —
walk away, come back to N reviewable PR branches. Sequential only; a
parallel variant is parked (`loom-pipeline/README.md` §Parked items).

### Queue file — `docs/loom/QUEUE.toml`

Human-edited, in the target project, one `[[change]]` array-of-tables entry
per change, authored at freeze time:

```toml
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
models = { code = "sonnet", review = "sonnet" }
[change.budgets]
run = 200000
perStation = { code = 40000, review = 20000 }
```

Required: `id`, `plan` (project-relative path to the change's plan),
`budgets.run`. Optional: `budgets.perStation`, `models`.

### Intent vs. state — two files, two owners

`QUEUE.toml` is the human's **intent** — hand-edited at freeze time, never
machine-written. `docs/loom/queue-state.json` is the machine's **state** —
owned by `batch_queue.py` alone (records `RUNNING`/`DONE`/`FAILED`/`SKIPPED`
per change id), never hand-edited. Neither file writes the other.

### Freeze predicate

An entry is eligible for `next` only when the loom-spec validator exits 0
for `docs/loom/<id>/` **and** the plan is committed — the worktree branches
from HEAD, so an uncommitted plan is invisible to it and the entry is
SKIPPED with its just-created worktree torn down. No segment 2.5: freezing
happens interactively before queueing, never inside the unattended run.

### The dispatcher-only loop

The main agent repeats exactly this loop, one iteration per change, until
`next` prints `{"done": true}` or exits 3 (circuit-breaker HALT):

1. `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py next --project <projectPath> --skills-root <skillsRoot>`
2. `Workflow({scriptPath: "<resolved assets/loom-pipeline.js>", args: <the JSON stdout from step 1, verbatim>})`
3. `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py mark <id> done|failed --run-id <the Workflow run id>`

The main agent is **dispatcher-only**: it never parses the queue file, it
never composes git commands, and it never diagnoses failures mid-batch —
all of that is script-owned (`batch_queue.py`) or deferred to the
end-of-batch human report below.

### `next` exit codes

| Code | Meaning |
|---|---|
| 0 | dispatched an entry (Workflow args JSON on stdout), or the queue is done (`{"done": true}`) |
| 1 | fail-loud error (malformed `QUEUE.toml`, etc.) |
| 2 | argparse usage error |
| 3 | circuit-breaker HALT — 2 consecutive `FAILED` entries; `--override-halt` bypasses after human review |

### End of batch

`python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py status --project <projectPath>`
prints the one-screen report a fresh session reads first. A finished batch
of N changes leaves N ledgers at
`<projectPath>/docs/loom/<changeId>/pipeline-ledger.md` and N PR-ready
`loom/<id>` branches — merge stays human (gate (d) is unchanged by batch
mode).
