# Brief — ASCII-graph skill (plain-text diagram/table for no-Mermaid channels)

Date: 2026-06-17 · Stage: brainstorming → writing-plans
Branch: `ascii-graph-visionlyzion`

## Problem

(Axis 1 — JTBD) *When I'm explaining complex logic or architecture to a
semi-technical reader during a coding session, in a channel that cannot
render Mermaid (primarily the Claude Code terminal itself; also plain-text
chat / PR body), I want a diagram or table that stays visually aligned and
readable as literal monospace text with Chinese/Japanese labels, so the
explanation lands without the reader needing any rendering tool.*

The acute failure mode is Anthropic-acknowledged: CC issue #13438 — "Tables
with CJK characters are misaligned in terminal output", diagnosed as a
**generation-side** bug (the model pads CJK as width-1). A prose-rules
approach does not fix it: the Grok-authored `ascii-graph-expert` SKILL.md
(652 lines) is the disproof — its own flagship "Good / correct alignment"
table is misaligned by one column when measured with a real display-width
model.

## Users

(Axis 2)
- **Operator**: kouko, generating explanations mid-coding-session in Claude Code.
- **Reader**: a "懂一點技術但不精通" stakeholder reading plain-text output
  (terminal copy, Slack, PR text). Labels in **Traditional Chinese / English /
  Japanese** (CJK trio; JP kana+kanji are the same UAX #11 Wide class as
  Chinese, so the width tooling covers JP at ~zero extra cost). Semi-technical ⇒
  can parse flowcharts / layered architecture / decision trees, and the subject
  matter may itself be **complex**, so structurally-rich diagrams are wanted.
  Quality principle: **density must serve comprehension**, not metadata-cramming.
