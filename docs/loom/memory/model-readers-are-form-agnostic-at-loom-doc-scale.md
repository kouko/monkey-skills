---
name: model-readers-are-form-agnostic-at-loom-doc-scale
description: At the scale of a loom brief section (5 options × 5 axes, ~4.6 KB document, 10 questions incl. cross-row ordering and an absent-fact trap), a markdown table and a numbered list carrying byte-identical facts showed NO DETECTED difference in model-reader comprehension across 12 fresh readers (haiku ×8, sonnet ×4) — but all 12 scored 10/10 on both forms, so the instrument hit its ceiling and the result licenses 'not detected', never 'no effect'; scope is TEXT CONTAINERS only (table/list/callout), never a diagram or any second representation shown alongside the prose
type: practice
origin: branch loom-doc-container (loom-code 0.85.0, 2026-08-17) — docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md §Addendum
---

Two variants of one brief, differing ONLY in `## Alternatives Considered`
(table vs numbered list, same facts, rest byte-identical), were each read
by fresh haiku and sonnet agents answering ten document-only questions
against a gold key. Every reader on every form scored 10/10 — a ceiling
on both sides.

**Why:** consistent with the literature the seed audit read (frontier
readers are format-indifferent; format harm appears when small models
WRITE structured output, not when they read it). The measured effect the
table rule buys is the human's, and that is what the arc's brief claimed.

**Read the ceiling honestly (corrected 2026-08-19).** 10/10 on every
reader × every form is not a null result — it is an instrument with no
resolution at this difficulty. The questions were recall and comparison
over facts stated in the document; nothing in the set could separate a
better reader from a worse one, so nothing in it could separate a better
form from a worse one either. An earlier wording of this entry concluded
"there is none to gain or lose", which contradicts its own ceiling
observation. The defensible claim is: *at this difficulty, table versus
list produced no detectable difference.* Any stronger claim needs a task
hard enough to score below ceiling first.

**Scope: text containers, never a second representation.** This entry
covers one arrangement of the same words versus another — table, list,
callout, paragraph net. It does NOT cover a diagram, and must not be
cited for one: a diagram is a different representational modality shown
IN ADDITION to the prose, so it changes document length, adds a second
statement of the same content, and introduces a failure mode this
measurement never touched — the diagram silently disagreeing with the
paragraph beside it. Evidence for that case, and the reasons it points
the other way, are in
`docs/loom/research/2026-08-19-cot-diagram-plus-prose-evidence.md`.

**How to apply:** when proposing another TEXT-CONTAINER rule for loom
artifacts (callouts, paragraph nets, more table slots), do not justify it
by model comprehension at this scale — none was detected, so there is no
measured gain to claim; justify it on human readability. If a model-side
claim is needed, test at the regime where the literature shows effects
(≳12 rows × 6 axes, distractor length, aggregation questions across
rows), and design the task to score below ceiling or the run repeats this
one's mistake.
