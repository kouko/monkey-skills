# 雇用系 / Labor

Japan macro indicators -- unemployment, wages, and labor market tightness.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

## unemployment: 完全失業率 / Unemployment Rate

- **Series code**: 0301010000020020010 (統計ダッシュボード)
- **Source**: 総務省統計局 (Ministry of Internal Affairs and Communications, Statistics Bureau)
- **Unit / 単位**: Percent (%)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~4 weeks after reference month
- **History**: From 1953 (878 observations)

**What it measures / 経済的意味**:
(EN) The percentage of the labor force that is unemployed and actively seeking work. Japan's official measure of labor market slack.
(JP) 労働力人口に占める完全失業者の割合。日本の労働市場の緩み度合いを測る公式指標。

**How to interpret / 解読方法**:
- Rising / 上昇 → Labor market weakening. Negative for consumption outlook and wage growth. / 労働市場の悪化。消費見通し・賃金上昇にネガティブ。
- Falling / 下落 → Labor market tightening. Positive for wage growth and consumption, but may add to inflation pressure. / 労働市場の逼迫。賃金・消費にポジティブだがインフレ圧力を助長する可能性。

**Market significance / 市場重要度**: ⭐⭐
Japan's unemployment is structurally low (2-3%) due to labor shortages from aging demographics. Less market-moving than in the US, but sustained rises above 3% would signal significant recession.

**When to use / 使用場面**:
Labor market assessment, wage-price spiral risk evaluation, consumption
outlook, BOJ policy input (full employment supports normalization).

**Japan-specific context / 日本固有の文脈**:
Japan's unemployment rate is structurally low (~2.5-3.0%) compared to
Western economies due to labor hoarding practices (雇用保蔵), lifetime
employment culture, and demographic shrinkage reducing labor supply. A move
from 2.5% to 3.0% in Japan is as significant as a move from 4% to 6% in the
US. Japan's labor market slack is better measured by the jobs-to-applicants
ratio (有効求人倍率, published by MHLW) than by the unemployment rate alone.

**Common pitfalls / よくある間違い**:
- Japan's unemployment rate underestimates true slack because discouraged workers exit the labor force rather than registering as unemployed (low labor force participation rate, especially among older women historically).
- The rate barely moved during COVID (peaked at 3.1%) due to massive government employment subsidies (雇用調整助成金). This masked the true impact.
- Do not compare Japan's 2.5% with US 4% and conclude Japan's labor market is tighter. Structural and definitional differences make absolute comparison misleading.

**Cross-indicator notes**:
- Japan's Phillips Curve is structurally flat: low unemployment does NOT reliably push up wages or CPI. Root cause: dual labor market (正規/非正規雇用) suppresses aggregate wage bargaining power.
  Source: Gregor Smith (2008) "Japan's Phillips Curve Looks Like Japan"; Springer (2022) on dual labor market effects.
- 有効求人倍率 provides more cyclical signal than unemployment in Japan because unemployment stays structurally low (~2.5%) due to labor shortage demographics.

---

## real-wages: 実質賃金指数 / Real Wage Index

- **Series code**: 0302030201010090010 (統計ダッシュボード)
- **Source**: 厚生労働省 (Ministry of Health, Labour and Welfare, MHLW)
- **Unit / 単位**: Index (2020 = 100)
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~5 weeks after reference month
- **History**: From 2012 (170 observations)

**What it measures / 経済的意味**:
(EN) The wage index for total cash earnings adjusted for consumer price inflation. Real wages = nominal wages minus CPI. It measures whether workers' purchasing power is increasing or declining.
(JP) 現金給与総額の賃金指数を消費者物価で実質化したもの。実質賃金＝名目賃金−CPI。労働者の購買力が上昇しているか低下しているかを測定する。

**How to interpret / 解読方法**:
- Rising (positive YoY) / 上昇 → Workers' purchasing power increasing. Supports consumption growth and virtuous wage-price cycle. / 労働者の購買力上昇。消費拡大と賃金・物価の好循環を支持。
- Falling (negative YoY) / 下落 → Inflation outpacing wage growth. Erodes purchasing power and suppresses consumption. / インフレが賃金上昇を上回る。購買力低下で消費を抑制。

**Market significance / 市場重要度**: ⭐⭐⭐
The most watched labor indicator in the current cycle. Sustained real wage growth is the BOJ's key condition for continued rate normalization. The "wage-price positive cycle" (賃金と物価の好循環) is the central narrative of Japan's post-deflation transition.

**When to use / 使用場面**:
BOJ policy prediction, consumption outlook assessment, wage-price spiral
analysis, living standards evaluation.

