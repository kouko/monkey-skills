---
name: loop-engine-must-null-guard-every-agent-dispatch
description: In a Workflow-driven convergence loop (goal-loop / wiki-update / principles-improve-loop), `agent()` returns null when the dispatched subagent dies on a terminal error (API overload, session/quota limit, user skip) after retries — so EVERY consumer that dereferences an agent() return (`.exitCode`/`.hash`/…) must null-guard first, or a transient infra death crashes the whole loop on `null.exitCode` instead of stopping honestly. The graceful-stop / "safe to leave unattended" guarantee is only as strong as its weakest unguarded agent() consumer.
type: gotcha
origin: branch fix-ratchet-wikilink-tokens (2026-07-24) — a wiki-update smoke re-run hit the Asia/Taipei session limit at round 3's compare grader; agent() returned null, the engine did `result.exitCode`, and the loop crashed ("null is not an object") instead of an honest stop. Fixed by a new INFRA_ABORT terminal + a sentinel-return `assertAgentAlive` guard at the two verdict-courier consumers (obsidian 3.20.1).
---

The failure defeats the exact promise the machine exists to make: an
unattended loop that crashes on a transient agent hiccup — rather than
stopping cleanly with a blockers report — is not safe to walk away from.
And infra deaths are common precisely in the long AFK runs these loops
target (overload, quota resets).

**The audit that matters at build time:** grep every `await agent(` in
the engine and trace each return's dereference. Most consumers may
already null-guard incidentally (`if (!x)`, `x && x.y`, return ignored)
— in the wiki-update engine 8 of 10 did — but the ones feeding a hot
`.exitCode`/`.hash` read are the crash sites. Do not trust "it works in
the happy-path smoke": the null path only fires on a real death, which a
green fixture run never triggers.

**Design notes that generalized:**
- Distinguish **INFRA_ABORT** (transient, re-runnable — dispatched agent
  died) from **MALFORMED** (fail-closed — the agent returned but its
  data is malformed). Same crash-avoidance, opposite operator advice.
- Sentinel-RETURN, not throw, when the engine body is module-level
  (top-level await): a throw skips the Report phase that writes the
  blockers report, and can't be caught without re-indenting the whole
  body. A guard that returns a `{infraAbort, stage, round}` sentinel and
  is checked at each consumer keeps the edit surgical (2 sites, not 300
  lines).
- Freeze/pre-baseline agent deaths correctly stay hard-throw — before a
  baseline exists there is no partial report to write — but attribute
  them honestly ("infra interruption, re-runnable"), never mislabel a
  null death as CONFIG DRIFT.
- If the abort path leaves executor edits un-reverted in the working
  tree, the operator-facing recovery text MUST say "clean the tree
  before re-running" — a dirty tree makes the next freeze preflight
  refuse, so a bare "just re-run" advice fails loud. (Same dirty-tree
  recovery contract as STUCK_EXECUTOR_OVERREACH.)

Relevant when the parked general goal-loop harness (BACKLOG
Rule-of-Three) is extracted: the null-guard-every-consumer rule and the
INFRA_ABORT/MALFORMED split belong in the shared skeleton, not
re-derived per adapter. See [[prose-only-enforcement-dies-on-weak-executors]]
for the sibling principle on the verdict path.
