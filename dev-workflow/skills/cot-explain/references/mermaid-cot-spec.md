# CoT Mermaid Diagram Spec

## Who owns what

Every rule below belongs to exactly one of three layers. The layer
decides what happens when rules conflict — and they will.

| Layer | Owns | When it conflicts |
|---|---|---|
| **Content** | What the reasoning is: which nodes exist, what each claims, how much evidence each carries, what relation each edge names | **Always wins.** Never trim a claim, drop a node, or invent a bullet to satisfy anything below. |
| **Layout** | How that chain is drawn: rows or columns, `direction`, which nodes share a subgraph | **Derived from the content**, never imposed on it. If the chain will not fit the layout, the layout was the wrong choice. |
| **Advisory** | Widths, squareness, bullet and node counts | **Never blocks.** Signals to weigh. Acting on one by damaging a claim is the failure this split exists to prevent. |

This ordering was not the original design. The first version expressed
layout as rules the author had to obey *while extracting*, and it
inverted: a cold-read run stated that it chose four bullets rather than
five "mainly to offset" a width warning — deciding how much to take from
the source by looking at a layout metric. Measurement then showed the
two goals actively pointing apart (see the appendix): the squarest
fan-out diagram was the one that hid a whole branch. Layout is now
downstream of content, and the numbers are a record, not a target.

---

## Content layer

### What is a node

A reasoning **state**, carrying a claim. "驗證假設後推翻原方案" is a
node. "專案背景" is a heading, not a node — it belongs only if it
actually asserts something.

**How many nodes: as many as the reasoning has.** Below 5 a diagram
rarely earns its place — say so and offer prose. Above 9 the source
usually holds more than one arc — consider splitting into one diagram
per arc. Both are observations about what usually happens, not limits.
A chain with 11 genuine steps is drawn with 11 nodes.

Reversals push against this range and should be allowed to. Each costs
two nodes — the judgment held, then the judgment after it was overturned
— so a source with two or three reversals reaches 9 while remaining one
arc. Merging or dropping one to hit a number destroys exactly the
structure the reversal rule exists to preserve.

### What is in a node

A short title, then bullets — **as many as that node actually has**.
Three to five is what that usually comes to; the range reports the
outcome and sets no quota. Each bullet states a concrete fact, figure, or
claim, not a category label. Do not pad to reach a number, and do not cut
a real piece of evidence to stay under one.

Padding through the *advisory* is a real observed failure, not a
hypothetical: a cold-read run inflated a node the source gave one
sentence "to satisfy the 3–5 advisory". A number does not need
enforcement to distort content — being printed is enough.

Bullets are pointers. The full claim, evidence, and consequence live in
that node's card in the HTML body, which has no width limit at all.

### Edges name real relations

Every edge carries a label naming *why* the second node follows from the
first: `塑造文化根基`, `半年後再次挑戰`, `量測推翻前提`. An unlabeled
edge is a defect — it is the reader's only handle on the jump.

Empty connectives are defects too: `導致`, `然後`, `接著`, `所以` carry
no information.

**Several edges may share one label.** When three branches merge into
the same node for the same reason, they all read `三路匯入`. Inventing
three phrasings to avoid repetition manufactures a distinction the
reasoning does not have.

| Syntax | Means |
|---|---|
| `-->` | ordinary derivation — B follows from A |
| `-.->` | weak / background link — A merely supplies context or enables B |
| `==>` | the culminating step into the conclusion |

`==>` usually appears once, on the last edge. If the reasoning has two
culminations, use two.

---

## Layout layer

The layout is **read off the shape of the chain**, after the chain
exists. Two shapes; the choice is mechanical.

### Shape 1 — a linear chain → rows

One sequence. Outer `graph TB`; each row is a `subgraph` declaring
`direction LR`; rows hold up to three nodes and stack down the page.

**A node-level relation cannot cross a row.** Two nodes that must be
joined directly — a cross-link, or co-premises feeding one node — have
to sit in the same subgraph, because a node edge leaving its row
destroys that row's layout (see the invariants below). Rows are a layout
choice and the content decides them, so the fix is to regroup: put the
linked nodes in one row. If the reasoning genuinely runs in parallel
tracks, that is Shape 2, and the same rule holds inside it. If neither
grouping works, the relation is not lost — it belongs in the node's card
as 依據, stated in prose rather than drawn.

