---
name: model-readers-are-form-agnostic-at-loom-doc-scale
description: At the scale of a loom brief section (5 options × 5 axes, ~4.6 KB document, 10 questions incl. cross-row ordering and an absent-fact trap), a markdown table and a numbered list carrying byte-identical facts produce identical model-reader comprehension — 12 fresh readers (haiku ×8, sonnet ×4) scored 120/120 on both forms — so a container-routing rule's beneficiary at this scale is the human reader; argue it on human readability, not on model comprehension
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

**How to apply:** when proposing another container rule for loom
artifacts (callouts, paragraph nets, more table slots), do not justify it
by model comprehension at this scale — the evidence says there is none to
gain or lose; justify it on human readability, and if a model-side claim
is needed, test at the regime where the literature shows effects (≳12
rows × 6 axes, distractor length, aggregation questions across rows).
