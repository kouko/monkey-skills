# Brief — ascii-graph v2-C: sequence-diagram generator

> Consumed by `writing-plans`. Extends the shipped `ascii-graph` skill
> (`ascii-graph-toolkit/skills/ascii-graph/`). Brownfield — adds a 6th generator
> alongside table / flow / tree / bar / arch.

## Problem

(Axis 1 — JTBD)

When the assistant explains a *flow of interactions over time* — "User calls the
API, API queries the DB, DB returns rows, API returns a token" — to a
semi-technical reader in a Mermaid-incapable channel (CC terminal / Slack / PR),
the natural shape is a **UML sequence diagram** (participants with vertical
lifelines, time flowing down, labeled message arrows between them). Today there is
no generator for it; hand-drawing one is the worst alignment case yet — multiple
vertical lifelines that must each stay at a fixed display-column while horizontal,
CJK-labeled arrows cross between them. The job: **"turn an ordered list of
who-sends-what-to-whom into a guaranteed-aligned ASCII sequence diagram in one
shot,"** the same deterministic-generation promise the other five shapes keep.

## Users

(Axis 2)

The assistant itself, mid-conversation, explaining a request/response or
event-ordering flow to a reader who *懂一點技術但不是非常精通*. Job story:
**When** I need to show the time-ordered exchange between a few components,
**in** a plain-text channel, **I want** to hand a `{participants, messages}`
structure to a generator, **so I can** get a CJK-aligned sequence diagram without
hand-counting columns across many lifelines.

## Smallest End State

(Axis 3)

A sixth generator, **`seq`**, wired into `generate.py`:

- **Input:** `{"participants": [str, ...], "messages": [{"from": str, "to": str,
  "label": str}, ...]}`. `from`/`to` name participants and must be **distinct**
  (self-messages deferred). Messages render top-to-bottom in list order.
- **Output:** each participant in a box across the top, a vertical lifeline (`│`)
  dropping from each box's center column; each message renders as **two rows** — a
  centered label row and an arrow row (`────►` left-to-right / `◄────`
  right-to-left) spanning from the source lifeline column to the target lifeline
  column. Arrows that span non-adjacent participants pass **through** the
  intermediate lifeline columns (the arrow line occupies those cells on its row).
  Between messages, every lifeline shows `│` at its fixed column.
- **Column math:** each participant column sits at a fixed display-column; column
  spacing = max(participant box widths, and the widest message label that must fit
  in each gap), all measured via `width.display_width`, so CJK (2-cell) participant
  names and message labels stay aligned.
- **Guarantee:** output is **aligned by construction** and verified by the
  generator's own **structural tests** — see the Decision below for why this
  generator's correctness contract differs from the others'.
- **Surfaces touched:** `generate.py` (`_SHAPES` + `render()` + import), new
  `gen_seq.py`, `tests/test_gen_seq.py`, `SKILL.md` (routing row + worked example +
  bundled-files + honest-ceiling), and the manifest description/version.

Illustrative shape (exact glyphs settled in the plan):

```
┌──────┐         ┌─────┐         ┌──────┐
│ User │         │ API │         │  DB  │
└──┬───┘         └──┬──┘         └──┬───┘
   │   ログイン       │               │
   │───────────────►│               │
   │                │   査詢         │
   │                │──────────────►│
   │                │   rows        │
   │                │◄──────────────│
   │   token        │               │
   │◄───────────────│               │
```

## Current State Evidence

(Brownfield — same generator pattern as the shipped five.)

- **Forward (invocation):** stdin JSON → `generate.py:64` → `render(shape, payload)`
  dispatch (`generate.py:29-48`) → per-shape `render_X` → stdout; allow-list is the
  `_SHAPES` tuple (`generate.py:26`); user-facing routing is the SKILL.md table.
  A new generator follows `gen_arch.py` / `gen_flow.py` exactly: insert `scripts/`
  on sys.path, `from width import display_width`, return a `\n`-joined string.
- **Reverse (SSOT ownership):** no sync/distribute script governs these scripts
  (standalone plugin). In-skill SSOT is `width.py` (display-width) and `glyphs.py`
  (box-drawing taxonomy). `seq` imports `width.display_width`; it MAY import the
  arrow glyphs (`► ◄`) from `glyphs.py:ARROWS` rather than hardcoding them (keeps
  the taxonomy single-sourced — a small SSOT win over the v2-A arch generator,
  which used only default light glyphs).
- **Error:** unknown shape → `ValueError` (`generate.py:48`) / `return 2`. Adding
  `seq` extends `_SHAPES` + `render()` + the usage string together.
- **Data:** payload JSON on stdin; new payload `{"participants", "messages"}`.
- **Boundary — the load-bearing one:** the alignment oracle `align.py` (wiring
  `checks_seam` / `checks_table` / `checks_kink`) models **vertical seams** and
  **vertical ▼/▲ arrowheads landing in boxes** (`checks_kink.py:1-16`). A sequence
  diagram's **horizontal** message arrows **crossing** vertical lifelines is a
  *different topology* — an arrow row legitimately interrupts every lifeline it
  spans, which the seam-straightness / kink checks would read as broken seams.
  So `seq` output is NOT expected to pass `align.py` clean, and that is correct,
  not a defect (see Decision).

