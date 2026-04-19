# Taiwan Stock Data Sources (v1.13.0)

Authoritative reference for `taiwan-stock-snapshot` data architecture: Tier 1
primary (MOPS + TWSE/TPEx OpenAPI), Tier 2 fallback (FinMind), decision tree,
rate limits, and calendar conventions.

---

## 1. Tier 1 Primary: MOPS JSON API

**Source**: `https://mops.twse.com.tw/mops/api/*`
**Script**: `investing-toolkit/scripts/mops_client.py`
**Authority**: 金管會 / 證期局 / 臺灣證券交易所 公開資訊觀測站
**Grounding tier**: **A (法定揭露 primary source)**
**Auth**: none (User-Agent header required)
**Launched**: 2025-02 (new public JSON API; replaces legacy form-post scraping)

### Full action catalog (16 actions)

| Action | MOPS endpoint | Purpose | Statutory basis |
|--------|---------------|---------|-----------------|
| `company-basic` | `t05st03` | 公司基本資料（法人代碼/行業/資本額/董事長） | — |
| `company-overview` | `t05st03_v1` | 擴充公司概況 | — |
| `balance-sheet` | `t164sb03` | 資產負債表（季頻） | 證交法第14條之2 |
| `income-statement` | `t164sb04` | 綜合損益表（季頻） | 證交法第14條之2 |
| `cash-flow` | `t164sb05` | 現金流量表（季頻） | 證交法第14條之2 |
| `financial-status` | `t05st10` | 財務狀況彙整 | — |
| `monthly-revenue` | `t05st10_ifrs` | 月營收（每月10日前公布） | 證交法第36條 |
| `dividends` | `t05st09_2` | 股利政策（除權除息） | — |
| `director-holdings` | `stapap1` | 董監事持股與質押 | 證交法第25條 |
| `insider-trades` | `query6_1` | 內部人持股轉讓事前申報 | 證交法第22條之2 |
| `ex-dividend` | `t108sb19` | 除權除息預告 | — |
| `shareholder-meetings` | `t108sb16_q1` | 股東常會公告 | 公司法第170條 |
| `china-investment` | `t108sb17` | 大陸投資 | — |
| `historical-announcements` | `t05st01` | 公司歷史重訊 | 證交法第36條之1 |
| `day-announcements` | `t05st02` | 當日重大訊息 | 證交法第36條之1 |
| `realtime-announcements` | `t05st01_all` | 即時重大訊息（市場彙整） | — |
| `search-announcements` | `t05st01` | 重訊條件搜尋 | — |

### Known error semantics

All responses are HTTP 200 with envelope `code`:
- `code:200` 查詢成功
- `code:406` 查無相符資料 → returns empty (not an error)
- `code:500` 傳入參數異常 → `MopsParameterError`
- HTTP 302 → `MopsEndpointError` (endpoint renamed / removed)

### Historical depth

- Financial statements: typically 5y backfill; some tickers deeper.
- 月營收: archive 10y+.
- 重訊 / 除權息: rolling; `historical-announcements` supports date range.

---

## 2. Tier 1 Primary: TWSE + TPEx OpenAPI

**Sources**:
- TWSE: `https://openapi.twse.com.tw/v1/*`
- TPEx: `https://www.tpex.org.tw/openapi/v1/*`

**Script**: `investing-toolkit/scripts/twse_openapi_client.py`
**Authority**: 臺灣證券交易所 / 證券櫃檯買賣中心
**Grounding tier**: **A (exchange-authoritative primary source)**
**Auth**: none
**Rate limit**: no explicit limit published; client uses 24h daily / 7d static
cache to minimize traffic.

### Action catalog