- **Constraint**: target channel cannot render Mermaid; monospace assumed; the
  CC terminal itself has known CJK *rendering* quirks (a cluster beyond #13438,
  e.g. #23534 wrap-clip, #56622 fullscreen wcwidth-unaware clip) that a
  generation-side skill **cannot** fix.

## Smallest End State — v1 (in-house only, user-selected "ship fast")

v1 takes **zero external binaries**. New skill = thin `SKILL.md` router + two
pure-Python tools (+ `wcwidth`):

1. **Deterministic generators** (`generate.py`) — one-shot, no iteration — for
   layout-trivial shapes (no hard graph-layout problem): CJK-aligned **tables**,
   **linear / layered flows** (boxes + down-arrows), **trees / hierarchies**,
   **horizontal bar charts**. Pure Python + wcwidth; full CJK control; best
   quality where applicable.
2. **Alignment oracle** (`align.py`) — the **verify-loop**: model drafts a
   diagram → runs `align.py` → it prints per-line display width + flags
   vertical-seam drift (line + display-col) → model fixes → repeat until ✓.
   **PoC-validated** (below): converged in 2 rounds on a mixed 中/日 flowchart.
3. **SKILL.md** routes: layout-trivial shape → generator (one-shot);
   model-drawn (flowchart / medium / annotation layout) → verify-loop. Width
   policy: box-drawing = 1, Ambiguous = 1, **emoji not an alignment anchor**.
   Languages CN / EN / JP.

**Honest ceiling (stated in-skill):** dense/complex graphs may not converge via
the loop (layout is genuinely hard); **class / ER / state / gantt / mindmap / C4
are NOT v1 aligned-ASCII** — for those, emit **Mermaid source as the faithful
SSOT**. External renderers are deferred (see Out of Scope / v2).

What this is NOT: not prose-rules; not a home-grown graph-layout engine; not
external-binary-dependent (in v1).

## Current State Evidence

`N/A — greenfield`. New skill; no existing ASCII-graph skill in the repo.
- Forward/Reverse/Error/Data/Boundary: no pre-existing code touched.
- Closest neighbour: `obsidian/skills/obsidian-mermaid-visualizer` — Obsidian-
  scoped, renders Mermaid *in Obsidian*; does not address plain-text/terminal
  rendering or CJK ASCII alignment. Not a touch point.

## Decision

Build a **zero-dependency in-house v1**: deterministic generators for
layout-trivial shapes + a wcwidth **verify-loop** oracle for model-drawn
diagrams + thin SKILL router. Smallest shippable end state that actually fixes
the real bug (#13438 generation-side CJK drift), with best CJK control and full
portability. External renderers and the long-tail diagram types are explicitly
**deferred to v2**.

What drove this: **hand-testing (not doc claims)** showed **no single
off-the-shelf tool renders all types CJK-correct**. So leaning on a renderer for
"all types" is a mirage; the in-house verify-loop is the robust core, renderers
are additive later.

## Alternatives Considered (Axis 4 — researched + hand-tested)

1. **Prose-rules only** (Grok `ascii-graph-expert` / npm `ascii-fix-rules`) —
   REJECTED. Prose-only, 0 stars, no width computation; Grok's own showcase
   misaligns. Crutch-class, proven unreliable.
2. **Renderer-dependent** (mermaid-ascii / merman / beautiful-mermaid) —
   **DEFERRED to v2**. Hand-test verdict: no engine is all-types-CJK-correct;
   would need two complementary binaries (Go + Rust) for partial coverage;
   conflicts with the zero-dep grain for v1.
3. **Build our own full graph-layout engine** — REJECTED. Reinvents
   elkjs/graphviz-class layout; existing tools embody years of work; violates
   simplicity / YAGNI.
4. **In-house generators + verify-loop** — CHOSEN for v1. PoC-validated,
   zero-dep, covers the highest-value shapes; renderers additive in v2.
- Do **not** reinvent width computation — `wcwidth` / `go-runewidth` /
  `unicode-width` are canon (tabulate / rich already correct).

**Hand-tested engine survey (2026-06-17) — why no engine is turnkey:**

| Engine | flowchart | sequence | class | ER | state | CJK box width |
|---|---|---|---|---|---|---|
| mermaid-ascii (Go) | ✓ | ✓ | ✗ | ✗ | ✗ | correct (its types); edge-label mojibake; no diamonds |
| merman (Rust) | overflow | overflow | ✓ | ✓ | ✗(svg) | class/ER correct, flowchart/seq overflow |
| beautiful-mermaid (TS) | render | render | render | render | render | **all overflow** (1-cell-per-char canvas) |

Sources: [#13438](https://github.com/anthropics/claude-code/issues/13438) ·
[ascii-fix-rules](https://github.com/L-ubu/ascii-fix-rules) ·
[wcwidth](https://github.com/jquast/wcwidth) ·
[UAX #11](https://www.unicode.org/reports/tr11/tr11-40.html) ·
[mermaid-ascii](https://github.com/AlexanderGrooff/mermaid-ascii) ·
[merman](https://github.com/Latias94/merman) ·
[beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid)

## PoC Result — verify-loop (2026-06-17, `/tmp/poc/align.py`)

- `align.py` (wcwidth oracle): prints per-line display width + flags any box
  `│` with no structural connector above/below at the same display-column (the
  CJK-overflow signature). Exit 0/1.
- **Round 1** (naive draft, boxes sized by char-count): **6 drifts caught** with
  exact line + display-col; width dump made each obvious.
- **Round 2** (boxes resized to display-width from that feedback): **✓ converged**;
  a column audit confirmed the seams are genuinely straight (not a false pass).
- Zero external dep (pure Python + `wcwidth`; width table could be inlined for
  true zero-dep).
- **Oracle blind-spots to harden (TDD):** seam-straightness (off-by-one connector
  kinks), arrowhead-into-box, table-block equal-width. v0 "connect above-OR-below"
  is lenient.

## What Becomes Obsolete

(Axis 5) Greenfield ⇒ nothing in the repo is removed. The downloaded
`~/Downloads/SKILL (2).md` is a *rejected reference*, superseded as the design
we will NOT build. The skill makes the *idea* of a prose-rules ASCII skill
obsolete for this repo.

## Out of Scope (v1)

- External renderers (mermaid-ascii / merman) → **v2** (optional enhancers).
- Aligned-ASCII for class / ER / state / gantt / mindmap / C4 → emit **Mermaid
  source as SSOT** instead.
- Home-grown graph-layout engine; reinventing wcwidth.
- Fixing CC's rendering-side CJK bugs (wrap-clip, UTF-8-boundary corruption).
- Metadata-cramming density.

## Open Questions / plan inputs

1. **Oracle hardening scope** — seam-straightness + arrowhead-into-box +
   table-block equal-width. First plan tasks, TDD (RED test per blind-spot).
2. **v1 generator set** — tables + linear/layered flow + tree + bar. Confirm.
3. **Home + name** (deferred per user) — recommend new plugin
   `ascii-graph-toolkit`, skill `ascii-graph`; **provisional** path for planning,
   confirm at plan review (a rename is cheap).
