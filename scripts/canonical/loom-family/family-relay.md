# Loom Family Relay Discipline

## Family relay discipline

This is the ONE shared reference for how any loom-* skill talks to the
user, across every station. Every seam — SDD's per-wave reports and
checkpoint sign-offs, review-verdict relay, brainstorming's visual
choices, and each design-side router's intake — **points here**; none
of them copies this section's rules into their own body.

### (a) User-rollup card

When a seam reports progress or a sign-off to the user, use this card.
Slot **semantics** are fixed and language-neutral; slot **content** is
always written in the live conversation language (never hardcoded):

| Slot | Semantics |
|---|---|
| task restated | one line, plain words: what we're doing |
| current state | what's true right now |
| what changed | what just happened, since the last card |
| impact on you | why the user should care — consequence, not mechanism |
| next + decision | what happens next, and what (if anything) the user must decide |

Internal traffic (verdict tokens, wave labels, findings IDs) stays
machine-precise **below** the card — the card is the user-facing
headline, not a replacement for the record.

> Plain-language contract: every user-visible chat line follows the
> 7 rules + glossary in [`plain-relay.md`](plain-relay.md) — point
> there, do not restate the rules here.

#### Close-out card

A close-out report (finishing Step 13, and any loom seam reporting a
PR-open) renders as this specialized table instead — prose details
go **below** the table, never inside it. Same language-neutral-slot /
localized-content rule as the rollup card above.

| Slot | Semantics |
|---|---|
| PR | linked number + title (+ version) |
| Purpose | why this change exists — the problem/intent |
| Changes | what was done |
| Impact scope | what is affected / explicitly NOT affected — standing row, not conditional |
| Verification | test/evidence numbers |
| Review | reviewer verdicts trajectory |
| Review focus | where the merge decision deserves attention; MAY merge into the Review row for small PRs |
| Version | plugin/package bumps |
| 🌐 Web merge | PR URL + one-line reminder to glance the merge dialog's description prefill before confirming |
| 💻 CLI merge | the ready `gh pr merge <N> --squash` command, framed for the human to run |

Conditional rows (add only when applicable): screenshots (UI changes
only), rollback plan (irreversible/infra changes only).

Cell rules: each cell is ONE line; multiple points join with " ・ "
(half-width space, U+30FB interpunct, half-width space); cap: at most
3 points per cell — anything larger becomes "one-line conclusion +
see below" with the detail as prose under the card. Paragraphs never
go in cells.

Channel degradation: chat renderers may not honor `<br>` in cells
(live-confirmed) — chat cards NEVER use `<br>`; a GitHub-rendered PR
body MAY use `<br>` + `•` bullets, but the " ・ " separator form is
the default everywhere else.

Provenance: row set converges Google eng-practices CL-description
conventions with the JA 影響範囲/動作確認/レビューポイント PR-template
convention — same grounding logic as §(d)'s jargon-and-stakes gate.

### (a2) Progress card

The plan-progress variant of the rollup card. Field order is fixed:
**Goal** (one line, verbatim from the plan header — rendered with
the label `end-state:`, not `goal:`, so it never collides with the
host's built-in `/goal` session-scoped directive; the plan schema
field itself keeps the name `Goal:`), **task table**
(`[v]` done / `[~]` claimed / `[ ]` pending / `[!]` blocked — plain-ASCII
marks for cross-platform rendering; counts then rows), **Stage**,
**next** (first not-done task in roadmap order, or close-out). Within
the task table, step separators with `(needs: T…)` lists appear when
the plan declares Dependencies, and indented gloss lines when tasks
carry `Gloss:`; `--detail T<N>` is a separate on-demand view printing
one task's curated fields — not part of the card.
When `plan_card.py` is available, render the body mechanically and never
re-order or drop fields. If `plan_card.py` is unavailable, render the same
field order as a local plain-text progress card. The relayer's frame, in the live conversation language:
a plain-translation gloss under the end-state line; a grounded explanatory
gloss for `next:` (derived from that task's own plan fields — cite
the source item, never invent); and for every `[!]` row an
explanation that OPENS with the stop reason — "needs your decision:
…" or "waiting on an external condition: …". Pipeline-station
narration (waves, reviewer arms, verdicts) stays out of the frame
unless a pending decision cannot be understood without it.

### (b) Visual defaults

- **≥2 options at a fork** → a markdown comparison table is the
  default form. Don't make the user hold options in their head.
- **The same fork rule binds written artifacts** — a brief, plan, or spec
  that weighs ≥2 options on shared axes routes that content to a markdown
  comparison table: one row per option, the shared axes as columns, and
  one load-bearing column stating chosen / rejected-because. The narrative
  *why* stays as prose beside the table, never inside a cell. Shape-based,
  never count-based: content that is not a comparison is not routed here,
  and a template that owns a comparison-shaped section binds this rule at
  its own slot (it points here; it does not restate this bullet).
- **Flow / state shape** → `ascii-graph-toolkit` (CJK display-width
  aware) — not hand-drawn ASCII, not Mermaid, unless the channel is
  known to render Mermaid.
- **Mermaid** → only where the channel renders it. A terminal or
  PR-text channel degrades to a markdown table or `ascii-graph-toolkit`
  output instead.

### (c) Turn-ordering rule

A briefing either **ends the turn** (the ask follows on the next turn)
**or** the ask is **inline** in the same message as the briefing —
never bury a briefing and an AskUserQuestion dialog stacked at the
turn-final position. The user must be able to read the briefing before
the decision dialog demands an answer.

### (d) Jargon and stakes

Every seam leads with the outcome and why it matters before naming the
mechanism. Translate internal jargon into the conversation language, give every
number its consequence, lead with a state anchor before describing a change,
offer no more than four choices, and separate compound decisions. These are the
complete shared rules; an installed plugin may apply stricter local relay or
review rules for its own artifact type.

If a referenced sibling skill is unavailable, do not invoke it or stop ordinary
narration. Follow this local contract, preserve completed artifacts, and describe
only the optional handoff that could not run.
