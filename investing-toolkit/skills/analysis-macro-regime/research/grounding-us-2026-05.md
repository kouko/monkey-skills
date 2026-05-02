# US Macro Regime — Grounding Delta Refresh 2026-05-02

**Type**: Partial recalibration per [recalibration-protocol.md](../references/recalibration-protocol.md) — short delta from prior vintage; full audits covered separately.

**Prior full grounding**: 2026-04-18 (v1.9.0, commit `59fe397`).
**Prior partial refresh**: 2026-04-19 (v1.11.0 addendum, commit `31f7ec8`).
**This refresh**: 2026-05-02 (PR-2 of v2.1.0 Phase 1 per ADR-0004).

## Status

**No material policy events between 2026-04-19 and 2026-05-02.** The 13-day window did not trigger any of the mandatory recalibration events listed in `recalibration-protocol.md`:

- ❌ No FOMC SEP update (next: Mar / Jun / Sep / Dec 2026)
- ❌ No new HLW vintage from NY Fed (typically Q1)
- ❌ No CBC quarterly statement (next: 2026-Q2 ~ June)
- ❌ No policy-rate change since 2025-12 (Fed held)
- ❌ No regime shift events

**Conclusion**: `thresholds-us.md` remains current at 2026-Q1 vintage. Calibrations carried over verbatim into `calibrations/us.yaml`.

## Calibration carry-over (verbatim from thresholds-us.md)

| Field | Value | Source vintage |
|---|---|---|
| `inflation_target` | 2.0 | FOMC 2012-01-25 |
| `inflation_target_framework` | FIT (post-FAIT) | Powell Jackson Hole 2025-08-22 |
| `policy_rate_neutrality.hlw_real` | 0.75 | NY Fed 2025-Q4 |
| `policy_rate_neutrality.lubik_matthes_real` | 1.68 | Richmond Fed 2025-Q4 (updated 2026-03-10) |
| `policy_rate_neutrality.fomc_sep_longer_run_real` | 1.0 (median) | FOMC Dec 2025 SEP |
| `nairu` | 4.5 (band 4.4-4.6) | CBO 2026 forecast |
| `real_rate_4tier.clearly_restrictive.lower` | 1.75 | Cross-method central tendency 1.25-1.75% |

## Anchored Quotes (verified currency)

> "The current stance of monetary policy is modestly restrictive."
> — Williams, "Resilience" speech, 2025-12 (referenced in [thresholds-us.md](../references/thresholds-us.md))

> "The labour market remains close to full employment."
> — Powell, FOMC press conference 2025-12-17

These remain the qualitative anchors used in `classify_us.py`'s `fed_qualitative_anchor` field (surfaced when `real_rate_decomposition.band` is `moderately_restrictive` or `clearly_restrictive`).

## Phase 1 PR-2 Implementation Notes

- `calibrations/us.yaml` extracts `thresholds-us.md` numeric values as YAML keys for machine-readable consumption by `classify_us.py`
- `classify_us.py` reads YAML calibration via `load_calibration("us")` and applies 4-tier real-rate band thresholds + 4-state yield curve thresholds
- Fed qualitative anchor surfaces only on restrictive bands — preserves v1.9.0 design intent that the anchor is a "decisive" supplement, not always-shown commentary
- `native_verdict.ic_quadrant` mirrors legacy classifier output for parity (regression test in `test_chain_us_classifier_e2e`)

## Next Recalibration Triggers

Watch for:
- **FOMC Mar 2026 SEP** (mandatory; ~30-day latency target) — will refresh longer-run real anchor
- **NY Fed HLW Q2 2026 vintage** (recommended) — refreshes hlw_real
- **Jackson Hole 2026** (recommended) — potential FIT framework revisits
- **Williams next speech** with quantitative real-rate framing — refresh fed_qualitative_anchor

If any fires, update `thresholds-us.md` first, then re-extract numeric values into `calibrations/us.yaml`. CI drift-detection test (planned for later PR) will catch numeric mismatches.
