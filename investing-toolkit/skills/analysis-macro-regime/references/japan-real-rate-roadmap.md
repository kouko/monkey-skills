# Japan Real-Rate Block — Restoration Roadmap (v2.1)

**Status**: Deferred in v2.0.0 — `real_rates` block emits `null` for JP
with a `notes` entry. This file tracks the v1.10.0 C+D+E framework and
what `data-jp/pack.py --pack regime-pack` must emit to restore the
block in v2.1.

---

## v1.10.0 framework (C+D+E)

The v1.10.0 implementation triangulated the JP 10Y real rate from three
independent paths because Japan has neither a deep CPI-linker market
(JGBi outstanding < 1% of JGB stock) nor a single canonical
market-implied real-rate series comparable to US `DFII10`.

### C — ECB ex-post real rate (model-implied)

- Source: ECB Data Portal (Statistical Data Warehouse) JP real-yield
  curve. Series ID(s) tracked under the ECB
  "long-term real interest rate" block; ECB publishes a monthly
  ex-post real yield using realised CPI as the deflator.
- Tier: A (ECB primary).
- Strength: clean, monthly, reproducible.
- Weakness: ex-post (uses past CPI), so it lags forward-looking real
  rates. Acts as the **anchor**.

### D — Tankan inflation expectations (survey-implied)

- Source: BOJ Tankan 「企業の物価見通し」(Inflation Outlook by
  Enterprises) — 1Y / 3Y / 5Y forward expectations across all
  industries, large + SME splits.
- Tier: A (BOJ primary).
- Strength: forward-looking; published quarterly; BOJ's own watchline.
- Weakness: quarterly cadence (not monthly); survey responses cluster.
- Use: subtract Tankan 5Y "all enterprises" expectation from JGB 10Y
  nominal yield to derive a survey-implied 10Y real rate.

### E — JGBi auction-implied breakeven

- Source: MoF (財務省) 物価連動国債 (10-year JGBi) auction results
  + secondary market quote (BOJ Bond Market Statistics).
- Tier: A (MoF primary).
- Strength: market-implied, like US T10YIE.
- Weakness: thin secondary market liquidity; auction-cycle-dependent;
  outstanding stock < 1% of JGBs so price discovery is noisy.
- Use: nominal 10Y JGB yield − JGBi 10Y breakeven = market-implied real
  rate.

### Triangulation rule (v1.10.0)

- Report all three estimates with their tiers.
- Take the **median** as the headline real_10y.
- If C/D/E spread > 50 bp, flag `divergent` in `notes` and emit each
  estimate explicitly so the analyst can pick.

---

## What data-jp regime-pack must emit (v2.1 contract)

For `analysis-macro-regime` to restore the JP real-rate block, the JP
regime-pack JSON must include the following series under
`series` (or grouped equivalents — the resolver tolerates both):

```jsonc
{
  "series": {
    // Existing v2.0.0 minimum
    "DGS10_jp":           [...],   // alias accepted: "jgb-10y"
    "cpi-all-items":      [...],

    // v2.1 additions for real-rate block
    "ecb.real-yield-10y": [...],   // ECB JP real-yield curve, 10Y point
    "tankan.cpi-5y-all":  [...],   // Tankan 5Y inflation outlook, 全規模
    "jgbi.breakeven-10y": [...]    // MoF JGBi auction-derived breakeven
  }
}
```

Naming follows the pattern already established in v1.10.0
(`tankan.cpi-*` / `jgbi.*`) and the data-jp facade convention
(`{source-prefix}.{indicator}`).

---

## Restoration checklist

1. Land the ECB JP real-yield fetcher in `data-jp/scripts/ecb_client.py`
   (already present at v1.10.0 — just needs the regime-pack emit).
2. Add `tankan.cpi-5y-all` extraction to `data-jp/scripts/boj_client.py`
   Tankan adapter.
3. Add `jgbi.breakeven-10y` derivation in
   `data-jp/scripts/mof_client.py` (or equivalent JGBi adapter).
4. Wire all three into `data-jp/scripts/pack.py --pack regime-pack`
   under `series`.
5. In `analysis-macro-regime/scripts/regime_compose.py`, extend
   `compute_us_real_rate` (or add `compute_jp_real_rate`) to read the
   three series, compute C/D/E estimates, take median, emit
   `divergent` flag on > 50 bp spread.
6. Update `references/thresholds-japan.md` with the JP real-rate
   four-tier signal thresholds (mirror the US scheme but calibrate to
   BOJ neutral r* = -0.25%, per BOJ WP24-J-09).
7. Update the cross-country coverage grid in `SKILL.md` (JP real-rate
   row from ⚠️ deferred → ✅).

---

## Timeline

- **v2.0.0** (current): JP real-rate emits `null` + `notes` entry.
- **v2.1** (planned): restoration per checklist above. Gating
  conditions:
  - data-jp regime-pack contract stable (no key renames in 2+ minor
    versions).
  - Tankan 5Y inflation expectation series confirmed available in
    BOJ Tankan API extracts.
- **Owner**: investing-toolkit (data layer) + analysis-macro-regime
  (compute layer); `domain-teams:investing-team` reviews the JP
  threshold calibration.
