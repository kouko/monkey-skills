# japan-macro

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Japan macroeconomic data skill for investing-toolkit.
日本マクロ経済データスキル。日本宏觀經濟資料技能。

## Overview

Fetches Japan macroeconomic indicators from two government data sources --
Bank of Japan (日本銀行) Time-Series API and the Statistics Dashboard
(統計ダッシュボード) API -- and returns structured JSON grouped by rates,
inflation, growth, money, tankan, forex, and balance. This is a data-only
skill -- it does not analyze, map to regimes, or generate investment verdicts.

**Monthly GDP proxy**: Japan's official GDP is quarterly (統計DB). The
景気動向指数 CI trio (先行 / 一致 / 遅行) published monthly by 内閣府 is the
industry-standard monthly GDP proxy, with the 一致指数 (`coincident-index`)
being the definitive "what's the economy doing right now" reading, parallel
to us-macro's `nowcast` group and china-macro's 三大數據.

日本銀行の時系列統計APIと統計ダッシュボードAPIから日本マクロ指標を取得し、
グループ別の構造化JSONを返す。データ取得のみで、分析やレジーム判定は行わない。

## Data Sources

### BOJ Time-Series API (日本銀行 時系列統計)

- **URL**: `https://www.stat-search.boj.or.jp/api/v1/`
- **Auth**: None required
- **Covers**: Call rate, CGPI, money stock M2, TANKAN DI, USD/JPY, REER,
  current account balance
- **Update**: Daily at 8:50 AM JST (23:50 UTC previous day)
- **Docs**: https://www.stat-search.boj.or.jp/info/api_guide_en.html

### 統計ダッシュボード API (Statistics Dashboard)

- **API Endpoint**: `https://dashboard.e-stat.go.jp/api/1.0/`
- **API Docs**: https://dashboard.e-stat.go.jp/static/api
- **Auth**: None required
- **Covers**: CPI, core CPI, industrial production, unemployment, GDP,
  10-year JGB yield
- **Update**: Varies by indicator and managing agency

### Why Two Sources?

Japan's economic statistics are managed by the agency responsible for each
domain. No single API covers all indicators:

| Agency | Indicators |
|--------|-----------|
| 日本銀行 (Bank of Japan) | Interest rates, CGPI, money supply, TANKAN, forex |
| 総務省 (MIC, Statistics Bureau) | CPI, unemployment |
| 内閣府 (Cabinet Office) | GDP |
| 経済産業省 (METI) | Industrial production |
| 財務省 (MOF) | JGB yields, current account (jointly with BOJ) |

The BOJ API serves data the Bank of Japan itself collects. Everything else
flows through the e-Stat system (統計ダッシュボード), which aggregates data
from multiple ministries into a single API.

### Why Not FRED?

FRED carries some Japan series, but with severe limitations:

- Japan CPI on FRED is **annual frequency only** (last data point: 2024)
- Japan Industrial Production on FRED is **2+ years stale**
- Japanese government APIs provide **monthly data current to 2026-02/03**

Using the source APIs directly provides monthly granularity and timely data.

## Indicators

### Tier 1: Core Indicators (16)

| 日本語 | English | Source | Frequency | Typical Lag |
|--------|---------|--------|-----------|-------------|
| 無担保コールO/N物レート | Call Rate, Uncollateralized O/N | BOJ (FM01) | Daily | 1 business day |
| 基準割引率・基準貸付利率 | Basic Discount / Loan Rate | BOJ (IR01) | Irregular | Same day |
| 消費者物価指数 CPI | Consumer Price Index | 統計DB | Monthly | ~3-4 weeks |
| コアCPI | Core CPI (less fresh food) | 統計DB | Monthly | ~3-4 weeks |
| 企業物価指数 CGPI | Corporate Goods Price Index | BOJ (PR01) | Monthly | ~2 weeks |
| 国内総生産 GDP | Gross Domestic Product | 統計DB | Quarterly | ~6 weeks |
| マネーストック M2 | Money Stock M2 | BOJ (MD02) | Monthly | ~2 weeks |
| 鉱工業生産指数 | Industrial Production Index | 統計DB | Monthly | ~6 weeks |
| 完全失業率 | Unemployment Rate | 統計DB | Monthly | ~4 weeks |
| 新発10年国債利回り | 10-Year JGB Yield | 統計DB | Monthly | ~1 week |
| 短観 業況判断DI | TANKAN Business Conditions DI | BOJ (CO) | Quarterly | ~1 week |
| USD/JPY 為替レート | USD/JPY Exchange Rate | BOJ (FM08) | Daily | 1-2 business days |
| 実効為替レート | Effective Exchange Rate (REER) | BOJ (FM09) | Monthly | 1-2 business days |
| 景気動向指数 CI 一致指数 | Composite Coincident Index (**monthly GDP proxy**) | 統計DB | Monthly | ~6-8 weeks |
| 景気動向指数 CI 先行指数 | Composite Leading Index | 統計DB | Monthly | ~6-8 weeks |
| 景気動向指数 CI 遅行指数 | Composite Lagging Index | 統計DB | Monthly | ~6-8 weeks |

