# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Claude Code 跨國投資 plugin — Data / Analysis / Report 三層架構（three-layer architecture）涵蓋 5 個市場（US/JP/TW/KR/CN）。16 個 skill 嚴格分層：以國家為單位 bundled 的 `data-*` 只做 pure I/O、`analysis-*` 只做 pure compute、`report-*` 負責 orchestration 並把分析委派給 `domain-teams:investing-team`。

## Cowork 相容性

⚠️ **僅支援 Claude Code CLI。** Claude Desktop Cowork 的 sandbox URL allowlist 同時阻擋 subprocess 與 plugin 內 MCP 的 HTTP request，因此外部 data fetch（yfinance、FRED、NBS、EDINET 等）在 Cowork 內無法到達 provider。v1.16.1 已 empirical 驗證 — retrospective 與 "what works where" 對照表請見 [`docs/mcp-setup.md`](docs/mcp-setup.md)。

## Version 與 part-of

- Version：2.0.0
- Part of：[`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License：MIT

## 從 v1.x 升上來？

v2.0.0 是 breaking change：所有 skill 改用三層 prefix 慣例（`data-*` / `analysis-*` / `report-*`）重新命名，slash command 也跟著一起換。**沒有 alias shim。** 完整 v1.x → v2.0.0 對照與 migration 指南見 [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md)；架構決策記錄見 [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md)。

## Background

investing-toolkit 是跨國投資研究的 **toolkit layer**，負責三件事——抓 primary source 資料、做機械式彙總、orchestrate 最終交付——並嚴格分層放置。Toolkit 端不嵌入任何投資判斷：BUY/HOLD/SELL verdict、gate enforcement、primary-source anchoring 都放在 `domain-teams:investing-team`，由 `report-equity-memo` 委派過去。詳見後段 [Cross-Plugin Delegation Contract](#cross-plugin-delegation)。

## 架構：三層 + Router

```
┌─ Layer 1: Data（5 skill，country-bundled，pure I/O）─────┐
│  data-us  data-jp  data-tw  data-kr  data-cn             │
└──────────────────────────────────────────────────────────┘
        ↓ pack.py 輸出 JSON（5 種 pack：snapshot /
        ↓ memo-fetch / comps-multiples / screener-batch /
        ↓ regime-pack）
┌─ Layer 2: Analysis（6 skill，pure compute）──────────────┐
│  analysis-dcf       analysis-comps     analysis-screener │
│  analysis-technical analysis-portfolio analysis-macro-regime │
└──────────────────────────────────────────────────────────┘
        ↓ compute script 輸出 analysis JSON
┌─ Layer 3: Report（4 skill，orchestrator）────────────────┐
│  report-equity-memo       report-stock-snapshot          │
│  report-portfolio-review  report-screener-list           │
└──────────────────────────────────────────────────────────┘
        ↓ Markdown 輸出

Router：using-investing-toolkit
```

**分層規則**（ADR-0001）：

| Layer | 負責 | 禁止 | 跨 skill 呼叫 |
|-------|------|------|---------------|
| Data（`data-*`） | Network I/O、tier routing、cache、單一 + 批次抓取（`pack.py --ticker` / `--tickers`）。1 skill = 1 國家 = 該國全部 client。 | 計算指標、產生 Markdown | 無 |
| Analysis（`analysis-*`） | Pure function：input JSON → output JSON。RSI/MACD/BB 計算、DCF iteration、comps multiples、screener filter+score+rank、portfolio P&L、regime classification。 | Network I/O、sub-agent dispatch — **零例外** | 無 |
| Report（`report-*`） | 透過 Bash + temp file 做 orchestration（`data-X/scripts/pack.py > /tmp/data.json` 後再跑 `analysis-Y/scripts/compute.py --in /tmp/data.json`）、依 ticker suffix 路由國家、Markdown 格式化。可委派至 `domain-teams:investing-team` / `domain-teams:docs-team`。 | 重新實作 multiple、在裡面手刻 RSI、直接呼叫 yfinance | 是（跨 plugin） |

層與層之間的銜接走 subprocess + temp file — 確定性（deterministic）、可觀察、可重播。Sub-agent dispatch 只保留給需要 autonomy 的工作（例如 `domain-teams:investing-team` 的 Worker / Evaluator agent）。

## Slash command

| Command | 路由至 | 說明 |
|---------|--------|------|
| `/using-investing-toolkit` | `using-investing-toolkit` | Router — 描述目標後 dispatch |
| `/analysis-macro-regime` | `analysis-macro-regime` | 5-block regime dashboard（`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`） |
| `/report-equity-memo {ticker}` | `report-equity-memo` | 完整 memo pipeline → `domain-teams:investing-team` |
| `/report-screener-list {tickers}` | `report-screener-list` | 跨國家分組的多條件 screener，含複合 score 排名 |
| `/report-portfolio-review` | `report-portfolio-review` | P&L snapshot + 總經 regime overlay + rebalance |
| `/report-stock-snapshot {ticker}` | `report-stock-snapshot` | Snapshot card；依 ticker suffix 自動 route 至 `data-{country}` |

## Skill 清單（16）

### Layer 1：Data（5 skill）

每個 `data-{country}/scripts/pack.py` 提供 5 種 pack 模式 — `snapshot` / `memo-fetch` / `comps-multiples` / `screener-batch` / `regime-pack`，並支援 `--ticker`（單檔）與 `--tickers`（批次）兩種模式。

| Skill | 內含 client | 說明 |
|-------|-------------|------|
| `data-us` | yfinance、sec_edgar、fred | SEC EDGAR Tier A primary；yfinance 原生 batch |
| `data-jp` | yfinance、edinet、tdnet、boj、estat、ecb | EDINET-key tier routing 邏輯放在 `pack.py` 內 |
| `data-tw` | yfinance、mops、twse_openapi、finmind、cbc、dgbas、ndc、statgov | MOPS + TWSE Tier A；FinMind Tier 2 fallback |
| `data-kr` | yfinance、fdr | FDR 走 BOK ECOS-KEYSTAT |
| `data-cn` | yfinance、nbs、akshare、fred | NBS new-SPA API |

### Layer 2：Analysis（6 skill，pure compute）

| Skill | 計算內容 | 輸出 |
|-------|----------|------|
| `analysis-dcf` | 三段式 DCF（Damodaran 2012 Ch.12）+ 3×3 sensitivity | 內在價值區間 JSON |
| `analysis-comps` | 同業 multiples 中位數/平均/四分位 + anchor 偏離（Trailing P/E、Forward P/E、EV/EBITDA、P/S、P/B） | Comps table JSON |
| `analysis-screener` | Filter + 複合 score + 排名（8 個 preset：value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced） | Top-N JSON |
| `analysis-technical` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200（從 OHLCV 計算） | 指標 JSON |
| `analysis-portfolio` | 部位 P&L + 持倉統計 | Review JSON |
| `analysis-macro-regime` | 5 國 IC + Hedgeye GIP regime call + Rate Stress Dashboard | Regime card JSON |

### Layer 3：Report（4 skill，orchestrator）

| Skill | Orchestration | 最終輸出 |
|-------|--------------|----------|
| `report-equity-memo` | data → analysis-* → 委派至 `domain-teams:investing-team`（Deep Equity Research Memo + 2 MUST + 4 SHOULD + 1 MAY gate）→ 選用 `domain-teams:docs-team` | Investment memo（Markdown） |
| `report-stock-snapshot` | 依 ticker suffix 自動偵測國家 → `data-{country}/pack.py --pack snapshot` → 排版 card | Snapshot card（Markdown） |
| `report-portfolio-review` | 逐部位 → 依國家批次呼叫 `data-{country}` → `analysis-portfolio` → `analysis-macro-regime` overlay → 排版 | Portfolio review（Markdown） |
| `report-screener-list` | 解析 ticker list → 依國家分組 → 平行 `data-{country} --pack screener-batch` → 串接 → `analysis-screener` → 輸出 top-N 表格 | Screener result table（Markdown） |

### Router

| Skill | 說明 |
|-------|------|
| `using-investing-toolkit` | 入口 — 上述 15 個 skill 的 intent routing |

## Quick start 範例

```bash
# AAPL 投資 memo — 串接 data-us → analysis-dcf + analysis-comps + analysis-technical → investing-team
/report-equity-memo AAPL

# 跨國家 screener
/report-screener-list AAPL,MSFT,2330.TW,7203.T --preset quality

# Snapshot card；ticker suffix 自動 route 到 data-tw
/report-stock-snapshot 2330.TW

# 亞太 macro regime dashboard
/analysis-macro-regime --region asia-pac

# 投組 review（CSV path 或 inline list）
/report-portfolio-review --holdings my-holdings.csv
```

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
|------|------|----------|
| `FRED_API_KEY` | 提高 US rate limit（不設也可匿名使用） | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FINMIND_API_TOKEN` | 提高 Taiwan rate limit（不設也可匿名使用） | [finmindtrade.com](https://finmindtrade.com/) |
| `EDINET_API_KEY` | JP Tier A 財報資料（沒設則 yfinance financials Tier 2 fallback） | [disclosure2dl.edinet-fsa.go.jp](https://disclosure2dl.edinet-fsa.go.jp/) — 5 分鐘免費自助申請 |

完整 troubleshooting 與 Cowork retrospective 見 [`docs/mcp-setup.md`](docs/mcp-setup.md)。

## Data source

Adapter 集中在 [`scripts/`](scripts/)，這是 **canonical home**。每個 `data-{country}/scripts/` 收到的是 MD5-locked 副本，CI 會擋下任何 drift。詳見 [`scripts/README.md`](scripts/README.md) 與 [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications。

| 地區 | Adapter | Source |
|------|---------|--------|
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

investing-toolkit 負責 data fetch + 機械計算 + orchestration。投資**分析**放在 `domain-teams:investing-team`。橋樑是 `report-equity-memo` — 它彙整 Layer 1 + Layer 2 的 JSON 輸出，再委派給 `investing-team`，傳遞的是 **path**（不是檔案內容）與結構化 seed context。委派目標 skill 自己執行 gate。

```
investing-toolkit                              domain-teams:investing-team
  report-equity-memo                ───→       Deep Equity Research Memo protocol
    Layer 1：data-{country}/pack.py              2 MUST gate
    Layer 2：analysis-dcf + analysis-comps       4 SHOULD gate
             + analysis-technical                1 MAY gate（Taiwan Local Rigor）
                                               verdict：BUY / HOLD / SELL  ───→ 回傳給 caller
                                                 ↓（選用）
                                               domain-teams:docs-team
                                                 格式化收尾
```

Contract 規範於 [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract。Toolkit skill 不複製 `investing-team` standards、不在本地執行 gate logic、傳遞路徑而非檔案內容。

## 跨國參考 doc

- [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) — 三層架構決策記錄
- [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md) — v1.x → v2.0.0 對照與 migration 指南
- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design 原則（v1.14.0 + v1.16.3 hypothesis-vs-reality 失誤教訓）
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — 5 市場 sector coverage 與 release cadence 對照
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install / troubleshooting / Cowork sandbox retrospective / MCP vs subprocess 的 token・latency trade-off

## Version 歷史

完整 version 歷史（v1.0.0 → v2.1.0）見 [`ROADMAP.md`](ROADMAP.md)。近期：v2.1.0（`analysis-macro-regime` Phase 1 國別 classifier 化，見 [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md)）、v2.0.0（三層架構重構 + `analysis-comps`）、v1.16.5（Phase 3 retarget 至 investing-team）。

## Contributing

- Bug 回報與 PR：[github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- 與 Cowork 相關的 issue 請先看 [`docs/mcp-setup.md`](docs/mcp-setup.md) — 通常是已紀錄的 sandbox 限制，不是 plugin 的 bug
- 歡迎新增 data adapter 的 PR；請依照既有 `*_client.py` pattern（`register_mcp_tools()` + subprocess CLI + cache TTL 標頭），並補上 contract test fixture。Adapter 放在 `scripts/`（canonical），並把使用它的 `data-{country}` skill 加進 `scripts/sync-clients.sh`

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
