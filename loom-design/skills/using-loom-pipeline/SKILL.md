---
name: using-loom-pipeline
# firing-evidence: 2026-07-14 baseline 4/4 EXACT (docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md)
description: >-
  Drives the loom principles→design→spec→code pipeline end-to-end via
  deterministic Claude Code Workflow segments. Use when asked to run the
  whole pipeline or auto-implement a change from principles through code.
  CONDITIONAL: fires only when Workflow is available and both station plugins
  are installed; otherwise report `loom-design: N/A` with the reason (Codex is
  N/A). Triggers: "run the loom pipeline", "全管線", "全流程跑一遍", 自動實作,
  "run the conductor".
version: 0.1.0
---

<SUBAGENT-STOP>
If dispatched as a subagent with an explicit role, follow that prompt; do not re-derive fire conditions or invoke Workflow yourself.
</SUBAGENT-STOP>

# using-loom-pipeline — thin conductor over 4 of 5 loom stations

This skill only collects run inputs, resolves the driver, invokes Workflow,
and records orchestration. It never authors station artifacts or verdicts.

## §Intake

Before checking this skill's own fire conditions:

1. **前站檢查** — check the repo against [family reception](../using-loom-design/references/family-reception.md)'s On-ramp criteria table (SSOT); do not copy it here.
2. **對站檢查** — interactive design/spec work goes to `using-loom-design`; use `loom-code:using-loom-code` for code work.
3. **本站再確認** — apply the BOTH-conditions gate below. Intake never permits hand-driving Workflow stations or auto-opening Workflow.

## §When it fires — BOTH conditions, checked first

1. The **Workflow tool is available** (Claude Code exposes `Workflow` with an arbitrary `scriptPath`).
2. Both station plugins are installed: `loom-design` and `loom-code`. Discovery is interactive-only and is not a segment.

If either is false, emit **`loom-design: N/A`** with the failed condition and
stop: never silently skip, and never fake the orchestration inline by manually
calling stations. **Codex hosts: N/A by definition** because they lack Workflow;
report `loom-design: N/A (no Workflow primitive on this host)` and stop. There
is **no fallback path** or shell substitute; that is a separate parked retrigger.

## §Run inputs — exactly 6 fields

Missing required data is a fail-loud stop; only stated defaults apply.

| Field | Required | Default / contract |
|---|---|---|
| **change-id** | yes | None. Identifies `docs/loom/<change-id>/`; thread through unchanged. |
| **target project path** | yes | None; absolute consumer-project path. |
| **token budgets** | yes | `{ run, perStation }`; run defaults to the host cap, while omitted station keys use `STATION_TOKEN_BUDGETS` in `driver_20_runstation.js`. Names: `principles`, `design`, `design-critic`, `spec`, `critic`, `validator`, `code`, `review`, `probe`. Either overage fails loud. |
| **model policy** | yes | Claude default tier; per-station or blanket. Workflow is Claude-family only. |
| **resumeRunId** | no | None; maps to `resumeFromRunId`. Live-verified 2026-07-03 by F5 run `wf_667ec006-ec2` and pipeline dogfood. |
| **skillsRoot** | segment 2 | None; absolute installed loom-design plugin root, rendered as `${CLAUDE_PLUGIN_ROOT}`. The validator path must fail loud, never be guessed. |

## §Invocation — absolute driver path, one call per segment

Resolve the **absolute** path to `assets/loom-pipeline.js` from the host's
**Base directory for this skill**: append `skills/using-loom-pipeline/assets/loom-pipeline.js`
when given the plugin root, or `assets/loom-pipeline.js` when given this skill
directory. Never derive it from the current working directory.

Invoke Workflow once per segment:

```text
Workflow({scriptPath: "<absolute assets/loom-pipeline.js>", args: {
  segment: <1|2|3>, changeId, projectPath,
  budgets: {run, perStation: {principles, design, "design-critic", spec,
    critic, validator, code, review, probe}},
  models, skillsRoot: "<required for segment 2>",
  resumeRunId: "<optional; omit when fresh>"
}})
```

## §Segments — 3 segments

Use one Workflow call per segment, never one call for the whole run.

1. **Segment 1 — Principles + Design.** `loom-design:product-principles`, then `loom-design:design-system` + `loom-design:interaction-flows`, then the `loom-design:design-critic` panel.
2. **Segment 2 — Spec.** `loom-design:spec-expansion`, then `loom-design:completeness-critic`, then the spec validator must exit 0.
3. **Segment 3 — Code.** `loom-code:subagent-driven-development` under TDD, then whole-branch `loom-code:requesting-code-review`, then `loom-code:ui-verification` on the running surface.