**Japan-specific context / 日本固有の文脈**:
Japan's wage-setting system revolves around the annual spring wage negotiations
(春闘, shunto) between employers and unions each February-March. Shunto results
set the tone for wage growth for the entire fiscal year. Real wages were negative
for 27 consecutive months (2022-2024), the longest streak since records began,
despite nominal wage growth turning positive. This prolonged real wage decline
was a key reason the BOJ was cautious about rate hikes even as headline inflation
exceeded 2%.

**Common pitfalls / よくある間違い**:
- Real wages can be negative even with rising nominal wages if CPI is rising faster. Always check both the nominal and real series.
- The Monthly Labour Survey (毎月勤労統計) that produces this index was at the center of a major statistical scandal in 2018 (sampling methodology irregularities). While corrected, it reduced public trust in the data.
- Total cash earnings includes bonuses, which cause seasonal spikes in June and December. Use the seasonally adjusted series for trend analysis.
- Part-time worker composition effects can distort the average wage. An increase in part-time employment share pushes down the average even if individual wages are rising.

**Cross-indicator notes**:
- BOJ Governor Ueda's policy normalization framework (2023–present) requires a "virtuous cycle between wages and prices" (賃金と物価の好循環). Three conditions: (1) firms pass wage costs into selling prices (2) inflation expectations become forward-looking (3) wage momentum persists beyond commodity shocks.
  Source: BOJ Governor speech, 2024-05-08 https://www.boj.or.jp/en/about/press/koen_2024/ko240508a.htm
  Note: This framework is current as of 2026 but may change with future BOJ leadership.

---

## job-ratio: 有効求人倍率 / Job-to-Applicant Ratio

- **Series code**: 0301020001000010020 (統計ダッシュボード, `--cycle fiscal-year`)
- **Source**: 厚生労働省 (Ministry of Health, Labour and Welfare, MHLW)
- **Unit / 単位**: Ratio (倍)
- **Frequency / 頻度**: Fiscal-year (年度) -- use `--cycle fiscal-year`
- **Publication lag / 公表遅延**: ~4 weeks after reference month (original MHLW source is monthly; 統計DB only has fiscal-year aggregates)
- **History**: From 1963 (758 observations)

**What it measures / 経済的意味**:
(EN) The ratio of active job openings to active job seekers at public employment offices (Hello Work). A value of 1.0 means there is exactly one job available for each job seeker. Above 1.0 indicates more jobs than applicants (labor shortage); below 1.0 indicates more applicants than jobs (labor surplus).
(JP) 公共職業安定所（ハローワーク）における有効求人数と有効求職者数の比率。1.0＝求人と求職が均衡。1.0超＝人手不足、1.0未満＝就職難。

**How to interpret / 解読方法**:
- Rising (above 1.0) / 上昇 → Labor market tightening, labor shortage intensifying. Upward pressure on wages. / 労働市場の逼迫、人手不足の深刻化。賃金上昇圧力。
- Falling (toward or below 1.0) / 下落 → Labor market loosening. A fall below 1.0 is a strong recession signal. / 労働市場の緩和。1.0割れは景気後退の強いシグナル。

**Market significance / 市場重要度**: ⭐⭐
A sensitive labor market tightness indicator. Ratios above 1.0 (more jobs than applicants) confirm tight labor conditions. Used alongside unemployment for a fuller picture of labor supply/demand balance.

**When to use / 使用場面**:
Labor market tightness assessment, wage growth prediction, consumption outlook,
BOJ policy input, recession risk gauge.

**Japan-specific context / 日本固有の文脈**:
The data comes from Hello Work (ハローワーク), Japan's public employment service.
It does not capture the full labor market (private recruiters, direct hiring are
excluded), but its long history and consistency make it the standard benchmark.
Japan's demographic decline (shrinking working-age population) creates a
structural upward bias -- even in downturns, the ratio often stays above 1.0.
The ratio fell to 0.42 during the 2009 financial crisis (the lowest since 1999)
and recovered to 1.6+ by 2018.

**Common pitfalls / よくある間違い**:
- The data only covers Hello Work registrations. Many job openings and job seekers use private channels. The level may undercount both sides, but the trend is reliable.
- Regional variation is enormous. Tokyo may be at 2.0+ while rural prefectures are at 0.8. The national average masks significant geographic disparities.
- "Effective" (有効) means both opening and application are currently active (not expired). "New" (新規) refers to newly posted that month. Use the effective (有効) series for trend analysis.
- The seasonally adjusted series is the standard for analysis. Raw data shows strong seasonal patterns (April hiring season spike).
- The Statistics Dashboard API only provides fiscal-year aggregates for this indicator. For monthly data, use the MHLW e-Stat original statistics directly. Use `--cycle fiscal-year` with estat_client.py.