| Action | Endpoint | Purpose | Notes |
|--------|----------|---------|-------|
| `listed-companies` | `/opendata/t187ap03_L` | 上市公司名冊 | Metadata |
| `daily-price-all` | `/exchangeReport/STOCK_DAY_ALL` | 全市場日行情 snapshot | Latest session only |
| `daily-price` | (derived) | 單檔日行情 | Filters STOCK_DAY_ALL by ticker |
| `pe-pb-yield` | `/exchangeReport/BWIBBU_ALL` | 個股 PE / PB / 殖利率 | Latest session |
| `margin-balance` | `/exchangeReport/MI_MARGN` | 融資融券餘額 | TWSE 上市 |
| `three-investor` | `/fund/MI_QFIIS_sort_20` | 外資持股 top-20 snapshot | NOT daily flow; holding % only |
| `industry-eps` | `/opendata/t187ap14_L` | 產業 EPS 彙整 | — |
| `ex-dividend-calendar` | `/opendata/t187ap34_L` | 除權除息預告 | Market-wide |
| `tpex-daily-close` | `/tpex_mainboard_daily_close_quotes` | 上櫃日行情 snapshot | — |
| `tpex-margin-balance` | `/tpex_mainboard_margin_balance` | 上櫃融資融券 | — |

### Known Tier 1 gaps (documented 2026-Q2)

| Gap | Impact | Mitigation |
|-----|--------|-----------|
| 日 per-stock 三大法人 flow (T86 dataset) | OpenAPI only exposes `MI_QFIIS_sort_20` (holding snapshot) and `MI_QFIIS_cat` (industry). No per-stock daily buy/sell. | Route to FinMind `TaiwanStockInstitutionalInvestorsBuySell` by default |
| 歷史 STOCK_DAY by date for single ticker | Only `STOCK_DAY_ALL` (latest session) exposed | Route to FinMind `TaiwanStockPrice` for time-series |
| 市場合計三大法人 `BFI82U` | Endpoint returns HTML, not JSON | Route to FinMind `TaiwanStockTotalInstitutionalInvestors`, or skip |

### SSL note

Both `mops.twse.com.tw` and `openapi.twse.com.tw` have known SSL certificate
issues (missing Subject Key Identifier) on some macOS cert chains. Both clients
use `verify=False` with `InsecureRequestWarning` suppressed.

---

## 3. Tier 2 Fallback: FinMind

**Source**: `https://api.finmindtrade.com/api/v4/data`
**Script**: `investing-toolkit/scripts/finmind_client.py`
**Authority**: FinMind (community aggregator; not a statutory source)
**Grounding tier**: **B (curated aggregator; useful for cross-check / gap fill)**
**Auth**: `FINMIND_API_TOKEN` env var (optional)
**Rate limit**: 300 req/hr anonymous; 600 req/hr with token; 1000+ with Pro tier
**Free token**: https://finmindtrade.com/

### Role in v1.13.0

FinMind is NOT deprecated — it serves three purposes:

1. **Pattern A auto-fallback** — triggered when Tier 1 returns HTTP 5xx /
   network error / timeout > 30s / schema drift.
2. **Pattern B manual override** — `--source finmind` forces FinMind path
   for cross-validation or ISQ gate stress-test.
3. **Coverage gap filler** — datasets Tier 1 does not provide (see decision
   tree below).

### Dataset-to-endpoint mapping

| FinMind Dataset ID | Tier 1 equivalent | Role |
|-------------------|-------------------|------|
| `TaiwanStockPrice` | TWSE STOCK_DAY_ALL (snapshot only) | **Gap fill** — historical time-series |
| `TaiwanStockInstitutionalInvestorsBuySell` | (none; TWSE OpenAPI lacks T86) | **Gap fill** — daily per-stock 三大法人 flow |
| `TaiwanStockMarginPurchaseShortSale` | TWSE MI_MARGN (snapshot) | **Gap fill** — time-series; also fallback |
| `TaiwanStockHoldingSharesPer` | MOPS `director-holdings` (stapap1) | Fallback / cross-check |
| `TaiwanStockMonthRevenue` | MOPS `monthly-revenue` (t05st10_ifrs) | Fallback / cross-check |
| `TaiwanStockFinancialStatements` | MOPS `balance-sheet` + `income-statement` | Fallback |
| `TaiwanStockProfitLossStatement` | MOPS `income-statement` | Fallback |