### Tier 2: Extended (30+)

Additional BOJ database series for deeper analysis -- interest rates
(IR02-IR04), money market rates (FM02-FM07), monetary aggregates
(MD01, MD03-MD14), lending (LA01-LA05), balance sheets (BS01-BS02),
flow of funds (FF), and services prices (PR02-PR04).

See `references/japan-macro-indicators.md` for full bilingual documentation.

### Tier 3: Complete BOJ DB Catalog (40+)

All databases available through the BOJ Time-Series API, including public
finance (PF01-PF02), BIS international banking (BIS), derivatives (DER),
and settlement systems (PS01-PS02).

See `references/japan-boj-db-catalog.md` for the complete lookup table.

## Architecture

```
japan-macro skill
├── SKILL.md                           <- Claude reads this
├── scripts/
│   ├── boj_client.py                  <- BOJ API adapter
│   ├── estat_client.py                <- 統計ダッシュボード adapter
│   └── setup.sh                       <- auto-install uv
└── references/
    ├── japan-macro-indicators.md      <- Tier 1+2 bilingual reference
    └── japan-boj-db-catalog.md        <- Tier 3 complete DB catalog
```

Scripts are synced copies from `investing-toolkit/scripts/` via
`sync-scripts.sh`. The skill directory is self-contained so Claude Code
resolves all paths relative to the skill root.

## How It Works

1. **Resolve series list** -- The `--indicators` parameter (default: `all`)
   maps to BOJ database/code pairs and 統計DB presets. For example,
   `--indicators inflation` resolves to BOJ PR01 (CGPI) plus 統計DB presets
   `cpi` and `core-cpi`.

2. **Launch data-fetcher for BOJ series** -- The skill dispatches fetch
   requests to the `data-fetcher` agent, which runs `boj_client.py` via
   `uv run`. For series marked "(discover via getMetadata)", the agent
   first queries the BOJ `getMetadata` endpoint to find the current valid
   series code (codes change with base-year revisions), then fetches data.

3. **Launch data-fetcher for 統計DB series** -- A second set of fetch
   requests runs `estat_client.py` with preset names (e.g., `--preset cpi`).
   GDP uses `--cycle quarterly` since it is not available at monthly frequency.

4. **Merge into unified output** -- BOJ and 統計DB results are combined
   into a single JSON structure grouped by indicator group. Each data point
   retains a `"_source"` tag (`"boj"` or `"estat_dashboard"`) for provenance.

## Output Contract

```json
{
  "fetched_at": "2026-04-16T08:50:00Z",
  "groups": {
    "rates": {
      "call_rate_on": {
        "latest": { "date": "2026-04-15", "value": 0.479 },
        "prior":  { "date": "2026-04-14", "value": 0.478 },
        "direction": "Rising",
        "_source": "boj"
      },
      "jgb10y": {
        "latest": { "date": "2026-03", "value": 1.520 },
        "prior":  { "date": "2026-02", "value": 1.380 },
        "direction": "Rising",
        "_source": "estat_dashboard"
      }
    },
    "inflation": {
      "cgpi":     { "...": "...", "_source": "boj" },
      "cpi":      { "...": "...", "_source": "estat_dashboard" },
      "core_cpi": { "...": "...", "_source": "estat_dashboard" }
    },
    "growth":  { "ip": { "..." }, "unemployment": { "..." }, "gdp": { "..." } },
    "money":   { "m2": { "...", "_source": "boj" } },
    "tankan":  { "tankan_di": { "...", "_source": "boj" } },
    "forex":   { "usdjpy": { "...", "_source": "boj" }, "reer": { "...", "_source": "boj" } },
    "balance": { "current_account": { "...", "_source": "boj" } }
  }
}
```

The `_source` field distinguishes BOJ-sourced data from 統計DB-sourced data.
Always check `latest.date` to confirm the reference period.

## Japan-Specific Context

Key context documented in the indicator reference that affects interpretation:

