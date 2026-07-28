# Planted-defect A/B — docs-only review mode vs default dispatch

- **Date**: 2026-07-28
- **Plan**: `docs/loom/plans/2026-07-28-docs-citation-check-and-review-mode.md`, Task 5
- **Question it answers**: does `requesting-code-review`'s new docs-only
  dispatch mode (Task 4) reproduce, on a controlled fixture, the detection
  gain that motivated it — the source audit's whole-artifact rounds
  (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md:215-225`,
  rounds 7–9)?
- **Status**: complete, n=1 per arm, direction-only.

## Method

Two review arms, same tier (sonnet), same fixture, dispatched blind
(neither arm was told this was a test or that defects were planted).

- **Control**: current default `requesting-code-review` dispatch shape —
  the diff (`change.diff`) as the review object, code-shaped dimensions
  (Correctness / Architecture / Naming / Security / Tests / Refactoring).
- **Treatment**: Task 4's docs-only mode dispatch text verbatim — whole
  changed artifact (`article.md`) read in full with the diff as context,
  the five prose-defect dimensions (omission / ambiguity / inconsistency /
  incorrect-fact / missing population), plus `check_doc_citations.py`'s
  output run over the changed file included in the dispatch packet
  (treatment's report opens with this pre-pass: *"Population check
  (mechanical pre-pass, verified): `loom-code/scripts/living_spec_drift.py`
  is 42 lines long (confirmed via `wc -l`)"*).

Both arms ran as `general-purpose` agents carrying the dispatch text
directly, not the installed `loom-code:code-reviewer` subagent type — see
Limitations.

## Fixture verification (before any dispatch)

`t5-fixture/fixture-manifest.md` records one planted defect per taxonomy
class in `article.md` (80 lines; diff region `article.md:32-51`, 20 lines,
~25% of the file) against `article_base.md`. Each defect's verify command
was run and its output captured in the manifest **by the fixture-building
agent**, then **independently re-run by the orchestrator** as a second
mechanical pass before dispatch — both transcripts agree:

```
$ grep -n "loom-code/scripts/living_spec_drift.py:92" article.md
38:`loom-code/scripts/living_spec_drift.py:92`.
$ wc -l loom-code/scripts/living_spec_drift.py
42 loom-code/scripts/living_spec_drift.py
$ python3 loom-code/scripts/check_doc_citations.py article.md
article.md:38 -> loom-code/scripts/living_spec_drift.py:92 line 92 exceeds file length (42 lines)
EXIT=1
```
(full command list and output: `t5-fixture/fixture-manifest.md:16-52`)

`diff -u article_base.md article.md` confirmed a single hunk touching only
lines 32-51 — nothing outside the designated diff region was altered,
which is what makes defect #4 (below) a genuine outside-diff instance and
not diff noise.

## Results — per-class detection

| # | Class | Location | Control | Treatment |
|---|---|---|---|---|
| 1 | incorrect-fact / stale citation | `article.md:38` | CAUGHT — 🔴 "fabricated/wrong source citation" | CAUGHT — 🔴 incorrect-fact |
| 2 | ambiguity / false absolute | `article.md:40` | **MISSED** — no finding at this line | CAUGHT — 🟡 ambiguity |
| 3 | missing population | `article.md:43` | CAUGHT — 🟡 "unsupported/unverifiable statistic" | CAUGHT — 🟡 missing population |
| 4 | cross-paragraph contradiction (outside-diff) | `article.md:19-21` vs `:45-47` | CAUGHT — 🔴, quotes both sides | CAUGHT — 🔴 inconsistency, quotes both sides |
| 5 | omission | `article.md:49-50` | CAUGHT — 🔴 "dangling forward reference" | CAUGHT — 🔴 omission |

**Control: 4/5. Treatment: 5/5.** Control's one miss is defect #2, the
unsupported absolute ("Only the checkout-webhook endpoint ever produced a
retry storm") — its verdict never names line 40.

## The unplanted sixth finding

Treatment additionally reported:

> incorrect-fact — lines 27-28 (Method) / referenced again at line 63
> (Adjudication) … anchored to `docs/loom/dogfood/2026-07-20-retry-replay-harness.md`
> … No such file exists anywhere in the repo (checked `docs/loom/dogfood/`
> directory listing and a repo-wide `find` … zero hits).

This citation is scenery the fixture builder wrote for narrative
plausibility (present, byte-identical, in both `article_base.md:27-28` and
`article.md:27-28` — outside the diff, never scored in the manifest's five
rows). Nobody planted it as a defect to be found; it was simply not
verified by the builder before dispatch. Treatment's whole-artifact +
citation-pre-pass framing caught it anyway. **Control's verdict makes no
mention of the harness-doc citation at all** — it did not check it. Net:
treatment's real catch count on this fixture is 5 planted + 1 incidental
= 6; control's is 4 planted + 0 incidental.

## Advisory nits — not false positives

Both arms produced one 🟢: control flagged the `article.md:32` heading
rename as an accurate, non-issue nit; treatment flagged the "batch-export
path" vs. "batch queue" naming proximity (`article.md:45-47` vs. `:71-72`)
as a naming-clarity nit. Neither invents a defect where none exists — both
are explicitly scoped by their authors as "no issue" / "not a
contradiction." Reading 5 (either arm invents a defect) is therefore
**not triggered** by either 🟢.

## Which pre-written reading matched: none

The five readings, quoted verbatim from `t5-interpretation-rules.md`
(written before either arm was dispatched):

> 1. **Treatment catches ≥4 of 5 classes AND control misses the outside-diff
>    contradiction** → the mode reproduces the source-audit rounds-7-9 result;
>    ship as-is. (The outside-diff contradiction is the load-bearing class —
>    it is what diff-scoped review is structurally blind to.)
> 2. **Treatment catches the outside-diff contradiction but ≤3 classes total**
>    → the mode works where it is structurally different and is weak on
>    in-diff prose classes; ship, record per-class gaps as BACKLOG residual,
>    no seventh wording round.
> 3. **Treatment misses the outside-diff contradiction** → the mode's central
>    claim fails on its first controlled test; do NOT ship T4 as-is — surface
>    to the user with both transcripts.
> 4. **Control catches everything treatment catches** → the mode adds no
>    marginal detection on this material; surface to the user — the honest
>    reading is that dispatch text is not the binding constraint for a
>    sonnet reviewer, and the mode's value claim rests on the weak-tier/
>    source-audit evidence only.
> 5. **Either arm flags planted-defect-free text as defective (invents a
>    defect)** → record as arm-level false positive; does not change ship/
>    no-ship by itself but must appear in the note.

None fires cleanly. Rule 1's first clause holds (treatment 5/5 ≥ 4) but its
second clause fails: **control did not miss the outside-diff contradiction
— it caught it, quoting both `:19-21` and `:45-47`.** Rules 2 and 3 require
treatment to miss ≥2 classes or the contradiction outright; it missed
nothing. Rule 4 requires control to catch everything treatment caught; it
did not — control missed the false-absolute class (#2) and the incidental
harness-doc citation. Rule 5's trigger condition is false (adjudicated
above).

**The pre-registered readings did not anticipate this outcome shape:
treatment strictly dominates (5/5 planted + 1 incidental, zero invented
defects) while control also independently catches the load-bearing
outside-diff class the readings were built around.** The disposition below
is therefore judgment applied after seeing the results, not the execution
of a pre-committed rule — flagged as such rather than folded into rule 1's
language.

## Disposition

**Ship — already shipped as Task 4; this measurement supports it and adds
no reason to revisit.** Grounds: strict dominance (treatment ≥ control on
every class, +2 marginal catches — the false-absolute class and the
incidental harness-doc citation), zero invented defects in either arm.

**But the mode's central structural claim — that diff-scoped review is
blind to out-of-diff defects — did not manifest on the class built to test
it.** Control caught the planted outside-diff contradiction unaided. The
claim remains supported only by the source audit's live branch result
(`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md:215-225`,
rounds 7-9: six diff-scoped rounds missed a defect that surfaced only once
review went whole-artifact). The likely reason the discriminating
condition wasn't reproduced here: this fixture is ~80 lines with the diff
region covering ~20 of them (~25%) — reading the remaining three-quarters
of the file is nearly free for any reviewer regardless of dispatch
framing, unlike the source audit's real branch (11 commits, multi-file).
One partial counter-note: the *incidental* harness-doc citation — an
out-of-diff defect nobody scored in advance — was caught only by treatment
and missed entirely by control, which is a small, non-preregistered signal
in the predicted direction; it should not be read as confirming the
preregistered class, only as one more n=1 data point.

A candidate re-test design that would reproduce the discriminating
condition: a large real document (hundreds of lines, multiple sections)
with a small diff (a handful of lines) placing the planted contradiction's
unchanged half far from the changed region. This design is not yet
built; recording it here rather than in BACKLOG.md since it is a
measurement-design note, not an open product item.

## Limitations

- **n=1 per arm.** This establishes occurrence, not rate. A second run
  could differ, most plausibly on the false-absolute class (#2), which sat
  closest to the detection boundary.
- **Agent-type confound.** Both arms ran as `general-purpose` carrying the
  dispatch text as instructions, not the installed `loom-code:code-reviewer`
  subagent type (which also carries the 12-rule baseline injection).
  Behavior should be close but was not measured under the real dispatch
  path.
- **Single material.** One fixture, one defect per class. No coverage of
  multiple defects in the same class, or defects that straddle two
  classes.
- **Sonnet only.** The plan's n≥2-at-weak-tier clause was not exercised;
  haiku behavior on this taxonomy is unmeasured, and the source audit's
  own findings (`docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`)
  suggest weak tiers can diverge from sonnet on judgment-shaped severity
  calls even when the mechanical action succeeds.
- **Fixture-scale ceiling on this result specifically.** As stated above,
  the discriminating out-of-diff condition was not reproduced at this
  file size; this result cannot be read as evidence the mode fails to add
  value on larger documents — only that this fixture did not test that
  regime.
