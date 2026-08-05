Source: `writing-plans/SKILL.md` §"Cross-skill contract" + §"What this skill does NOT do" — serves `writing-plans`.

# Cross-skill contract

| Direction | Skill | Contract |
|---|---|---|
| **Upstream** | `brainstorming` | Produces brief at `docs/loom/specs/<topic>.md`. writing-plans reads it via Read tool. |
| **Upstream** | `loom-spec:spec-expansion` | Produces the validated change-folder consumed per §Consuming a loom-spec change-folder. |
| **Downstream** | `subagent-driven-development` | Consumes plan at `docs/loom/plans/<topic>.md`. SDD reads plan + dispatches per-task triad. |
| **Downstream (opt-in)** | `dispatching-parallel-agents` | Consumes tasks marked `Independent: true` with disjoint `Files touched`. Dispatches their implementers in one assistant message for concurrent execution. Fall back to SDD's sequential dispatch if either condition fails. |
| **Self-review** | `plan-document-reviewer` (evaluator subagent) | writing-plans dispatches it after producing the plan. Returns PASS / NEEDS_REVISION. |
| **Recursive (BLOCKED fallback)** | `writing-plans` (self) | When SDD's implementer returns BLOCKED with decomposition signal, orchestrator re-invokes this skill on the failing task. |
| **Optional delegation** | `dev-workflow:complexity-critique` | If the plan produces >3 tasks and you suspect Axis 3 (smallest end state) was too generous, optionally invoke complexity-critique before falling back to brainstorming. |

Delegation contract per CLAUDE.md: pass **paths + structured seed context**, not file content. The target skill loads its own resources via Read.

## What this skill does NOT do

- Does **not** write code. Atomic-task production is metadata about future work, not the work.
- Does **not** dispatch SDD subagents. That's SDD's job. writing-plans hands off the plan; SDD picks it up.
- Does **not** invoke the implementer / spec-reviewer / code-quality-reviewer prompts directly. Only plan-document-reviewer (a different evaluator scope).
- Does **not** estimate dev-time at all — the split-trigger is criterion 1 (one failing test); see the main SKILL.md's §No time-box criterion.
- Does **not** decide priority or sequencing beyond what the dependency graph requires. The user (or SDD) decides which independent tasks run first.
