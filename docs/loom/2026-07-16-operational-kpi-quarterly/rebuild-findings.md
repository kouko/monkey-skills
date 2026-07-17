# Scope-B quarterly — rebuild findings & decision record (2026-07-17)

Status: **facts consolidated; restart scope deferred to the user** (2026-07-17
decision — "consolidate facts first, decide restart scope together"). This doc is
the review surface for that decision. No code decision is executed by writing it.

## What happened

Scope B (quarterly 10-Q operational-KPI) ran through SDD Wave 1. Four data-layer
tasks (T1 duration_months, T2 revenue-concept allow/deny+$-unit filter, T3
per-filing dei calendar, T4 20-F N/A) each passed a per-task spec+quality triad
and are individually sound. T10 (per-quarter coverage honesty) was built on a
**root-cause defect** and took 3 patch rounds, each fixing the same bug on a new
call site. An attempt to split T1-T4 out and ship early, then a review-driven
remediation of the split, BOTH failed whole-branch review on the SAME root cause —
the second reintroducing it in a worse form (a filing-level stamp mislabeling
prior-year comparatives). The split branch and its remediation were abandoned.

## The root cause (one defect, surfaced 4+ times)

`_filing_period_year` returns `int(period_of_report[:4])` — the **calendar** year —
while its docstring claims "the fiscal year a filing REPORTS". Correct for a 10-K
(year-end's calendar year == FY label by SEC convention); **wrong for a 10-Q at
every non-December-FYE filer.** Scope A only fetched 10-Ks, so it shipped dormant
in 2.21.0; scope B reuses the primitive for 10-Qs and inherits the lie at every
call site (selection, per-fact label, coverage grouping, coverage projection).
Symptom-patching one site at a time is why it kept resurfacing. Full detail +
live evidence: `docs/loom/references/xbrl-verification-universe.md` §Root-cause
defect + §Fiscal-calendar findings; the durable lesson:
`docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md`.

## Established facts (all live-verified this session — see verification-universe.md)

- The filing declares its own fiscal year+quarter: `dei:DocumentFiscalYearFocus` /
  `DocumentFiscalPeriodFocus` **present + correct 90/90** across 6 filers × 5 FYs.
- `dei:CurrentFiscalYearEndDate` **exact (0-day)**; a `+12mo` projection drifts
  1-6 days (the two 6-day misses are 53-week years, unpredictable). Both stay
  inside a 20-day tolerance → projection is a safe fallback, the tag is authority.
- Correct fiscal-year label = each fact's OWN `period_end` vs the filing's dei
  calendar — NOT `period_end[:4]` (trap: calendar year) and NOT the filing focus
  stamped on every fact (trap: mislabels comparatives — AAPL FY2019 collapses
  FY2017/18/19 to 2019).
- Filing deadlines are published regulation (10-Q +40/45d, 10-K +60/75/90d; tier
  from `dei:EntityFilerCategory`); lateness is self-declared via Form NT — so
  "not-yet-due vs overdue vs late" is derivable, not estimated.
- Calc-linkbase coverage probe (22 filers): viable but its unique value (insurance)
  is small — insurers' dimensional revenue concepts already carry "Revenue". It is
  a defense-in-depth option, not a prerequisite. (Parked.)
- Industry has NO coverage-report standard; closest art is Compustat's missing-data
  codes + point-in-time (RDQ) "known-as-of-date" modeling. Absence should be
  time-relative: not-yet-due / due-but-unfiled / filed-but-facts-absent.

## Open design question the rebuild must answer (do not pre-decide)

**Should the per-fact `fiscal_year` field exist at all?** The sole downstream
consumer (`kpi_xbrl.py:143`) derives its period key from `period_end[:4]` and its
docstring says "NEVER from the `fiscal_year` column". The field this session spent
two failed rounds trying to label correctly is a field nothing reads. Options for
the rebuild: (a) delete it, classify fiscal period only where a consumer needs it
(T5's job, from period_end vs the dei calendar); (b) keep it but source it
correctly per-fact. Deleting removes the whole trap class; the rebuild plan should
rule on this explicitly rather than inherit the field.

## Spec defects to fix (route via loom-spec — change-folder is read-only to SDD)

1. `spec.md:198` — `CollaborativeRevenue` names a tag that does not exist; the real
   GAAP tag is `RevenueFromCollaborativeArrangement...` (the shipped code correctly
   denies `CollaborativeArrangement`).
2. `spec.md:192-199` — deny clause omits FP class 6 (REIT pro-forma / ladder) that
   its own grounding doc lists; the head clause still governs, and the code covers
   it, but the spec should name it.
3. `spec.md:211-214` — the "$-unit guard rejects a percentage `*Revenue*`" scenario
   credits a mechanism that never fires for its own named fixtures (BA/HON are
   caught by the `Percent` deny first); split into a deny-list scenario + a separate
   ADMIT-default backstop scenario (synthetically covered, no real filer case today).
4. `spec.md:175,182-185` — names `fetch_error` as one of three absence states, but a
   filings-list absence cannot ground a retryable-fetch claim; the real triple is
   not-yet-filed / out-of-range / unclassified. Retitle + re-scope.
5. `spec.md:174` — forbids "deriving quarter boundaries from scratch" but pre-fetch
   selection has no dei and MUST infer; scope that MUST to the classification layer,
   sanction index-metadata derivation for selection.
6. `spec.md:221` — requirement title ("A foreign/ADR filer with no 10-Q") is broader
   than its own 20-F+6-K grounding; narrow it.
7. **NEW requirement**: a fiscal-year range request must select filings belonging to
   those FISCAL years (declared), not filings whose period end falls in the same
   calendar year. Currently uncovered — this is the root-cause defect's spec home.

## Git state (nothing lost; all reversible)

- On `feat-operational-kpi-quarterly`: the 5 doc commits + T1-T4 (8c0df63a..097dc3f4)
  + T10's 3 rounds (46f8ca72, 36d9d45f, f7e45497) + the plan re-home commit
  (e9c31280). T1-T4 UNTOUCHED per the 2026-07-17 decision.
- Abandoned: split branch `feat-quarterly-data-layer` (its version bump + the failed
  remediation `10ff0cbc`). Still in reflog; the one reusable artifact (a real NVDA
  range fixture) is preserved at `git show 10ff0cbc:investing-toolkit/tests/data/
  fixtures/xbrl_quarterly_nvda_range.json`.

## Recommended restart shape (for the deferred decision — not executed)

Surgical: keep T1-T4 (sound, gate-passed, machine-captured fixtures), discard T10's
3 rounds, and re-plan P0 (fix the primitive + decide the `fiscal_year` field) +
T5-T9 + a rebuilt T10 on the corrected primitive, with the spec pass first so the
plan builds on a spec that matches reality. Full-reset (back to zero code) is the
alternative — safer against inherited rot, but discards sound fixtures/tests. The
choice is the user's.
