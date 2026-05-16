---
name: brainstorming
description: 'Use BEFORE implementing — for any task that touches new behavior, new module boundaries, or non-obvious design space. Enforces a HARD-GATE: explore intent and alternatives FIRST through a 5-axis framework (Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete), then emit a structured brief that writing-plans consumes. Refuses "this is simple", "I know what to build", "let''s just start coding" rationalizations. Grounded in Jobs-To-Be-Done (Christensen 1997, ISBN 978-0875845852) and Klement (2018) job-story format. ブレインストーミング・要件発掘・先に探索。腦力激盪・需求探索・先想清楚再寫。'
version: 0.4.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / debugger), the parent orchestrator already finished discovery. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **DO NOT START IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT.**

This is not a guideline. The pressure to skip — *"this is simple,"* *"I know what to build,"* *"let's just start coding"* — is exactly the failure mode this skill exists to prevent. **The first 5 minutes of brainstorming saves the next 50 minutes of building the wrong thing and the 500 minutes of refactoring out of it.**

If you catch yourself drafting code, opening files, or reaching for the Skill tool to call `tdd-iron-law` *before* the user has answered the 5 axes below — **stop**. Return to this skill. Beck's *"if it's hard to test, it's probably hard to use"* (Preface, 2002) has a discovery-phase analogue: *if it's hard to articulate what success looks like, it's probably the wrong target.*

### What counts as "before implementation"

| Phase | Iron-Law on TDD applies? | brainstorming applies? |
|---|---|---|
| User says *"add feature X"* | Not yet (no code being written) | **YES — start here** |
| Brief sketched, plan being drafted | Not yet | Skill complete; hand off to `writing-plans` |
| writing-plans split into atomic tasks | Each task triggers it | Skill complete |
| implementer subagent dispatched | YES — Iron Law applies | Skill complete (subagent has the brief in its prompt) |

If you are in the first row and the task is non-trivial (touches new behavior, new module boundary, or non-obvious design space), this skill is **mandatory** before anything else.

## When NOT to use

