---
name: 2026-08-18-remaining-container-rules-callout-toc-paragraph-net-plan-tables
description: the four container rules the artifact-layer table-routing arc (PR #699) deliberately left out — callout roles, TOC, a 2–4-sentence paragraph net, plan-level tables — each with the cost/risk that parked it and the evidence that would unpark it
status: OPEN
origin: PR #699 close-out (2026-08-17) — brief `docs/loom/specs/2026-08-17-artifact-table-routing.md` §Out of Scope; user-ratified evaluation in the same session that only comparison→table was worth doing without further evidence
start: docs-reviewer's table-routed-prose omission dimension yields its first real findings, or ≥30 post-#699 briefs/specs exist so the seed audit's corpus measurement can be re-run — whichever comes first
---

- Origin: PR #699 close-out (2026-08-17) — brief
  `docs/loom/specs/2026-08-17-artifact-table-routing.md` §Out of Scope;
  user-ratified evaluation in the same session that only comparison→table
  was worth doing without further evidence

- Start: docs-reviewer's table-routed-prose omission dimension yields its
  first real findings, or ≥30 post-#699 briefs/specs exist so the seed
  audit's corpus measurement can be re-run — whichever comes first

**Where this comes from.** The seed audit
(Obsidian `research/2026-08-17 loom 產出文件的可讀性結構稽核.md` and its
companion inventory note) measured a readable 231-note corpus at 97%
table / 89% callout / 75% Mermaid / 2.5 headings per 1k chars / 70-char
median paragraph, against loom plans at 3% table / 0% callout. PR #699
shipped the one rule that was both the measured main effect and
mechanically checkable (comparison-shaped content → table, bound at
template slots + the spec validator) plus the diagram-semantics rule. The
rest of the inventory was evaluated and parked, not rejected.

**The four items, with the judgment that parked each** (so the next
session does not re-derive it):

| Rule | What it would do in loom | Cost / risk today | Unpark when |
|---|---|---|---|
| Callout roles (`> [!NOTE]`-style, one type per job) | Pull key conclusions / limits / open items out of prose | Function already carried by required sections (`## Decision`, `## Open Questions`, `## Blind spots`); GitHub renders only 5 alert types (no abstract/success/question); a `> - BI-1` line breaks `check_scenario_coverage.py:123`'s declaration regex; adjudication split does not model blockquotes; type choice is judgment-shaped (weak models mis-pick) | A finding shows a required section is not enough to surface a limit, AND the two parsers are taught blockquotes first |
| TOC (verbatim heading list) | Navigation at the top of brief/plan | H2 units already drive the adjudication view; a TOC is a content-free extra unit for `adjudication_split.py` | Only if a reader-side complaint appears; expected never |
| Paragraph net (≈2–4 sentences, one idea per paragraph) | Bound the pure-narrative paragraphs containers cannot reach | Obsidian data shows containers explain only part of the short-paragraph effect (r=−0.255); English sentence counts need their own threshold; no loom-internal evidence yet; would be a docs-reviewer sentence + a mechanical sentence-count check | The table dimension's findings show long narrative paragraphs surviving beside tables |
| Plan-level tables (task summary / Acceptance as table) | Read a plan's task list at a glance | Per-task fields are already structured; a hand-written summary table is a second source that drifts (SSOT violation); the Task-flow diagram already carries dependencies; plans are read mostly by machines | Only as a generated view (rendered from the per-task fields, like `plan_card.py`), never hand-written |

**Ordering if unparked:** paragraph net first (cheapest, one reviewer
sentence + one mechanical check), plan tables only as a derived view,
callouts last (parser work first), TOC probably never.

**Do not stack rules blind.** PR #699's table rule has not yet been
observed in a real whole-branch docs review; adding rules before that
would make the evidence for each indistinguishable (the same reason the
arc shipped one rule, not four).

**Related evidence:** `docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md`
(cold-reader A/B: brief table 0/2→3/3, diagram two-layer nodes 0→7/7;
reader-comprehension table vs prose 120/120 both forms — the rules buy
human readability, not model comprehension);
`docs/loom/memory/model-readers-are-form-agnostic-at-loom-doc-scale.md`;
`docs/loom/memory/a-cold-template-probe-proves-slot-binding-not-pipeline-drift.md`.
