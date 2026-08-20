---
name: 2026-08-07-52-53-week-calendar-boundary-never-verified-against-a-real-filer
description: The quarterly series' day-span classifier was never verified against a 52/53-week filer — Task G planned it, the branch shipped without it
status: open
origin: planned as Task G of the US quarterly-statement-series arc (`docs/loom/plans/2026-07-28-us-quarterly-statement-series.md`), which shipped 9 of its 10 tasks. A whole-branch reviewer noticed the branch had filed backlog entries for two lesser deferrals while the one planned blocking task that was never built had neither an amendment nor an entry. **Verified 2026-08-07**: neither `us_52_53_week_periods.json` nor `test_52_53_week_period_keys_classify_to_their_exact_kind` exists in the tree.
start: before trusting the quarterly series on a 52/53-week filer — retailers and many manufacturers use one. Also the natural moment to close brief Open Question 4, which this task was written to answer.
---

- Start: before trusting the quarterly series on a 52/53-week filer — retailers
  and many manufacturers use one. Also the natural moment to close brief Open
  Question 4, which this task was written to answer.
- Origin: planned as Task G of the US quarterly-statement-series arc
  (`docs/loom/plans/2026-07-28-us-quarterly-statement-series.md`), which shipped
  9 of its 10 tasks. A whole-branch reviewer noticed the branch had filed backlog
  entries for two lesser deferrals while the one planned blocking task that was
  never built had neither an amendment nor an entry. **Verified 2026-08-07**:
  neither `us_52_53_week_periods.json` nor
  `test_52_53_week_period_keys_classify_to_their_exact_kind` exists in the tree.
- **A contradiction to settle first, between this entry and the task it carries.**
  Plan Task G's Description says a 52/53-week filer's quarters "can fall outside a
  naive 80-100 day window". Measured against `_DISCRETE_QUARTER_SPAN = (80, 100)`
  that is wrong for the quarters themselves — 13 weeks is 91d and 14 weeks is 98d,
  both inside — and Task G's own RED already concedes "a 91-98 day span". The real
  boundary risk is the ANNUAL window: a 53-week year is 371d against `(350, 380)`,
  which is inside, but a 52-week year is 364d and the YTD spans move with it. So
  the task's stated motivation is imprecise; its acceptance criteria are not.
  Whoever picks this up should fix the Description rather than inherit it.
- **Prior art, so this is not started from zero**: the sibling entry
  `2026-07-18-investing-toolkit-52-53-week-filer-support-2-24-0-post-ship-debt`
  (SHIPPED) covers 52/53-week machinery that already exists elsewhere in the KPI
  lane — `_week_lane_duration_class(week_lane_band, duration_weeks)` at
  `investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py:180`, which is
  fail-closed (returns `None` rather than guessing an unknown band). **Verified
  2026-08-07 by opening it.** There is no contradiction — that lane classifies a
  filer's week band from XBRL facts, while this entry is about
  `kpi_us_quarterly_periods` bucketing a period key by raw day span — but
  whoever picks this up should read it first rather than re-deriving the domain.
- **What is unverified**: `kpi_us_quarterly_periods.period_kind` buckets a period
  by day span, with `discrete_quarter` at 80–100 days. A 52/53-week filer's
  quarters are 13 weeks (91d, inside) or 14 weeks in a 53-week year (98d, also
  inside) — but the annual window is 350–380 and a 53-week year is 371 days, and
  nothing has measured a real filer's actual keys against those windows.
- **What ships without it, and why it is the safe direction**: an out-of-window
  span classifies `unknown`, which the module documents as an answer rather than
  a failure. So the risk is a quarter that reads `unknown` instead of
  `discrete_quarter` — visible, not silent. The unsafe direction (a cumulative
  column mislabelled as a quarter) is structurally prevented by the windows being
  disjoint, which Task E's guard now enforces loudly.
- **Carry these two findings from Task E's review** — they are the reason this
  task is not a free-standing test:
  1. **Task E's role resolution is correct only while Task C's four windows stay
     DISJOINT and ASCENDING.** A reviewer widened the nine-month window to
     `(260, 380)` — a widening this task's own acceptance authorises — and
     measured: on a fiscal year carrying both a ~273-day and a ~364-day column
     both match, the role has two candidates, and Task E correctly refuses. The
     consequence is that **Q3 and Q4 are both suppressed, silently, for every
     such year**. Since Task E round 2, `_reject_overlapping_role_windows` raises
     at window-read time instead — so expect a `ValueError` if you widen into an
     adjacent window. That is the guard working.
  2. **Task E requires EXACTLY TWO year-to-date windows.** Widening the existing
     two is safe; adding a third is a breaking change — a third window names no
     third role, so there is nothing to pair it with.
- Fix shape: capture one 52/53-week filer's quarters into a fixture, assert each
  real period key against its ONE expected kind (13-week and 14-week quarters →
  `discrete_quarter`; the 371-day annual → `annual`; each YTD → `ytd`).
  **Disjunctive acceptance is forbidden** — "classifies OR returns unknown" would
  pass without any 52/53-week-specific work. If a row does not match, widening
  Task C's windows is part of the fix, subject to the two findings above.
- Note on span parameterisation: the arc's fixtures are captured with a
  run-date-relative `years=N` span, which already cost one fixture a filing
  between two consecutive days. Brief Open Question 2 (years back vs explicit
  start/end) is still open and is worth settling before capturing a new fixture,
  or this one inherits the same property.
