# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Claude Code 跨國投資資料 plugin — 涵蓋 5 個市場總經（US/JP/TW/KR/CN）、個股 snapshot、DCF 與 screener workflow，以及將分析委派給 `domain-teams:investing-team` 的 memo pipeline。

## Cowork 相容性

⚠️ **僅支援 Claude Code CLI。** Claude Desktop Cowork 的 sandbox URL allowlist 同時阻擋 subprocess 與 plugin 內 MCP 的 HTTP request，因此外部 data fetch（yfinance、FRED、NBS、EDINET 等）在 Cowork 內無法到達 provider。v1.16.1 已 empirical 驗證 — retrospective 與 "what works where" 對照表請見 [`docs/mcp-setup.md`](docs/mcp-setup.md)。

## Version 與 part-of

- Version：1.16.5
- Part of：[`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License：MIT

## Background

investing-toolkit 是跨國投資研究的 **data layer**。從 14 個以上的 public provider 取得 primary source 的總經與個股資料、執行機械式彙總（regime call、screener、DCF、P&L），再把結構化 fixture 交給 `domain-teams:investing-team` 進行分析、gate enforcement，並產生 BUY/HOLD/SELL verdict。Plugin 嚴格區分 `data ↔ analysis` — toolkit 端不嵌入投資判斷，domain-team 端不直接連 data source。詳見後段 [Cross-Plugin Delegation Contract](#cross-plugin-delegation)。

## Monthly GDP proxy framework

5 個 country macro skill 都提供一致的 **monthly GDP proxy**，讓跨市場 regime call 能 like-for-like 比較。主要經濟體官方 GDP 多為季度發布；proxy framework 用各統計機關既有的 pre-aggregated 系列填補月度缺口。

| 市場 | Proxy 類型 | 指標 |
|--------|-----------|------------|
| US | Pre-aggregated Fed nowcast | `nowcast` group：GDPNow、CFNAI、WEI、OECD CLI |
| JP | Pre-aggregated 內閣府合成指數 | 景氣動向指數 CI trio：一致 (proxy)、先行、遅行 |
| TW | Pre-aggregated NDC + DGBAS | `signal`（五色景氣燈號 — 台灣特色）、領先指標、同時指標 |
| KR | Pre-aggregated BOK ECOS | 동행지수순환변동치 (proxy) + 선행지수순환변동치 |
| CN | Raw 元件（無共識 aggregator） | 三大數據：industrial-yoy、retail-yoy、fai-yoy + services-production-yoy |

US/JP/TW/KR 直接提供統計機關的 **pre-aggregated** 值。CN 保留 raw 元件 — 因為沒有市場共識的月度合成方法（李克強指數 2012 年後過時、SF Fed CAT 是季度且為標準差單位、Goldman / Bloomberg 是 proprietary），合成屬於需要對方法論負責的 analysis layer。

Sector 層級（產業）的 cadence 細節見 [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md)。

## Slash command

| Command | 路由至 | 說明 |
|---------|-----------|-------------|
| `/invest` | `using-investing-toolkit` | Router — 描述目的後 dispatch |
| `/invest-macro` | `macro-regime-snapshot` | 5-block regime dashboard (`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`) |
| `/invest-memo {ticker}` | `investment-memo-writer` | 完整 memo pipeline → `domain-teams:investing-team` |
| `/invest-screen {tickers}` | `stock-screener` | 多條件 screener 並依複合 score 排名 |
| `/invest-portfolio` | `invest-portfolio` | P&L snapshot + 總經 regime overlay + rebalance |

## Skill

15 個 skill，分為三層 + 1 router。

### Data layer

| Skill | 說明 |
|-------|-------------|
| `us-macro` | FRED CSV — 31 系列 / 14 group（rates / inflation / growth / nowcast / real-rates / pmi / swap-spreads + 7 個對應 sector ETF 的產業 group） |
| `japan-macro` | BOJ + 統計ダッシュボード + ECB SDMX + MoF 物価連動国債落札快照 — 27 preset / 10 group（含 v1.10.0 的 `real-rates` C+D+E multi-source） |
| `taiwan-macro` | stat.gov.tw + CBC + DGBAS + NDC — 32 個指標（含五色景氣燈號 + CIER PMI/NMI） |
| `korea-macro` | FinanceDataReader BOK ECOS-KEYSTAT — 54 個指標 / 13 group（含每月 industry activity 層） |
| `china-macro` | NBS new-SPA API + PBOC/Caixin via akshare + FRED + yfinance — 36 個指標（含 Caixin + NBS 雙系統 PMI） |
| `us-stock-snapshot` | yfinance 價格/估值 + SEC EDGAR 10-K/10-Q/8-K + XBRL facts + Item-section narrative |
| `taiwan-stock-snapshot` | MOPS JSON + TWSE/TPEx OpenAPI Tier A primary、FinMind Tier 2 fallback（三大法人 / 月營收 / 融資融券 / 董監持股 / 重大訊息） |
| `japan-stock-snapshot` | EDINET v2 + TDnet (Yanoshin) + yfinance `.T` — dual-mode（有 `EDINET_API_KEY` → Tier A，沒有則 yfinance financials Tier 2 fallback） |
| `technical-snapshot` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200（從 OHLCV 計算） |

### Aggregation layer

| Skill | 說明 |
|-------|-------------|
| `macro-regime-snapshot` | 5 國 IC + Hedgeye GIP regime call + Rate Stress Dashboard（real rate + swap spread）；5×9 跨國 coverage grid |
| `stock-screener` | 對使用者提供的 ticker list 進行複合 score screener（8 個 preset：value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced） |
| `dcf-valuation` | 三段式 DCF（Damodaran 2012 Ch.12）+ 3×3 sensitivity table + Graham/Klarman verdict |
| `invest-portfolio` | Holdings parser + 批次價格抓取 + 總經 overlay + 部位 P&L |

### Delegation layer

| Skill | 說明 |
|-------|-------------|
| `investment-memo-writer` | 完整 memo pipeline：data-fetcher agent → macro-regime-snapshot → `domain-teams:investing-team`（Deep Equity Research Memo protocol + 2 MUST + 4 SHOULD + 1 MAY gate）→ 選用 `domain-teams:docs-team` |

### Router

| Skill | 說明 |
|-------|-------------|
| `using-investing-toolkit` | 入口 — 14 個 skill 的 intent routing |

## Architecture

```
slash command           skill                       agent / delegate           data source
─────────────           ─────                       ────────────────           ───────────
/invest-memo NVDA   →   investment-memo-writer  →   data-fetcher (haiku)   →   yfinance, FRED, ...
                                                ↘   macro-regime-snapshot
                                                ↘   domain-teams:investing-team   (analysis + gate)
                                                ↘   domain-teams:docs-team        (選用)
```

Adapter 的 SSOT 集中在 [`scripts/`](scripts/)。每支 `*_client.py` 有三種呼叫方式：任何 skill 透過 `uv run` subprocess 執行、註冊在 [`servers/mcp_server.py`](servers/mcp_server.py) 的 MCP tool（18 個 client / 29 個 tool），或當作 Python module 直接 import。Subprocess 與 MCP 兩條路徑回傳 byte 等價的 JSON，CI guard（`tests/test_mcp_equivalence_auto.py`）持續監控避免 drift。

`skills/*/scripts/` 下的 skill 內副本由 [`sync-scripts.sh`](scripts/sync-scripts.sh) 從正本 `scripts/` 同步，CI 用 [`sync-check.sh`](scripts/sync-check.sh) 驗證。

## Setup

Plugin 在首次安裝時會自動 bootstrap，幾乎不需手動 setup。

```bash
# 在 Claude Code CLI 內執行
/plugin marketplace add kouko/monkey-skills
/plugin install investing-toolkit
```

首次啟動時 MCP bootstrap（`servers/mcp_bootstrap.sh`）會背景執行 `setup.sh` 安裝 [`uv`](https://docs.astral.sh/uv/)（優先 Homebrew，fallback 到 Astral 官方 installer），並預熱 Python 3.11 + 約 66 個 wheel cache。等到 `~/.cache/investing-toolkit/.mcp_ready` 出現後重啟 Claude 即可。

選用的 API key（在 shell 環境變數或 `~/.claude.json` 中設定）：

| 變數 | 用途 | 取得方式 |
|----------|-------------|------------|
| `FRED_API_KEY` | 提高 US rate limit（不設也可匿名使用） | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FINMIND_API_TOKEN` | 提高 Taiwan rate limit（不設也可匿名使用） | [finmindtrade.com](https://finmindtrade.com/) |
| `EDINET_API_KEY` | JP Tier A 財報資料（沒設則 yfinance financials Tier 2 fallback） | [disclosure2dl.edinet-fsa.go.jp](https://disclosure2dl.edinet-fsa.go.jp/) — 5 分鐘免費自助申請 |

完整 troubleshooting 與 Cowork retrospective 見 [`docs/mcp-setup.md`](docs/mcp-setup.md)。

## Data source

Adapter 都集中在 [`scripts/`](scripts/) — 盡量採用 primary source，僅使用免費 tier。

| 地區 | Adapter | Source |
|--------|---------|--------|
| 跨市場 | `yfinance_client.py` | Yahoo Finance（價格 + info + financials，非官方 scraper） |
| 跨市場 | `ta_client.py` | 本地 OHLCV → 指標（無外部 API） |
| US | `fred_client.py` | Federal Reserve Economic Data (FRED) CSV |
| US | `sec_edgar_client.py` | SEC EDGAR (`data.sec.gov`) |
| JP | `boj_client.py` | 日本銀行 Time-Series Statistics + Tankan |
| JP | `estat_client.py` | e-Stat 統計ダッシュボード API |
| JP | `edinet_client.py` | 金融庁 EDINET v2 REST API |
| JP | `tdnet_client.py` | TDnet（透過 Yanoshin WEB-API） |
| JP / EU | `ecb_client.py` | ECB Data Portal SDMX |
| TW | `mops_client.py` | MOPS 公開資訊觀測站 JSON API（16 個 endpoint） |
| TW | `twse_openapi_client.py` | TWSE + TPEx OpenAPI（10+ 個 action） |
| TW | `finmind_client.py` | FinMind aggregator（Tier 2 / T86 補洞） |
| TW | `statgov_client.py` | 中華民國統計資訊網 (stat.gov.tw) chart JSON |
| TW | `cbc_client.py` | 中華民國中央銀行 Open Data |
| TW | `dgbas_client.py` | 行政院主計總處 (DGBAS) Excel |
| TW | `ndc_client.py` | 國家發展委員會 (NDC) ZIP/CSV + 政府資料開放 dataset 6100 |
| KR | `fdr_client.py` | FinanceDataReader → BOK ECOS-KEYSTAT |
| CN | `nbs_client.py` | 國家統計局 (NBS) new-SPA API |
| CN | `akshare_client.py` | akshare（PBOC / SHIBOR / Caixin via eastmoney） |

## Cross-plugin delegation

investing-toolkit 是 data layer，分析放在 `domain-teams:investing-team`。Delegation 只傳遞路徑與結構化 seed context，不傳檔案內容；委派目標 skill 自己執行 gate。

```
investing-toolkit                    domain-teams:investing-team
  investment-memo-writer    ───→     Deep Equity Research Memo protocol
                                       2 MUST gate
                                       4 SHOULD gate
                                       1 MAY gate（Taiwan Local Rigor）
                                     verdict: BUY / HOLD / SELL  ───→ 回傳給 caller
                                       ↓（選用）
                                     domain-teams:docs-team
                                       格式化收尾
```

Contract 規範於 [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract。Toolkit skill 不複製 `investing-team` standards、不在本地執行 gate logic、傳遞路徑而非檔案內容。`data-fetcher` agent 只負責 I/O，不做分析。

## 跨國參考 doc

- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design 原則（從 v1.14.0 + v1.16.3 hypothesis-vs-reality 失誤學到的教訓）
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — 5 市場 sector coverage 與 release cadence 對照
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install / troubleshooting / Cowork sandbox retrospective / MCP vs subprocess 的 token・latency trade-off
- 各 skill 內 deep reference：`skills/{country}-macro/references/`、`skills/{country}-macro/docs/`（BOK ECOS catalogue、NBS 2908-leaf tree、JGBi auction 歷史 等）

## Version 歷史

完整 version 歷史（v1.0.0 → v1.16.5）與通往 v2.0.0 的 roadmap（backtesting + factor model）見 [`ROADMAP.md`](ROADMAP.md)。近期 release：v1.16.5（Phase 3 retarget 至 investing-team）、v1.16.4（TWSE `/rwd/` 接線 + design-principles 文件）、v1.16.3（empirical yfinance 驗證）。

## Contributing

- Bug 回報與 PR：[github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- 與 Cowork 相關的 issue 請先看 [`docs/mcp-setup.md`](docs/mcp-setup.md) — 通常是已紀錄的 sandbox 限制，不是 plugin 的 bug
- 歡迎新增 data adapter 的 PR；請依照既有 `*_client.py` pattern（`register_mcp_tools()` + subprocess CLI + cache TTL 標頭），並補上 contract test fixture

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
