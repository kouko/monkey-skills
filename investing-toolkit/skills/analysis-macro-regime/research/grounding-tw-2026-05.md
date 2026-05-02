# Taiwan Macro Regime — Grounding Delta Refresh 2026-05-02

**Type**: Partial recalibration per [recalibration-protocol.md](../references/recalibration-protocol.md) — short delta from prior vintage; full audit covered separately.

**Prior full grounding**: 2026-04-18 (v1.9.0, commit `59fe397`).
**Prior partial refresh**: 2026-04-19 (v1.11.0 addendum in `thresholds-taiwan.md`).
**This refresh**: 2026-05-02 (PR-4 of v2.1.0 Phase 1 per ADR-0004 — TW classifier).

## Status

**No material policy events between 2026-04-19 and 2026-05-02.** The 13-day window did not trigger any of the mandatory recalibration events listed in `recalibration-protocol.md`:

- ❌ No new CBC 理監事聯席會議 (next: 2026-06-18, Q2)
- ❌ No NDC 五色景氣燈號 methodology revision (current: 2024 9-indicator version)
- ❌ No DGBAS NAIRU publication (no official; academic 3.5-4.0% range unchanged)
- ❌ No policy-rate change since 2024-09 cut to 2.00%
- ❌ No regime shift events

**Conclusion**: `thresholds-taiwan.md` remains current at 2026-Q1 vintage. Calibrations carried over verbatim into `calibrations/tw.yaml` with the corrections from v1.9.0 grounding (9 構成 corrected names: 工業及服務業加班工時 + 製造業營業氣候測驗點 TIER) preserved.

## Native-language verification (繁體中文)

This refresh re-verified the load-bearing TW thresholds via 繁體中文 primary-source web search per `recalibration-protocol.md` § "Native-Language Source Priority":

| Claim | Source vintage | Confirmation |
|---|---|---|
| NDC 五色景氣燈號 score band 9-45 | NDC ndc.gov.tw 景氣指標查詢系統 | ✅ unchanged |
| 2026-02 score = 40 分, 紅燈 (third consecutive red light) | NDC index.ndc.gov.tw + StockFeel commentary | ✅ confirms doc's "Phase 2 Overheat 持續定調有效" |
| CBC 貼現率 2.00% maintained 2026-03-19 | cbc.gov.tw 理監事聯席會議新聞稿 cp-302-189508 | ✅ unchanged |
| CBC policy language "適時調整" (NOT "彈性") | cbc.gov.tw 2026-03 statement | ✅ confirms 彈性 is 場外解釋語 only |
| DGBAS CPI 2026-03 = 1.20% YoY | dgbas.gov.tw / stat.gov.tw | ✅ matches doc |
| DGBAS unemployment 2026-03 = 3.34% | DGBAS press release | ✅ within structural 3.3-3.4% band |
| CIER PMI 2026-03 = 55.4 (manufacturing expansion, 6th consecutive month) | cier.edu.tw | ✅ confirms expansion regime |
| TSMC TAIEX weight 2026-03 ≈ 45% | TWSE 加權指數成分股暨市值比重 | ✅ slightly above 44.30% baseline (2026-03-31), within "40%+" range |
| DGBAS 2026 forecast: GDP 3.54%, CPI 1.61% | DGBAS dgbas.gov.tw News 235532 | ✅ context — CBC outlook "CPI < 2%" confirmed |

**Delta items captured**:

⚠️ **TSMC TAIEX weight drift**: 2026-03-10 spot reading ≈ 45.0% per HiStock/nStock. v1.9.0 baseline 44.30% (2026-03-31). 0.7 pp drift over 21 days — within normal market volatility. Calibration band (`tsmc_top_10_concentration`) widened to `[40, 50]` rather than locked at 44.30 to absorb intra-quarter drift. Next official monthly update expected ~2026-04-30 (post-fixture date).

⚠️ **NDC 2026-03 = 紅燈 39 分** (per fixture observation): one notch below 2026-02's 40 分 but still 紅 (≥ 38). Direction "Falling" within red band. No methodology change.