Narrow, enumerated exemption list. If your task is **not** on this list, the HARD-GATE applies.

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **One-line known-pattern fix** | Typo in a string literal; bumping a version number in `package.json`; flipping a documented config value (no behavior change for the user). | A "small change" that touches behavior (e.g. retries: 3 → 5 — that's a retry-policy decision, not a config tweak). |
| **Pure refactor under existing test coverage** | Rename a private function; extract a method while all existing tests stay green. | Architecture-shifting refactor (extract a new module boundary, replace a synchronous call with an event). |
| **Bug fix where the failing test already exists** | A test is RED reproducibly; you know which line is wrong. | A bug where *"the test should fail but doesn't"* (false-green diagnostic; see `tdd-iron-law/SKILL.md` §False-green diagnostic). |
| **Explicit user override** | User says *literally* "skip brainstorming, here's the spec, go" AND hands in a written spec / plan that already covers the 5 axes. | User says *"just figure it out"* — that's an instruction to brainstorm, not to skip. |

When uncertain, ask: *"Could a reasonable engineer pick the wrong solution from the user's prompt as written?"* If yes, you are in brainstorming scope.

## The 5-axis exploration framework

Walk all five. Don't skip any. If an axis returns *"don't know"* or *"need more from user"* — that is itself a discovery output and goes into Open Questions in the brief.

### Axis 1 — Problem

What is the user trying to accomplish? **Not the solution they proposed — the problem behind the solution.**

If the user says *"add a CSV export button,"* the problem is not *"have a button."* It might be *"share daily numbers with a non-technical stakeholder who lives in Excel,"* OR *"backup data before deletion,"* OR *"feed data into a downstream pipeline."* Each problem has different success criteria.

Grounded in: **Christensen, C.M. (1997) *The Innovator's Dilemma*, Harvard Business School Press, ISBN 978-0875845852** — the original Jobs-To-Be-Done framing: *"customers don't buy products; they hire them to do a job."* Articulate the job before the product.

### Axis 2 — Users

Who specifically? Under what conditions? With what existing tools and constraints?

*"Internal data analysts who currently export by SQL-copy-paste to Sheets, on a daily cadence, blocked by IT from installing new desktop tools"* is a different design than *"external API consumers who need a stable CSV format for nightly ETL."*

Grounded in: **Klement, A. (2018) *When Coffee and Kale Compete*, ISBN 978-1718626751** — job story format: *"When [situation], I want to [motivation], so I can [expected outcome]."* Use this format when articulating Axis 1+2 together.

### Axis 3 — Smallest End State

What is the *minimum* shippable end state that solves the problem? Defaulting to the user's first-suggested solution is a smell — the first solution is usually bigger than necessary.

Examples of "smaller than first ask":
- *"Add a CSV export button"* → smallest may be: *"add a `?format=csv` query param to the existing report URL"* (no UI work at all).
- *"Add a feature-flag system"* → smallest may be: *"add one env var + a hardcoded list check"* (defer the whole flag system).
- *"Refactor `OrderService`"* → smallest may be: *"extract just the email-notification subset that's blocking the current bug"* (defer the rest).

This axis often delegates to `dev-workflow:complexity-critique` for systematic deletion-first triage. See §Cross-skill delegation.

### Axis 4 — Alternatives Considered

What are 2-3 other ways this could be solved, and why were they rejected? Force the user (or yourself, in conversation with the user) to enumerate.

The point is not to pick from the alternatives — it is to make the chosen path's trade-offs visible. *"We picked X over Y because Z"* is a sentence that survives 6 months of context loss; *"X is the obvious choice"* does not.

If you cannot articulate 2-3 alternatives, you have not explored enough. Push for more — *"what if we did nothing,"* *"what if we did it manually for a quarter and revisited,"* *"what if we delegated to an existing tool."*

### Axis 5 — What Becomes Obsolete

What existing code / process / convention does this make redundant? Anything that becomes obsolete and is **not removed in the same change** is technical debt by design.

Examples:
- New CSV export endpoint → the documented Sheets-copy-paste runbook becomes obsolete; delete it in the same PR.
- New feature flag → the hardcoded behavior it replaces becomes obsolete; remove it in the same PR.
- New helper function → if it's covering for an existing API's shortcomings, can the existing API be improved instead?

If nothing becomes obsolete, that is a flag: either the change is purely additive (probably YAGNI — see `dev-workflow:complexity-critique`) or the design space wasn't explored enough.

## Output Contract — the brief

Brainstorming's deliverable is a **structured brief** that `writing-plans` consumes. Schema in [`references/handoff-brief-format.md`](references/handoff-brief-format.md); minimum required sections:

```markdown
## Problem
(Axis 1 — the JTBD-style job behind the user's request)

## Users
(Axis 2 — who specifically, in what conditions)

## Smallest End State
(Axis 3 — minimum shippable resolution)

## Decision
(One paragraph: what we will build, what we will NOT build, why)

## Out of Scope
(Bulleted list of adjacent things explicitly NOT in this change)
```

Optional but recommended sections: Alternatives Considered (Axis 4), What Becomes Obsolete (Axis 5), Open Questions.

The brief lands in the user's repo at a path of their choice — typical conventions: `docs/superpowers/specs/<date>-<topic>.md` (mirrors monkey-skills) or `docs/specs/<topic>.md` (project-local).

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"This is simple, no need to brainstorm."* | The framing *"this is simple"* almost always means *"I have already picked a solution and am defending against discovery friction."* | Refuse. Walk Axis 1+2 with one clarifying question each; if both come back trivial, the §When NOT to Use exemption may apply — name it explicitly. |
| *"I know what to build, let's just start."* | Same rationalization, agent-side. Common after the user has framed the task and the agent feels the cost of asking back. | Refuse. Articulate Axis 3 (smallest end state) in writing first; if it matches the user's first ask exactly, the discovery was redundant — but the writing-down made it visible. |
| *"Let's just start coding and see what happens."* | Iterative-prototyping rationalization. Discovery and prototyping are different — prototyping happens INSIDE the smallest end state, not in place of articulating one. | Refuse. The smallest-end-state articulation is the prototype-scope decision; do that first. |
| *"The user already gave me a spec."* | Maybe — but specs that skip Axis 4 (alternatives) and Axis 5 (what becomes obsolete) leave the agent unable to make follow-on decisions intelligently. | Read the spec against the 5 axes. If any axis is empty, ask the user — do not invent. |
| *"It's just refactoring, no new behavior."* | Refactoring under existing test coverage is the §When NOT to Use exemption — but architecture-shifting refactor (new module boundary, new contract) is NOT covered by that exemption. | Distinguish: rename / extract-under-coverage = exempt; new boundary / new contract = brainstorm. |
| *「太簡單了不用討論 / 簡単すぎる / こんな簡単な話」* | Same rationalization, localized. | Same refusal — walk the 5 axes minimally; if trivial after, name the §When NOT to Use exemption. |

## Cross-skill delegation

| When | Delegate to | Why |
|---|---|---|
| Axis 3 surfaces "this change might be bigger than necessary" (smell of accidental complexity / YAGNI) | `dev-workflow:complexity-critique` | Systematic deletion-first triage (three questions: smallest end state / before-after LOC / what becomes obsolete). Optional but strongly recommended. |
| Axis 4 produces 3+ real options that need triage | `dev-workflow:proposal-critique` | Evidence-grounded KEEP / DEFER / DROP triage. Optional. |
| Brainstorming output indicates work >1 hour OR >1 module | `writing-plans` (next stage) | Brief becomes the input to plan-splitting. |
| Brainstorming output indicates a simple one-line known-pattern fix | Skip writing-plans; route straight to `tdd-iron-law` | The brief documented the smallness; trust it. |

Delegation contract (see CLAUDE.md cross-plugin section): pass **paths + structured seed context**, not full file content. The target skill loads its own resources.

## Visual companion

For non-trivial system design — especially when axes 1+2 (problem + users) need a flow / interaction diagram, or axis 5 (what becomes obsolete) needs an architecture-before-and-after — see [`references/visual-companion.md`](references/visual-companion.md). The companion documents when a Mermaid sequence / C4 / ER diagram pays for itself vs when prose is enough.

## What this skill does NOT do

- Does **not** write code. The brief is text + diagrams; implementation starts in `writing-plans` → SDD → `tdd-iron-law`.
- Does **not** make the final decision for the user. It surfaces the 5 axes so the *user* can decide intelligently. The agent's role is to enforce the framework, not to choose.
- Does **not** replace `dev-workflow:complexity-critique`. complexity-critique runs deletion-first against a specific proposal; brainstorming runs discovery against an open problem. Sequence: brainstorming first, complexity-critique invoked on demand from inside brainstorming.
- Does **not** require all 5 axes to surface novel content. Sometimes Axis 4 returns *"no real alternatives — the problem space is narrow"* and that is a valid output. The discipline is walking the axes, not generating volume.

## See also

- [`references/visual-companion.md`](references/visual-companion.md) — when to reach for diagrams.
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — output schema for `writing-plans` consumption.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; routes to this skill at Stage 1 (Discovery) of any coding task.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — the discipline that fires once implementation begins.
- `dev-workflow:complexity-critique` — optional delegation target when Axis 3 surfaces complexity smell.
- `dev-workflow:proposal-critique` — optional delegation target when Axis 4 surfaces multi-option triage.
