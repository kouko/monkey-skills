# Brief — presentation structure-hint lever (report-shape, Option A)

date: 2026-06-16 · skill: deep-deep-research · stage: brainstorming → writing-plans
grounding eval: `docs/skill-dogfood/2026-06-15-presentation-format-eval/REPORT.md` (4 seeds × 3 arms, cross-model)

## Problem
(Axis 1 — JTBD) The pipeline renders EVERY report through one fixed flat template (summary +
flat `findings[]` bullets + caveats + open-Qs). For **comparison** ("X vs Y") and **decision**
("should I…") questions this destroys the artifact the reader actually needs — an attribute-aligned
comparison table / an options×criteria matrix + a recommendation — even though the underlying model
*can* produce it. The eval showed the gap is **reliability, not capability**: given freedom the model
self-structures (tables for comparisons, gate-first + decision affordances for decisions), but the
fixed template suppresses it, and the one structure it never self-produces reliably is the true
**options×criteria matrix**. **Job: let comparison/decision reports carry the scannable structure
their question type needs, without forcing structure on question types that don't want it.**

## Users
(Axis 2) Readers acting on a deep-deep-research report for a **comparison or decision** — pick-a-tool,
trim/hold/add, migrate-or-not. Job story: *When I read the report to choose between options, I want
the options laid side-by-side on the same criteria with a recommendation, so I don't have to re-pivot
a flat bullet list into a comparison in my head.*

## Current State Evidence
- **No JSON enforcement exists** (verified 2026-06-16): `grep jsonschema|validate` over `scripts/*.py`
  → zero. `schemas.py report` only `print(json.dumps(REPORT_SCHEMA))` (`schemas.py:208`) — it prints
  the schema *for the model to read*, validates nothing. SKILL.md (`L21`) instructs the model to
  "write the report yourself, emitting JSON that conforms" — self-conformance, not a code gate.
- **REPORT_SCHEMA allows extra fields**: `schemas.py:104-126` has `required`+`properties` but NO
  `"additionalProperties": false` → a model emitting an extra field still conforms; and nothing
  validates anyway. **So no synced-schema edit is needed.**
- **The renderer is the only real constraint, and it's HOUSE code**: `synthesis.py _render_markdown`
  (`synthesis.py:121-159`) reads only `summary / findings / caveats / openQuestions / refuted` via
  `.get()` and prints flat. It has no branch for a table / free-form body. `synthesis.py` is NOT
  synced (house code, editable).
- **Forward** (call site): SKILL.md Stage 6 step 3 (model emits report) → final-render step
  (`synthesis.py report`). Opt-in levers PREPEND to the synthesis prompt; order today
  purpose-fit → meta-mode → calibration → base.
- **Reverse** (SSOT): `prompts.py` synthesis + `schemas.py` REPORT_SCHEMA are SYNCED primitives —
  **not touched** by this design (the lever PREPENDs + edits the house renderer only).
- **Boundary** (template to mirror): `mode_route.py` (classify-prompt + per-mode block + CLI) is the
  pattern for the type-classifier + per-type hint.

Evidence paths: `research-toolkit/skills/deep-deep-research/{SKILL.md, scripts/schemas.py,
scripts/synthesis.py, scripts/mode_route.py}`.

## Decision
Build an **opt-in report-shape lever** (new house module, e.g. `report_shape.py`) that:
1. **Classifies the question type** → `comparison` / `decision` / `other` (a small classify-prompt
   like mode_route; or keyword pre-filter). `other` (descriptive/how-to/causal/forecast) → no change.
2. For `comparison` / `decision`, **PREPENDs a soft structure hint** to the synthesis prompt AND
   instructs the model to additionally emit a free-form **`markdown_body`** field:
   - comparison → "render the core as an attribute-aligned markdown comparison table (options as
     columns, decision attributes as rows) + a short which-fits-which synthesis."
   - decision → "render an options×criteria matrix + a recommendation with confidence + the triggers
     that would flip it; lead with any mooting/dominating factor."
3. **Adds a render branch to `synthesis.py _render_markdown`** (HOUSE code): if the report carries a
   non-empty `markdown_body`, render it (with the `# question` header + the existing caveats/open-Qs/
   refuted tail appended for continuity); else fall back to the current flat findings render. The
   model still also emits the normal `findings[]` (so the structured/machine-parseable form is
   retained alongside the rich body — no loss).

**Soft hint, NOT a hard template engine** (eval verdict): the model self-structures; the hint only
*reliably orders/completes* it (esp. the decision matrix the model misses on its own). Hard per-type
engines over-fire on mis-detection (the Raft control previewed the empty-table harm). **Opt-in +
additive**: default flat path byte-unchanged; `other` types unchanged.

Cost (re-estimated after the 2026-06-16 code check — cheaper than first thought): one new house
module (classify + hint, mirrors mode_route/calibrate) + one render branch in the house renderer +
a SKILL.md opt-in subsection. **Zero synced-primitive edits**, no validator to fight.

## Alternatives Considered (Axis 4)
- **B — relax instruction toward FREE, no classifier/hint**: gets ~80% (model self-tables) but
  **misses the options×criteria matrix** every time (eval) — and still needs the same renderer branch
  to emit any table. So B = "A minus the cheap high-value hint"; not worth saving the hint. Rejected.
- **Hard template engine** (force a structure per detected type): rejected — over-structures on
  mis-detection; Raft control shows the slot-it-can't-fill harm; redundant with model's self-structuring.
- **Don't build / park**: viable — the win is real but marginal-over-FREE except the decision matrix,
  and it's lower value than verification-class work. The fallback if A isn't pursued.

## What Becomes Obsolete (Axis 5)
Nothing removed (additive opt-in). The fixed flat render stays as the default + the `other`-type path.

## Out of Scope
- Editing `prompts.py` / `schemas.py` (SYNCED — and unnecessary; renderer is house code).
- A hard template engine / mandatory per-type layouts.
- `other` question types (descriptive/how-to/causal/forecast) — they keep the flat path; structure
  hints for those are not eval-justified (Raft control: flat is fine).
- Default-on (ship opt-in like sibling levers; revisit after more eval).
- Interaction polish with the other levers beyond declaring a PREPEND order (plan-time detail).

## Open Questions
- **Prepend order vs the other levers**: the structure hint governs OUTPUT SHAPE (orthogonal to
  stance/relevance/calibration). Propose it as the OUTERMOST prepend (frames the whole output), but
  exact placement is a plan-time call — confirm it doesn't fight calibration's "summary ≤ body".
- **Classifier confidence / fail-safe**: on low-confidence or `other`, fail-safe to the flat path
  (never force structure) — mirrors meta-mode's fail-safe-to-unsettled.
- **`markdown_body` + flat findings co-existence**: model emits both; renderer prefers body. Confirm
  this doesn't double-render or bloat. (Decision: body replaces the Findings section only; Summary/
  Caveats/Open-Qs/Refuted still from their fields for consistency — or fold all into body? plan-time.)
- Whether to also pass the type signal to calibration (e.g. comparison tables still must obey
  weakest-link confidence in cells) — likely yes, note for plan.
