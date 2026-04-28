# investing-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**版本**：1.16.5
**所屬於**：[monkey-skills](https://github.com/kouko/monkey-skills)

投資研究 toolkit — **5 國 macro 資料**（US / JP / TW / KR / CN）、
個股 snapshot（US / TW / JP）、technical indicator、DCF valuation、stock screener、
portfolio 檢視，以及透過 `domain-teams:investing-team` 完成的完整 investment memo pipeline。

純資料層：本 toolkit 只負責抓取與結構化資料。分析、regime 判讀、
quality gate 把關後的 memo 皆在 `domain-teams:investing-team` 進行。

## Monthly GDP Proxy 框架

從 v1.7.3 起，五個 country-macro skill 共享一致的 monthly GDP proxy 慣例：

| 市場 | Proxy 類型 | 指標 |
|--------|-----------|------------|
| US | 預先彙整的 Fed nowcast | `nowcast` group：`GDPNOW`、`CFNAI`、`WEI`、`USALOLITOAASTSAM`（OECD CLI） |
| JP | 預先彙整的內閣府 composite | 景気動向指数 CI 三件組：`coincident-index`（即 proxy）、`leading-index`、`lagging-index` |
| TW | 預先彙整的 NDC + DGBAS | `signal`（五色景氣燈號 — Taiwan 特色）、`leading-index`、`coincident-index` |
| KR | 預先彙整的 BOK ECOS | `cycle` group：`coincident-cycle` K253（即 proxy）、`leading-cycle` K254（KEYSTAT 不含 lagging） |
| CN | 原始組件（無共識 composite） | 三大数据：`industrial-yoy`、`retail-yoy`、`fai-yoy` + `services-production-yoy` |

US / JP / TW / KR 皆提供來自各統計機關（Fed / 內閣府 / NDC+DGBAS / BOK ECOS）
**預先彙整**的數值。China 之所以保留原始組件，是因為市場對綜合 composite
尚無共識（克強指數已過時、SF Fed CAT 為季資料、Goldman / Bloomberg 為自有資料）。
Composite 的合成歸屬於 `domain-teams:investing-team`，因為方法論的選擇必須對
分析結果負責。

## Slash Commands

| 指令 | 功能 | 狀態 |
|---------|-------------|--------|
| `/invest` | 路由到適當的 skill | v1.0.0 |
| `/invest-macro [--region us\|japan\|global]` | IC + FRED/BOJ regime 判讀 | v1.0.0 |
| `/invest-memo {ticker} [--scope deep\|quick]` | 完整 memo pipeline → investing-team | v1.0.0 |
| `/invest-screen {tickers} [--pe-max N] [--above-sma200]` | 批次 screener + 綜合排名 | v1.2.0 |
| `/invest-portfolio [holdings.csv]` | Portfolio 檢視 + 再平衡 | v1.2.0 |

## Skills

Skill 分為三層（對應 `using-investing-toolkit` router）：

- **data** — 從外部來源抓取原始時間序列，不做分析
- **aggregation** — 將資料合成 / 評分 / 轉換為單一目的的輸出
- **delegation** — 橋接到 `domain-teams:investing-team` 進行完整研究

| Skill | 層級 | 用途 | 狀態 |
|-------|-------|---------|--------|
| `us-macro` | data | US macro 透過 FRED（約 31 series、14 group，含新增 `pmi` [OECD CLI] + 新增 `swap-spreads` [T-SOFR 3M]） | v1.10.0 |
| `japan-macro` | data | Japan macro 透過 BOJ + e-Stat + ECB + MoF auction（27 preset / 10 group，含新增 `real-rates` group，C+D+E 多來源） | v1.10.0 |
| `taiwan-macro` | data | Taiwan macro 透過 stat.gov.tw + CBC + DGBAS + NDC（32 指標，含新增 `pmi` group — CIER PMI/NMI 透過 NDC 政府資料開放 dataset 6100） | v1.11.0 |
| `korea-macro` | data | Korea macro 透過 FinanceDataReader BOK ECOS-KEYSTAT（**54 指標、13 group**，含 monthly `industry` activity layer；完整 98-code 目錄見 `docs/`） | v1.8.1 |
| `china-macro` | data | China macro 透過 NBS new-SPA API + PBOC + FRED + yfinance（36 指標，含新增 `pmi` group — Caixin mfg/svc 透過 akshare + NBS mfg/non-mfg/composite 透過 nbs_client；優先採用 primary-source） | v1.11.0 |
| `us-stock-snapshot` | data | yfinance 價格 + info + **SEC EDGAR Tier A fundamentals**（XBRL + Item sections） | v1.13.0 |
| `taiwan-stock-snapshot` | data | **MOPS + TWSE/TPEx OpenAPI Tier A primary**（公司揭露 + 交易）；FinMind Tier 2 fallback | v1.13.0 |
| `japan-stock-snapshot` | data | **EDINET v2 Tier A fundamentals**（有報/四半期/臨時/大量保有）+ TDnet 當日 index + yfinance Tier 2 fallback — 由 `EDINET_API_KEY` dual-mode routing | v1.15.0 |
| `technical-snapshot` | data | RSI / MACD / Bollinger / ATR / SMA 透過 `ta_client.py` | v1.2.0 |
| `macro-regime-snapshot` | aggregation | 5 國 IC + GIP（US/JP/TW/KR/CN）+ Rate Stress Dashboard + v1.11.0 跨國一致性更新（Block 1 PMI 3/5 live；5×9 coverage grid；2026-Q2 grounding） | v1.11.0 |
| `stock-screener` | aggregation | 批次 screener — 估值 + 動能 + 趨勢 composite 評分 | v1.2.0 |
| `dcf-valuation` | aggregation | 3 階段 DCF + 敏感度表 | v1.0.0 |
| `invest-portfolio` | aggregation | Portfolio 檢視 — 損益 + regime overlay + 再平衡 | v1.2.0 |
| `investment-memo-writer` | delegation | 完整 memo pipeline — 委派至 `domain-teams:investing-team` | v1.0.0 |
| `using-investing-toolkit` | router | 路由用入口 skill | v1.0.0 |

## 架構

```
investing-toolkit/
├── README.md
├── ROADMAP.md
├── scripts/                        # Source of truth（僅在此編輯）
│   ├── yfinance_client.py          #   US + 全球 equity snapshot
│   ├── fred_client.py              #   US macro + China FX fallback
│   ├── finmind_client.py           #   Taiwan stocks (FinMind)
│   ├── ta_client.py                #   Technical indicator
│   ├── boj_client.py               #   Japan macro (BOJ Time-Series)
│   ├── estat_client.py             #   Japan macro (統計ダッシュボード)
│   ├── statgov_client.py           #   Taiwan macro (stat.gov.tw)
│   ├── cbc_client.py               #   Taiwan (CBC Open Data API)
│   ├── dgbas_client.py             #   Taiwan (DGBAS Excel)
│   ├── ndc_client.py               #   Taiwan (NDC CSV)
│   ├── fdr_client.py               #   Korea (FinanceDataReader BOK ECOS)
│   ├── nbs_client.py               #   China (NBS new-SPA API, direct)
│   ├── akshare_client.py           #   China (PBOC + SHIBOR via akshare)
│   ├── sync-scripts.sh             #   Source 複製到 skill 目錄
│   └── sync-check.sh               #   CI：驗證複本一致
├── agents/data-fetcher.md          # 共用 I/O agent 規格
├── skills/
│   ├── us-macro/                   # data 層
│   ├── japan-macro/
│   ├── taiwan-macro/
│   ├── korea-macro/
│   ├── china-macro/
│   ├── us-stock-snapshot/
│   ├── taiwan-stock-snapshot/
│   ├── technical-snapshot/
│   ├── macro-regime-snapshot/      # aggregation 層
│   ├── stock-screener/
│   ├── dcf-valuation/
│   ├── invest-portfolio/
│   ├── investment-memo-writer/     # delegation 層
│   │   └──→ domain-teams:investing-team（分析 + quality gate + ISQ）
│   │   └──→ domain-teams:docs-team（格式化，可選）
│   └── using-investing-toolkit/    # router
└── commands/                       # /invest-* slash command
```

每個 skill 都是**自包含**，內含自己的 `scripts/` 與 `references/`。
Plugin 層級的 `scripts/` 目錄為單一事實來源 —
編輯後請執行 `sync-scripts.sh`，並用 `sync-check.sh` 驗證。

## 安裝設定

```bash
# Step 1 — 安裝 uv（優先 Homebrew，fallback 到 curl，已安裝則略過）
sh investing-toolkit/scripts/setup.sh

# Step 2（可選）— FRED API key 以提高 rate limit（免費）
# https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY=your_key_here

# Step 3（可選）— FinMind token 用於 Taiwan stocks（免費註冊）
# https://finmindtrade.com
export FINMIND_API_TOKEN=your_token_here
```

其他資料來源（NBS、BOJ、e-Stat、stat.gov.tw、CBC、DGBAS、NDC、
透過 akshare 的 PBOC/SHIBOR、FinanceDataReader BOK ECOS、yfinance）皆
**不需 API key**。Scripts 透過 `uv run` 配合 inline 相依套件 — 步驟 1 之後
不需 `pip install`。

## 資料來源

| 來源 | 資料 | 認證 | 透過 |
|--------|------|------|-----|
| yfinance | US + 全球 equity 價格/info；China/HK 指數 | 無 | `yfinance_client.py` |
| FRED | US macro（利率/通膨/GDP/nowcast）；CN FX | 可選 | `fred_client.py` |
| SEC EDGAR | US 財務（手動 URL） | 無 | — |
| FinMind | Taiwan 三大法人 / 月營收 / 融資融券 / 董監持股 / 財報 | 可選 | `finmind_client.py` |
| CasualMarket MCP | Taiwan 即時報價（可選） | 無 | MCP |
| BOJ Time-Series API | Japan 政策利率、JGB、貨幣、TANKAN、外匯 | 無 | `boj_client.py` |
| 統計ダッシュボード (e-Stat) | Japan CPI、GDP、IP、失業率、景気動向指数 CI 三件組 | 無 | `estat_client.py` |
| stat.gov.tw | Taiwan CPI、失業率、貿易等（隱藏圖表 JSON） | 無 | `statgov_client.py` |
| CBC Open Data API | Taiwan 政策利率、外匯存底、M1B/M2 | 無 | `cbc_client.py` |
| DGBAS | Taiwan GDP、IP、景氣燈號（Excel .xls） | 無 | `dgbas_client.py` |
| NDC | Taiwan 景氣對策信號 + composite index（ZIP/CSV） | 無 | `ndc_client.py` |
| FinanceDataReader BOK ECOS | Korea 28 指標（KEYSTAT preset） | 無 | `fdr_client.py` |
| NBS new-SPA API | China macro 直連（`data.stats.gov.cn`）— 21 指標 | 無 | `nbs_client.py` |
| PBOC（chinamoney）透過 akshare | China LPR / RRR / 社融增量 / new loans | 無 | `akshare_client.py` |
| SHIBOR（shibor.org）透過 akshare | China 銀行間利率 | 無 | `akshare_client.py` |

## Cross-Plugin Delegation

`investment-memo-writer` 是本 repo 第一個跨 plugin 的 delegation skill：

```
investing-toolkit:investment-memo-writer
  ├── data-fetcher agent (I/O)
  ├── macro-regime-snapshot（regime 上下文）
  ├── domain-teams:investing-team（分析 + gates）   ← 跨 plugin
  └── domain-teams:docs-team（格式化，可選）        ← 跨 plugin
```

慣例請參見 `CLAUDE.md` §Cross-Plugin Delegation Contract。
資料層位於本 toolkit；分析 / 裁決 / quality gate 位於
`domain-teams:investing-team`。

## 跨國參考文件

Plugin 層級的跨市場參考文件（補充各 skill 內部 references）：

- [Industry Indicator Cadence](docs/industry-indicator-cadence.md) — 五國（US/JP/TW/KR/CN）產業層級指標覆蓋率、發布頻率（daily → annual 各 tier）、發布時滯、與投資視野對應指南
- [Design Principles](docs/design-principles.md) — 本 plugin 架構的 meta 慣例，包含 **empirical-first design** 原則（透過 v1.14.0 + v1.16.3 「假設 vs 現實」事後檢討而確立）
- [MCP Setup](docs/mcp-setup.md) — 安裝路徑 + 誠實說明 Cowork sandbox 限制

## 版本重點

### v1.16.5 (2026-04-20) — investment-memo-writer Phase 3 重新指向 investing-team

修正 v1.16.4 沿用自 v1.12.0 的過時路由：
memo Phase 3 原本派送至 `domain-teams:research-team`，前提是
誤認 `investing-team` 為「v5.0.0-v5.1.0 暫時性」。
Git log 顯示 investing-team 自 v5.0.0 起已是常設，並擁有
完整的 standards/protocols/rubrics 堆疊；research-team 自身的 SKILL.md
也將投資工作改導回 investing-team，使先前的路由成為浪費的
中介層，同時違反 CLAUDE.md 的 Cross-Plugin Delegation Contract
canonical target。

- `skills/investment-memo-writer/SKILL.md`：Phase 3 標題 + 內文 +
  description + 敘述 + Cross-Plugin Delegation Contract §
  從 research-team 改為 investing-team。
- Gate 表格替換為 investing-team **真實**的 gate 堆疊
  （原本列出 7 個自創的「research-team gate」；現在列出 investing-team
  rubrics/ 中真正的 2 MUST + 4 SHOULD + 1 MAY）。
- 保留歷史註記作為 audit trail — 回顧性說明
  v1.12.0 的錯誤前提與 v1.16.5 的修正。

無 code / script / test 變更。Regression suite 維持不變（26/26 pass）。

### v1.16.4 (2026-04-19) — taiwan-stock-snapshot 接通 TWSE `/rwd/` + design-principles 文件

收尾 v1.16.3 的兩項未竟之事：

- **A1 — TWSE `/rwd/` stock-day-history 不再是孤兒**：
  taiwan-stock-snapshot Phase 1 現在會明確將 `.TW` ticker 在 memo 需要
  監管機構引用（ISQ Narrative Anchor）時路由至 Tier A 原始價格 endpoint。
  與 technical-snapshot 既有的 yfinance-primary 預設互補 — 原始價與
  還原價如今有清楚分工的消費者。
- **A3 — `docs/design-principles.md`**：將 v1.14.0（MCP Cowork 前提失敗）
  + v1.16.3（yfinance TW 覆蓋率假設失敗）所累積的 empirical-first
  design 原則正式編成文件。把兩個事故轉化為可重複使用的設計前
  探查 checklist。

無 code 變更，僅 SKILL.md / docs。Regression test 維持不變
（26/26 pass，與 v1.16.3 相同）。

### v1.16.3 (2026-04-19) — TWSE `/rwd/` 歷史 OHLCV action（Tier A、memo-citation 模式）

使用者反映 `technical-snapshot` / `stock-screener` 將 OHLCV
hard-code 為 `yfinance_client.py`，可能造成 TW/KR/CN 覆蓋不全。
新增 Tier A TWSE 歷史 endpoint 給 `.TW`。隨後實證驗證 yfinance
在台積電 2330.TW（243 列 / 1y、完整 info、SMA-200 可計算）+ 3105.TWO
穩懋 — **yfinance 對 TW 的覆蓋實際上完全沒問題，且採用 split-adjusted
價格（TA 標準）**。所以最終路由維持 **yfinance 為所有市場的預設**，
並把 TWSE `/rwd/` endpoint 暴露為 *explicit-request* 模式，供 caller
需要監管機構原始價格作為 memo primary-source citation 時使用。

- **`scripts/twse_openapi_client.py::stock-day-history`**（新 action）：
  包裝 `https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY` — 即
  TWSE 公開 stock-day.html 頁面背後的 endpoint。Tier A
  primary-source，約 16 年歷史，月粒度（client 內部循環 N 個月）。
  過往月份 cache 30 天；當月 1 天。標準化輸出符合 ta_client 的輸入合約：
  西元日期、小寫 `open/high/low/close/volume`、解析後的浮點數
  （千分位分隔已剝除）。
- **`scripts/ta_client.py` 強化**：當來源未在 top level 提供
  `latest_date` / `latest_close` 時，自動從 `data[]` 計算。讓 ta_client
  可在 yfinance + FinMind + TWSE `/rwd/` 之間零來源特化 shim 通用。
- **`technical-snapshot` SKILL.md Phase 1**：yfinance 維持為所有市場
  （含 `.TW` / `.TWO`）的預設。TWSE `/rwd/` action 文件化為
  Advanced / memo-citation 模式，用於原始 primary-source 價格。
- **`stock-screener` SKILL.md Phase 1**：對完整 ticker 清單採用單一
  yfinance batch 呼叫（保留 v1.16.3 前的 shape）。在 taiwan-stock-snapshot
  memo 上下文中標註 TWSE `/rwd/` 指引。
- **2026-04-19 實證驗證**：
  - 台積電 2330.TW 透過 yfinance 1y → 243 列、SMA-200 可計算、
    幣別 TWD、完整 info（sector/PE/PB/yield）；與 TWSE `/rwd/`
    收盤價完全一致（2030.0 @ 2026-04-17）。
  - 3105.TWO（穩懋、上櫃）透過 yfinance 3mo → 55 列、收盤 539.0。
  - yfinance 價格為 split/dividend-adjusted（TA 業界標準）；
    TWSE `/rwd/` 價格為原始（供監管機構引用使用）。
- **Regression**：MCP 合約測試 26/26。對 US / JP / 既有 TW / TWO 使用者
  相較於 v1.16.2 無行為變更。

注意事項：
- TWSE `/rwd/` endpoint 並未列於 openapi.twse.com.tw 目錄。
  Tier A（TWSE 自家發行）但無正式文件 — 維持為 explicit-request
  action，非預設路徑。
- TPEx（.TWO）無 /rwd/ 對應 — yfinance 為建議預設；FinMind
  TaiwanStockPrice 在 `taiwan-stock-snapshot` memo 上下文中仍可作為
  明確的 Tier 2 fallback。

### v1.16.2 (2026-04-19) — mops_fetch 必填參數驗證（使用者回報的 bug 修正）

修復 `mops_fetch` 在缺少必填參數時的隱晦 runtime 錯誤。例如：
`mops_fetch(action="director-holdings", ticker="6741")` —
缺少 `year`/`month` — 過去會以
`unsupported format string passed to NoneType.__format__`（下游 f-string
作用於 `None`）crash。現在會回傳：

```json
{"error": "action 'director-holdings' requires: --year, --month. (ROC calendar for --year: 西元 - 1911; e.g. 2026 → 115)", "action": "director-holdings"}
```

- **scripts/mops_client.py**：新增 `_REQUIRED_PARAMS` 表（action → 必填
  參數名）+ `_validate_action_params(args)` 輔助函式，在 `_run_action()`
  最上方呼叫。缺少參數會以清楚的 flag 清單 raise `SystemExit`；既有的
  `mops_fetch` SystemExit handler 會轉換為友善的 error dict。
  目前 5 大類別的 13 個 action 全部驗證。
- **mops_fetch docstring**：以明確的 `[required, params]` 標註
  per action 重寫 — 取代過去模糊的「Insider / governance (ticker,
  year [+ month])」語法，避免誤導 LLM caller 哪些參數為必填。
- **tests/test_mcp_equivalence_auto.py**：新增 6 個參數化的 negative-case
  regression test，涵蓋 director-holdings、monthly-revenue、
  day-announcements、balance-sheet、insider-trades 缺少參數路徑。

修正涵蓋 MCP 與 CLI 兩條路徑（皆透過 `_run_action` 匯流）。
姊妹 client（twse/edinet/sec_edgar）原本就安全 — mops 是唯一沒有
top-level 驗證的 dispatcher-pattern client。

### v1.16.1 (2026-04-19) — Cowork sandbox 事後檢討 + 維護自動化

**事後檢討**：v1.14.0 的核心前提 — plugin 安裝的 stdio
MCP server 可繞過 Claude Desktop Cowork sandbox URL allowlist —
是錯的。v1.16.1 的實證測試確認 plugin-MCP 與 plugin-subprocess 都
跑在**同一**個 sandbox 內，因此兩條路徑在 Cowork 同樣被擋。
Anthropic 自家 plugin 全部使用 remote `type: http`
MCP 正是這個原因，我們誤讀了這個訊號。

**這代表什麼**：
- Claude Code CLI / Desktop Code 分頁：subprocess 與 MCP 都
  正常運作；subprocess 是較便宜的預設（零 token 開銷）。
- Claude Desktop Cowork 分頁：兩條路徑都無法執行 URL fetch
  scripts。請改用 Claude Code CLI 操作此 plugin。

**v1.16.1 的變更**：
- `docs/mcp-setup.md` 改寫，誠實說明事後檢討 + Code CLI
  vs Cowork 指南 + token/latency 取捨表。
- 9 個 SKILL.md 的 MCP-aware blockquote 從「prefer MCP」中性化為
  「Claude 兩條路徑皆可用；都回傳相同 JSON」；新增明確的
  Cowork 限制說明；per-skill tool-name 列舉移到單一權威目錄
  `docs/mcp-setup.md`。
- **新增 `tests/test_mcp_equivalence_auto.py`** — 參數化的 MCP↔CLI
  drift guard，涵蓋所有公開 client 的 14 個 fixture。在 action helper
  變動時捕捉靜默偏離。
- **新增 `tests/test_skill_md_sync.py`** — 強制要求 canonical
  事後檢討用語 + 標記 SKILL.md 中過時的 MCP tool 參考。
- **新增 `tools/validate_mcp_tools.py`** — schema + description linter；
  目前 29 個 tool 全部通過。

**MCP 基礎設施未回退** — 在 Code CLI 中可正常運作、
保留未來轉向 remote-HTTP-MCP 的彈性、且 v1.16.1 投入約 1
天的 CI 自動化將未來維護從 ~3.5-6.5 h/6mo 降至 <1 h/6mo。

### v1.16.0 (2026-04-19) — MCP tool surface 完整化

包裝 v1.14.0 延後的 8 個資料抓取 script 為 MCP tool，
讓 Cowork 使用者不再被 macro / regime 工作擋住。
本 toolkit 所有 primary 資料 adapter 現在都可由 MCP 存取。

- **JP macro MCP tool**（Commit 1）：`boj_fetch`、`boj_tankan_inflation_outlook`、
  `ecb_series`、`estat_fetch`、`estat_search`。
- **TW macro MCP tool**（Commit 2）：`cbc_fetch`、`dgbas_fetch`、
  `ndc_fetch`、`statgov_fetch`。
- **KR macro MCP tool**（Commit 3）：`fdr_fetch`（BOK ECOS-KEYSTAT 54
  指標 / 13 group）。
- **中央註冊**（Commit 4）：`servers/mcp_server.py` 匯入 18
  client / 暴露 29 tool。合約測試已更新；3 個 pass。
- **Session token 成本**：~4.4K（29 × 150）— 低於 v1.14.0 5K-split
  門檻；core/extras MCP 拆分仍延後。

**已知非目標**：`ta_client.py` **不**包裝，因為它在本地
轉換 OHLCV 而非抓取外部資料（MCP caller 若需要可組合
`yfinance_history` 並執行 CLI 轉換）。

### v1.15.0 (2026-04-19) — Japan 個股 skill（Path γ 完成）

收尾 v1.13.0 的 stacked PR：Japan 加入 US + TW，成為
第三個擁有專用個股資料 skill 的市場。

- **scripts/edinet_client.py**（739 行）：金融庁 EDINET v2 REST API
  Tier A primary-source adapter。7 種表單類型（有報 120 / 四半期 140 /
  半期 160 / 臨時 180 / 自己株買付 220 / 大量保有 350 + 訂正版）。CSV
  type=5（FSA 於 2024-04 新增）為 MVP 路徑 — 將 iXBRL-flattened
  BS/PL/CF 解析為 canonical key_metrics dict，shape 與 sec_edgar /
  mops 一致。Ticker → EDINET code 解析透過免費公開的
  Edinetcode.zip 下載（不需 key）。PDL 1.0 授權 —
  須附「出典：金融庁 EDINET」即可重新散佈。

- **scripts/tdnet_client.py**：當日適時開示情報 index，透過
  Yanoshin WEB-API。涵蓋 決算短信 / 業績予想 / 配当予想 / 自己株
  買付 / 株主総会 / 役員異動 — 這些事件 EDINET 臨時報告書要
  ~45 天才會出現。Index-only 指引模式；完整文件由 JPX
  （release.tdnet.info）抓取。

- **yfinance_client.py --action financials**（新）：JP（與跨市場）
  Tier 2 BS/PL/CF fallback，使用 Yahoo Finance。Provenance
  明確標註 `data_tier: "tier_2"` 並附警告。在 Toyota FY2025-03-31
  上對 EDINET 進行驗證 — revenue / operating / net
  income / total assets / operating CF 皆精準到日圓相符。

- **skills/japan-stock-snapshot/**：Dual-mode tier routing SKILL.md。
  `EDINET_API_KEY` 設置 → Tier A 模式；未設置 → Tier 2 yfinance
  fallback，並顯著提示升級路徑。已知缺口已記載（信用取引残高
  per-stock / 空売り / daily 投資部門別 — 全部鎖在 J-Quants Standard
  付費 tier 後或免費版確實無法取得）。

- **investment-memo-writer**：Phase 1 擴充以將 4 位數 JP
  ticker（`^\d{4}(\.T|\.TO)?$`）路由至新 skill。Output shape
  與 US/TW snapshot 相同，讓 `domain-teams:research-team` 收到
  market-agnostic 的 fixture。

- **MCP surface**：13 → 19 tool（+4 edinet、+1 tdnet、+1
  yfinance_financials）。`--self-check` 回傳 10 個 client。合約
  測試已更新；3 個 pass。

### v1.14.0 (2026-04-19) — MCP migration（Claude Desktop Cowork 解封）

將 8 個 data-fetch script 透過單一 plugin 層級的 MCP server 暴露為 **13 個 MCP tool**。
Claude Code 與 Claude Cowork 在 plugin 安裝時自動啟用；MCP
process 跑在 Claude Desktop sandbox 之外，
所以原本擋住 Cowork 內每一個 data-fetch 呼叫的 URL 限制
從架構上被繞過。

- **servers/mcp_server.py**：FastMCP 入口，匯入全部 8 個 client
  module。共 13 個 tool（yfinance × 3、sec_edgar × 4、fred / mops /
  twse_openapi / finmind / akshare_china_macro / nbs_china_macro 各 × 1）。
  `--self-check` flag 預熱 uv cache + 相依套件，不進入 MCP loop。

- **.mcp.json + servers/mcp_bootstrap.sh**：plugin 自動註冊。
  雙路徑 router：FAST PATH（marker + uv 就緒 → 在 <3 秒內 exec 真正的 server）、
  BOOTSTRAP PATH（背景 spawn setup.sh，exec stdlib
  wrapper，在 Claude Desktop 60 秒 handshake timeout 內即時回應 —
  2026-04-19 實證探查）。

- **servers/setup.sh**：silent-auto 階梯式安裝（Homebrew → curl
  astral.sh/uv/install.sh），接著用 `--self-check` 預熱 66 個 wheel
  安裝，寫入 plugin 版本 marker。非開發者使用者
  不需要打開 Terminal。

- **servers/mcp_wrapper.py**：stdlib JSON-RPC；在 provisioning 視窗
  期間暴露 `investing_toolkit_status`，讓 Claude
  可以即時回報 setup 進度，並在就緒時要求重啟。

- **Dual-mode scripts**：8 個 client script 全部新增 `register_mcp_tools()`；
  `uv run scripts/xxx.py` CLI 路徑維持不變 — MCP
  與 CLI 回傳相同 JSON（由
  `tests/test_mcp_contract.py` 強制保證）。

- **SKILL.md MCP-aware 文字**：8 個 skill 標註為當 MCP tool 已註冊
  時優先使用；subprocess command 仍為 canonical fallback。

- **docs/mcp-setup.md**：使用者安裝指南 — Claude Code CLI、
  Claude Cowork（Team 私有 fork）、Pro/Max 限制說明、
  troubleshooting。

安裝路徑請見 [`docs/mcp-setup.md`](docs/mcp-setup.md)。

### v1.13.0 (2026-04-19) — 個股 fundamentals（US + TW）

收尾 Pattern C NVDA demo 4 個資料缺口（SEC EDGAR 缺、forward
guidance、consensus、peer），涵蓋 US + TW 市場：

- **sec_edgar_client.py**：JSON API 涵蓋 7 種 SEC 表單類型（10-K /
  10-Q / 8-K / Form 4 / 13F / S-1 / DEF 14A）。XBRL 結構化 fact +
  HTML 敘述 Item-section parser。User-Agent 必填、10 req/sec
  合規內建、tiered cache TTL。

- **mops_client.py**：透過新 MOPS JSON API（mops.twse.com.tw 於
  2025-02 上線）涵蓋 16 個 endpoint。包含 公司基本資料 + 財報 BS/IS/CF +
  月營收 + 持股 + 股利 + 重大訊息 + 股東會。歷史深度：IFRS
  財報 13 年（2013+）、歷史重大訊息 30 年（1996+）。無 auth/cookie/CSRF。
  Primary-source Tier A（金管會法定揭露）。

- **twse_openapi_client.py**：TWSE/TPEx 公開 OpenAPI for 交易資料
  （日行情 / 融資融券 / 三大法人 snapshot / 產業 EPS / 除權息日曆）。
  MOPS 未涵蓋此部分 — 設計上分流。

- **taiwan-stock-snapshot 重構**：MOPS + TWSE OpenAPI Tier 1
  primary；FinMind Tier 2 自動 fallback（Pattern A+B）。已知 Tier 1
  缺口（daily T86 per-stock flow、歷史 STOCK_DAY）預設路由至 FinMind
  並附警告 log。

- **dcf-valuation 啟用**：先前因缺乏財務報表而結構性殘廢；現在
  自動從 SEC EDGAR（US）或 MOPS（TW）取得來源。

- **investment-memo-writer Phase 1 更新**：新增 SEC EDGAR + MOPS + TWSE
  OpenAPI command；FinMind 保留為 Tier 2 fallback 路徑。

JP 個股 skill 延後至 v1.14.0 stacked PR（Path γ
架構決策）。

Pattern C 重跑預期：v1.13.0 merge 後，NVDA 與 2330.TW 的 ISQ
verdict 為 `PASS`（非 `PASS_WITH_NOTES`）。

### v1.12.0 (2026-04-19) — Pattern C UX（檔案寫入 + 可見度）

修正 v1.11.0 NVDA Pattern C demo 暴露的 3 個 UX 問題：

- **investment-memo-writer Phase 5**：檔案寫入預設 —
  `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
  使用 deep/quick mode 分檔名（同一 mode 重跑覆寫）。Obsidian
  模式自動偵測：`$OBSIDIAN_VAULT_PATH` env var
  或探查 `~/kouko-obsidian-vault/` 等；讀取 vault `CLAUDE.md` 取得
  資料夾慣例；透過 `obsidian:obsidian-markdown` skill 路由。
  Chat 交付僅顯示 executive summary + gate verdict + 檔案連結
  （完整 memo 存在檔案中，不在 chat 重複）。

- **investment-memo-writer Phase 3 target 修正**：將
  `domain-teams:investing-team` 參考替換為
  `domain-teams:research-team`（依 research-team 的「investment 或
  macro analysis」scope）。歷史註記保留。

- **skill-team Visibility Convention（domain-teams v5.2.0）**：7 個
  workflow skill（research / code / design / docs / devops / qa /
  planning）獲得 compliance block，要求在 3 個層級發出 `TaskUpdate`：
  phase 轉換 + milestone + heartbeat（最多 ≤60 秒沉默）。
  Narration Convention（軸 1）加入
  investment-memo-writer 用於 dispatch 前的期待設定。

架構替代方案（軸 3 phase-split）若軸 1+2 不足，延後至 v1.13.0+。
機率性 vs 結構性保證的取捨已記載於
skill-team SKILL.md §Visibility Convention。

跨 plugin PR：investing-toolkit（1.11.0 → 1.12.0）+ domain-teams
（5.1.0 → 5.2.0）。3-commit 堆疊，~3.5 天範圍。

### v1.11.0 (2026-04-19) — 跨國一致性更新

處理 v1.10.0 的 PMI 不對稱 + grounding vintage drift：
- **china-macro**：新增 `pmi` group（Caixin mfg/svc 透過 akshare + NBS
  官方 mfg/non-mfg/composite 透過既有 nbs_client — 優先採
  primary-source）。填補 Block 1 CN PMI 缺口。
- **taiwan-macro**：新增 `pmi` group（PMI/NMI 透過 NDC data.gov.tw CSV —
  v1.11.0 APAC 探查時意外發現的免費 tier 存取；
  授權：政府資料開放授權條款-第1版 等同 CC BY）
- **japan-macro / korea-macro**：PMI URL-only 參考正式化
  （au Jibun Bank / S&P Global Korea 授權 — 無免費 tier 路徑）
- **macro-regime-snapshot**：Block 1 PMI 列覆蓋從 1/5 →
  3/5 live（+CN +TW）；Data Source Architecture 章節擴充為
  5×9 跨國覆蓋網格
- **grounding 更新**：CN + JP 全面重新審計到 2026-Q2 vintage
  （CN 2026 政府工作報告 GDP 4.5-5% 區間；BOJ 在 2026-01/03 維持 0.75%）；
  US + TW + KR delta 增補（FOMC SEP r* 3.0→3.1%；CBC 維持 2.00%；
  BOK 7 連續維持）。共 16 🔴 + 17 ⚠️ 修正。
- **research/grounding-v1.11.0.md**：合併 299 行 audit trail

JGBi YTM solver（原本考慮在 v1.11.0 加入）為了架構一致性
刻意拒絕 — 會讓 JP 成為 5 個 country-macro skill 中唯一做
bond-math 的國家，違反「country-macro = 純資料層」紀律。
透過腦力激盪審計再次確認。

### v1.10.0 (2026-04-19) — PMI + JP real rates + swap spread

收尾 v1.9.0 延後清單中的三個資料覆蓋缺口：
- **us-macro**：新增 `pmi` group（OECD CLI USALOLITOAASTSAM 作為 FRED-available
  proxy — ISM/S&P Global 依 St. Louis Fed blog 已於 2016 從 FRED 移除）
  + 新增 `swap-spreads` group（Treasury-SOFR 3M 利差作為貨幣市場
  流動性 proxy — 後 LIBOR 時代 FRED 沒有乾淨的 term swap series）
- **japan-macro**：新增 `real-rates` group，透過 C+D+E 多來源框架
  （MoF JGBi auction anchor + ECB 月度 ex-post + BOJ Tankan 1Y/3Y/5Y
  預期通膨）。JSDA YTM solver 延後至 v1.11.0，因為探查
  確認 JSDA 將 JGBi 殖利率遮蓋（999.999 sentinel）。新增 `ecb_client.py`
  並擴充 `boj_client.py` 以支援 Tankan。
- **macro-regime-snapshot**：Block 1 每國一個 PMI 列（US 已抓取；
  JP/TW/KR/CN URL-only）。Block 3 改名為「Rate Stress Dashboard」，含
  JP real-rate 子區塊與 US swap spread 子區塊。
- **research**：新增 `grounding-v1.10.0.md`，記載 3 個新 JP 資料來源
  （MoF auction / ECB SDMX / BOJ Tankan）的 primary-source 審查
  以及 JSDA / JBTS 路徑的拒絕理由。

- **v1.9.0** — macro-regime-snapshot 5 國更新（US/JP/TW/KR/CN）+ LSEG-style 5-block dashboard（Macro Summary / Yield Curve / Real Rate / IC+GIP Regime / Asset-Class Tilts）+ us-macro 新 US `real-rates` group（T5YIE / T10YIE / DFII5 / DFII10 — real-rate 分解區塊）。新增 signal-label 語意（Expansion/Contraction、Accommodative/Restrictive 等）
- **v1.8.1** — Korea-macro monthly 產業活動層（43 → 54 指標；新 `industry` group：K201-K217 行業活動 — manufacturing inventory/shipment/operating-rate、services production、retail sales、wholesale-retail、credit-card usage、machinery orders、capital-goods output、construction completion/orders）
- **v1.8.0** — Korea-macro 目錄 + 結構性 refactor + 15 Tier-B preset（28 → 43 指標）
- **v1.7.3** — Taiwan + Korea monthly GDP proxy 標記（5 市場框架完成）
- **v1.7.2** — Router 同步 + Layer 欄位
- **v1.7.1** — China monthly GDP proxy 標記（與 US/JP 達成 Tier 2 對等）
- **v1.7.0** — US（nowcast group）+ JP（CI 三件組）的 monthly GDP proxy
- **v1.6.0** — China macro（34 指標，透過 NBS direct + PBOC + FRED + yfinance）
- **v1.5.0** — Korea macro（28 指標，透過 FinanceDataReader）
- **v1.4.0** — Taiwan macro（30 指標、4 個政府來源）
- **v1.3.0** — US + Japan macro skill
- **v1.2.0** — stock-screener、technical-snapshot、invest-portfolio
- **v1.1.0** — Taiwan stock 資料透過 FinMind
- **v1.0.0** — 核心：macro-regime-snapshot、us-stock-snapshot、DCF、memo writer

完整歷史與 v2.0.0 Quantitative Layer 規劃請見 [ROADMAP.md](ROADMAP.md)。