```
graph TB
subgraph r1["階段標題"]
direction LR
  A["<div style='text-align:left'>節點標題<br/>━━━━━━<br/>• 條列一<br/>• 條列二<br/>• 條列三</div>"]
  B["..."]
  C["..."]
end
subgraph r2["階段標題"]
direction LR
  D["..."]
  E["..."]
end
A -->|邊標籤| B
B -->|邊標籤| C
D ==>|邊標籤| E
r1 -->|邊標籤| r2
style A fill:#f8f9fa,stroke:#868e96,stroke-width:2px
```

### Shape 2 — a branching chain → columns

The reasoning forks into tracks that run in parallel before merging.
Outer `graph LR`; **each branch is one `subgraph` declaring
`direction TB`**, running down the page; branches sit side by side.

```
graph LR
subgraph c1["起點"]
direction TB
  A["..."]
end
subgraph c2["甲線"]
direction TB
  B["..."]
  D["..."]
end
subgraph c3["乙線"]
direction TB
  C["..."]
  E["..."]
end
subgraph c4["收束"]
direction TB
  F["..."]
  G["..."]
  H["..."]
end
B -->|各自查證| D
C -->|各自查證| E
F -->|再找反證| G
G ==>|無反證乃定案| H
c1 -->|分出第一條| c2
c1 -->|分出第二條| c3
c2 ==>|兩線合流| c4
c3 ==>|兩線合流| c4
style A fill:#f8f9fa,stroke:#868e96,stroke-width:2px
```

Forcing a branching chain into rows is what the earlier version did, and
it split parallel nodes across different rows so the fork became
invisible. Columns make parallelism structural: one branch, one box.

### Mechanical invariants — both shapes

Rules mermaid itself imposes. Breaking one renders wrong, so the gate
fails on them.

- **Every node lives inside a subgraph.** A node outside one escapes the
  structure entirely.
- **Every subgraph declares its own `direction`** on its own line,
  immediately after the `subgraph` line — `LR` for rows, `TB` for
  columns. Without it the grouping buys nothing.
- **No node edge may leave its subgraph. Rows and columns are joined
  SUBGRAPH to SUBGRAPH.** This is the single rule the whole layout rests
  on. mermaid drops a subgraph's `direction` the moment one of its nodes
  has an edge to anything outside it — **including an edge to another
  subgraph's id** — and the boxes then stack along the parent's axis
  instead. So `A -->|…| B` inside one row, and `r1 -->|…| r2` between
  rows; never `C -->|…| D` across rows, and never `C -->|…| r2`.
  Measured identical on mermaid 11.13.0 and 11.17.0; see the appendix.
- **A subgraph holds a connected run of nodes**, so that its members read
  as one stage. A subgraph holding exactly ONE node is fine — it has no
  inner edge to be part of, and renders correctly.
- **Subgraph ids are `r1`/`r2`/… or `c1`/`c2`/…**, never a bare capital
  letter, which would collide with a node id.
- **Node ids are single uppercase letters** in reading order.
- Sections in order: the `graph` line → every `subgraph` block → every
  edge → every `style` line.

### Node label — exact shape

```
<ID>["<div style='text-align:left'>TITLE<br/>━━━━━━<br/>• B1<br/>• B2<br/>• B3</div>"]
```

- The `<div style='text-align:left'>` wrapper is **mandatory**. Mermaid
  centers multi-line labels, making bulleted content unreadable.
- The separator is the literal `<br/>━━━━━━<br/>` — six U+2501 (`━`).
  Not `---`, not `<hr>`, not a different count. This is the vault's
  house convention, observed across 7,924 notes under the vault's
  `references/` tree (238,764 nodes; counted 2026-08-19 by matching the
  `<div style='text-align:left'>` node wrapper).
- Bullets are prefixed `• ` (U+2022 + space), joined with `<br/>`.
- Quoting is nested: **double** quotes wrap the label, **single** quotes
  wrap the HTML attribute. Swapping them breaks mermaid's parser.

### Styling

One inline `style` line per node id, after all edges. No `classDef` —
the vault uses it in exactly one outlier file.

| Role | fill | stroke |
|---|---|---|
| Premise / starting context | `#f8f9fa` | `#868e96` |
| Supporting evidence | `#fff4e6` | `#e67700` |
| Obstacle / conflict / counter-evidence | `#ffe3e3` | `#c92a2a` |
| Attempt / intermediate move | `#ffe8cc` | `#d9480f` |
| Turning point / synthesis | `#e5dbff` | `#5f3dc4` |
| Conclusion | `#c5f6fa` | `#0c8599` |

Assign by role, not by position. The same colour repeats as often as the
role does; only the conclusion colour is expected to appear once.

---

