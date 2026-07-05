# Hook: Parallel Sub-Worker Fan-Out

Deep-mode collection-dispatch hook — when sub-questions are
independent, fan out to N parallel sub-workers with isolated
context to reduce wall-clock time and per-worker context load.

Inspired by Anthropic Multi-Agent Research System (Anthropic
Engineering, 2024). Implements lead/worker fan-out without a
dedicated coordinator agent — main agent itself plays coordinator.

## When This Applies

- Mode: **deep only** (quick mode caps at ≤5 sources — fan-out
  yields no meaningful speedup at that scale)
- Phase: decision made at the **start of Phase 1 (Scoping)**,
  immediately after sub-questions are defined (typically by the
  multi-perspective hook)
- Workflows: applies when `mode=deep` AND ≥3 sub-questions exist

## Decision Rule

Evaluate sub-question independence:

- **Fan out** when ALL of the following hold:
  - ≥3 sub-questions are defined
  - Sub-questions do **not share source pools** (different
    domains, vendors, or stakeholders)
  - Sub-questions do **not depend** on each other's findings
    (later questions don't reference earlier results)
- **Run sequentially** otherwise (one worker, all sub-questions)

## Fan-Out Mechanics

When fan-out is selected:

1. **N ≤ 4** parallel sub-workers (cap to prevent context blow-up
   in the main agent's integration step)
2. Each sub-worker receives:
   - Isolated context (does NOT see other sub-workers' work)
   - **Subset of standards** relevant to its sub-question only
     (not all 7 standards) — this is where the token savings come
     from
   - One sub-question + its perspective tag from the
     multi-perspective hook
   - Source / search budget pro-rated from the deep-mode total
     (e.g., 4 workers × 4 sources each = 16 sources, fits the
     ≤15 cap with rounding)
3. Each sub-worker runs Phase 2-3 independently and returns a
   focused mini-artifact

## Integration Rule

Main agent integrates N mini-artifacts in **Phase 3 (Synthesis)**:

- De-duplicate cross-cutting findings
- Reconcile contradictions explicitly (do not silently pick one)
- Apply Booth 5-element argument model across the integrated whole
- The Self-Critique hook then runs on the integrated artifact, not
  per sub-worker

## Failure Mode

If sub-workers' outputs contradict and main agent cannot reconcile
without additional research, return `BLOCKED: sub-worker
contradiction unresolved` with both positions surfaced. Do NOT
silently average or pick the more confident one.

## Graceful Degradation — Runtime Without Nested Subagent Dispatch

In some runtime environments the worker itself runs as a subagent
and cannot spawn further subagents (no subagent-spawning capability
in the worker's tool set — Claude Code: no `Agent` tool; Codex: the
`multi_agent` feature disabled or the worker's own agent profile
forbids nested spawns; see
`domain-teams/skills/using-domain-teams/references/{claude-code-tools.md,codex-tools.md}`
for how to detect this per host — including why tool-presence alone
is not sufficient on Claude Code and the fail-safe default when
recursion-permission can't be positively confirmed). True fan-out — N independent
agent processes each with isolated context — is impossible in
this configuration. The hook degrades rather than aborts:

| Property | True fan-out | Degraded (single-agent parallel I/O) |
|---|---|---|
| Wall-clock parallelism | N agent processes run concurrently | Single agent issues N tool calls in one round |
| Context isolation | Each sub-worker sees only its sub-question | All sub-question results land in one context |
| Standards subsetting | Each sub-worker loads only relevant standards | All standards loaded once, used selectively |
| Speedup | ~N× on tool I/O **and** on integration synthesis | ~N× on tool I/O only |
| Token cost per integration | Sum of N small mini-artifacts | One agent draft from one larger context |

### Degraded execution rules

When the worker detects no nested-dispatch capability (no
subagent-spawning tool/feature available, or the harness explicitly
disallows recursive spawning), apply:

1. **Decision rule still runs** — evaluate the three independence
   conditions in §Decision Rule as if true fan-out were available.
   If the conditions don't pass, run sequentially (same as the
   non-degraded path).
2. **Execute as parallel tool-call batches** — instead of N
   sub-workers, the worker issues N concurrent web searches /
   fetches / tool calls per Phase 2 collection round, one batch
   per sub-question.
3. **Standards are still effectively subsetted** — the worker
   consults only the standards relevant to the sub-question
   currently being collected, even though all standards files
   are in context. The token savings vs true fan-out is reduced
   but not zero.
4. **Mandatory Self-Critique disclosure** — the `## Self-Critique`
   block (per `hook-self-critique.md`) MUST explicitly mark
   context isolation as approximated:

   ```
   - Fan-out mode: degraded (single-agent parallel I/O) — context
     isolation approximated, not enforced. Cross-sub-question
     contamination cannot be ruled out.
   ```

   Without this disclosure, a reader cannot tell whether the
   artifact came from N truly-independent investigations or from
   one agent that happened to issue parallel calls. The disclosure
   IS the contract.

### When degradation is acceptable

Acceptable when the task is descriptive (each sub-question stands
alone, no comparison) and contamination risk is low. Examples:
the three-SDK vendor profile from this hook's validation test;
a per-platform feature inventory; a multi-region market sizing
where each region's data is fetched separately.

### When degradation is NOT acceptable

Reject the degraded mode and return `BLOCKED: nested subagent
dispatch required` when the task explicitly requires
**adversarial independence** — for example, a red-team / blue-team
analysis where each sub-worker must form its conclusion without
seeing the other's evidence. Approximating isolation here would
launder the cross-contamination as if it were independent
verification, which is exactly what the contract forbids.

The worker decides degradation acceptability based on the task's
shape, and records the decision in Self-Critique alongside the
fan-out mode line.
