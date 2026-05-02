# Credit Impulse — Methodology Note (China-specific)

**Scope**: methodology choice for `_compute_credit_impulse()` in
`data-cn/scripts/pack.py` and consumption by `classify_cn.py`.
**Owner**: data-cn (computation) + analysis-macro-regime (interpretation).
**Vintage**: 2026-Q2.

---

## 1. Definition (academic)

**Credit impulse** (信贷脉冲) — coined by Michael Biggs (2008,
Deutsche Bank) — is defined as:

> the **change in new credit flow as a share of GDP**.

Mechanically this is the **second derivative** of credit stock (the
first derivative being new credit flow itself). In equation form:

```
CI_t = (ΔCreditFlow_t / GDP_t) - (ΔCreditFlow_{t-12} / GDP_{t-12})
```

Where `ΔCreditFlow` is the new credit issued in a 12-month window.

**Why second derivative**: Biggs showed that **economic growth depends
on the change in credit growth**, not the level. A constant high
credit-flow level produces no incremental boost; only an *acceleration*
in flow does.

**Forward-looking property** (per CICC 2022, 中信 / 中金 research): in
recent CN credit cycles, credit-impulse turning points lead 社融存量同比
(TSF stock yoy) turning points by **6-9 months**, and lead asset-price
inflection (CSI300, property) by ~3-6 months.

---

## 2. Three flavors used in CN macro research

| Flavor | Formula | Lead vs growth | Practitioners |
|--------|---------|----------------|---------------|
| **Strict (Biggs 2008)** | (12m new credit / GDP) − (12m prior new credit / GDP_{t-12}) | longest, ~6-9 mo | 中金 (CICC) 2022 大类资产研究 |
| **TSF stock yoy 12m change** | TSF stock yoy at t − TSF stock yoy at t-12 | ~3-6 mo lead | 中信证券, 国信证券 multi-asset team |
| **TSF stock yoy (level)** | (TSF_stock_t − TSF_stock_{t-12}) / TSF_stock_{t-12} | first-order, coincident | PBOC monthly press release; mainstream financial media |

**Choice for v2.1.0**: **TSF stock yoy 12-month change** (middle row).
Reason: balance between forward-looking signal and data availability /
robustness. The strict Biggs formula requires nominal-GDP series at
monthly frequency (CN GDP is quarterly with no monthly proxy consensus
per v1.7.1 research), which forces interpolation noise that defeats the
methodology's precision.

---

## 3. Available data + flow-to-stock proxy

**Authoritative source**: PBOC monthly «社会融资规模存量统计数据报告»
publishes both **stock** (社会融资规模存量) and **flow** (社会融资规模
增量, 当月新增). Stock yoy is published directly:
- 2024-12-end: 8.0%
- 2025-12-end: 8.3% (up 0.3pp; PBOC 2026-01 release).
- 2025 full-year flow: ¥35.6T (up ¥3.34T YoY).

**akshare exposure**: `macro_china_shrzgm` returns **monthly flow only**
(in 亿元). Stock series is **NOT** in akshare's CN macro layer as of
2026-04 — would require a separate scrape from PBOC tongji or NBS.

**Decision**: derive a **flow-yoy** second-derivative proxy from monthly
flow via trailing-12m sum. Specifically:

```
flow_yoy_t      = (Σ flow over [t-11, t]) / (Σ flow over [t-23, t-12]) − 1
flow_yoy_t-12   = (Σ flow over [t-23, t-12]) / (Σ flow over [t-35, t-24]) − 1
credit_impulse  = flow_yoy_t − flow_yoy_t-12       (in pp)
```

**This is NOT stock-yoy.** Important:

- PBOC publishes **stock-yoy** directly (numerator = annual flow;
  denominator = multi-decade accumulated stock). 2025-12 stock-yoy = 8.3%.
- Our **flow-yoy** uses denominator = one year of flow. Magnitudes run
  **5-20pp larger** than stock-yoy in absolute terms (the AAPL-vs-Apple-
  shareholders-equity ratio analogy).