🔴 None — no material corrections required.

## Calibration carry-over (verbatim from thresholds-taiwan.md)

| Field | Value | Source vintage |
|---|---|---|
| `signal_band.red.lower` | 38 | NDC 2024 revision methodology |
| `signal_band.green.lower` | 23 | NDC 2024 revision methodology |
| `signal_band.blue.upper` | 16 | NDC 2024 revision methodology |
| `inflation_target_framing` | "彈性定義" (CBC 場外解釋語) | CNA 2024-06-19 |
| `policy_rate_discount` | 2.00 | CBC 2024-09 cut, maintained 2026-03-19 |
| `nairu_estimate` | 3.5-4.0 (academic only) | CBC 季刊 NAIRU 專題, unchanged |
| `tsmc_taiex_weight` | 44.30 | TWSE 2026-03-31 |
| `top_10_taiex_weight` | 58.27 | TWSE 2026-03-31 |
| `tsmc_in_electronics_index` | 56.32 | TWSE 2026-03-31 |
| `historic.first_red_2024_02` | 40 | NDC 2024-02 (31 年新高) |
| `historic.no_red_2014_2023` | true | NDC 10-year window 2014-01 to 2023-12 |

## Anchored Quotes (verified currency)

> 「台灣作為小型開放經濟體，採具彈性的物價穩定定義，應較妥適。」
> — CBC 高層對外場外解釋語, CNA 2024-06-19 ([cna.com.tw](https://www.cna.com.tw/news/afe/202406190101.aspx))

> 「將適時調整貨幣政策，以達成物價穩定與金融穩定。」
> — CBC 2026-03-19 理監事聯席會議新聞稿 ([cbc.gov.tw](https://www.cbc.gov.tw/tw/cp-302-189508-c6f08-1.html))

These remain the qualitative anchors used in `classify_tw.py`'s `cpi_context.cbc_framing` field.

## Phase 1 PR-4 Implementation Notes

### Fixture inspection — 8 of 9 components present (structural NDC bundle gap)

The TW regime-pack fixture (`tests/data/fixtures/data-tw-regime-pack-sample.json`) contains 8 of the 9 NDC 2024-revision constituent indicators. The missing component is `製造業營業氣候測驗點 (TIER)` — the 2024-revision specifically lists this as the 9th component, but **NDC's bulk-download ZIP CSV has not been updated to the 2024 schema**.

Empirically verified 2026-05-02 (per ROADMAP §v2.1.x-b research):

```
$ unzip -l 景氣指標及燈號.zip | grep 構成
  景氣對策信號構成項目.csv      # canonical 9-component file
  schema-景氣對策信號構成項目.csv

$ head -1 景氣對策信號構成項目.csv
"Date","貨幣總計數M1B","股價指數","工業生產指數","工業及服務業加班工時",
"海關出口值","機械及電機設備進口值","製造業銷售量指數","批發、零售及餐飲業營業額"
# → 8 columns + Date. TIER absent.
```

The `schema-景氣對策信號構成項目.csv` companion file lists the same 8 columns. So even the published schema lags the 2024 revision narrative.

**Why TIER is not a simple ndc_client preset addition**: TIER is published by 台灣經濟研究院 (Taiwan Institute of Economic Research) — a different institution from NDC — as a monthly press-release **PDF** (`tier.org.tw/forecast/forecast.aspx → 202605.pdf` etc). It is not in:
- `data.gov.tw` (search returns no matching dataset for «製造業營業氣候測驗點» or «台灣經濟研究院»)
- NDC's `ws.ndc.gov.tw/Download.ashx` ZIP (verified)
- A free TIER API (Aremos 經統資料庫 is paid subscription)

Routes that *could* surface TIER, ordered by maintainability:
1. **TIER monthly-PDF scrape** — fragile (PDF layout shifts), one number per month
2. **NDC `index.ndc.gov.tw/n/zh_tw/lightscore` web-app XHR** — Cloudflare-protected, no public API contract
3. **Manual / curated fixture overlay** — opt-in calibration vintage, not live

**Implication for classify_tw**: `tier_manufacturing_climate.value` is structurally `None` until a TIER fetcher lands. `data_quality.missing` lists `tier (製造業營業氣候測驗點 — 9th component)`. Confidence is **already high** with 8/9 components — the threshold is `≥ 6 components found + leading + coincident + cpi-yoy present`, which v2.1.x-c (CPI YoY 修正) made hit. Adding TIER would close the dispersion gap from 8/9 → 9/9 but would not change the confidence verdict.

**Re-scoped** (per ROADMAP §v2.2.0-g, post-2026-05-02):
- Original v2.1.x-b assumption (TIER lives in NDC's bundle) is empirically false.
- TIER fetcher requires either PDF parser (fragile) or a paid Aremos contract.
- Demoted to v2.2.0 candidate with explicit upstream-source research as blocker.

### Reading native verdict from structured pack

`classify_tw.py` reads from BOTH the flat `series` block (for direction-classifying CPI / leading-index / coincident-index / pmi) AND the structured `ndc.signal.data.presets["signal-components"].components` dict (for per-component dispersion + score / color latest values). This dual-read mirrors data-cn's CN-component overlay approach and avoids the flatten ambiguity where multiple components share the `signal-components` preset key (only the first survives the flatten — see pack.py `_flatten_regime_to_series` first-write-wins).

### TSMC concentration overlay

`classify_tw.py` exposes a `tsmc_concentration_overlay` block in `native_verdict` that surfaces:

- `weight_pct` — fixed at calibration vintage (44.30) since the regime-pack fixture does not currently include TWSE monthly weight data (T1 layer scope, not T2)
- `top_10_pct` — fixed (58.27)
- `tsmc_in_electronics_index_pct` — fixed (56.32)
- `historic_5y_delta_pp` — +17 pp from 2020 ~28%
- `note` — "TAIEX ≈ TSMC ADR 代理 — regime tilts must account for TSMC = TW equity cycle"

This is **not** a live signal in PR-4. PR-7 or v2.2.0 may add TWSE monthly weight ingestion to data-tw and wire it through.

### Score-band semantic mapping

```
score >= 38  → 紅 / overheated / "31 年來首度紅燈" (if first in ≥ 10 years)
32-37        → 黃紅 / warm
23-31        → 綠 / stable
17-22        → 黃藍 / caution
9-16         → 藍 / recession
```

The "31 年來首度紅燈" qualifier in `score_band_meaning` is set when score ≥ 38 AND the historical context flag is true (calibration: `historic.first_red_2024_02 = 40` triggers acknowledgment that 2024-02's 40 ended a 10-year no-red streak). The current fixture (39 分 at 2026-03) is the third consecutive red — semantic = "三度連續紅燈".

## Next Recalibration Triggers

Watch for:
- **CBC 2026-Q2 理監事 (~2026-06-18)** — mandatory; check policy rate stance + 2026 GDP/CPI forecast updates
- **NDC monthly signal release** — every ~25th of month for prior-month data; flag if signal color shifts (i.e. 紅 → 黃紅 transition)
- **TWSE monthly market value table** (~end-of-month) — refresh `tsmc_taiex_weight` if drift exceeds ±2 pp
- **DGBAS quarterly economic forecast revision** — typically February / May / August / November; refresh CPI / GDP outlook
- **CIER PMI monthly** — flag PMI drop below 50 (regime change to contraction)

If any fires, update `thresholds-taiwan.md` first, then re-extract numeric values into `calibrations/tw.yaml`. Drift-detection CI (PR-1) flags numeric mismatches between MD and YAML.

## See Also

- `references/thresholds-taiwan.md` — primary-source threshold reference (Vintage 2026-Q1, addendum 2026-04-19)
- `references/recalibration-protocol.md` — partial-refresh template
- `research/grounding-us-2026-05.md` — analogous PR-2 grounding note for US
