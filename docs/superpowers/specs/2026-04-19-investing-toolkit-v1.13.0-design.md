# Design Spec: investing-toolkit v1.13.0 — Individual Stock Fundamentals (US + TW)

**Date**: 2026-04-19
**Previous release**: investing-toolkit v1.12.0 (PR #95, merged 2026-04-19) — Pattern C UX
**Cross-plugin**: investing-toolkit only (domain-teams unchanged)

## 1. Goal

Pattern C NVDA demo (2026-04-19) + post-merge audit surfaced that individual stock analysis is **structurally insufficient** for fundamental deep-dive. research-team's ISQ verdict hit `PASS_WITH_NOTES` (not clean `PASS`) specifically because of 4 data gaps:

1. **Missing SEC EDGAR** 10-K / 10-Q / 8-K / Form 4 / 13F / S-1 / DEF 14A → revenue quality, segment mix, customer concentration, insider flow all qualitative-only
2. **Missing forward guidance**
3. **Missing analyst consensus distribution**
4. **Missing peer financials**

Separately, `dcf-valuation` skill is **structurally pre-crippled** — without income statement + cash flow data, 3-stage DCF is unbuildable from toolkit fetched data.

v1.13.0 closes this gap for **US + TW** (user's main markets). **JP defers to v1.14.0 stacked PR** per Path γ architecture decision.

## 2. Context

### 2.1 Pattern C demo observation (2026-04-19)

- NVDA memo via investment-memo-writer → research-team Deep Equity Research Memo → ISQ `PASS_WITH_NOTES`
- Explicit reason: yfinance lacks financial statements; no SEC EDGAR fetcher in toolkit
- research-team self-recommendation quote: "If this memo will drive an allocation decision >$100k, escalate to deep mode with a data-fetcher run pulling (a) NVDA latest 10-K + 10-Q from SEC EDGAR, (b) sell-side consensus, (c) peer comp set"

### 2.2 MOPS JSON API probe (2 rounds, 2026-04-19)

New MOPS (`mops.twse.com.tw`, launched 2025-02) has a **public JSON API at `/mops/api/*`** accessible via standard POST + `User-Agent: Mozilla/5.0`. No auth / session / cookie / CSRF needed.

**16 confirmed endpoints** covering 公司揭露 + 財務報表 + 持股 + 重大訊息 + 股利 + 股東會 + 除權息. Historical depth: IFRS 財報 ROC 102→115 (13 years), 月營收 ROC 103→115 (12 years), 歷史重大訊息 ROC 85→115 (30 years).

**MOPS = 公司揭露 only**. No price / trading / 三大法人 / 融資融券 via MOPS — those live in TWSE OpenAPI (`openapi.twse.com.tw`).

### 2.3 Primary-source hierarchy for TW

| Source | Tier | Coverage |
|--------|------|----------|
| **MOPS JSON API** | **A primary** (金管會法定揭露) | 公司揭露 + 財報 + 持股 + 股利 |
| **TWSE/TPEx OpenAPI** | **A primary** (交易所官方) | 交易資料 + 行情 + 三大法人 / 融資融券 |
| FinMind | B aggregator | 前兩者的 re-curated 版本 — **保留作 Tier 2 fallback** |

### 2.4 SEC EDGAR scope (US)

SEC EDGAR `data.sec.gov` REST API — 官方 free, no auth. 2 layers:

- **Structured (XBRL facts)**: `/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json` — 數字 facts with period/filing reference
- **Narrative (Item sections)**: HTML filings at `www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary}.htm` — parse by Item headers (10-K Item 1 Business / 1A Risk / 7 MD&A / 7A Market Risk / 8 FS+Notes; 10-Q Item 1 FS / Item 2 MD&A)

Forms covered: **10-K + 10-Q + 8-K + Form 4 + 13F + S-1/S-3 + DEF 14A** (user decision Q1 Option C — 全都要).

### 2.5 User's 3 main markets per Path γ decision

- **v1.13.0 (this PR)**: US + TW
- **v1.14.0 (stacked next)**: JP — new `japan-stock-snapshot` skill; EDINET / TDnet considerations evaluated after v1.13.0 learnings
- Later: KR / CN as demand surfaces

## 3. Scope — single PR, 8 commits

### 3.1 Commit 1 — `sec_edgar_client.py`

**File**: `investing-toolkit/scripts/sec_edgar_client.py` (NEW)

Style: match `fred_client.py` convention (uv inline script + `INVESTING_TOOLKIT_CACHE` env var + `_provenance` block + CLI argparse).

**API surface**:
```python
def resolve_cik(ticker: str) -> str:
    # data.sec.gov/files/company_tickers.json → mapping
    # Cache 7 days (rarely changes)

def fetch_facts(ticker: str, concept: str = None) -> dict:
    # /api/xbrl/companyfacts/CIK{cik}.json (all facts)
    # Or /api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json (single)

def fetch_filings(ticker: str, forms: list = None, limit: int = 10) -> list:
    # /submissions/CIK{cik}.json → recent filings index
    # forms filter: 10-K, 10-Q, 8-K, 4, 13F-HR, S-1, S-3, DEF 14A

def fetch_narrative(accession: str, ticker: str = None) -> dict:
    # Download primary HTML filing from Archives
    # Parse by Item regex, return {"Item 1 Business": "...", "Item 1A Risk Factors": "...", ...}
    # Cache per accession (10-K filings don't change)
```

**CLI**:
- `--ticker NVDA --action cik` → resolve ticker to CIK
- `--ticker NVDA --action facts` → full companyfacts JSON
- `--ticker NVDA --action facts --concept Revenues` → single concept time-series
- `--ticker NVDA --action filings --forms 10-K,10-Q --limit 8` → recent filings
- `--accession 0001045810-24-000316 --action narrative` → Item-parsed HTML

**Cache**:
- `$CACHE/sec_edgar/tickers.json` (7 day TTL)
- `$CACHE/sec_edgar/facts_{CIK}.json` (24 hr TTL)
- `$CACHE/sec_edgar/submissions_{CIK}.json` (24 hr TTL)
- `$CACHE/sec_edgar/filing_{accession}_{concept}.md` (permanent — filings don't change)

**Rate limit**: SEC EDGAR requires identified `User-Agent: "kouko (noreply@anthropic.com)"` format + ≤10 req/sec. Built-in throttle.

**Narrative parser**: regex `^Item\s+(\d+[A-Z]?)\.\s+(.+?)$` to detect section boundaries; extract text between consecutive Item headers; store per-Item as separate markdown cache file.

### 3.2 Commit 2 — `us-stock-snapshot` SKILL.md enhance

**Files**:
- `investing-toolkit/skills/us-stock-snapshot/SKILL.md`
- `investing-toolkit/skills/us-stock-snapshot/references/sec-edgar-guide.md` (NEW)

**SKILL.md changes**:
- New data source: SEC EDGAR via `sec_edgar_client.py`
- Workflow: yfinance (price + metadata) + SEC EDGAR (financial statements + narrative)
- Explicit note: yfinance becomes the **snapshot** layer; SEC EDGAR becomes the **fundamental** layer
- Data gap reduction: from 4 explicit gaps (Pattern C demo) to ~0-1

**Reference doc** (new):
- SEC EDGAR API overview + rate limit conventions
- Form coverage + use cases (10-K for annual deep-dive; 10-Q for current quarter; 8-K for events; Form 4 for insider; 13F for institutional ownership; S-1/S-3 for offerings; DEF 14A for governance)
- XBRL fact taxonomy basics (us-gaap concepts)
- Narrative Item-section extraction methodology

### 3.3 Commit 3 — `mops_client.py`

**File**: `investing-toolkit/scripts/mops_client.py` (NEW)

**API surface** (15 real working endpoints + `t146sb10` optional):
```python
class MopsClient:
    BASE = "https://mops.twse.com.tw/mops/api"
    
    def _post(endpoint: str, body: dict) -> dict:
        # Shared POST with User-Agent, JSON body, 406/500 handling
    
    def get_company_basic(ticker: str) -> dict:       # t05st03
    def get_company_overview(ticker: str) -> dict:    # t146sb05
    def get_financial_status(ticker: str, year: int, season: int) -> dict:  # t163sb01
    def get_balance_sheet(ticker: str, year: int, season: int) -> pd.DataFrame:  # t164sb03
    def get_income_statement(ticker: str, year: int, season: int) -> pd.DataFrame:  # t164sb04
    def get_cash_flow(ticker: str, year: int, season: int) -> pd.DataFrame:  # t164sb05
    def get_monthly_revenue(ticker: str, year: int, month: int) -> dict:  # t05st10_ifrs
    def get_dividends(ticker: str, first_year: int, last_year: int) -> dict:  # t05st09_2
    def get_director_holdings(ticker: str, year: int, month: int) -> dict:  # stapap1
    def get_insider_trades(ticker: str, year: int, month: int) -> dict:  # query6_1
    def get_ex_dividend(ticker: str, year: int) -> dict:  # t108sb19
    def get_shareholder_meetings(ticker: str, year: int) -> dict:  # t108sb16_q1
    def get_realtime_announcements(market: str = "sii", count: int = 10) -> list:  # home_page/t05sr01_1
    def get_historical_announcements(ticker: str, year: int) -> list:  # t05st01
    def get_day_announcements(year: int, month: int, day: int) -> list:  # t05st02
    # Optional P3:
    def search_announcements(ticker: str, first_date: str, last_date: str, announcement_type: int) -> list:  # t146sb10
```

Helper:
- `_roc_to_gregorian(roc_year: int) -> int`: ROC → 西元
- `_gregorian_to_roc(year: int) -> int`: 西元 → ROC
- `_parse_report_list(report_list: list) -> pd.DataFrame`: parse `reportList` into tidy DataFrame with 金額 + % columns

**CLI**:
```
uv run mops_client.py --ticker 2330 --action balance-sheet --year 113 --season 4
uv run mops_client.py --ticker 2330 --action monthly-revenue --year 115 --month 3
uv run mops_client.py --ticker 2330 --action insider-trades --year 113 --month 12
```

**Cache**: `$CACHE/mops/{action}_{ticker}_{period}.json` — 24hr TTL for most, permanent for filed reports (BS/IS/CF past quarters).

**Error handling**:
- `code:200` → success
- `code:406` → no data for given period → log warning, return empty
- `code:500` → bad params → raise exception
- HTTP 302 → endpoint name invalid → raise exception (no retry)

**Rate limit**: observed zero throttling at 20 concurrent during probe. Conservative sleep 0.3s between calls in batch mode.

### 3.4 Commit 4 — `twse_openapi_client.py`

**File**: `investing-toolkit/scripts/twse_openapi_client.py` (NEW)

Covers data NOT in MOPS (交易 / 行情 / 法人 / 融資融券):

**API surface**:
```python
BASE_TWSE = "https://openapi.twse.com.tw/v1"
BASE_TPEX = "https://www.tpex.org.tw/openapi/v1"

class TwseOpenApiClient:
    def get_three_investor_buy_sell(ticker: str) -> dict:  # /fund/MI_QFIIS_sort_20
    def get_margin_balance() -> pd.DataFrame:  # /exchangeReport/MI_MARGN
    def get_daily_price(ticker: str, date: str = None) -> dict:  # /exchangeReport/STOCK_DAY_ALL or STOCK_DAY
    def get_listed_companies() -> pd.DataFrame:  # /opendata/t187ap03_L (ALL listed + basic info)
    def get_daily_market_announcements(date: str = None) -> list:  # /opendata/t187ap04_L
    def get_industry_eps_summary() -> pd.DataFrame:  # /opendata/t187ap14_L
    def get_ex_dividend_calendar() -> pd.DataFrame:  # /opendata/t187ap34_L
```

**CLI**:
```
uv run twse_openapi_client.py --ticker 2330 --action three-investor
uv run twse_openapi_client.py --action daily-price --ticker 2330
uv run twse_openapi_client.py --action industry-eps
```

**Cache**: `$CACHE/twse_openapi/{action}_{date}.json` — 24hr TTL for daily data, 1hr TTL for intraday.

### 3.5 Commit 5 — `taiwan-stock-snapshot` SKILL.md rebuild

**Files**:
- `investing-toolkit/skills/taiwan-stock-snapshot/SKILL.md`
- `investing-toolkit/skills/taiwan-stock-snapshot/references/data-sources.md` (enhanced)

**Architecture**:

```
Tier 1 PRIMARY (Tier A authoritative):
  ├── mops_client.py (公司揭露: 財報 / 月營收 / 持股 / 重大訊息 / 股利)
  └── twse_openapi_client.py (交易: 三大法人 / 融資融券 / 個股行情)

Tier 2 FALLBACK (Pattern A+B):
  └── finmind_client.py (aggregator — triggered only on HTTP 5xx / network fail / timeout)
      ├── Auto-fallback with warning log
      ├── CLI --no-fallback disables
      └── CLI --source finmind forces explicit use (testing / cross-validation)
```

**Default fetch payload** for `taiwan-stock-snapshot` invocation on ticker 2330:
- `company_info` (mops_client)
- `latest_balance_sheet` (mops_client, most recent quarter)
- `latest_income_statement` (mops_client)
- `latest_cash_flow` (mops_client)
- `monthly_revenue_12m` (mops_client, past 12 months)
- `director_holdings` (mops_client)
- `insider_trades_recent` (mops_client, past 3 months)
- `dividends_5y` (mops_client)
- `price_1y` (twse_openapi_client, 1y daily OHLCV or yfinance.T fallback)
- `three_investor_recent` (twse_openapi_client, recent 30 days)
- `margin_balance_recent` (twse_openapi_client)

Extended (--deep flag):
- `historical_financials_5y` (20 quarters via mops_client)
- `ex_dividend_history_5y` (mops_client)
- `shareholder_meetings_3y` (mops_client)

### 3.6 Commit 6 — `dcf-valuation` SKILL.md enhance

**File**: `investing-toolkit/skills/dcf-valuation/SKILL.md`

Update to reflect financial statements now available:
- **US**: DCF derived from SEC EDGAR `revenues / costOfGoodsSold / operatingIncomeLoss / netIncomeLoss / cashAndCashEquivalents / propertyPlantAndEquipmentNet` etc. XBRL facts + narrative 10-K context
- **TW**: DCF derived from MOPS 損益表 / 資產負債表 / 現金流量表 (3 tables × 46-80 rows pre-parsed)
- **Data gap note removed**: previously flagged as "needs SEC EDGAR manual supply"; now auto-fetched

### 3.7 Commit 7 — `investment-memo-writer` Phase 1 commands

**File**: `investing-toolkit/skills/investment-memo-writer/SKILL.md`

Extend Phase 1 data-fetcher commands per market:

**US ticker** additions:
```
uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action filings --forms 10-K,10-Q,8-K,4 --limit 8
uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action facts
```

**Taiwan ticker** (replaces current FinMind commands):
```
uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action balance-sheet --year {current_roc} --season {last_reported_q}
uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action income-statement --year {current_roc} --season {last_reported_q}
uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action cash-flow --year {current_roc} --season {last_reported_q}
uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action monthly-revenue --year {current_roc} --month {current_month}
uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action three-investor
uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action margin-balance
uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action director-holdings --year {current_roc} --month {current_month}
```

FinMind commands demoted to "fallback — invoked only when primary fails or user sets --source finmind".

### 3.8 Commit 8 — Plugin-level sync

- `investing-toolkit/.claude-plugin/plugin.json` — `1.12.0` → `1.13.0`
- `investing-toolkit/README.md` — v1.13.0 Version Highlights prepended
- `investing-toolkit/ROADMAP.md` — v1.13.0 current with 8-phase breakdown + v1.13.x / v1.14.0 candidates

## 4. Data Flow

```
US ticker (e.g. NVDA):
  yfinance (price + metadata)
    + SEC EDGAR JSON API (XBRL facts + filings list)
    + SEC EDGAR HTML narrative (Item-parsed 10-K / 10-Q)
  → us-stock-snapshot (enriched data fixture)
  → macro-regime-snapshot (regime call)
  → investment-memo-writer Phase 3 → research-team (deep memo)

Taiwan ticker (e.g. 2330.TW):
  MOPS JSON API (16 endpoints: 公司 + 財報 + 持股 + 揭露 + 股利)
    + TWSE/TPEx OpenAPI (三大法人 / 融資融券 / 行情)
    + FinMind fallback (auto on Tier 1 failure; opt-out via --no-fallback)
  → taiwan-stock-snapshot (enriched fixture)
  → macro-regime-snapshot (regime call)
  → investment-memo-writer Phase 3 → research-team (deep memo w/ Taiwan gate auto-triggered)
```

## 5. Error Handling

- **SEC EDGAR 429** (rate limit): respect Retry-After header; exponential backoff up to 3 retries
- **SEC EDGAR filing not found**: return empty with `_provenance.note: "No filing matching criteria"`
- **MOPS 406** (no data for period): log warning, return empty (not an error)
- **MOPS 500** (bad params): raise `MopsParameterError` with exact `message` field
- **MOPS HTTP 302** (endpoint invalid): raise `MopsEndpointError`
- **TWSE OpenAPI schema change**: schema drift tolerated; unknown fields preserved in `_raw` subkey
- **FinMind fallback trigger**: warning log `"Primary source X failed (reason); falling back to FinMind"`
- **FinMind fallback disabled + Tier 1 fail**: raise error to caller; no silent data loss

## 6. Testing & Verification

Per-commit smoke tests:

| Commit | Smoke test |
|--------|-----------|
| 1 | `uv run scripts/sec_edgar_client.py --ticker NVDA --action filings --forms 10-K --limit 3` returns latest 3 NVDA 10-K filings with accession numbers |
| 1 | `uv run scripts/sec_edgar_client.py --ticker NVDA --action facts --concept Revenues` returns revenue time-series |
| 1 | `uv run scripts/sec_edgar_client.py --accession {recent_nvda_10k} --action narrative` returns dict keyed by Item sections |
| 2 | us-stock-snapshot SKILL.md references sec_edgar_client.py in data source table |
| 3 | `uv run scripts/mops_client.py --ticker 2330 --action balance-sheet --year 113 --season 4` returns ≥ 50 rows |
| 3 | `uv run scripts/mops_client.py --ticker 2330 --action monthly-revenue --year 115 --month 3` returns 2026-03 data |
| 4 | `uv run scripts/twse_openapi_client.py --ticker 2330 --action three-investor` returns 30-day foreign/investment-trust flow |
| 4 | `uv run scripts/twse_openapi_client.py --ticker 2330 --action margin-balance` returns margin 餘額 |
| 5 | taiwan-stock-snapshot SKILL.md orchestrates mops + twse_openapi; references FinMind as Tier 2 |
| 6 | dcf-valuation SKILL.md references financial statements availability |
| 7 | investment-memo-writer Phase 1 has SEC EDGAR + MOPS + TWSE OpenAPI commands |
| 8 | `plugin.json` version = 1.13.0; sync-check exit 0 |

**Pattern C re-run verification** (end-to-end, after all commits):
```
/invest-memo --ticker NVDA --scope deep
```
Expected: ISQ verdict `PASS` (no longer `PASS_WITH_NOTES`) because 4 data gaps are now filled. Memo includes real 10-K MD&A narrative excerpts + actual revenue history + peer comparable framework.

```
/invest-memo --ticker 2330.TW --scope deep
```
Expected: ISQ `PASS`; memo includes MOPS 損益表 / 資產負債表 / 現金流量表 + 月營收 trajectory + 三大法人 recent flow + 董監持股 snapshot.

## 7. Explicit Non-goals

- **NO** japan-stock-snapshot (v1.14.0 stacked)
- **NO** korea-stock-snapshot / china-stock-snapshot (later)
- **NO** analyst consensus distribution (v1.13.x or v1.14.0+)
- **NO** options IV / Greeks / unusual activity
- **NO** paid API integration (finnhub / alphavantage)
- **NO** historical full-filing archive backfill (fetch-on-demand only)
- **NO** TWSE 舊版 mopsov.twse.com.tw scraper (new API covers needs)
- **NO** playwright browser automation (pure requests sufficient)

## 8. Branch + PR

```
Branch: feat/individual-stock-fundamentals-v1.13.0
PR title: feat(investing-toolkit): v1.13.0 individual stock fundamentals (US SEC EDGAR + TW MOPS)
Base: main
Stack: 8 commits
```

## 9. Self-Review

- **Placeholder scan**: no TBD / TODO in spec. `sec_edgar_client.py` CIK mapping + XBRL concept taxonomy = implementation-time probing (documented).
- **Internal consistency**: 8-commit structure mirrors v1.9.0-v1.12.0 patterns.
- **Scope check**: ~6 days — larger than v1.12.0 (3.5 days) smaller than v1.11.0 (~6.5 days). Appropriately sized.
- **Ambiguity check**:
  - FinMind fallback pattern (Pattern A+B combo) — auto-fallback + CLI override. Default is primary-only with auto-fallback on 5xx/timeout
  - SEC EDGAR narrative parsing scope — regex Item-section headers, per-accession cache. Format drift on rare formatting = `PASS_WITH_NOTES` in log, not error
  - MOPS `dataType` — client always uses `"2"` (reproducible historical) for default fetches; `"1"` (latest) only for realtime dashboard mode

## 10. Deferred to v1.13.x / v1.14.0+

- **v1.14.0 (stacked)**: japan-stock-snapshot (yfinance .T + evaluate EDINET XBRL)
- **v1.13.x patches**: analyst consensus (finnhub / alphavantage), options data, market-wide MOPS queries (t146sb10 broader coverage)
- **v1.15.0+**: korea-stock-snapshot (FDR + DART), china-stock-snapshot (akshare extended)
- **Analysis enhancements**: peer comp batch fetcher, earnings surprise tracker, insider flow aggregator