- The **direction** (expanding / contracting) is symmetric across both
  flavors. The **magnitude** is not.

**Use the trend tag, not the value, for verdict construction.** The
`value` field is reported transparently in the regime-pack but should
be interpreted as a flow-yoy second derivative — useful for relative
comparisons across CN's own history, NOT directly comparable to PBOC's
stock-yoy series.

**Future hardening**: if data-cn ever exposes PBOC's stock-yoy series
directly (via a tongji scraper or akshare additions), pass it via the
`tsf_stock_yoy=` parameter and the helper will switch to canonical
stock-yoy 12mo Δ — at which point the magnitudes will be directly
comparable to CICC published charts.

`_compute_credit_impulse()` accepts both:
- `tsf_stock_yoy` (preferred): if Layer 1 client ever fetches stock-yoy
  directly from PBOC, pass it here for canonical computation.
- `tsf_flow_monthly` (current default): monthly flow series (亿元);
  helper computes trailing-12m-sum yoy internally and feeds that as a
  stock-yoy proxy.

If neither is available → fall back to `m2_yoy` 12-month change (less
precise; M2 growth tracks broad money, not standard credit; in 2024-2025
re-categorization weakened the M2 ↔ credit linkage).

---

## 4. Threshold calibration (`calibrations/cn.yaml`)

```yaml
credit_impulse:
  primary_methodology: tsf_stock_yoy_12m_change
  primary_pp_threshold: 0.5     # |Δ| > 0.5pp → expanding/contracting
  fallback_methodology: m2_yoy_12m_change
```

**Trend tagging**:
- `Δ > +0.5pp` → **expanding** (credit cycle accelerating; bullish for
  cyclical / property / 上游 commodities)
- `Δ < −0.5pp` → **contracting** (deceleration; defensive tilt)
- `|Δ| ≤ 0.5pp` → **neutral** (within noise band)

**Why 0.5pp**: empirically the standard deviation of 1-year forward
changes in TSF stock yoy in CN since 2015 is ~0.7-0.8pp. ±0.5pp is
roughly 2/3 sigma — keeps the alarm firing on directional moves while
filtering monthly noise.

---

## 5. Interpretation note (regime context)

CN credit impulse has been **structurally weak** since the 2021 property
crisis:
- 2020 COVID stimulus credit impulse spike → sharp reversal 2021.
- 2022-2024 multiple half-hearted easing rounds; impulse oscillated
  near zero.
- 2025 适度宽松 + 7D OMO 1.40% + 结构性降息 — TSF stock yoy improved
  from 8.0% → 8.3% (Dec); whether this becomes a sustained positive
  impulse depends on 2026 Q1-Q2 follow-through.

**Within `classify_cn.py`**: `credit_impulse.trend = "expanding"`
combined with `cpi_framing.policy_stance = "below_target_persistent"`
and `pboc_stance = "适度宽松"` is the canonical **early-recovery
signal** in the CN regime model — Phase 1 (recovery) lean even when
headline IC quadrant prints elsewhere due to stale CPI/growth direction.

---

## 6. Sources

- **Biggs, Mayer & Pick (2010)**, "Credit and Economic Recovery:
  Demystifying Phoenix Miracles", DB Securities (originally Biggs 2008).
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1595980
- **中金大类资产 (CICC) 2022-01-17** — 「从信贷脉冲看风格轮动」
  https://finance.sina.com.cn/stock/stockzmt/2022-01-17/doc-ikyamrmz5618477.shtml
- **国信证券策略研究 2023-05-15** — 「国信多资产系列指数介绍 (一)」
  (信贷脉冲 vs 社融存量同比 对比章节)
- **中国人民银行 2026-01** — 2025 年金融统计数据报告 (TSF stock yoy 8.3%)
  http://www.pbc.gov.cn/diaochatongjisi/116219/116319/index.html
- **彰化銀行 2018-09** — 「信貸脈衝指數 (Credit impulse) 之介紹」
  (TW central-bank affiliate primer; useful in zh-TW context)
  https://www.bankchb.com/chb_2a_resource/leap_do/gallery/1538720906905/67-9.pdf
