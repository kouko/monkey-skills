---
name: 2026-07-24-investing-toolkit-kpi-tearsheet-multi-granularity-per-market-period-menu
description: investing-toolkit KPI tearsheet — multi-granularity + per-market period menu
status: OPEN
origin: 2026-07-24 first real tearsheet dogfood (JNJ, US annual — CLEAN) then a mixed annual+quarterly probe surfaced that a flat date-sorted table interleaves granularities; user asked whether it should be per-market. Research: `docs/loom/research/2026-07-24-market-period-granularity-regimes.md` (PR #609), three regulator-primary-source agents (US/JP/TW/KR/CN) + a layout survey + a local `_qtrs` probe.
start: a real need to tearsheet a TW/JP company (monthly / half-year data), or the next substantive touch of `report-kpi-tearsheet` / `kpi_store`'s period classifier. NOT triggered by US-only annual+quarterly use — that works today.
---

- Start: a real need to tearsheet a TW/JP company (monthly / half-year data), or
  the next substantive touch of `report-kpi-tearsheet` / `kpi_store`'s period
  classifier. NOT triggered by US-only annual+quarterly use — that works today.
- Origin: 2026-07-24 first real tearsheet dogfood (JNJ, US annual — CLEAN) then a
  mixed annual+quarterly probe surfaced that a flat date-sorted table interleaves
  granularities; user asked whether it should be per-market. Research:
  `docs/loom/research/2026-07-24-market-period-granularity-regimes.md` (PR #609),
  three regulator-primary-source agents (US/JP/TW/KR/CN) + a layout survey + a
  local `_qtrs` probe.
- What (the coupled design the research scoped — do NOT cut it into "annual vs
  quarterly", that was the US-centric assumption the research disproved):
  1. **Sub-quarter classifier, STORE-owned.** `_qtrs` refuses spans <1 quarter, so
     a monthly period gets a null `period_axis_key` and renders as an orphan
     column (12×N for N monthly KPIs — probe-verified). Extend the classifier to
     give monthly (and any sub-quarter) span a real identity. Belongs in the store,
     never the formatter (2.32.0 Decision: alignment identity is store-owned).
  2. **Per-market granularity menu**, not a global binary: US = annual+quarterly;
     TW = annual+quarterly+**monthly** (證交法§36, mandatory); JP = annual+
     **half-year** (the sole legally-mandated interim filing since the 2024 FIEA
     reform)+quarterly(cumulative, now exchange-rule); KR/CN = annual+half-year+
     quarterly(cumulative). No market files a standalone Q4; JP/KR/CN file no
     standalone Q2 — do NOT build Q4/Q2 collision handling for ingest.
  3. **Discrete-vs-cumulative axis** must surface in the rendered output — US/TW
     file both natively; JP, CN, and KR-through-Q3 file cumulative-only (discrete
     = derived by subtraction). Two columns that look alike but sit on different
     axes is the silent-lie class this repo keeps getting bitten by.
  4. **Layout**: separate views per granularity (a `--granularity` flag or
     distinct sections), never one date-sorted table — every shipped product
     surveyed (US terminals, 四季報, 株探) keeps them apart; none groups quarters
     under a year.
  Already-solid foundation (do not re-solve): the store's raw `(period_start,
  period_end)` identity already separates a cumulative Q3 from a discrete Q3
  unmodified — the hard cross-market case falls out of the observation-history
  date-pair decision.
- Sequencing note: this is the tearsheet successor in the longitudinal trilogy
  (tearsheet ✅ 2.32.0 → THIS / Part-3 hardening → replay-matrix). User-stated
  intent (2026-07-24): decide priority against Part 3 after more real tearsheet
  use; the monthly gap only bites on TW/JP data, so US-only use does not force it.
