---
name: 2026-07-15-operational-kpi-full-dimensional-signature-slice-follow-ups-2026-07-15
description: operational-kpi full-dimensional-signature slice — follow-ups (2026-07-15)
status: OPEN
---

Context: docs/loom/{specs,plans}/2026-07-15-operational-kpi-full-dimensional-signature.md
(branch feat-operational-kpi-xbrl-pilot). All non-blocking review notes, deferred by
agreement of the per-task + whole-branch reviewers.

- What: retire the OLD pilot fixture `investing-toolkit/tests/analysis/fixtures/xbrl_aapl_factpack.json`.
  5 tests still consume it (incl. `test_cli_build_resolves_binding_and_prints_points`); their
  old single-{axis,member} facts have no `dimensions` key, so `resolve_binding` degrades to a
  coincidental concept-only match (`{} == {}`). Migrate those 5 to `xbrl_signature_factpack.json`
  + full-signature bindings, then delete the old fixture. Also fix the now-stale
  `AMBIGUOUS_OVERLAPPING_BINDING` docstring in test_kpi_xbrl.py (it cites fy-range overlap; fy_min/
  fy_max are dead fields). (T1/T7 review + whole-branch 🟡-adjacent.)
- What: `sec_edgar_client.acquire_filing` (~:973) has the SAME `.latest()` amendment-shadowing bug
  that sig-slice T6 fixed in `extract_dimensional_revenue` — a 10-K/A can shadow the real 10-K.
  Apply the same exact-form filter. (T6 code-quality 🟢.)
- What (watch-list, no live evidence yet): `_is_revenue_concept` excludes only
  `ContractWithCustomerLiabilityRevenue*`; sibling deferred concepts `DeferredRevenueCurrent`/
  `Noncurrent` also contain "Revenue". Add to the exclusion set IF a survey ever surfaces them
  polluting a real fact-pack. (Whole-branch 🟢.)
- What (DRY nit): the dedup-by-period key in `kpi_xbrl.resolve_binding` (~:264) re-implements
  ad-hoc `period_end[:4]` slicing instead of reusing `_require_period`'s validated parsing — no
  correctness impact (the surviving representative still fails loud via _require_period). (Whole-branch 🟢.)
- What (next capability, NOT a defect): multi-filing historical fetch — `extract_dimensional_revenue`
  fetches one 10-K (~3 comparative years). The full ~16-year live history needs fetching + stitching
  multiple filings across eras (the offline era-stitching + declared-break machinery already handles
  the cross-era join; only the multi-filing FETCH is missing). Unlocks the deep live trend.
