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