Evidence paths: `…/scripts/generate.py`, `…/gen_arch.py`, `…/gen_flow.py`,
`…/glyphs.py`, `…/width.py`, `…/align.py`, `…/checks_kink.py`, `…/SKILL.md`, `…/tests/`.

## Decision

Build a deterministic **`seq`** generator that renders
`{participants, messages}` as a classic UML sequence diagram (participant boxes +
fixed-column vertical lifelines + two-row labeled horizontal message arrows),
CJK-aligned via `width.display_width`. **Correctness contract:** unlike the other
five generators, `seq` output is guaranteed by **construction + its own structural
tests** (every line equal display width; each lifeline `│` sits at its participant's
fixed column on every non-arrow row; each arrow starts/ends exactly on its
source/target lifeline column with the arrowhead on the target side), **NOT** by
passing `align.py`. Reason: `align.py` models vertical-seam diagrams, and a
sequence diagram's horizontal arrows crossing lifelines fall outside that model —
feeding `seq` output to `align.py` would produce false-positive "broken seam"
reports. We will **NOT** teach `align.py` a sequence-aware rule in this change
(that is a separate, larger effort), and we will **NOT** build self-messages,
activation bars, notes, or alt/loop/par fragments (deferred). This keeps the work
deterministic and bounded while honestly scoping the verification model.

## Alternatives Considered

(Axis 4 — researched EN + JA)

1. **Status quo: hand-draw + `align.py`.** Pros: no new code. Cons: multi-lifeline
   alignment is the hardest hand-draw case, AND `align.py` can't even validate it
   (horizontal-arrow topology) — so the user gets neither generation nor a working
   oracle. **Rejected** as the path for this shape.
2. **External ASCII sequence tool** (Diagon, textart.io ASCII Sequence Creator,
   PlantUML `ascii-art` mode). Source: arthursonzogni.com/Diagon, textart.io/sequence,
   plantuml.com/ascii-art (EN); GitMind JP. Pros: mature layouts, fragments. Cons:
   all are Western-ASCII — **none are CJK display-width-aware** (the same v1
   renderer-survey finding that deferred external engines); a 2-cell 中/日 label
   overflows their 1-cell-per-char canvas. **Deferred** to v2-D (external-engine
   track), not chosen here.
3. **Teach `align.py` a sequence-aware check, then require seq to pass it.** Pros:
   uniform "passes the oracle" contract across all generators. Cons: large scope
   (a new horizontal-arrow/lifeline-crossing model in the checks), and unnecessary
   for a generator that is already aligned by construction. **Rejected for this
   change** (the structural per-generator tests give the same guarantee at far less
   cost); revisitable later if hand-drawn sequence diagrams become a need.

**My take:** Recommend the in-house deterministic generator (Decision) with a
**construction + structural-test** correctness contract, explicitly NOT the
align.py contract. PlantUML's left/right/center message-text alignment
(plantuml.com/sequence-diagram) confirms "label sits over the arrow span" is the
conventional rendering — we center the label over its arrow. **Conditional
reversal:** if users later hand-draw sequence diagrams (not just generate them),
that justifies the alternative-3 work (a sequence-aware `align.py` check).

EN ↔ JA agreement: both describe the same lifeline + horizontal-message model; the
JA sources explicitly note no monospace/CJK-AA-specific generator exists —
consistent with picking an in-house generator.

## What Becomes Obsolete

(Axis 5)

- The SKILL.md routing currently sends any non-fitting box-and-arrow diagram to the
  hand-drawn verify-loop. Once `seq` ships, sequence diagrams move to the
  `generate.py seq` row. Add the row + worked example; update honest-ceiling so
  sequence is listed as a generator shape. The honest-ceiling note that `align.py`
  validates hand-drawn diagrams stays accurate — `seq` simply documents its
  construction-based guarantee instead. Nothing is deleted (additive generator).

## Out of Scope

- Self-messages (`from == to`), activation bars, notes/comments, and
  alt/opt/loop/par fragments (deferred — each is its own layout problem).
- Return-arrow / async styling (dashed/open-head) — v1 uses one solid arrow style.
- Numbering / autonumber.
- Teaching `align.py` a sequence-aware check (alternative 3 — separate effort).
- External-engine fallback (v2-D).
- `align.py --fix` (v2-B).

## Open Questions

1. **Arrow glyph choice** — `►/◄` (from `glyphs.py:ARROWS`, 1-cell, align-safe) vs
   ASCII `>`/`<`. Lean: `►/◄` for consistency with the box-drawing palette; settle
   in plan. (The arrow *shaft* is `─`; the head sits on the target lifeline column.)
2. **Label wider than the arrow span** — when a message label is wider than the gap
   between its two lifelines, the column spacing must widen to fit it. Lean: column
   gap = max(default spacing, widest label needing that gap) — deterministic, settle
   in plan; covered by a test with a long CJK label.
3. **Self-message** is explicitly deferred; the generator should reject (or clearly
   error on) `from == to` rather than mis-render. Settle the error contract in plan.
