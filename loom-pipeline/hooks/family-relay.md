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

### (b) Visual defaults

- **≥2 options at a fork** → a markdown comparison table is the
  default form. Don't make the user hold options in their head.
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

### (d) Jargon and stakes — point, don't copy

Every seam that translates internal jargon and leads with stakes
before mechanism follows the loom-code ③ gate — see
[`loom-code/skills/requesting-code-review/SKILL.md`](../../loom-code/skills/requesting-code-review/SKILL.md)
§③ "How to phrase" for the canonical rule set (outcome-not-mechanism,
translate jargon, numbers carry meaning, state-anchor first, ≤4
options, compound-ask discipline). Cite that section by name; do not
restate its rules here or in any seam that adopts it — one rule body,
many pointers.