Segment names intentionally match the driver's Principles + Design / Spec /
Code phases. That keeps a paused run's numeric segment aligned with its owning
station phase. Segment 1 closes only after the design critic has searched for
surface omissions. Segment 2 closes only after the completeness critic has
hunted specification omissions and the binary validator succeeds. Segment 3
closes only after task-by-task implementation, cumulative-diff review, and the
conditional running-surface check. The driver orchestrates these owners; it
does not replace their own protocols or quality decisions.

Discovery remains interactive-only: surface family reception's on-ramp row 4
before minting a change-id; never sequence discovery as a segment.

## §Human gates — exactly 4

Each gate stops and waits for the human.

(a) **Change-id minting** — before Segment 1; the human names `docs/loom/<change-id>/`.

(b) **Product forks** — when any segment surfaces a genuine product decision, brief it via the **#475 complex-fork escalation** (`loom-workflow:brief-before-asking`); never improvise a default.

(c) **Cost policy** — before each segment, reconfirm or revise that segment's budgets and model tier; never reuse prior confirmation silently.

(d) **Final merge** — after Segment 3. The pipeline never merges; it returns PR branches plus the ledger for human action.

Gate (b) covers product judgment, not ordinary implementation details. Gate
(c) is deliberately per-segment because later phases have different cost
profiles; a confirmation is not durable across a segment boundary. Gate (d)
also bounds authorization: producing a reviewable branch does not authorize a
push, merge, or equivalent judgment-bearing action.

## §Driver prohibitions

- The driver never edits station artifacts.
- The driver never produces verdicts.
- The driver never merges.

Judgment remains in the four Workflow-driven station plugins (cross-plugin delegation contract); discovery is the fifth station and is never driven.
Under the **stable-prefix** convention, append the per-change payload to
cacheable station preambles — appended, never prepended.

## §Batch mode — frozen decisions, unattended sequential queue

Batch mode moves gates (a) and (c) to freeze time, then runs Segment 3
sequentially. Parallel execution remains parked in `loom-design/README.md`.

### Queue intent and machine state

`docs/loom/QUEUE.toml` is the human's **intent**, hand-edited only at freeze
time. Each `[[change]]` requires `id`, project-relative `plan`, and
`budgets.run`; `budgets.perStation` and `models` are optional.

```toml
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
models = { code = "sonnet", review = "sonnet" }
[change.budgets]
run = 200000
perStation = { code = 40000, review = 20000 }
```

`docs/loom/queue-state.json` is the machine's **state**, owned only by
`batch_queue.py`, with `RUNNING`/`DONE`/`FAILED`/`SKIPPED` per id. Neither
file writes the other.

### Freeze predicate

The plan must be committed, and one form must hold:

- **Change-folder form** — `docs/loom/<id>/` exists and its loom-design validator exits 0. Failure is a hard reject, never fallback.
- **Brief+plan form** — the folder is absent and the plan contains `Plan-document-reviewer verdict: PASS`.

Ineligible entries skip before worktree creation. A plan invisible from HEAD
is detected after creation, marked SKIPPED, and its new worktree/branch removed.
There is no segment 2.5: freeze interactively before queueing.

The two freeze forms are alternatives, not fallback stages. If a change folder
exists, its failed validator cannot be bypassed by finding a PASS line in the
plan. Conversely, the brief+plan form applies only when that folder does not
exist. This keeps freeze-time human intent stable during the unattended run
and prevents the dispatcher from manufacturing readiness.

### Safe invocation

Every `batchQueueArgv` below is an **argument vector (argv)** beginning with
the verb, never shell text. Each dynamic project path, id, run id, session
directory, reason, and plugin root occupies one literal array element.

Prefer `["python3", batchQueueScript, ...batchQueueArgv]` without a shell. For
a Bash-string-only host, encode the argv as a UTF-8 **JSON list of strings**,
then `base64.urlsafe_b64encode(json_bytes).decode("ascii").rstrip("=")`;
require `[A-Za-z0-9_-]+` and substitute it as the sole payload in:

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pipeline/argv_exec.py" <URL_SAFE_BASE64_JSON_ARGV>`

The bridge validates the closed schema and directly calls packaged
`batch_queue.py`; decoded data never reaches a shell. Set `pluginRoot` to
rendered `${CLAUDE_PLUGIN_ROOT}` and `batchQueueScript` to
`pluginRoot + "/scripts/pipeline/batch_queue.py"`.

### Dispatcher lifecycle

A fresh session taking over an active batch MUST run reconciliation before
its first `next`; an empty-state start may omit it:

`batchQueueArgv = ["reconcile", "--project", projectPath]`

This reconciliation checks entries left RUNNING by the prior session against
wf-record evidence. Below, `batch_queue.py next` means the argv form using the
installed packaged script, not shell-composed command text.

Then repeat until `next` reports `{"done": true}` or exits 3. If non-terminal
QUEUED/RUNNING entries remain, it reports `{"done": false,
"non_terminal": [{"id", "status", "reason"}, ...]}` rather than silently
claiming completion.

Run one iteration per change and preserve the returned JSON unchanged. The
dispatcher does not inspect TOML, choose branches, build git commands, or
reinterpret a failure. `next` owns selection, freeze validation, worktree
creation, and Workflow arguments; the later state-recording steps attach host
evidence and record the terminal outcome. This ownership split is what makes a
restarted session safe to reconcile.

1. `batchQueueArgv = ["next", "--project", projectPath, "--skills-root", pluginRoot]` — also reconciles internally.
2. Call `Workflow({scriptPath: "<resolved assets/loom-pipeline.js>", args: <step-1 JSON verbatim>})`.
3. Immediately on return call `batchQueueArgv = ["mark-running", id, "--run-id", workflowRunId, "--session-dir", sessionDir, "--project", projectPath]` so reconcile has definitive evidence. `sessionDir` contains the `workflows/` subfolder, not that subfolder itself. Typical shape: `~/.claude/projects/<project-slug>/<session-id>/`, containing `workflows/wf_<runId>.json`. **Grounding:** this undocumented host-internal layout was confirmed across 16 terminal files; see `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4c (2026-07-18). **Fallback:** if the dispatcher cannot locate its session directory, skip this `mark-running` call rather than guess; reconcile can then reach only stale `SUSPECT`, never definitive wf-record evidence.
4. `batchQueueArgv = ["mark", id, outcome, "--project", projectPath, "--run-id", workflowRunId]`, where outcome is exactly `done` or `failed`.

The main agent is **dispatcher-only**: it never parses the queue file, it never composes git commands, and it never diagnoses failures mid-batch. The script owns those mechanics and the human receives the end report.

### Recovery verbs — human operator only

The dispatcher never calls these autonomously:

- `batchQueueArgv = ["reset", id, "--project", projectPath, "--reason", reason]` requeues RUNNING/FAILED to QUEUED, increments attempts, and appends audit. The reason is optional; if absent, omit both elements.
- `batchQueueArgv = ["force-fail", id, "--reason", reason, "--project", projectPath]` moves confirmed-dead RUNNING to FAILED with audit and breaker impact.

Reconcile surfaces two informational flags and never mutates state for either
of these two flags: **SUSPECT** means stale RUNNING without definitive evidence
(human uses reset/force-fail); **SUSPECT-COMPLETE** means wf-record completion
without a recorded outcome (human confirms, then uses mark). Definitive
failed/killed wf-record evidence instead auto-transitions RUNNING to
**AUTO-FAILED**, a real breaker-visible mutation that may trigger HALT.

Do not treat either SUSPECT flag as a workflow outcome. `reset` is appropriate
when the human wants another attempt; `force-fail` is appropriate only after
confirming the run is dead. SUSPECT-COMPLETE requires checking the actual
result before `mark`. These are operator recovery decisions, so the unattended
dispatcher may surface them but cannot select a recovery verb.

### `next` exit codes

| Code | Meaning |
|---|---|
| 0 | Dispatched JSON, `{"done": true}`, or explicit stuck `{"done": false, "non_terminal": [...]}`. |
| 1 | Fail-loud error such as malformed `QUEUE.toml`. |
| 2 | Argparse usage error. |
| 3 | circuit-breaker HALT after 2 consecutive FAILED entries; `--override-halt` requires human review. |

### Terminal state

`batchQueueArgv = ["status", "--project", projectPath]` prints the report a
fresh session reads first. A completed N-change batch leaves N
`docs/loom/<changeId>/pipeline-ledger.md` files and N PR-ready `loom/<id>`
branches. Merge remains human under gate (d).

The status report is also the handoff surface after interruption: read it
before deciding whether the queue is terminal, halted, or waiting for an
operator. Terminal means every entry has left QUEUED/RUNNING and the promised
ledgers and branches exist; an exit-0 response containing non-terminal entries
is explicitly not completion. Preserve that distinction when reporting batch
results, and never present a paused or suspect queue as successfully finished.

The final branch/ledger pair remains review material, not proof of merge or
deployment. The conductor's authority ends at this terminal state, matching
the same human-only merge boundary used by interactive segmented mode.
