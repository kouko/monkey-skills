# Brief format — handoff from `brainstorming` to `writing-plans`

> Companion to [`../SKILL.md`](../SKILL.md). Defines the output contract: the structured brief that `brainstorming` produces and `writing-plans` (Phase 2) consumes.

## Why a structured format

`writing-plans` splits work into atomic one-failing-test tasks. To do that well, it needs:

- A clear problem statement (so each task ladders to the goal).
- A scoped end state (so it knows when to stop splitting).
- An explicit out-of-scope list (so it doesn't over-split into adjacent work).

Free-form discovery notes can hold these signals but force `writing-plans` to re-extract them; the structured format makes the extraction free.

## Where the brief lives

| Mode | Path | When |
|---|---|---|
| File | `docs/loom/specs/YYYY-MM-DD-<topic>.md` | **Default for non-trivial work.** The brief becomes a load-bearing artifact (referenced by `writing-plans`, code review, post-ship retrospectives). |
| Inline (no file) | The brainstorming conversation itself | For genuinely small work that the §When NOT to Use exemption was on the edge of — write the brief in the chat but do not commit it. `writing-plans` consumes from chat context. |

When in doubt, write it to a file. The cost of the file is one `git add`; the cost of losing the brief is re-doing the discovery 6 months later.

## Required sections

These five must appear in every brief, plus a sixth (`Current State Evidence`) when the change touches existing code or process, and `## Design-side on-ramp` — always present, whether the reception's on-ramp criteria fired or not (when they don't, the `not fired` line records that). `## Design-side on-ramp` sits at the TOP of the brief: immediately after the title / author metadata, before `## Problem` — see §Template for the exact skeleton. Order matters — `writing-plans` parses top-down.

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

