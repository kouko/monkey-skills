# 物價系 / Prices

Japan macro indicators -- consumer and producer price indices.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

## cpi: 消費者物価指数 CPI / Consumer Price Index

- **Series code**: 0703010501010030000 (統計DB)
- **Source**: 総務省統計局 (Statistics Bureau)
- **Unit / 単位**: YoY % change (前年同月比)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~3-4 weeks after reference month
- **History**: From 1971 (662 observations)

**What it measures / 経済的意味**:
(EN) Year-over-year percentage change in the consumer price index for all items, covering the prices of goods and services purchased by households nationwide. This is Japan's headline inflation measure.
(JP) 全国の世帯が購入する商品・サービスの価格変動を測定する消費者物価指数（総合）の前年同月比。日本のヘッドライン・インフレ指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Inflation is accelerating. If sustained above BOJ's 2% target, supports hawkish policy expectations. / インフレ加速。2%目標を持続的に超えれば引締め観測を強化。
- Falling / 下落 → Disinflation or deflation risk. Supports dovish policy stance. / ディスインフレまたはデフレリスク。緩和スタンスを支持。

**Market significance / 市場重要度**: ⭐⭐⭐
Japan's headline inflation gauge. After decades of deflation, sustained CPI above 2% (2022-) has fundamentally changed the BOJ policy equation. CPI releases directly drive JPY, JGB yields, and BOK/Fed policy expectations for Japan.

**When to use / 使用場面**:
Investment Clock inflation axis, BOJ policy prediction, real return
calculations, GIP quadrant mapping.

**Japan-specific context / 日本固有の文脈**:
Japan experienced chronic deflation from the late 1990s through 2021. The
BOJ's 2% inflation target (introduced 2013) was not sustainably achieved until
the post-COVID supply shock + weak yen period (2022-). Japanese CPI is heavily
influenced by administered prices (electricity, gas subsidies), food prices,
and the yen exchange rate. Government energy subsidies can distort CPI by
0.5-1.0 percentage points.

**Common pitfalls / よくある間違い**:
- The 統計DB preset returns YoY % change directly, unlike FRED CPI which returns the index level. No manual YoY calculation needed.
- Japan CPI uses a different basket weighting than US CPI. Shelter (rent) weight is much lower in Japan (~20% vs ~36% in US) because Japan has high home ownership and controlled rents.
- "Core CPI" in Japan means "less fresh food" (生鮮食品を除く), NOT "less food and energy" as in the US. The US-style core is called "core-core CPI" (生鮮食品及びエネルギーを除く) in Japan.

**Cross-indicator notes**:
- 円安→CPI pass-through is structurally weak in Japan: 1% yen depreciation → 2% import price increase (immediate) → only 0.1% core CPI increase (12-month lag). Small firms with weak pricing power buffer consumer prices.
  Source: RIETI Research Paper https://www.rieti.go.jp/jp/publications/nts/19e078.html
- CGPI (企業物価) can spike while CPI stays flat — this "pass-through gap" signals that cost pressure is building in the corporate sector but hasn't reached consumers yet. The lag is typically 6-12 months.

---

## cgpi: 企業物価指数 CGPI / Corporate Goods Price Index

- **Series code**: PR01 (BOJ API)
- **Source**: 日本銀行 (Bank of Japan)
- **Unit / 単位**: YoY % change or Index (2020 base = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~2 weeks after reference month (published before CPI)
- **History**: From 1960 (monthly)

**What it measures / 経済的意味**:
(EN) The price change of goods traded between corporations at the producer level. Formerly called the Wholesale Price Index (WPI). Covers domestically produced goods, exports, and imports. It is a leading indicator for CPI because B2B price pressures eventually pass through to consumer prices.
(JP) 企業間で取引される財の価格変動を測定。旧名「卸売物価指数」。国内品、輸出品、輸入品を含む。B2B価格圧力はやがて消費者物価に転嫁されるため、CPIの先行指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Input cost pressures building for corporations. If sustained, expect pass-through to CPI with a 3-6 month lag. Margin pressure for companies without pricing power. / 企業のコスト圧力上昇。3-6ヶ月のラグでCPIに転嫁される可能性。
- Falling / 下落 → Deflationary pressure at the producer level. Eases corporate cost burden but signals weak demand. / 生産者段階のデフレ圧力。コスト負担は軽減するが需要の弱さを示唆。

**Market significance / 市場重要度**: ⭐⭐
Leading indicator for CPI with 3-6 month lag. Published by the BOJ (unique among central banks). The CGPI-CPI gap reveals corporate pass-through intentions — a widening gap signals building margin pressure.

**When to use / 使用場面**:
Leading indicator for CPI trajectory, corporate margin analysis,
import price pass-through assessment, yen depreciation impact analysis.

**Japan-specific context / 日本固有の文脈**:
CGPI is compiled by the BOJ (not the statistics bureau), making it unique
among major economies where the central bank directly measures producer prices.
The import component is heavily influenced by the JPY exchange rate and oil
prices. In 2022-2023, CGPI spiked to 9-10% YoY while CPI was still 3-4%,
illustrating the delayed pass-through from B2B to consumer prices.

**Common pitfalls / よくある間違い**:
- CGPI != CPI. CGPI measures business-to-business goods prices (日銀管轄); CPI measures consumer prices (総務省管轄). CGPI can spike while CPI remains flat when companies absorb input costs instead of passing them through.
- The PR01 database has multiple sub-series (domestic, export, import). Ensure you select the correct aggregate code.
- Base year revisions (currently 2020 base) change series codes. Always use getMetadata to discover the current code.

---

## Extended Indicators (Tier 2)

### Prices / 物価関連

| DB | 日本語名 | English Name | Description |
|----|---------|--------------|-------------|
| PR02 | 企業向けサービス価格指数 | Services Producer Price Index (SPPI) | B2B services price index. Services inflation leading indicator. / 企業間サービス価格指数。サービスインフレの先行指標。 |
| PR03 | 製造業部門別投入・産出物価指数 | Input-Output Price Index (IOPI) | Manufacturing input vs output prices by sector. Margin pressure gauge. / 製造業の投入・産出物価。マージン圧力の指標。 |
| PR04 | 最終需要・中間需要物価指数 | Final/Intermediate Demand Price Index | Price index by demand stage. US PPI-equivalent structure. / 需要段階別物価指数。米国PPIに相当する構造。 |
