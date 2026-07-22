---
name: skill-in-subagent-loses-internal-orchestration
description: Handing a multi-agent skill to ONE subagent silently strips its internal orchestration — subagents expose no Agent/Task/Workflow tool (live-probed 2026-07-23), so a writer≠evaluator gate panel degrades to one agent auditing its own draft with no error surfaced; drive such skills from the main conversation and dispatch their panel as sibling subagents
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
