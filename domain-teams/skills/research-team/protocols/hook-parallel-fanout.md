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
