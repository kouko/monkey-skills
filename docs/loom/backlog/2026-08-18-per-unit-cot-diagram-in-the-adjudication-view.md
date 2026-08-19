---
name: 2026-08-18-per-unit-cot-diagram-in-the-adjudication-view
description: a 譯注-tagged mermaid CoT diagram per unit in the adjudication view, never in the agent-consumed artifact — but the always-on diagram-beside-prose layout decided inside this entry is REJECTED by 2026-08-19 evidence (redundancy and expertise reversal predict harm for an expert at a sign-off gate, and a machine-drawn diagram compounds it); what survives is a toggle rather than a pair, and a navigation purpose rather than a comprehension one, neither buildable before the measurement in docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md is run
status: OPEN
origin: kouko, 2026-08-18 — raised during the adjudication_render staleness arc after asking whether per-paragraph CoT diagrams (as used in the Obsidian vault's references/ notes) belong in the source markdown or the view
start: NOT the original merge condition (met, and superseded) — this arc opens only after the three-condition measurement in docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md has been run and shows the diagram earns its place
---

# Per-unit CoT diagram in the adjudication view

The adjudicator reads a brief/plan through the document view. A mermaid
diagram explaining each unit's content would help that reading. The
question the arc settled was **where the diagram lives**, and the answer
follows from who benefits.

- **Origin**: kouko, 2026-08-18 — raised during the adjudication_render staleness arc after asking whether per-paragraph CoT diagrams (as used in the Obsidian vault's references/ notes) belong in the source markdown or the view
- **Start**: NOT the original merge condition (met, and superseded) — this arc opens only after the three-condition measurement in docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md has been run and shows the diagram earns its place

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

> **RETRACTED 2026-08-19 — do not cite the sentence above.** All 12
> readers scored 10/10 on both forms, so that A/B hit its ceiling and
> licenses "not detected", never "neither helped nor hurt". It also
> compared two text containers, not a diagram. See the corrected
> `docs/loom/memory/model-readers-are-form-agnostic-at-loom-doc-scale.md`
> and §"Evidence arrived 2026-08-19" at the end of this entry.

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

## Start condition met; a narrowing candidate from 2026-08-19

The staleness arc this entry's `start` names
(`docs/loom/specs/2026-08-18-adjudication-render-staleness-visible.md`)
merged as PR #706 (loom-code 0.88.0). This entry's start condition is
now met and the arc can open.

Separately, `docs/loom/plans/2026-08-19-field-value-microstructure.md`
classified the loom corpus's long-paragraph population into (T)
comparison-shaped / (S) sequential-field-list / (N) reasoning-chain
(8 / 26 / 23 of 57 measured) and left (N) — the class this diagram is
for — entirely to this entry (see Out of Scope in
`docs/loom/specs/2026-08-19-field-value-microstructure.md`). That
measurement is a **narrowing candidate** for this entry's scope when it
opens: the diagram duty need only fire on units whose prose is (N)-shaped
(a reasoning chain), not on every unit — (T)/(S)-shaped units already get
a structural rule (table or bullet) that the diagram would duplicate.
Not decided here; the arc that opens this entry should re-derive the
(N) test from `plan-format.md`'s narrative-declaration grammar rather
than re-classifying paragraphs by hand.

## Evidence arrived 2026-08-19 — the design above needs revising before it opens

Commissioned by kouko after this entry's start condition was met. Full
record with citations:
`docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md`.

**Do not open this arc against the design decided above.** That design —
diagram and prose rendered together, always on — is the one configuration
the literature predicts is worst for this reader.

Three findings change it:

1. **Expertise reversal.** Experts perform better with diagram-only OR
   text-only than with both; the integration work is itself the cost once
   the reader already understands the domain. The reader here is an expert
   at a sign-off gate — though every study behind the effect measures
   learners in instructional settings, and none covers review at a gate,
   so the transfer is argued, not demonstrated. This does not say "no diagram" — it says "not both
   at once", which is a toggle, and this entry never considered one.
2. **Redundancy survives the layout fix.** Option A above (diagram beneath
   the rendition) is the textbook remedy for split-attention, which was
   never the risk. Redundancy fires under perfect integration. The layout
   decision was sound and solves a different problem than it was credited
   with.
3. **The machine-generation risk is worse than "accepted residual".** LLM
   diagram hallucination rises with source complexity and models fail to
   self-detect it; separately, plausible-looking AI output raises trust and
   automation bias suppresses scrutiny. A subtly wrong diagram at a
   sign-off gate is therefore more likely to be trusted than caught —
   stated as the research record states it, an inference across two
   literatures, not a study of "wrong diagram versus no diagram", which
   nobody has run. The
   §"Residual risk, stated" section above accepted this risk without
   knowing it compounds.

**What survives.** Keeping the diagram out of the agent-consumed artifact
is MORE justified than this entry argued, but for a replaced reason: not
"the model reader is unaffected" (untested, and the nearest evidence points
at contradiction risk and attention dilution) but "a second statement of
the same content carries an uncharacterized failure mode with no measured
offsetting gain". The §"Why not the source artifact" section's citation of
the 2026-08-17 A/B must not be reused as-is — that result is at ceiling and
covers text containers, not diagrams; see the corrected
`docs/loom/memory/model-readers-are-form-agnostic-at-loom-doc-scale.md`.

**The candidate that is still alive.** Reframe the purpose from
comprehension to **navigation** — the diagram helps decide which paragraph
deserves a close read, not what it means. Redundancy never fires if the
reader does not read both. No evidence exists for or against this, which
makes it the honest thing to measure rather than the honest thing to
assume.

**Measure before building, and design the task to score below ceiling.**
The A/B shape, including the load-bearing condition where the diagram
disagrees subtly with its prose, is in the research record's final section.
