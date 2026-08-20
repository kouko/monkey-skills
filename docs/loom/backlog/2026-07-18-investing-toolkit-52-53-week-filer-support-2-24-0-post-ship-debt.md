---
name: 2026-07-18-investing-toolkit-52-53-week-filer-support-2-24-0-post-ship-debt
description: investing-toolkit 52/53-week filer support 2.24.0 — post-ship debt
status: closed
---

- Debt (all 🟢, fire on next touch of the named file):
  - kpi lane: `_duration_months`/`_duration_weeks`/`week_lane_band` each
    re-parse period dates via `_duration_span_days` (2-3 parses per fact) —
    single computed span pass-through if the path ever gets hot
    (sec_edgar_client.py, T1/branch review nit).
  - e2e: real-COST Q4 assertion recomputes from the fixture's own operands
    instead of an independently-pinned literal
    (test_kpi_xbrl_quarterly_e2e.py, T6 nit).
  - protocol: "Walmart-style" term overload vs the spec Out-of-Scope's
    "Walmart-style week-53→week-1 lookback" (deep-equity-research-memo.md,
    T7 nit); month-lane derived Q4 mints deliberately omit duration_weeks
    (byte-identical month lane) — revisit only if a consumer needs it.
  - report-equity-memo SKILL.md ~:385 pre-existing "Live-verified …
    AAPL/NVDA/COST" comment describes the 2.23.0-era COST refusal — reads
    stale now that COST classifies; one-line reframe on next touch.
