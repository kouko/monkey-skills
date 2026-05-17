# Brief format — handoff from `brainstorming` to `writing-plans`

> Companion to [`../SKILL.md`](../SKILL.md). Defines the output contract: the structured brief that `brainstorming` produces and `writing-plans` (Phase 2) consumes.

## Why a structured format

`writing-plans` splits work into atomic ≤5-minute tasks. To do that well, it needs:

- A clear problem statement (so each task ladders to the goal).
- A scoped end state (so it knows when to stop splitting).
- An explicit out-of-scope list (so it doesn't over-split into adjacent work).

Free-form discovery notes can hold these signals but force `writing-plans` to re-extract them; the structured format makes the extraction free.

## Where the brief lives

| Mode | Path | When |
|---|---|---|
| File | `docs/code-toolkit/specs/YYYY-MM-DD-<topic>.md` | **Default for non-trivial work.** The brief becomes a load-bearing artifact (referenced by `writing-plans`, code review, post-ship retrospectives). |
| Inline (no file) | The brainstorming conversation itself | For genuinely small work that the §When NOT to Use exemption was on the edge of — write the brief in the chat but do not commit it. `writing-plans` consumes from chat context. |

When in doubt, write it to a file. The cost of the file is one `git add`; the cost of losing the brief is re-doing the discovery 6 months later.

## Required sections

These five must appear in every brief, plus a sixth (`Current State Evidence`) when the change touches existing code or process. Order matters — `writing-plans` parses top-down.

### `## Problem`

The Jobs-To-Be-Done framing from Axis 1. **Not the solution.**

Format: 1-3 sentences. If longer than 3 sentences, you are mixing in solution language — strip it back to the job.

Klement (2018) job-story form is recommended but optional:

> When [situation], I want to [motivation], so I can [expected outcome].

### `## Users`

Axis 2 — who, in what conditions, with what existing tools and constraints.

Format: bulleted list. Each bullet names a user category + their relevant constraints. Avoid generic *"users"* — be specific enough that a designer reading this could draw the right interface.

### `## Smallest End State`

Axis 3 — the minimum shippable resolution.

Format: 2-5 sentences describing what will be true when this change ships. Include success criteria (how do we know it solved the Problem?) and explicit non-criteria (what we will NOT measure).

### `## Current State Evidence`

**Required when this change touches existing code or process.** Documents what the agent actually read while exploring (Axes 1, 4, 5) so `writing-plans` and downstream reviewers can verify the brief was grounded, not invented.

If the work is genuinely greenfield (new module, no existing system touched), write `N/A — greenfield` and skip the sub-bullets. Do not use `N/A` to dodge reconnaissance work — see anti-patterns below.

Five sub-bullets (each takes a 1-liner with `file:line` citation, or `N/A — <reason>`):

- **Forward** — downstream impact when the touched code/process runs (1-3 bullets, each citing `file:line`).
- **Reverse** — upstream callers / dependants of the touch points (1-3 bullets, each citing `file:line`).
- **Error** — current failure-handling at the touch points; what the change preserves / changes / breaks (1-2 bullets, or `N/A — not error-path code`).
- **Data** — input / output / persistence flowing through the touch points (1-3 bullets, or `N/A — pure logic`).
- **Boundary** — external systems the change reaches. Tag with `[SECURITY]` / `[DB]` / `[API]` / `[ASYNC]` / `[FRAGILE]` (1-3 bullets, or `N/A — no boundaries crossed`).

Plus a citations appendix:

- **Evidence paths** — bullet list of every `file:line` the agent actually read while filling the five sub-bullets above. Reviewers spot-check this list to verify reconnaissance was real.

The agent fills this section by running `grep` / `Read` / dispatching `Explore` — the user does not answer 5 new questions; they review the recon recommendation, same model as Axis 4 research.

### `## Decision`

One paragraph: what we will build, what we will NOT build, and the trade-off summary. This is the section a future maintainer reads first when archaeologizing the commit history.

Format: 3-6 sentences.

### `## Out of Scope`

Bulleted list of adjacent things explicitly NOT in this change. Each bullet should be a thing someone might reasonably ask *"why didn't you also do…"* — the bullet preempts that question.

## Optional sections

Strongly recommended for non-trivial work; can be omitted for genuinely small changes.

### `## Alternatives Considered`

Axis 4 — 2-3 other ways this could be solved, and why they were rejected. Even if the chosen path is obviously best, write the alternatives down. Format: numbered list, each with a one-sentence rejection rationale.

If `dev-workflow:proposal-critique` was invoked during discovery, paste its KEEP / DEFER / DROP verdicts here. If `dev-workflow:complexity-critique` was invoked, paste its smallest-end-state / LOC-delta / obsolescence verdicts.

### `## What Becomes Obsolete`

Axis 5 — what existing code / process / convention this change removes. Bulleted list. Each bullet should be a thing that gets deleted **in the same PR**. If it's not getting deleted in the same PR, name the cleanup ticket and link it.

### `## Open Questions`

Questions that came up during brainstorming and were left for the user to resolve before `writing-plans` starts. Numbered list. Each item should be specific enough to answer in one round.

If Open Questions is non-empty, `writing-plans` is **blocked** until they are answered. Either resolve in the same brainstorming session or hand back to user with a clear *"need answers to Q1-Q3 before proceeding to plan"*.

### `## Diagrams`

Mermaid blocks per [`visual-companion.md`](visual-companion.md). Embed inline (not as separate files). Each diagram preceded by a 1-sentence caption explaining what to look at.

## Template

Copy-paste this skeleton:

```markdown
# <topic> — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: YYYY-MM-DD
> **Author**: <human / agent>

## Problem

(JTBD-form: when [situation], I want to [motivation], so I can [outcome])

## Users

- (user category 1) — (constraints / context)
- (user category 2) — (constraints / context)

## Smallest End State

(what will be true when shipped; success criteria; non-criteria)

## Current State Evidence

(Required when touching existing code. Five sub-bullets; each with file:line or `N/A — <reason>`. Use `N/A — greenfield` only when nothing pre-existing is touched.)

- **Forward**: (downstream impact, file:line)
- **Reverse**: (upstream callers, file:line)
- **Error**: (current failure-handling, file:line)
- **Data**: (input/output/persistence, file:line)
- **Boundary**: (external systems hit — `[SECURITY]` / `[DB]` / `[API]` / `[ASYNC]` / `[FRAGILE]`, file:line)
- **Evidence paths**: (file:line citations the agent actually read)

## Decision

(what we will build, what we will NOT build, why)

## Out of Scope

- (adjacent thing 1 we are NOT doing)
- (adjacent thing 2 we are NOT doing)

## Alternatives Considered

1. **(Alt 1 name)** — (1-sentence why rejected)
2. **(Alt 2 name)** — (1-sentence why rejected)

## What Becomes Obsolete

- (existing thing 1 deleted in same PR)
- (existing thing 2 deleted in same PR)

## Open Questions

(empty if none)

## Diagrams

(embed Mermaid blocks; preceded by 1-sentence captions; remove this section if no diagrams)
```

## Anti-patterns

- ❌ **Solutionizing in Problem.** *"Add a CSV button"* is a solution; the problem is *"share daily data with a non-technical stakeholder."*
- ❌ **Vague Users.** *"All users"* is not a user category. Constrain — *"daily report consumers blocked from installing new tools."*
- ❌ **Smallest End State that matches the first proposal verbatim.** Possible, but suspicious. Did you actually explore Axis 3 or just copy the user's first ask?
- ❌ **Empty Out of Scope.** Every non-trivial change has 2-5 things someone might ask *"why didn't you also…"* Name them.
- ❌ **Open Questions left unanswered going into `writing-plans`.** `writing-plans` is **blocked** until resolved. Don't slip ahead.
- ❌ **Current State Evidence bullets without `file:line` citations.** Hallucinated reconnaissance — the section exists precisely to be verifiable. Bullets that read *"this probably calls X somewhere"* defeat the purpose; run `grep` / `Read` / `Explore` and quote what you actually read.
- ❌ **`N/A — greenfield` on a brief that clearly touches existing code.** Dodge. If the change adds a new method to an existing class, integrates with an existing API, or modifies an existing config — that is not greenfield. Fill the sub-bullets.
- ❌ **Empty `Evidence paths` while sub-bullets are populated.** The appendix proves the recon happened. If you cited file:line in any sub-bullet, the same file:line belongs in Evidence paths.

## See also

- [`../SKILL.md`](../SKILL.md) — the 5-axis discovery framework.
- [`visual-companion.md`](visual-companion.md) — when to embed Mermaid diagrams in the brief.
- `../../writing-plans/SKILL.md` *(Phase 2, ships next)* — consumes this brief and produces a task plan.