---

## 4. Fallback Decision Tree

```
                        ┌─────────────────────────┐
                        │  User invokes skill     │
                        └────────────┬────────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       │                           │
              --source finmind?                Default
                       │                           │
                       ▼                           ▼
              ┌──────────────┐          ┌─────────────────┐
              │ FinMind only │          │  Try Tier 1     │
              │ (Pattern B)  │          │  (MOPS + TWSE)  │
              └──────────────┘          └────────┬────────┘
                                                 │
                                  ┌──────────────┴──────────────┐
                                  │                             │
                              Success                      5xx / timeout /
                                  │                        schema drift
                                  ▼                             │
                        ┌──────────────┐                        ▼
                        │ Return Tier 1│            ┌───────────────────────┐
                        │ + provenance │            │  --no-fallback?       │
                        └──────────────┘            └────────┬──────────────┘
                                                             │
                                              ┌──────────────┴──────────────┐
                                              │                             │
                                             Yes                           No
                                              │                             │
                                              ▼                             ▼
                                  ┌───────────────────┐         ┌─────────────────────┐
                                  │  Fail loud        │         │ Log warning →       │
                                  │  (Tier 1 error)   │         │ FinMind equivalent  │
                                  └───────────────────┘         │ (Pattern A)         │
                                                                └─────────────────────┘
```

### Per-field fallback table

| Requested field | Tier 1 primary | Auto-fallback target | By-design routing |
|-----------------|----------------|----------------------|-------------------|
| 公司基本 | MOPS `company-basic` | FinMind `TaiwanStockInfo` | Tier 1 |
| BS / IS / CF | MOPS `balance-sheet` / `income-statement` / `cash-flow` | FinMind `TaiwanStockFinancialStatements` | Tier 1 |
| 月營收 | MOPS `monthly-revenue` | FinMind `TaiwanStockMonthRevenue` | Tier 1 |
| 董監持股 | MOPS `director-holdings` | FinMind `TaiwanStockHoldingSharesPer` | Tier 1 |
| 股利 | MOPS `dividends` | — (MOPS only) | Tier 1 |
| 重大訊息 | MOPS `realtime-announcements` | — (MOPS only) | Tier 1 |
| 日行情 snapshot | TWSE `daily-price` | FinMind `TaiwanStockPrice` (last row) | Tier 1 |
| PE / PB / 殖利率 | TWSE `pe-pb-yield` | — (TWSE only) | Tier 1 |
| 融資融券 snapshot | TWSE `margin-balance` | FinMind `TaiwanStockMarginPurchaseShortSale` | Tier 1 |
| 外資持股 % snapshot | TWSE `three-investor` | — (holding only; not flow) | Tier 1 |
| **歷史 OHLCV** | (Tier 1 gap) | — | **FinMind default** |
| **日 三大法人 flow** | (Tier 1 gap) | — | **FinMind default** |
| **融資融券 time-series** | (Tier 1 gap) | — | **FinMind default** |

---

## 5. Rate Limits & Conventions

| Source | Rate limit | Cache TTL (client default) |
|--------|-----------|----------------------------|
| MOPS JSON API | Unpublished; client self-throttles 0.3s between calls | 24h current / permanent historical / 5min realtime |
| TWSE OpenAPI | Unpublished; no throttle in client | 24h daily / 7d metadata |
| TPEx OpenAPI | Unpublished | 24h |
| FinMind | 300 req/hr anon / 600 w/ token | 24h |

### Retry policy

- `mops_client.py`: 3 retries with exponential backoff (base 2s)
- `twse_openapi_client.py`: 3 retries with exponential backoff (base 2s)
- `finmind_client.py`: 3 retries with exponential backoff

