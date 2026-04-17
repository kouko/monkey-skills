# Labor / 勞動系

---

## unemployment: 失業率 / Unemployment Rate

- **Series code**: sid=t.3 (stat.gov.tw)
- **Source**: statgov (stat.gov.tw)
- **Unit**: Percent (%)
- **Frequency**: Monthly
- **Publication lag**: ~4 weeks after reference month
- **History**: 578 points from 1978-01

**What it measures**: The percentage of the labor force that is unemployed and
actively seeking work. Taiwan's headline unemployment rate (失業率_合計).

**How to interpret**:
- Rising → Labor market weakening. More people seeking work than available jobs.
  Negative for consumer spending and economic outlook. The CBC considers labor
  conditions in rate decisions.
- Falling → Labor market strengthening. Supports consumer confidence and
  spending. Taiwan's structural unemployment floor is ~3.5-3.8%.

**Market significance**: ⭐⭐
An important but lagging indicator for the Taiwan economy. Unemployment
responds slowly to economic conditions — firms in Taiwan tend to reduce
overtime hours and implement hiring freezes before laying off workers.
The monthly release generates modest media coverage.

**When to use**: Labor market slack assessment, CBC growth outlook input, consumption forecast, structural employment analysis.

**Taiwan-specific context**:
- Taiwan's unemployment rate is structurally lower than the US and most
  developed economies, typically ranging 3.5%-4.5%. The tighter range means
  smaller absolute changes carry more significance.
- Youth unemployment (15-24 age group, available in `LM0109A1M.xml`) is
  significantly higher (~11-13%) and more cyclically volatile.
- Taiwan has a relatively small informal economy compared to other Asian
  countries, making the official unemployment rate a reasonable measure
  of labor market conditions.
- Seasonal patterns: unemployment typically rises in June-August as new
  graduates enter the job market, then falls in Q4 as holiday hiring peaks.

**Common pitfalls**:
- Taiwan's unemployment definition follows ILO standards (available for work
  and actively seeking), but cultural factors (family businesses, part-time
  arrangements) may understate true underemployment.
- Backup source: NDC lagging indicators CSV (`ndc_client.py --preset
  unemployment`) provides the same data from an independent source.
- Do not compare Taiwan's unemployment rate directly with the US or Europe
  without adjusting for structural differences.
