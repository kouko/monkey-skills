# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Claude Code 向けクロスカントリー投資 plugin — Data / Analysis / Report の three-layer architecture で 5 市場（US/JP/TW/KR/CN）をカバー。16 個の skill が層を厳密に分離する：国別 bundle の `data-*` は pure I/O、`analysis-*` は pure compute、`report-*` は orchestration を担い分析は `domain-teams:investing-team` に委譲する。

## Cowork 互換性

⚠️ **Claude Code CLI 専用。** Claude Desktop Cowork の sandbox URL allowlist は subprocess と plugin 同梱 MCP の HTTP request 双方を遮断するため、外部 data fetch（yfinance、FRED、NBS、EDINET 他）は Cowork 内からは provider に到達できません。v1.16.1 で empirical 検証済み — retrospective と "what works where" matrix は [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

## Version と part-of

- Version: 2.0.0
- Part of: [`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License: MIT

## v1.x からの移行

v2.0.0 は breaking change です：すべての skill を three-layer prefix 規約（`data-*` / `analysis-*` / `report-*`）で改名し、slash command も同時に移行しました。**alias shim はありません。** v1.x → v2.0.0 の rename map と migration walkthrough は [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md)、アーキテクチャ決定の根拠は [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) を参照。

## Background

investing-toolkit はクロスカントリー投資調査の **toolkit layer** です。3 つの責務 — primary source データ取得、機械的集計、最終配信の orchestration — を所有し、それぞれ独立した layer に置きます。Toolkit 側は投資判断を埋め込みません：BUY/HOLD/SELL verdict、gate enforcement、primary-source anchoring はすべて `domain-teams:investing-team` に置き、`report-equity-memo` がそこへ委譲します。後述の [Cross-Plugin Delegation Contract](#cross-plugin-delegation) を参照。

## Architecture: three-layer + router

```
┌─ Layer 1: Data（5 skill、country-bundled、pure I/O）─────┐
│  data-us  data-jp  data-tw  data-kr  data-cn             │
└──────────────────────────────────────────────────────────┘
        ↓ pack.py が JSON 出力（5 種 pack：snapshot /
        ↓ memo-fetch / comps-multiples / screener-batch /
        ↓ regime-pack）
┌─ Layer 2: Analysis（6 skill、pure compute）──────────────┐
│  analysis-dcf       analysis-comps     analysis-screener │
│  analysis-technical analysis-portfolio analysis-macro-regime │
└──────────────────────────────────────────────────────────┘
        ↓ compute script が analysis JSON を出力
┌─ Layer 3: Report（4 skill、orchestrator）────────────────┐
│  report-equity-memo       report-stock-snapshot          │
│  report-portfolio-review  report-screener-list           │
└──────────────────────────────────────────────────────────┘
        ↓ Markdown 出力

Router: using-investing-toolkit
```

**Layer ルール**（ADR-0001）：

| Layer | 担当 | 禁止 | クロス skill 呼出 |
|-------|------|------|-------------------|
| Data（`data-*`） | Network I/O、tier routing、cache、単一 + バッチ取得（`pack.py --ticker` / `--tickers`）。1 skill = 1 国 = その国の全 client。 | 指標計算、Markdown 整形 | なし |
| Analysis（`analysis-*`） | Pure function: input JSON → output JSON。RSI/MACD/BB 計算、DCF iteration、comps multiples、screener filter+score+rank、portfolio P&L、regime classification。 | Network I/O、sub-agent dispatch — **例外なし** | なし |
| Report（`report-*`） | Bash + temp file による orchestration（`data-X/scripts/pack.py > /tmp/data.json` の後 `analysis-Y/scripts/compute.py --in /tmp/data.json` を実行）、ticker suffix による国 routing、Markdown 整形。`domain-teams:investing-team` / `domain-teams:docs-team` に委譲可能。 | multiple の再実装、内部に手書き RSI、yfinance を直接呼ぶ | あり（クロス plugin） |

Layer 間の hand-off は subprocess + temp file — deterministic、観察可能、再現可能。Sub-agent dispatch は autonomy が必要な作業（`domain-teams:investing-team` の Worker / Evaluator agent 等）専用です。

## Slash command

| Command | Routes to | 説明 |
|---------|-----------|------|
| `/invest` | `using-investing-toolkit` | Router — 目的を伝えると dispatch される |
| `/invest-macro` | `analysis-macro-regime` | 5-block regime dashboard（`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`） |
| `/invest-memo {ticker}` | `report-equity-memo` | フル memo pipeline → `domain-teams:investing-team` |
| `/invest-screen {tickers}` | `report-screener-list` | クロスカントリー grouping 付き multi-criteria screener、複合 score ranking |
| `/invest-portfolio` | `report-portfolio-review` | P&L snapshot + macro regime overlay + rebalance |
| `/invest-snapshot {ticker}` | `report-stock-snapshot` | Snapshot card；ticker suffix で `data-{country}` に自動 route |

## Skill カタログ（16）

### Layer 1: Data（5 skill）

各 `data-{country}/scripts/pack.py` は 5 種類の pack mode — `snapshot` / `memo-fetch` / `comps-multiples` / `screener-batch` / `regime-pack` — を備え、`--ticker`（単一）と `--tickers`（バッチ）両方をサポート。

| Skill | 同梱 client | 備考 |
|-------|-------------|------|
| `data-us` | yfinance、sec_edgar、fred | SEC EDGAR Tier A primary、yfinance ネイティブ batch |
| `data-jp` | yfinance、edinet、tdnet、boj、estat、ecb | EDINET-key tier routing は `pack.py` 内 |
| `data-tw` | yfinance、mops、twse_openapi、finmind、cbc、dgbas、ndc、statgov | MOPS + TWSE Tier A、FinMind Tier 2 fallback |
| `data-kr` | yfinance、fdr | FDR 経由で BOK ECOS-KEYSTAT |
| `data-cn` | yfinance、nbs、akshare、fred | NBS new-SPA API |

### Layer 2: Analysis（6 skill、pure compute）

| Skill | 計算 | 出力 |
|-------|------|------|
| `analysis-dcf` | 3-stage DCF（Damodaran 2012 Ch.12）+ 3×3 sensitivity | 内在価値レンジ JSON |
| `analysis-comps` | 同業 multiples 中央値/平均/四分位 + anchor 乖離（Trailing P/E、Forward P/E、EV/EBITDA、P/S、P/B） | Comps table JSON |
| `analysis-screener` | Filter + 複合 score + ランキング（preset 8 種：value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced） | Top-N JSON |
| `analysis-technical` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200（OHLCV から計算） | 指標 JSON |
| `analysis-portfolio` | ポジション P&L + 持株統計 | Review JSON |
| `analysis-macro-regime` | 5 か国 IC + Hedgeye GIP regime call + Rate Stress Dashboard | Regime card JSON |

### Layer 3: Report（4 skill、orchestrator）

| Skill | Orchestration | 最終出力 |
|-------|--------------|----------|
| `report-equity-memo` | data → analysis-* → `domain-teams:investing-team` に委譲（Deep Equity Research Memo + 2 MUST + 4 SHOULD + 1 MAY gate）→ オプション `domain-teams:docs-team` | Investment memo（Markdown） |
| `report-stock-snapshot` | ticker suffix から国を自動判定 → `data-{country}/pack.py --pack snapshot` → card 整形 | Snapshot card（Markdown） |
| `report-portfolio-review` | ポジション毎 → 国別バッチで `data-{country}` → `analysis-portfolio` → `analysis-macro-regime` overlay → 整形 | Portfolio review（Markdown） |
| `report-screener-list` | リスト解析 → 国別 grouping → `data-{country} --pack screener-batch` を並列実行 → concatenate → `analysis-screener` → top-N 表 | Screener result table（Markdown） |

### Router

| Skill | 説明 |
|-------|------|
| `using-investing-toolkit` | Entry point — 上記 15 skill の intent routing |

## Quick start 例

```bash
# AAPL の equity memo — data-us → analysis-dcf + analysis-comps + analysis-technical → investing-team を orchestrate
/invest-memo AAPL

# クロスカントリー mixed list の screener
/invest-screen AAPL,MSFT,2330.TW,7203.T --preset quality

# Snapshot card；ticker suffix で data-tw に自動 route
/invest-snapshot 2330.TW

# Asia-Pac の macro regime dashboard
/invest-macro --region asia-pac

# Portfolio review（CSV path または inline list）
/invest-portfolio --holdings my-holdings.csv
```

## Setup

Plugin は初回 install 時に self-bootstrap します。手動 setup はほぼ不要。

```bash
# Claude Code CLI 内で実行
/plugin marketplace add kouko/monkey-skills
/plugin install investing-toolkit
```

初回起動時、MCP bootstrap（`servers/mcp_bootstrap.sh`）が `setup.sh` を detached で起動し、[`uv`](https://docs.astral.sh/uv/) を install（Homebrew 優先、なければ Astral 公式 installer に fallback）して Python 3.11 + ~66 wheel cache を pre-warm します。`~/.cache/investing-toolkit/.mcp_ready` が生成されたら Claude を再起動してください。

任意の API key（shell 環境変数または `~/.claude.json` で設定）：

| 変数 | 用途 | 取得方法 |
|------|------|----------|
| `FRED_API_KEY` | US の rate limit 緩和（匿名でも動作） | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FINMIND_API_TOKEN` | 台湾の rate limit 緩和（匿名でも動作） | [finmindtrade.com](https://finmindtrade.com/) |
| `EDINET_API_KEY` | JP Tier A 財務データ（無しなら yfinance financials Tier 2 fallback） | [disclosure2dl.edinet-fsa.go.jp](https://disclosure2dl.edinet-fsa.go.jp/) — 5 分の無料 self-service 登録 |

詳細な troubleshooting と Cowork retrospective は [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

## Data source

Adapter は [`scripts/`](scripts/) を **canonical home** とします。各 `data-{country}/scripts/` フォルダには MD5-locked のコピーが配置され、CI が drift を検出すると失敗します。詳細は [`scripts/README.md`](scripts/README.md) と [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications を参照。

| 地域 | Adapter | Source |
|------|---------|--------|
| Cross-market | `yfinance_client.py` | Yahoo Finance（price + info + financials、非公式 scraper） |
| Cross-market | `ta_client.py` | ローカル OHLCV → 指標（外部 API なし） |
| US | `fred_client.py` | Federal Reserve Economic Data (FRED) CSV |
| US | `sec_edgar_client.py` | SEC EDGAR (`data.sec.gov`) |
| JP | `boj_client.py` | 日本銀行 Time-Series Statistics + Tankan |
| JP | `estat_client.py` | e-Stat 統計ダッシュボード API |
| JP | `edinet_client.py` | 金融庁 EDINET v2 REST API |
| JP | `tdnet_client.py` | TDnet（Yanoshin WEB-API 経由） |
| JP / EU | `ecb_client.py` | ECB Data Portal SDMX |
| TW | `mops_client.py` | MOPS 公開資訊觀測站 JSON API（16 endpoint） |
| TW | `twse_openapi_client.py` | TWSE + TPEx OpenAPI（10+ action） |
| TW | `finmind_client.py` | FinMind aggregator（Tier 2 / T86 補完） |
| TW | `statgov_client.py` | stat.gov.tw 中華民國統計資訊網 chart JSON |
| TW | `cbc_client.py` | 中華民國中央銀行 Open Data |
| TW | `dgbas_client.py` | 行政院主計總處 (DGBAS) Excel |
| TW | `ndc_client.py` | 國家發展委員會 (NDC) ZIP/CSV + 政府資料開放 dataset 6100 |
| KR | `fdr_client.py` | FinanceDataReader → BOK ECOS-KEYSTAT |
| CN | `nbs_client.py` | 国家统计局 (NBS) new-SPA API |
| CN | `akshare_client.py` | akshare（PBOC / SHIBOR / Caixin via eastmoney） |

## Cross-plugin delegation

investing-toolkit は data fetch + 機械計算 + orchestration を担当。投資**分析**は `domain-teams:investing-team` に置きます。橋渡しは `report-equity-memo` — Layer 1 + Layer 2 の JSON 出力をまとめ、`investing-team` へ **path**（ファイル content ではなく）と構造化 seed context を渡して委譲します。委譲先 skill は自前の gate を enforcement します。

```
investing-toolkit                              domain-teams:investing-team
  report-equity-memo                ───→       Deep Equity Research Memo protocol
    Layer 1: data-{country}/pack.py              2 MUST gate
    Layer 2: analysis-dcf + analysis-comps       4 SHOULD gate
             + analysis-technical                1 MAY gate（Taiwan Local Rigor）
                                               verdict: BUY / HOLD / SELL  ───→ caller に返却
                                                 ↓（任意）
                                               domain-teams:docs-team
                                                 formatting 仕上げ
```

Contract は [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract に明記。Toolkit skill は `investing-team` standards を複製しない、gate logic を local 実行しない、ファイル content の代わりに path 参照を渡します。

## Cross-country 参考 doc

- [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) — three-layer architecture decision record
- [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md) — v1.x → v2.0.0 rename map と migration walkthrough
- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design 原則（v1.14.0 + v1.16.3 の hypothesis-vs-reality miss から得た教訓）
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — 5 市場の sector coverage + release cadence 比較
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install / troubleshooting / Cowork sandbox retrospective / MCP vs subprocess token・latency trade-off

## Version 履歴

完全な version 履歴（v1.0.0 → v2.1.0）は [`ROADMAP.md`](ROADMAP.md) を参照。直近: v2.1.0（`analysis-macro-regime` Phase 1 国別 classifier 化、[ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md) 参照）、v2.0.0（three-layer 再構築 + `analysis-comps`）、v1.16.5（Phase 3 を investing-team に retarget）。

## Contributing

- Bug 報告と PR: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- Cowork 関連の issue は先に [`docs/mcp-setup.md`](docs/mcp-setup.md) を確認 — ほぼ確実に doc 化済みの sandbox 制約であり、plugin の bug ではありません
- 新規 data adapter の PR を歓迎します。既存の `*_client.py` pattern（`register_mcp_tools()` + subprocess CLI + cache TTL header）に従い、contract test fixture を追加してください。Adapter は `scripts/`（canonical）に置き、それを使う `data-{country}` skill を `scripts/sync-clients.sh` に追記してください

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。