### User-Agent requirement

Both MOPS and TWSE reject requests without a browser User-Agent. Clients use:
`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36`

---

## 6. Calendar Convention

| Source | Year format | Date format | Notes |
|--------|-------------|-------------|-------|
| MOPS | **ROC year** (民國年 = Gregorian − 1911) | `YYY/MM/DD` in responses | 2024 = ROC 113 ; 2026 = ROC 115 |
| TWSE OpenAPI | Gregorian | `YYYYMMDD` | Most fields |
| TPEx OpenAPI | ROC inside response bodies | `YYY/MM/DD` in response | Convert before comparison |
| FinMind | Gregorian | `YYYY-MM-DD` | Standard ISO |

Conversion helpers in `mops_client.py`:
```python
_roc_to_gregorian(roc_year)   # 113 → 2024
_gregorian_to_roc(year)        # 2024 → 113
```

Caller responsibility: convert Gregorian → ROC BEFORE invoking `mops_client`
(year/season/month args).

---

## 7. Primary-Source Grounding Classification

| Source | Grounding tier | Rationale |
|--------|---------------|-----------|
| MOPS JSON API | **A (法定揭露)** | 證交法第14條之2 / 第25條 / 第36條 statutory disclosure; official 金管會 system |
| TWSE OpenAPI | **A (exchange primary)** | 臺灣證券交易所 official OpenAPI; exchange-authoritative market data |
| TPEx OpenAPI | **A (exchange primary)** | 證券櫃檯買賣中心 official OpenAPI |
| FinMind | **B (curated aggregator)** | Third-party aggregation of public data; useful for cross-check & gap fill; not authoritative |

All Tier 1 defaults in `taiwan-stock-snapshot` satisfy **primary-source
grounding Tier A** for the `domain-teams:investing-team` Taiwan-Specific
Diagnosis gate. FinMind-sourced fields (by-design gap-fill or fallback) carry
`_meta.grounding_tier: "B"` and should be cross-checked against MOPS on ISQ
gate if material.

---

## 8. Attribution Corrections (Taiwan domain)

Enforced in script `_processed` output and card rendering:

1. **月營收截止日是每月10日（曆日）** — per 證交法第36條 + FSC 行政命令.
   Not end-of-month, not the 15th.
2. **融資 vs 融券 方向相反** — 融資餘額↑ = 散戶加碼多單（bullish retail）;
   融券餘額↑ = 放空部位增加（bearish）. Do NOT combine into a single flow.
3. **三大法人 特性不同** — 外資（大型/趨勢跟隨）、投信（較小/常逆外資）、
   自營商（多為避險，方向參考意義較低）. Do NOT collapse to a single
   "法人" signal.
4. **董監持股質押率 > 50% = 治理紅旗** — high pledge ratio creates an
   incentive to depress stock price (葉銀華 2008).

---

## 9. Taiwan Market Calendar Notes

- **月營收公布**：每月10日前（逾期申報有罰則，證交法第36條第1項）
- **季報公布**：Q1 (5/15) / Q2 (8/14) / Q3 (11/14) / Q4 (翌年 3/31)
- **除息除權**：通常 7–9 月集中（Taiwan dividend season）
- **台股交易時間**：09:00–13:30 (TST, UTC+8)
- **台股代號格式**：上市 = 4碼.TW；上櫃 = 4碼.TWO；興櫃 = 4碼.TWG (少用)

---

## 10. External: CasualMarket MCP (optional real-time)

Not bundled. Install separately:
```bash
claude plugin add casualmarket
```

Provides real-time TWSE/OTC quotes (延遲15分鐘), live 三大法人 feed, and
real-time valuation multiples. When installed, skills can call it alongside
the Tier 1/2 primary-source pipeline above for a "live" layer — but verdicts
and ISQ gates always anchor on MOPS + TWSE OpenAPI primary sources.
