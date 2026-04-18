# Sentiment / 센티먼트

Survey-based sentiment indices published monthly by BOK via the ECOS
KEYSTAT interface. These are **qualitative diffusion-style indices**,
not business cycle CI components — for the latter, see
`indicators-cycle.md`.

---

## consumer-sentiment: 소비자심리지수 / Consumer Sentiment Index (CSI)

- **Series code**: K252 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (100 = neutral)
- **Frequency**: Monthly
- **Publication lag**: ~1 week after month-end (released around 27th of reference month)
- **History**: From 2008

**What it measures**: A survey-based index reflecting Korean consumers'
confidence about current and future economic conditions. Compiled by the
BOK from a monthly survey of ~2,300 households nationwide.

**How to interpret**:
- Above 100 → Consumers are optimistic. More consumers expect economic
  conditions to improve than worsen. Supports consumption spending.
- Below 100 → Consumers are pessimistic. Weakness in consumption expected.
- The direction of change matters more than the level: rising CSI → improving
  outlook; falling CSI → deteriorating outlook.

**Market significance**: ⭐⭐
A leading indicator for private consumption (~50% of GDP). Sharp drops in
CSI (as seen in 2008, 2020, 2022) precede consumption pullbacks. The BOK
watches CSI as an input to its growth outlook and rate decisions.

**When to use**: Consumption leading indicator, real estate wealth effect gauge, BOK growth outlook input, household spending direction.

**Korea-specific context**:
- Korean consumer sentiment is strongly influenced by: (1) real estate
  prices (housing is the primary household asset), (2) employment conditions,
  (3) stock market performance, and (4) geopolitical risks (North Korea).
- The real estate channel is particularly important. Rising apartment prices
  boost sentiment among homeowners (wealth effect) but depress sentiment
  among young non-owners (affordability anxiety). This creates divergent
  sentiment across demographics.
- North Korea provocations (missile tests, nuclear tests) cause temporary
  CSI dips that typically reverse within 1-2 months.

**Common pitfalls**:
- Data only from 2008. Shorter history than most other macro indicators.
- Sentiment can decouple from actual economic outcomes. Consumers may be
  pessimistic while GDP is growing, or vice versa.
- The survey methodology changed in 2008 when the BOK adopted the current
  CSI framework. Pre-2008 data uses a different methodology and is not
  directly comparable.

---

## economic-sentiment: 경제심리지수 / Economic Sentiment Index (ESI)

- **Series code**: K269 (ECOS-KEYSTAT)
- **Source**: Bank of Korea via FinanceDataReader
- **Unit**: Index (100 = long-run average)
- **Frequency**: Monthly
- **Publication lag**: ~1 week after month-end
- **History**: From 2008

**What it measures**: A composite sentiment index combining consumer and
business confidence surveys. Provides a broader picture of economic
sentiment than consumer-only or business-only surveys.

**How to interpret**:
- Above 100 → Sentiment above long-run average. Economy perceived as
  performing better than typical.
- Below 100 → Below long-run average. Economic pessimism.
- The ESI combines consumer sentiment (CSI) with the Business Survey
  Index (BSI), giving weight to both household and corporate sectors.

**Market significance**: ⭐⭐
More comprehensive than CSI alone. The composite nature makes it a better
summary statistic for overall economic mood. Useful for cross-country
comparison (similar to EU ESI methodology).

**When to use**: Broad sentiment summary statistic, cross-country comparison (EU ESI methodology), cycle turning point confirmation.

**Korea-specific context**:
- The ESI was introduced to provide a single summary indicator similar to
  the EU's Economic Sentiment Indicator. It follows a broadly similar
  methodology.
- During periods of divergence between consumer and business sentiment
  (e.g., businesses optimistic on exports but consumers pessimistic on
  housing), the ESI can mask important underlying dynamics.

**Common pitfalls**:
- Same limited history as CSI (from 2008).
- The "100 = long-run average" is calibrated to 2003-2017. As the sample
  period extends, the long-run average drifts.
- The weights given to consumer vs. business components are not transparent.

---

## Related files

- `indicators-cycle.md` — 경기종합지수 CI pair (K254/K253) — business cycle
  indicators (NOT sentiment surveys). Forms Korea's monthly GDP proxy.
