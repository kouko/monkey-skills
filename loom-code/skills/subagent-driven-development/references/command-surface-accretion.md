# Command-surface accretion notes

Companion file to `SKILL.md`'s Definition of Done — command-surface
accretion clause, kept out of the body to stay under the CHK-SKL-010
word cap. The full mechanics live here; the SKILL.md body keeps only
the core rule + a pointer here.

A task that introduces a **new runnable capability** (a new test suite, build step, lint target, e2e suite, `migrate` command, etc.) must have that verb **declared in the command surface** (the project's declared commands — `AGENTS.md` commands section, `make`/`just` recipes, `package.json` scripts) **AND verified to run** before the implementer reports `DONE`. This is **accretion**: it binds "add a capability" to "declare it in the surface" exactly as TDD binds "add behaviour" to "add a test". Enforcement lives in the **implementer's task-completion contract** (verify-before-declare + declare in the managed block, as specified in [`loom-code/agents/implementer.md`](../../../agents/implementer.md)) — it is the implementer that self-enforces this obligation, not the orchestrator's verdict-resolution table.

**Event-driven — not per-task polling.** A task that adds *no* new runnable capability triggers *no* surface change. The clause is a no-op for the common case. It is **not** a per-task audit of the whole surface, and it is **not** a build-once bootstrap. *Negative example:* a task that adds only a helper function, an internal class, or a private module — with no new top-level runnable verb — does NOT trigger this.

**Moving target.** "Complete" is relative to the project's *current* capabilities. Never pre-declare a verb that does not yet exist (no `deploy` entry before deployment exists; no `migrate` entry before a migration runner exists).

**Mechanics.** The implementer reuses the declared-first resolution from `verification-before-completion` to locate the surface. Full mechanics (managed block, shim pattern, verify-before-declare discipline) are in the implementer contract at [`loom-code/agents/implementer.md`](../../../agents/implementer.md).
