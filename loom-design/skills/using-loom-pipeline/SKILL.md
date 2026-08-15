---
name: using-loom-pipeline
# firing-evidence: 2026-07-14 baseline 4/4 EXACT (docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md)
description: >-
  Drives the loom principles→design→spec→code pipeline end-to-end via
  deterministic Claude Code Workflow segments. Use when asked to run the
  whole pipeline or to auto-implement a change from principles through
  code. CONDITIONAL: fires only when the Workflow tool is available AND
  the four station plugins are installed — otherwise `loom-pipeline: N/A`
  with the reason, loudly (Codex hosts are N/A). Triggers: "run the loom
  pipeline", "全管線", "全流程跑一遍", 自動實作, "run the conductor".
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher
already decided whether the pipeline conductor applies. Follow your dispatched
prompt directly — do not re-derive fire conditions or re-invoke Workflow
yourself.
</SUBAGENT-STOP>

# using-loom-pipeline — the thin conductor over 4 of the 5 loom station plugins

This skill is orchestration only. It never authors PRINCIPLES.md, DESIGN.md,
ui-flows.md, a spec draft, or code, and it never produces a verdict — those
stay with `loom-product-principles`, `loom-interface-design`, `loom-spec`,
and `loom-code`. Its entire job is: collect the run-input contract, resolve
the driver asset's absolute path, and invoke `Workflow({scriptPath})` once
per pipeline segment.

## §Intake

Run these three steps first, once per dispatch, before `§When it fires`
below gates on this skill's own two orchestration conditions.