- **マイナス金利政策 (Negative Interest Rate Policy, 2016-2024)** --
  Call rate was pinned near -0.1% for 8 years. Any positive reading is
  historically significant. The BOJ ended NIRP in March 2024.

- **YCC イールドカーブコントロール (Yield Curve Control, 2016-2024)** --
  The 10Y JGB yield was an administered rate, not market-clearing, during
  this period. Post-YCC yields are normalizing but remain suppressed by
  BOJ's ~50% JGB ownership.

- **CGPI and CPI are different** -- CGPI (企業物価, BOJ-managed) measures
  B2B goods prices; CPI (消費者物価, 総務省-managed) measures consumer prices.
  CGPI leads CPI by 3-6 months. Japan "core CPI" means "less fresh food",
  not "less food and energy" as in the US.

- **短観 DI interpretation** -- DI > 0 means more firms report "favorable"
  than "unfavorable." A falling DI that is still positive means conditions
  are deteriorating but not yet negative. The Large Manufacturers DI is
  the headline number.

- **経常収支 structure** -- Japan has a structural trade deficit (since
  Fukushima 2011) but a massive primary income surplus from overseas
  investments. The net current account usually remains positive, but
  the FX impact is muted because income is often reinvested abroad.

## Cross-Plugin Usage

```
japan-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```

1. **japan-macro** -- fetch BOJ + 統計DB data, return structured JSON
2. **macro-regime-snapshot** -- map to Investment Clock phase + Growth-Inflation
   Positioning (GIP) quadrant, output regime call
3. **domain-teams:investing-team** -- full analysis, conviction scoring,
   portfolio implications

Pass the output JSON verbatim as the `### Input` section when launching
`macro-regime-snapshot`.

## Setup

Requires only `uv` (Python package runner). The `setup.sh` script
auto-installs `uv` if not found. No API keys are needed for either
source -- both the BOJ API and 統計ダッシュボード API are free and
unauthenticated.

```bash
# Manual test -- BOJ call rate
uv run scripts/boj_client.py --db FM01 --code STRDCLUCON --start-date 202501

# Manual test -- e-Stat CPI
uv run scripts/estat_client.py --preset cpi
```

## Maintenance & Verification

### Verify all presets are active + returning data

**e-Stat presets (batch check):**

```bash
cd investing-toolkit/scripts

for p in cpi core-cpi core-core-cpi unemployment ip jgb10y \
  coincident-index leading-index lagging-index \
  machine-orders real-wages job-ratio \
  tertiary-index retail-sales service-sales; do
  uv run estat_client.py --preset "$p" --no-cache 2>&1 | \
    python3 -c "
import json,sys
p='$p'
d=json.load(sys.stdin)
l=d.get('latest') or {}
s=(d.get('_provenance') or {}).get('staleness_days','?')
print(f'{p:20} date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  stale={s}d')
"
done
```

**BOJ series:**

```bash
uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202601
```

### Verify presets are not discontinued

Use `getIndicatorInfo` API to check `toDate`:

```bash
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode={CODE}"
```

- `toDate = 99991200` → ACTIVE
- `toDate = 20241200` → DISCONTINUED — find replacement (see below)

### When a survey is discontinued

1. Check the e-Stat API metadata PDF for old/new StatCode:
   https://dashboard.e-stat.go.jp/static/api
2. Search by new StatCode: `getIndicatorInfo?StatCode={NEW_CODE}`
3. Find monthly + Japan-nationwide variant
4. Update `PRESETS` + `INDICATOR_NAMES` in `estat_client.py`
5. Run `sync-scripts.sh` + `sync-check.sh`

### Add a new indicator

1. Search: `uv run estat_client.py --search "keyword"` (English only)
2. Or by Category: `getIndicatorInfo?Category={CODE}` (see API metadata PDF)
3. Verify: `uv run estat_client.py --indicator {CODE} --no-cache`
4. Add to `PRESETS` dict + `INDICATOR_NAMES` dict + `SKILL.md` + indicator reference file

### Latest verification

**Date**: 2026-04-18 — All 16 indicators (1 BOJ + 15 e-Stat) ACTIVE + Monthly + 2026 data.
**v1.7.0 additions**: `leading-index` + `lagging-index` to complete the 景気動向指数 CI trio
(先行 / 一致 / 遅行) as Japan's monthly GDP proxy package.
**Fixes applied**: `service-sales` (old survey discontinued 2024-12, replaced with new StatCode),
`job-ratio` (old code was fiscal-year only, replaced with monthly code).
