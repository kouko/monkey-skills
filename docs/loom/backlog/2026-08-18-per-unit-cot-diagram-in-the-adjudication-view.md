---
name: 2026-08-18-per-unit-cot-diagram-in-the-adjudication-view
description: the adjudication view's translate step should emit one 譯注-tagged mermaid CoT diagram per unit, rendered directly beneath that unit's target-language rendition — no renderer change (measured), no new skill, three guardrails; the diagram never enters the agent-consumed artifact
status: OPEN
origin: kouko, 2026-08-18 — raised during the adjudication_render staleness arc after asking whether per-paragraph CoT diagrams (as used in the Obsidian vault's references/ notes) belong in the source markdown or the view
start: after the adjudication_render staleness arc (docs/loom/specs/2026-08-18-adjudication-render-staleness-visible.md) merges
---

# Per-unit CoT diagram in the adjudication view

The adjudicator reads a brief/plan through the document view. A mermaid
diagram explaining each unit's content would help that reading. The
question the arc settled was **where the diagram lives**, and the answer
follows from who benefits.

- **Origin**: kouko, 2026-08-18 — raised during the adjudication_render staleness arc after asking whether per-paragraph CoT diagrams (as used in the Obsidian vault's references/ notes) belong in the source markdown or the view
- **Start**: after the adjudication_render staleness arc (docs/loom/specs/2026-08-18-adjudication-render-staleness-visible.md) merges

## Decided (2026-08-18 session, with the user)

**The diagram is written by the translate step into the unit's
`rendition`** — the same LLM step that already produces the
target-language text. It therefore lives in the view, never in the
source artifact that `writing-plans` and implementers consume.

**Layout: option A** — the diagram renders directly beneath that unit's
target-language rendition, inside the same block; the English
`source_text` stays in its collapsed `原文` `<details>` below,
unchanged. Rejected: diagram beside the expanded English source
(kills the collapsed-by-default reading line), and a three-column
译文｜原文｜图 layout (52rem reading width cannot carry it, and the
print stylesheet would need rebuilding).

**Measured, not assumed**: a mermaid fence written into `rendition`
renders today with **zero renderer change** — probed 2026-08-18 on
`loom-code/scripts/adjudication_render.py` (0.86.0): 1 `class="mermaid"`
div, bundled mermaid.js emitted, the `譯注` marker preserved.
`adjudication_split.py`'s anchor extraction already skips fenced blocks
(`FENCE_RE`, `:56,126`), so a diagram adds no lint burden.

## Why not the source artifact

The plan is re-read on every implementer dispatch, so a per-section
diagram multiplies its cost by the dispatch count, and a diagram that
disagrees with its prose becomes a second source of truth a downstream
agent may follow. Against that: this repo's own 2026-08-17 A/B
(`docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md:74`)
found **no measurable comprehension difference for model readers** —
"the table rule buys human readability, and the model reader is neither
helped nor hurt". The benefit accrues to the human, who reads the view.
Caveat recorded honestly: that A/B tested tables, not diagrams, and one
structure in a 4.6 KB document — not ten diagrams. So "no effect on
agent interpretation" is unproven for the per-unit case; keeping the
diagram out of the agent-consumed artifact is what makes the question
moot rather than answered.

## Why not a standalone skill

`visual-companion.md` is already the when/how-to-draw SSOT (five
diagram types, channel degradation, and the 2026-08-17 diagram-semantics
rule: edges carry the causal relation, nodes carry title + supporting
reason), pointed at by brainstorming, writing-plans and plan-format, and
pinned by `test_visual_companion_semantics.py`. A skill would copy that
guidance and drift from it — the same multiple-copies failure this arc's
parent bug is about. The behavior is also a sub-step of a running
pipeline with no independent trigger, and loom-code already carries 14
skills against a known description-budget ceiling.

**Unpark to a skill only if** the diagram step grows its own workflow
(type routing, post-generation validation, a retry loop), **or** a
non-loom caller appears — and in that case the question is whether to
merge with `obsidian:obsidian-mermaid-visualizer`, not to open a third
copy.

## Three guardrails (two already exist — reuse, do not re-invent)

1. **Provenance**: the diagram is a translator addition, so it carries
   the protocol's existing `譯注` tag (adjudication-view protocol,
   §"Translator additions — provenance-tagged"). The adjudicator must be
   able to see at a glance that the picture is not in the artifact.
2. **Unit-scoped**: a diagram may depict only facts present in its own
   unit — no cross-unit synthesis, no content the artifact does not
   carry. This is the existing unit-1:1 rule, not a new one.
3. **Mechanical check (new, ~10 lines)**: `adjudication_lint.py` fails
   when a `rendition` contains a mermaid fence without the `譯注` marker.
   Cheap, mechanical, no judgment required. Per
   `docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md`, it
   needs a probe proving it cannot pass by matching nothing.

## Residual risk, stated

The diagram is machine-authored, unreviewed, and regenerated differently
on every render, and the adjudicator sees it **at a sign-off gate**. The
guardrails bound what it may claim; they do not verify that what it
claims is right. Accepted deliberately: the alternative that removes
this risk (human-authored companion file) puts the drawing work on the
human at authoring time, and a slot that needs manual upkeep decays to
N/A.

## Scope when this arc opens

- Protocol edit: the translate step's diagram duty + the `譯注` and
  unit-scope bindings, pointing at `visual-companion.md` for how to draw.
- `adjudication_lint.py`: guardrail 3 + its no-skip probe.
- No renderer change (measured above). No new skill. No change to any
  agent-consumed artifact template.