## Advisory layer

Reported as `WARN`, exit 0. Weigh them; do not obey them at the cost of
a claim.

- **The single widest bullet sets the column width for every node.**
  That one line is the cheapest thing to shorten, and the only one the
  gate mentions. Budgets are pixel-width, not character counts, and
  widen 1.4× for Latin-heavy text — a CJK glyph is about twice a Latin
  one, so an English phrase needs more characters to say the same thing.
- Node titles over ~10 CJK-widths start wrapping badly; row and column
  titles over ~8 compete with the node titles.
- Edge labels read best at 4–8 CJK-widths.
- Node count outside 5–9, or bullet count outside 3–5, is worth a second
  look at whether the arc is really one arc. Note that fewer than 5
  reasoning states is *also* SKILL.md Step 2's early exit, and that one
  is a **stop**, not an observation: the answer there is prose, not a
  diagram. The two are not in conflict — Step 2 decides whether to draw
  at all, this warning describes a diagram already being drawn — but a
  low node count should send you back to Step 2 before it sends you
  looking for a formatting fix.
- **Squareness is a reported observation, never a target.** The appendix
  shows why chasing it damages diagrams.

---

## Escaping traps

- **`number. space` runs in node text — a WARN, no longer a rule.**
  Inherited from `obsidian:obsidian-mermaid-visualizer`'s quirks list as
  the single most common mermaid failure: `1. 第一點` parsed as a markdown
  ordered list and died with `Parse error: Unsupported markdown: list`.
  Probed live against the pinned parser, mermaid-cli 11.16.0 renders it
  cleanly, both quoted (the form this spec mandates) and unquoted. The
  checker warns rather than fails, because "Step 1. do this" is an
  ordinary sentence and rejecting it costs more than the trap does.
  If the page is bound for an older renderer — Obsidian bundles its own
  mermaid — `1.第一點`, `①` or `(1)` still sidestep it, and `--render`
  answers it for whatever parser you actually have.
- No unescaped `"` inside a node label — the outer quotes end early.
- No `|` inside an edge label — it terminates the label.
- No literal newlines inside a node label — use `<br/>` only.
- Parentheses and square brackets inside labels are safe **because** the
  label is quoted. Verified by rendering, not assumed.

## What "verified" means

`scripts/verify_cot_html.py` has two stages. By default it checks the
text against this spec. With `--render` it pushes each diagram through
the real mermaid parser and reads the resulting SVG — necessary because
**mermaid-cli's exit code proves nothing either way.** The inherited
grounding records it writing an error image and exiting 0; a live probe
on 11.16.0 saw a malformed arrow exit 1 with no image written. The
checker therefore reads the output — no SVG, or an SVG carrying an error
marker, both count as failure — and never the exit status.

`FAIL` means the contract or the parser is broken; it exits 1. `WARN` is
advisory and never blocks.

`--stamp` records the outcome in the markdown as `pass @ <12 hex>`, the
hash being the page body the run actually judged. The converter compares
it against the body it renders, so a page edited after its check shows
**閘：stale** rather than the old pass. Re-run `--stamp` and re-render to
clear it.

Neither stage checks **fidelity** — whether the diagram represents the
source honestly. Nothing mechanical can. See SKILL.md Step 6.

## Why the vocabulary stays small

The obvious response to a fidelity failure is to add expressive power:
typed edges for attack and support, node shapes per epistemic status. The
evidence says do not.

- Argument mapping's demonstrated benefits come from **deliberately tiny**
  vocabularies — Rationale ships roughly reason / objection / rebuttal,
  Kialo ships pro / con, and those are the tools behind van Gelder's
  effect sizes.
- Suthers (2003) found that adding ontological elements made student
  diagrams *worse*, because the elements got used incorrectly. Scheuer
  et al.'s review names the costs: cognitive overhead and premature
  commitment to structure, with differentiability mattering more than
  the raw element count.
- Buckingham Shum's fifteen-year retrospective on gIBIS records overhead
  appearing as soon as node types beyond core IBIS were introduced, and
  states the design stance plainly: keep the representational scheme as
  simple as possible.
- This repo's own `think-orbit` reached the same place independently and
  from the other direction: it ships one relation (`inputs`) plus one
  boolean (`load_bearing`), and its spec records the rejection of
  auto-invalidating attack edges because attack-target agreement across
  corpora was zero. A separate double-blind experiment there found that
  richer node taxonomies collapse inter-annotator agreement.