1. **前站檢查 (upstream check)** — check the target repo against the loom
   family reception's on-ramp criteria table
   (`loom-pipeline/hooks/family-reception.md`, "On-ramp criteria table
   (SSOT)") — reference it by name/path, never copy its rows here.
2. **對站檢查 (station check)** — if the ask is interactive design/spec/code
   work rather than a full pipeline run, hand off to that family's own
   entry point instead of driving it from here: `using-loom-product-principles`,
   `using-loom-interface-design`, `using-loom-spec`, or `using-loom-code`.
3. **本站再確認 (this station's fire condition, unchanged)** — this skill
   still only fires under `§When it fires`'s BOTH-conditions gate below;
   its N/A-loud wording governs unchanged — nothing in this §Intake grants
   permission to hand-drive the four Workflow-driven stations or auto-open
   the Workflow door.

## §When it fires — BOTH conditions, checked first

1. **The Workflow tool is available** in this host (Claude Code exposes a
   `Workflow` primitive that accepts an arbitrary `scriptPath`).
2. **The four station plugins are installed**: `loom-product-principles`,
   `loom-interface-design`, `loom-spec`, `loom-code`. (`loom-discovery`,
   the fifth loom station, is v0.1 interactive-only and not required here
   — the conductor never drives it as a Workflow segment.)

Either condition false → emit **`loom-pipeline: N/A`** with the specific
reason (which condition failed) and stop. N/A is a first-class honest
outcome — **never silently skip, and never fake the orchestration inline**
(e.g. by hand-driving the four Workflow-driven stations one Task/Skill call at a time and
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

`loom-discovery` is v0.1 **interactive-only** — the conductor does not
drive it as a Workflow segment; pipeline runs start at Segment 1
(Principles + Design), and the discovery on-ramp (family reception's
on-ramp row 4) is surfaced to the human before minting a change-id, not
sequenced here.

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

Judgment stays in the four Workflow-driven station plugins (cross-plugin delegation contract)
— and in `loom-discovery`, the fifth loom station, which the conductor
never drives at all — the conductor only orchestrates and records.

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

An entry is eligible for `next` under either of two forms, both requiring
the plan file to be committed:

- **Change-folder form** — `docs/loom/<id>/` exists: it must pass the
  loom-spec validator (exit 0). A folder that exists but fails is a hard
  reject, never a fallback.
- **Brief+plan form** — no `docs/loom/<id>/` folder: the plan itself must
  carry a `Plan-document-reviewer verdict: PASS` line (the
  brainstorm→brief→plan path produces exactly this and no change folder).

An ineligible entry skips before any worktree exists; an uncommitted plan
(invisible to the worktree, which branches from HEAD) is caught after
worktree creation — that entry is SKIPPED and its just-created worktree
and branch are torn down. No segment 2.5: freezing
happens interactively before queueing, never inside the unattended run.

### The dispatcher-only loop

A fresh session **taking over an in-progress batch** (resuming after a
restart, a new session picking up someone else's queue) MUST run
`python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py reconcile --project <projectPath>`
once, BEFORE its first `next` call — this reconciles any entry left RUNNING
by the prior session against wf-record evidence (see below) before the loop
resumes. A session that starts a batch from empty state has nothing to
reconcile and may skip straight to `next`.

The main agent then repeats exactly this loop, one iteration per change,
until `next` prints `{"done": true}` or exits 3 (circuit-breaker HALT). While
non-terminal entries (QUEUED/RUNNING) remain, `next` instead prints
`{"done": false, "non_terminal": [...]}`, enumerating each blocking entry by
`id`/`status`/`reason` — `done` never goes silent on a stuck batch (see the
exit-code table below):

1. `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py next --project <projectPath> --skills-root <skillsRoot>`
   — this also runs `reconcile` internally at its top, so per-iteration
   staleness is caught even without a takeover.
2. `Workflow({scriptPath: "<resolved assets/loom-pipeline.js>", args: <the JSON stdout from step 1, verbatim>})`
3. Immediately after `Workflow()` returns, the dispatcher MUST call
   `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py mark-running <id> --run-id <the Workflow run id, wf_...> --session-dir <this session's directory — the one whose workflows/ subfolder holds wf_<runId>.json, NOT the workflows/ subfolder itself> --project <projectPath>`
   — without this the runId is never recorded and `reconcile`'s
   definitive-evidence path has nothing to check against.

   **Deriving `--session-dir`**: typical shape is
   `~/.claude/projects/<project-slug>/<session-id>/` — the directory that
   CONTAINS `workflows/wf_<runId>.json`, one level above `workflows/`.
   (Grounding: this wf-record layout is undocumented host-internal
   surface — not in code.claude.com/docs/en/workflows.md or sessions.md —
   confirmed against 16 observed `wf_*.json` files, all terminal status;
   see `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4c,
   verified 2026-07-18. Same grounding-note convention as the `resumeRunId`
   citation above.)

   **Fallback**: if the dispatcher cannot determine its own session
   directory, skip this `mark-running` call rather than guess a path —
   the entry then has no `sessionDir` recorded, so `reconcile` can only
   ever resolve it via the staleness path (`SUSPECT`, human decides),
   never via definitive wf-record evidence.
4. `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py mark <id> done|failed --project <projectPath> --run-id <the Workflow run id>`

The main agent is **dispatcher-only**: it never parses the queue file, it
never composes git commands, and it never diagnoses failures mid-batch —
all of that is script-owned (`batch_queue.py`) or deferred to the
end-of-batch human report below.

### Recovery verbs — human operator only

Two subcommands exist for a human operator to correct a stuck entry; the
dispatcher loop above never calls either on its own:

- `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py reset <id> --project <projectPath> [--reason <text>]`
  — requeues a RUNNING or FAILED entry back to QUEUED (`attempts += 1`,
  audit line appended). Use when a stuck or wrongly-failed entry should
  simply run again.
- `python3 <skillsRoot>/loom-pipeline/scripts/batch_queue.py force-fail <id> --reason <text> --project <projectPath>`
  — transitions a RUNNING entry straight to FAILED (audit line appended;
  counts toward the circuit breaker). Use when an entry is confirmed dead
  and should not be retried automatically.

`reconcile` (both the standalone verb and `next`'s internal call) surfaces
two informational flags for the human operator — it never mutates state
for either of these two flags:

- **`SUSPECT`** — a RUNNING entry with no definitive wf-record evidence,
  stale past its grace window. Informational only; the human decides via
  `reset` or `force-fail` above.
- **`SUSPECT-COMPLETE`** — wf-record evidence says the workflow finished,
  but the entry was never marked done/failed. The human confirms the
  actual outcome and records it via `mark`.

On definitive `failed`/`killed` wf-record evidence, reconcile instead
auto-transitions the RUNNING entry straight to `AUTO-FAILED` — a real,
breaker-visible mutation (unlike the two informational flags above) that
can trip HALT, with no human-confirmation step.

### `next` exit codes

| Code | Meaning |
|---|---|
| 0 | dispatched an entry (Workflow args JSON on stdout), or the queue is done (`{"done": true}`), or the queue is stuck with non-terminal entries remaining (`{"done": false, "non_terminal": [{"id", "status", "reason"}, ...]}`) |
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
