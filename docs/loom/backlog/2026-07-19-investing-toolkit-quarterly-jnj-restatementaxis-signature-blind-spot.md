---
name: 2026-07-19-investing-toolkit-quarterly-jnj-restatementaxis-signature-blind-spot
description: investing-toolkit quarterly — JNJ RestatementAxis signature blind spot
status: SHIPPED
---

- What: `_dimension_signature` (sec_edgar_client.py ~:2073, shipped
  2.22.0/#583, untouched by the 52/53-week arc) whitelists only the 4
  breakdown axes + ConsolidationItems and silently DROPS
  `srt:RestatementAxis` — a prior-period reclassification adjustment fact
  (JNJ Q3-2024 Shockwave ±20M, acc 0000200406-25-000209) collapses onto
  the real fact's signature → resolve_binding's intra-filing-ambiguity
  fail-loud fires (correctly, facing FALSE ambiguity) → and the abort is
  whole-series: one poisoned signature refuses the entire ticker (feed
  exits on empty input).
- Fix shape (two independent pieces): (1) treat RestatementAxis like
  ConsolidationItemsAxis — a separate reconciliation qualifier, never a
  breakdown collapse (per
  docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md);
  (2) consider narrowing the abort granularity from whole-series to
  per-signature refusal-with-gap so one poisoned signature doesn't zero a
  ticker. Evidence artifacts: scratchpad sweep_JNJ_series.err +
  jnj_probe.py (session 2026-07-19, volatile).
- Otherwise the sweep validated the design everywhere: JNJ's pack layer
  classified 6,462/6,462 facts dual-lane with zero unclassifiable
  (drifting 13-week quarter-ends absorbed); INTC (also a 52/53-week
  filer) produced 9 correct week_normalized_yoy points (13-vs-14wk,
  hand-verified −23.38%).