The operative rule that falls out, and the one to apply to any future
proposal: **add slots you fill by copying, never slots you fill by
judging.** "What limit did the source state on this claim" is copied and
stays reliable across readers. "How confident is this claim" is judged
and does not. That is why the card carries a rebuttal field and carries
the author's hedging verbatim, but has no confidence rating.

Three things the vocabulary deliberately does **not** get:

| Wanted | Standard name | Why no new syntax |
|---|---|---|
| "A is inert without B" | linked argument / co-premises | Two edges into one node already say it. No standard system ships an `enables` edge. |
| "attacks / refutes" | rebutting & undercutting defeaters | Belongs in the rebuttal field as text; typed attack edges are the documented failure mode. |
| settled / tentative / superseded | ADR `status`, Carneades statement status | Only carried when the source labels itself. Rating it is judging, not copying. |

---

## Appendix — the measurements

**Squareness alone is not a valid check, and treating it as one produced
a wrong rule.** `min(W,H)/max(W,H)` cannot tell "the rows are laid out
horizontally" from "the boxes happen to be wide", and one candidate
scored *best of three* while its rows were secretly stacked. Every row
below is therefore verified two ways: node coordinates parsed from the
SVG (each declared row must share one y and increase in x — columns, one
x and increasing y), and a PNG rendered on **two** mermaid versions and
compared byte for byte.

Versions: **11.13.0** (the line Obsidian and the VS Code preview ship)
and **11.17.0** (current). Every measurement below was byte-identical on
both, so these numbers are portable rather than a property of one
release.

**How the rows are joined** — a linear 6-node chain, 3 + 3:

| Cross-row edge | Size | Squareness | Rows really horizontal? |
|---|---|---|---|
| **`r1 -->\|…\| r2`** (subgraph to subgraph) | 773 × 530 | 0.686 | **yes** |
| `C -->\|…\| r2` (node to subgraph) | 773 × 958 | *0.807* | **no — stacked** |
| `C -->\|…\| D` (node to node) | 242 × 1386 | 0.175 | **no — stacked** |

The middle row is the whole reason the method changed: **it is the
squarest of the three here, and it is wrong.** It was briefly adopted on
the strength of that number, before the coordinates were read.

An independent reviewer re-ran the three forms on a different fixture and
got a different ORDER — there the false-square form scored below the
correct one. That does not rescue the metric, it condemns it further: a
number whose ranking depends on the fixture is not measuring the property
the rule needs. The collapse itself reproduced identically on both
fixtures.

**Node count**, subgraph-to-subgraph joins, rows of at most 3:

| Nodes | Rows | Size | Squareness |
|---|---|---|---|
| 5 | 3 / 2 | 773 × 530 | 0.686 |
| 6 | 3 / 3 | 773 × 530 | 0.686 |
| 7 | 3 / 2 / 2 | 773 × 824 | 0.938 |
| 8 | 3 / 3 / 2 | 773 × 824 | 0.938 |
| 9 | 3 / 3 / 3 | 773 × 824 | 0.938 |

A row holding a single node (3 / 3 / 1) renders correctly and is not a
defect — an earlier note called it a hazard, on evidence taken from a
diagram whose cross-row edges were the broken node-to-node form.

**Nodes per row**, fixed at 8 nodes so only the row width changes:

| Per row | Rows | Size | Squareness |
|---|---|---|---|
| 2 | 2/2/2/2 | 510 × 1118 | 0.456 |
| **3** | 3/3/2 | 773 × 824 | **0.938** |
| 4 | 4/4 | 1036 × 530 | 0.512 |

Three is a peak, and the fall-off is steep on both sides.

**Branching chains**, columns, 7 nodes in 4 groups:

| Cross-column edge | Size | Squareness | Columns really vertical? |
|---|---|---|---|
| **`c1 -->\|…\| c2`** (subgraph to subgraph) | 874 × 1014 | 0.862 | **yes** |
| `A -->\|…\| B` (node to node) | 1290 × 476 | 0.369 | **no — flattened** |

The same single rule fixes both shapes.

**What the earlier appendix got wrong.** It reported a rows layout at
0.81 and a flat `graph LR` chain at 0.07, and concluded that declaring
`direction` on each subgraph bought the difference. The diagrams it
measured joined rows node-to-node, so on almost every mermaid release
their `direction` was being discarded and the rows were stacking — the
0.81 came from a two-patch window (11.16.0 and 11.16.1) where mermaid
briefly honoured the declaration anyway, and 11.17 restored the
documented behaviour. Those numbers are withdrawn, not adjusted: they
were measured on a shape this spec no longer permits.