Each outcome declared here takes a brief item identifier — see [§Brief item identifiers](#brief-item-identifiers) for the shape and, since this section is prose, for where the declarations go.

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

Each outcome declared here takes a brief item identifier — see [§Brief item identifiers](#brief-item-identifiers) for the shape and, since this section is prose, for where the declarations go.

### `## Out of Scope`

Bulleted list of adjacent things explicitly NOT in this change. Each bullet should be a thing someone might reasonably ask *"why didn't you also do…"* — the bullet preempts that question.

### `## Design-side on-ramp`

**Required when the loom family reception's on-ramp criteria (`loom-code/hooks/family-reception.md` — point, don't copy) fire for this brief; otherwise still write the `not fired` line.** One line, exactly one of these four canonical forms:

- `not fired — <reason>`
- `fired: rows <comma-separated row numbers> — user chose <detour|direct>`
- `fired: rows <comma-separated row numbers> — standing <detour|direct> (DIRECTION.md)`
- `pending`

Any other wording is *unresolved* — never treated as a pass (lookalike wording does not resolve the gate). `pending` is what the agent writes until the user has answered; it is never the agent's own default. The `standing` form is legal only when `docs/loom/DIRECTION.md`'s `## On-ramp standing choices` section names every row cited on that line — that section's own grammar is owned by `loom-code/hooks/family-reception.md`, not repeated here.

## Optional sections

Strongly recommended for non-trivial work; can be omitted for genuinely small changes — except `## Diagrams` and `## Alternatives Considered`, which are fill-or-declare (see their entries): write the diagram or the pinned N/A line, never omit the heading.

### `## Alternatives Considered`

Axis 4 — 2-3 other ways this could be solved, and why they were rejected. Even if the chosen path is obviously best, write the alternatives down. Format: a markdown comparison table — one row per alternative, columns `Alternative | Who ships it / source | Why rejected` (add the shared trade-off axes as further columns when the comparison is multi-dimensional). This section is fill-or-declare: either fill the table, or replace the body with the single line `N/A — no alternatives found: <one-line reason>`. Do not delete the section heading — an absent heading or a bare section is a reviewable omission. The narrative rationale for the chosen path belongs in `## Decision`, not in a table cell.
Routing rule SSOT: `loom-code/hooks/family-relay.md §(b) Visual defaults`.

If `dev-workflow:proposal-critique` was invoked during discovery, paste its KEEP / DEFER / DROP verdicts here. If `dev-workflow:complexity-critique` was invoked, paste its smallest-end-state / LOC-delta / obsolescence verdicts.

### `## What Becomes Obsolete`

Axis 5 — what existing code / process / convention this change removes. Bulleted list. Each bullet should be a thing that gets deleted **in the same PR**. If it's not getting deleted in the same PR, name the cleanup ticket and link it.

Each outcome declared here takes a brief item identifier — see [§Brief item identifiers](#brief-item-identifiers) for the shape.

### `## Open Questions`

Questions that came up during brainstorming and were left for the user to resolve before `writing-plans` starts. Numbered list. Each item should be specific enough to answer in one round.

If Open Questions is non-empty, `writing-plans` is **blocked** until they are answered. Either resolve in the same brainstorming session or hand back to user with a clear *"need answers to Q1-Q3 before proceeding to plan"*.

### `## Diagrams`

Mermaid blocks per [`visual-companion.md`](visual-companion.md). Embed inline (not as separate files). Each diagram preceded by a 1-sentence caption explaining what to look at. These Mermaid blocks are for rendered venues (GitHub / Obsidian / VS Code); when relaying the brief in a terminal chat, apply visual-companion's channel-aware degradation instead.

This section is fill-or-declare: either embed the diagram(s) this section
names, or replace the body with the single line
`N/A — no flow/state/architecture-shaped content: <one-line reason>`.
Do not delete the section heading — an absent heading or a bare section is
a reviewable omission, and an N/A whose reason does not hold against the
artifact's own content is a reviewable claim. A paragraph that suffices
needs no diagram — the slot forces the declaration, not the drawing.
Channel rule SSOT: `loom-code/hooks/family-relay.md §(b) Visual defaults`.

When-to-draw judgment: see [visual-companion.md](visual-companion.md).

## Brief item identifiers

Every outcome-declaring item in a brief carries an identifier, so that a downstream plan can cite that exact item instead of re-quoting its wording. The identifier and the item's human-readable text travel together: the identifier is the half that stays stable, the text is the half that stays readable.

- **Form.** An identifier is written `BI-<n>` — the literal prefix `BI`, a hyphen, then a decimal number. `BI-1`, `BI-2`, `BI-17` are identifiers; `BI1`, `bi-1` and `B-1` are not.
- **Authored, never derived.** The brief's author types the identifier. It is never slugified, hashed, or otherwise generated from the item's heading or from the item's text. Authored-not-derived is what stops the identifier desyncing from its item when the item's text is later reworded.
- **Monotonic, never renumbered, never reused.** A new item takes the next unused number — the highest number this brief has ever used, plus one — regardless of where in the document the new item sits. Items already present keep the numbers they already have; an item inserted above `BI-3` does not become `BI-3`. When an item is deleted, its number is retired: no later item may carry it. Monotonic-never-reused is what keeps the id immutable when an item is inserted, since no insertion can shift a number that was never position-derived in the first place.
- **Scope: three named sections, plus any other that declares an outcome.** Identifiers go on the items of `## Smallest End State`, `## What Becomes Obsolete`, and `## Decision` — not only `## Smallest End State`. Those three are the known in-scope set, so an author satisfies this rule by matching a section name, never by adjudicating a category. The rule that generated the list still holds: identifiers belong on the items of every section that declares an outcome a task could deliver. When a brief carries such a section outside the three — the test being whether a reader could point at a line and say *"a task could ship that"* — its absence from the list is never an exemption: assign that section's identifiers now, in this brief, exactly as for a listed section. Extending the list above is a maintainer's edit to this file, not something a brief's author makes mid-session; record the unlisted section as an open question in this brief's own `## Open Questions` instead, so the pending extension stays visible rather than silently absent. The identifiers you already assigned stand whichever way that question is resolved.
- **Prose-form sections declare beneath the prose.** `## Decision` and `## Smallest End State` are written as prose, not as a bulleted list. Their identifiers go in a declaration list placed directly beneath the prose, one line per outcome the prose declares, in the same declaration shape as any other item. A section declaring a single umbrella outcome gets a single line. A prose-form section is not exempt, and its prose is not restructured into bullets to make room for the identifiers.
- **Adopting identifiers is all-or-nothing within one plan.** Declaring even a single `BI-<n>` in a brief switches its plan's coverage check into brief mode, and from that moment every task in that plan must cite a referent that resolves — an identifier, a change-folder join key, or `none — <reason>`. Tasks still carrying a bare quote from the brief become errors **at once**, not gradually: one identifier added to an otherwise-legacy brief produced ten unresolvable-citation errors in a measured probe. So adopt identifiers when starting a brief, or migrate a brief and its whole plan in one pass — never partway. A brief that declares no identifiers keeps working unchanged, indefinitely; legacy mode is not deprecated.
- **Split and merge retire both sides.** When one item is split into two, the original number is retired and both halves take new numbers — neither half inherits it. When two items are merged into one, both numbers are retired and the merged item takes a new number. Retiring both sides is what keeps a downstream citation from silently re-pointing at an item whose outcome has since narrowed or widened; the stale citation fails loudly against a retired number instead.
- **Language.** BI statements are machine-executed precision content, so they are written in English — they seed the spec's requirement lines.

Write each declaration as the identifier first, then the human-readable item text, on the same line:

```markdown
- BI-1 — Brief items carry an identifier that survives rewording.
- BI-2 — The coverage checker resolves a cited identifier to a declared item.
```

## Paragraph length

A paragraph over 600 characters in a prose section is fill-or-declare, in the same shape `## Diagrams` and `## Alternatives Considered` already use: either split it into bullets or a table, or carry a declaration line on its own line directly beneath the paragraph, in exactly this form:

`<!-- narrative: <one-line reason the sentences depend on each other> -->`

An empty or whitespace-only reason counts as absent — the comment must state why the sentences depend on each other, not just exist.

"Directly beneath" means the line immediately below, with no blank line between — a blank line ends the paragraph's block, so a declaration below one belongs to nothing and the paragraph reads as undeclared.

No checker classifies a paragraph as narrative; the author declares, the reviewer checks the declaration. A classifier would reintroduce the judgment this rule exists to remove.

This declaration uses an HTML comment instead of the `N/A — <reason>` form the other fill-or-declare slots use, because a visible `N/A —` line would break the narrative paragraph's own reading flow — staying readable prose is the whole point of the paragraph the declaration sits beneath.

Two sections are exempt from this rule, each for its own reason:

- `## Current State Evidence` — a citation appendix, not narrative prose.
- `## Alternatives Considered` — already table-routed by `loom-code/hooks/family-relay.md §(b) Visual defaults`.

## Template

Copy-paste this skeleton:

```markdown
# <topic> — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: YYYY-MM-DD
> **Author**: <human / agent>

## Design-side on-ramp

(one of: `not fired — <reason>` / `fired: rows <list> — user chose <detour|direct>` / `fired: rows <list> — standing <detour|direct> (DIRECTION.md)` / `pending`; any other wording is unresolved)

## Problem

(JTBD-form: when [situation], I want to [motivation], so I can [outcome])

## Users

- (user category 1) — (constraints / context)
- (user category 2) — (constraints / context)

## Smallest End State

(what will be true when shipped; success criteria; non-criteria)

- BI-1 — (outcome this change ships)
- BI-2 — (second outcome, if the end state declares more than one)

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

- BI-3 — (the umbrella outcome this decision commits to)

## Out of Scope

- (adjacent thing 1 we are NOT doing)
- (adjacent thing 2 we are NOT doing)

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| (Alt 1 name) | (source) | (1-sentence why rejected) |
| (Alt 2 name) | (source) | (1-sentence why rejected) |

## What Becomes Obsolete

- BI-4 — (existing thing 1 deleted in same PR)
- BI-5 — (existing thing 2 deleted in same PR)

## Open Questions

(empty if none)

## Diagrams

(embed Mermaid blocks with 1-sentence captions, or write the pinned N/A line — do not delete this section)
```

## Anti-patterns

- ❌ **Solutionizing in Problem.** *"Add a CSV button"* is a solution; the problem is *"share daily data with a non-technical stakeholder."*
- ❌ **Vague Users.** *"All users"* is not a user category. Constrain — *"daily report consumers blocked from installing new tools."*
- ❌ **Smallest End State that matches the first proposal verbatim.** Possible, but suspicious. Did you actually explore Axis 3 or just copy the user's first ask?
- ❌ **Empty Out of Scope.** Every non-trivial change has 2-5 things someone might ask *"why didn't you also…"* Name them.
- ❌ **Open Questions left unanswered going into `writing-plans`.** `writing-plans` is **blocked** until resolved. Don't slip ahead.
- ❌ **Current State Evidence bullets without `file:line` citations.** Hallucinated reconnaissance — the section exists precisely to be verifiable. Bullets that read *"this probably calls X somewhere"* defeat the purpose; run `grep` / `Read` / `Explore` and quote what you actually read.
- ❌ **`N/A — greenfield` on a brief that clearly touches existing code.** Dodge. If the change adds a new method to an existing class, integrates with an existing API, or modifies an existing config — that is not greenfield. Fill the sub-bullets.
- ❌ **Skipping the identifier on an in-scope item.** An item in `## Smallest End State`, `## What Becomes Obsolete`, or `## Decision` with no `BI-<n>` cannot be cited by a plan; the plan re-quotes its wording instead, and the quote rots at the first reword.
- ❌ **Renumbering on insert.** Inserting an item above `BI-3` and shifting the existing items down makes every already-written citation point at the wrong item, silently. The new item takes the next unused number wherever it sits in the document.
- ❌ **Reusing a retired number.** A deleted item's number stays dead. Handing `BI-2` to a new item makes an old citation resolve — to something the citing plan never meant.
- ❌ **Deriving the identifier from the heading.** Slugs and hashes of the item's text (`BI-smallest-end-state`, `BI-a1b2c3`) desync the moment the text is reworded. The author types the number.
- ❌ **Empty `Evidence paths` while sub-bullets are populated.** The appendix proves the recon happened. If you cited file:line in any sub-bullet, the same file:line belongs in Evidence paths.

## See also

- [`../SKILL.md`](../SKILL.md) — the 5-axis discovery framework.
- [`visual-companion.md`](visual-companion.md) — when to embed Mermaid diagrams in the brief.
- `../../writing-plans/SKILL.md` *(Phase 2, ships next)* — consumes this brief and produces a task plan.
