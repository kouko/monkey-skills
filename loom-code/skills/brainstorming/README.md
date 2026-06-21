# brainstorming

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **HARD-GATE — DO NOT START IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT.** Walks the user / agent through a 5-axis discovery framework (Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete) and produces a structured brief that `writing-plans` consumes. Refuses "this is simple", "I know what to build", "let's just start coding" rationalizations.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What the HARD-GATE means

The pressure to skip — *"this is simple,"* *"I know what to build,"* *"let's just start coding"* — is exactly the failure mode this skill exists to prevent. The 5 minutes of brainstorming saves the 50 minutes of building the wrong thing and the 500 minutes of refactoring out of it.

If the user or agent invokes implementation moves (drafting code, opening files, reaching for `tdd-iron-law`) *before* the 5 axes are walked, the skill refuses and routes back to discovery.

## The 5-axis framework

Walk all five. None are optional unless the §When NOT to Use exemption applies.

| Axis | Question | Grounded in |
|---|---|---|
| 1 — Problem | What job is the user hiring this change to do? **Not the solution they proposed.** | Christensen (1997) JTBD, ISBN 978-0875845852 |
| 2 — Users | Who, in what conditions, with what existing tools and constraints? | Klement (2018) job-story format, ISBN 978-1718626751 |
| 3 — Smallest End State | What is the minimum shippable resolution? | Often delegates to `dev-workflow:complexity-critique` |
| 4 — Alternatives Considered | What are 2-3 other ways this could be solved, and why rejected? | Forces trade-off articulation |
| 5 — What Becomes Obsolete | What existing code / process this change makes redundant — and removes in the same PR | YAGNI + same-PR cleanup discipline |

## Current State Evidence — recon discipline (v0.7.0+)

When the change touches existing code or process, the brief carries a `## Current State Evidence` section with 5 sub-bullets (Forward / Reverse / Error / Data / Boundary) + Evidence paths appendix — every bullet cites `file:line`. The agent fills this via `grep` / `Read` / dispatching `Explore`; recon is the agent's job, not the user's. Greenfield work allowed `N/A — greenfield` skip. See [`references/handoff-brief-format.md`](references/handoff-brief-format.md) §Current State Evidence for the schema.

## Output

A structured brief written to `docs/code-toolkit/specs/YYYY-MM-DD-<topic>.md`. Schema: see [`references/handoff-brief-format.md`](references/handoff-brief-format.md). `writing-plans` (Phase 2) consumes this brief to split work into atomic tasks.

## When NOT to use

Enumerated exemptions only — see [`SKILL.md`](SKILL.md) §When NOT to Use:

- One-line known-pattern fix (typo, version bump, documented config value with no behavior change)
- Pure refactor under existing test coverage (rename, extract-method, tests stay green)
- Bug fix where the failing test already exists and is reproducible
- Explicit user override AND a spec that already covers all 5 axes

If the task is not on this list, the HARD-GATE applies.

## Cross-skill delegation

- **`dev-workflow:complexity-critique`** — optional; invoked from Axis 3 when the change feels too big. Runs deletion-first triage (3 questions: smallest end state, before-after LOC, what becomes obsolete).
- **`dev-workflow:proposal-critique`** — optional; invoked from Axis 4 when 3+ real alternatives need KEEP / DEFER / DROP triage.
- **`writing-plans`** (Phase 2) — the next stage. Consumes the brief.
- **`tdd-iron-law`** — fires once `writing-plans` finishes and SDD dispatches an implementer subagent.

## What this skill does NOT do

- Does **not** write code.
- Does **not** make the final decision for the user. It surfaces axes; the user decides.
- Does **not** replace `dev-workflow:complexity-critique`. complexity-critique critiques a specific proposal; brainstorming explores an open problem.

## See also

- [`SKILL.md`](SKILL.md) — operational spec.
- [`references/visual-companion.md`](references/visual-companion.md) — when to reach for diagrams (Mermaid sequence / C4 / ER) during discovery.
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — output schema for `writing-plans` consumption.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 1 (Discovery).
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — fires once discovery is done and implementation begins.
