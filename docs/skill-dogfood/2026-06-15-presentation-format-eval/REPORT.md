# Eval — presentation: question-type-adaptive report structure vs fixed flat template

date: 2026-06-15 · skill: deep-deep-research · status: findings (eval-first, pre-build)

## Question (null to break)
A strong model's output through the current FIXED FLAT template is already good enough that
question-type-adaptive structure isn't worth building (or the model self-structures so a hint is
moot).

## Design
4 seeds × 3 arms, same confirmed claims per seed, content held ~constant, judge STRUCTURE only.
- Arms: **FLAT** (current fixed template: summary/flat-findings/caveats/open-Qs) · **FREE** (model
  picks its own structure, no instruction) · **HINT** (question-type-matched structure directive).
- Seeds: Postgres-vs-MySQL (comparison) · Nvidia-trim (decision) · macOS-MAS (decision + mooting
  gate) · Raft (descriptive CONTROL — tests over-structuring harm).
- Generators sonnet; judges opus (cross-model). 4 judges, one per seed.

## Results (unanimous across 4 cross-model judges)

| seed (type) | best→worst | FLAT loses? | FREE self-structures? | HINT > FREE? |
|---|---|---|---|---|
| Postgres (comparison) | HINT > FREE > FLAT | yes — option-vs-option comparability | **yes** (2 tables + decision matrix, unprompted) | marginal (matrix-first ordering) |
| Nvidia (decision) | HINT > FREE > FLAT | yes — comparability + recommendation + triggers | **partial** (tables + lean-toward, NOT a real matrix) | yes — the options×criteria matrix + rec |
| macOS (decision+gate) | HINT > FREE > FLAT | yes — comparability + recommendation; gate weakened | **yes** (gate-first headline + ASCII decision tree) | marginal (gate already moots; matrix near-redundant) |
| Raft (descriptive CONTROL) | HINT ≈ FREE > FLAT | barely — only learner-ordering | **yes** (sectioned + flow diagram, appropriate) | ~equal; FLAT genuinely adequate |

## The two load-bearing findings

1. **Bitter-Lesson splits capability vs reliability.** FREE (zero instruction) **self-structures**
   well — comparison→tables, decision→tables+lean-toward+gate-first, descriptive→sectioned narrative.
   So the *capability* is intrinsic (null holds for capability). BUT FLAT — identical content — loses
   comparability + recommendation. So the gap is **reliability, not capability** (= the
   [[feedback_ab_baseline_reveals_marginal_behavioral_delta]] pattern: the edit's value is
   reliability, not new behavior).

2. **The ONE thing the model does NOT reliably self-produce: the true options×criteria MATRIX**
   (criteria-rows × options-columns) for decision questions. FREE got ~70–80% (named options,
   lean-toward conditions, fact tables) but only **HINT** produced the actual comparable grid +
   explicit recommendation-with-confidence + triggers-that-flip. This **confirms (refined)** the prior
   prior-art claim ([[feedback_frameworks_are_completeness_audits_not_generators]] neighbourhood).

## Verdict (unanimous): SOFT PROMPT HINT — not a hard template engine, not nothing
- **Not "nothing"**: the fixed FLAT template actively destroys comparison/decision comparability;
  status-quo is the clear loser for those two regimes.
- **Not a hard template engine**: FREE proves the model self-emits the right structure; a coded
  per-type engine is brittle scaffolding that over-fires on mis-detection — the Raft control previews
  the harm (FREE's one near-empty "metrics" table = a slot the content didn't fill; a hard engine
  generalizes exactly that failure).
- **Soft hint wins on cost/value**: it doesn't create the capability (FREE has it) — it reliably
  *orders/completes* it (comparison→attribute-aligned table; decision→options×criteria matrix +
  recommendation + triggers), at near-zero cost. Descriptive/other → leave alone (flat fine).

## The build wrinkle (why this is bigger than the calibration lever)
The current pipeline forces output through **`schemas.py` REPORT_SCHEMA** = `{summary, findings[],
caveats, openQuestions}` (a flat findings array) and **`synthesis.py _render_markdown`** renders that
flat. A table / options×criteria matrix does NOT fit `findings[]`. So a structure hint can't just
PREPEND like calibrate/meta-mode/purpose-fit did — it needs the report to be free-form markdown for
structured types, which means either (a) touching the SYNCED `REPORT_SCHEMA` (forbidden without
sync), or (b) a parallel free-form render path for comparison/decision types. → materially more
invasive than the calibrate lever, whose win came purely from a prepended directive with unchanged
output shape.

## Options
- **A. Soft-hint lever + free-form render path** — opt-in: detect comparison/decision type → PREPEND a
  structure hint AND allow a free-form-markdown report (bypass the flat findings[] render for those
  types). Captures the win; cost = a parallel render path (avoids touching synced schema).
- **B. Minimal: relax the synthesis instruction toward FREE** — let the model choose structure
  (drop the rigid flat mandate) — but blocked by the synced flat REPORT_SCHEMA/renderer unless the
  render path is loosened; without that it can't emit tables. Effectively needs A's render path anyway.
- **C. Don't build / park** — FREE shows the model is ~80% there; the marginal win (decision matrix)
  may not justify touching the schema/render path. Lower value than verification-class work.

## Decision: PARKED (2026-06-16)
Built the brief (`docs/code-toolkit/specs/2026-06-16-presentation-structure-hint.md`, Option A,
cost re-estimated cheap after the code check showed NO JSON validator + house-editable renderer +
REPORT_SCHEMA allows extra fields → zero synced edits needed), then **decided NOT to build now**.

Rationale: this is the most **crutch-like** lever (Bitter-Lesson-fragile). The eval simultaneously
proves "worth changing" (FLAT loses for comparison/decision) AND "the model self-structures ~80% on
its own" (FREE arm) — i.e. presentation scaffolding decays in value as models improve, the opposite
of calibration (verification-class, which *gains* value). The only durable, model-doesn't-self-produce
win is the narrow **decision options×criteria matrix**. Against that: a classifier + a 2nd render path
to maintain, and giving up the machine-parseable `findings[]` guarantee for those report types. Value
ranks below verification-class work. → **Park.** Revisit only if real usage is actually blocked by
flat comparison/decision reports; if so, the **minimal slice = decision-matrix hint only** (skip
comparison + other) is the highest-CP build. Brief retained for pickup.

## Honest limits
- N=4, 1 seed per type, single judge per seed (cross-model opus vs sonnet generators — robust on the
  unanimous direction; the FLAT-loses / soft-hint-wins / hard-engine-risk pattern is consistent).
- Content held ~constant by construction; judges scored structure — but structure↔content bleed is
  possible (a matrix nudges sharper content). Not separated.
- Comparison/decision are the regimes where structure matters most; causal/forecast/how-to untested.
- The "hard engine harms" claim is shown by mechanism (Raft empty-table preview), not by an actually-
  forced wrong structure — directional, not proven.
