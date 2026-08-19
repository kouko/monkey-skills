---
name: skill-in-subagent-loses-internal-orchestration
description: Handing a multi-agent skill to ONE subagent degrades its internal orchestration — a writer≠evaluator gate panel becomes one agent auditing its own draft with no error surfaced; drive such skills from the main conversation and dispatch their panel as sibling subagents. NOTE the stated cause is CORRECTED: subagents DO expose the Agent tool (re-probed 2026-08-19); the 2026-07-23 "no Agent/Task/Workflow" finding is stale for Agent, and the advice now rests on the nested layer being where a child result gets dropped
type: gotcha
origin: 2026-07-23 JNJ memo e2e (report-equity-memo Phase 4 delegated to one sonnet subagent; chore-subagent-nesting-gotcha branch)
---

A subagent's toolbox contains no `Agent`, `Task`, or `Workflow` tool — not
even in the deferred-tool list (live probe 2026-07-23: `ToolSearch
"select:Agent"` returns no match inside a `general-purpose` subagent, even
though the agent-type listing says "Tools: *"). So when an orchestrator wraps
"execute skill X" into a single subagent and X internally mandates multi-agent
structure (worker/evaluator panels, review triads, debate stages), that
structure is silently unreachable: the subagent executes every role itself,
sequentially, and nothing errors. Observed live: `report-equity-memo` Phase 4
delegated to one sonnet subagent → investing-team's writer≠evaluator gate
panel became one agent self-auditing its own draft; all 7 gate verdicts were
produced by the artifact's own author. The run "succeeded" — only the
subagent's honest self-report revealed the degradation.

**Why:** gate verdicts exist to be independent; self-audit on a weak tier has
a documented self-certification failure record (repo memory: gate-hardening
arc). A silent structural downgrade of the verdict layer is worse than a loud
failure because the output looks fully gated.

**How to apply:** when a skill's contract includes internal multi-agent
structure, the MAIN conversation must drive it — load the skill in the main
loop and dispatch its workers/evaluators as sibling subagents (or encode the
stages as a Workflow script, whose agent() calls are also siblings). Never
wrap the whole skill into one subagent to save main-loop context. If a run
was nevertheless executed degraded, disclose it explicitly in the artifact
and the user report. Harness-fact sibling: loom-code environment-gotchas §A1
(named Agent dispatch needs SendMessage) — same Agent-tool family, different
trap.

**Correction (2026-08-19, re-probed live).** The tool-availability claim above
is **no longer true for `Agent`**. A `general-purpose` subagent in session
`db36bf57` found `Agent` in its own tool list, resolved its full schema via
`ToolSearch "select:Agent"`, and successfully dispatched a child that returned
a real result. `Task` and `Workflow` were still absent — no tool by either
name resolved, and the search fell back to `Agent` by name similarity rather
than refusing. So the honest state of this fact is: **`Agent` yes, `Task` and
`Workflow` no**, as of 2026-08-19; whether `Agent` was genuinely missing on
2026-07-23 or the probe that day was mis-read is not recoverable, so treat any
tool-availability claim in this store as needing a re-probe before it is
relied on, this one included.

**What this does and does not change.** It removes the *mechanism* this entry
originally offered — a subagent is not forced to self-execute a panel by a
missing tool, because the tool is there. The *observed degradation* stands:
the 2026-07-23 run really did produce all 7 gate verdicts from the artifact's
own author. And the recommendation stands, on new ground rather than the old
one: the nested layer is where a child's work gets dropped, because dispatch
returns an acknowledgement immediately and the child's actual output arrives
later as a separate notification — see
[[a-dispatch-return-is-a-receipt-not-the-work]]. A subagent that dispatches a
panel and then ends its own turn hands the parent that receipt instead of the
panel's verdicts, which looks like a completed delegation and is not one.
