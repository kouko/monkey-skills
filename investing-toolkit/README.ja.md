# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Claude Code 向けクロスカントリー投資データ plugin — 5 市場マクロ網羅（US/JP/TW/KR/CN）、個別株 snapshot、DCF/screener workflow、`domain-teams:investing-team` に分析を委譲する memo pipeline。

## Cowork 互換性

⚠️ **Claude Code CLI 専用。** Claude Desktop Cowork の sandbox URL allowlist は subprocess と plugin 同梱 MCP の HTTP request 双方を遮断するため、外部 data fetch（yfinance、FRED、NBS、EDINET 他）は Cowork 内からは provider に到達できません。v1.16.1 で empirical 検証済み — retrospective と "what works where" matrix は [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

## Version と part-of

- Version: 1.16.5
- Part of: [`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License: MIT

## Background

investing-toolkit はクロスカントリー投資調査の **data layer** です。14 以上の public provider から primary source の macro / equity データを取得し、機械的な集計（regime call、screener、DCF、P&L）を行ったうえで、構造化された fixture を `domain-teams:investing-team` に渡し、そちら側で分析・gate enforcement・BUY/HOLD/SELL verdict を担います。Plugin は `data ↔ analysis` を厳密に分離 — toolkit 側は投資判断を埋め込まず、domain-team 側は data source に直接アクセスしません。後述の [Cross-Plugin Delegation Contract](#cross-plugin-delegation) を参照。

## Monthly GDP proxy framework

5 つの country macro skill すべてが、cross-market regime call を like-for-like で比較できるよう、一貫した **monthly GDP proxy** を提供します。主要国の公式 GDP は四半期公表のため、proxy framework は各統計当局が既に公表している正規の pre-aggregated 系列で月次 gap を埋めます。

| 市場 | Proxy 種別 | 指標 |
|--------|-----------|------------|
| US | Pre-aggregated Fed nowcast | `nowcast` group: GDPNow、CFNAI、WEI、OECD CLI |
| JP | Pre-aggregated 内閣府 composite | 景気動向指数 CI trio: 一致 (proxy), 先行, 遅行 |
| TW | Pre-aggregated NDC + DGBAS | `signal` (五色景氣燈號 — 台湾固有), 領先指標, 同時指標 |
| KR | Pre-aggregated BOK ECOS | 동행지수순환변동치 (proxy) + 선행지수순환변동치 |
| CN | Raw component（合意 aggregator なし） | 三大数据: industrial-yoy、retail-yoy、fai-yoy + services-production-yoy |

US/JP/TW/KR は当該統計当局からの **pre-aggregated** 値をそのまま提供。CN は component を raw のままにします — market consensus の monthly composite が存在しないため（李克強指数は 2012 年以降陳腐化、SF Fed CAT は四半期、Goldman / Bloomberg は proprietary）。合成 (synthesis) は方法論選択に説明責任が伴う analysis layer に置きます。

Sector レベル（産業別）の cadence 詳細は [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) を参照。

## Slash command

| Command | Routes to | 説明 |
|---------|-----------|-------------|
| `/invest` | `using-investing-toolkit` | Router — 目的を伝えると dispatch される |
| `/invest-macro` | `macro-regime-snapshot` | 5-block regime dashboard (`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`) |
| `/invest-memo {ticker}` | `investment-memo-writer` | フル memo pipeline → `domain-teams:investing-team` |
| `/invest-screen {tickers}` | `stock-screener` | 複合 score ranking 付き multi-criteria screener |
| `/invest-portfolio` | `invest-portfolio` | P&L snapshot + macro regime overlay + rebalance |

## Skill

15 skill。3 つの layer + router 構成。

### Data layer

| Skill | 説明 |
|-------|-------------|
| `us-macro` | FRED CSV — 14 group / 31 系列（rates / inflation / growth / nowcast / real-rates / pmi / swap-spreads + sector ETF mapping 7 group） |
| `japan-macro` | BOJ + 統計ダッシュボード + ECB SDMX + MoF 物価連動国債落札履歴 — 27 preset / 10 group（v1.10.0 で `real-rates` C+D+E multi-source 追加） |
| `taiwan-macro` | stat.gov.tw + CBC + DGBAS + NDC — 32 指標（五色景氣燈號 + CIER PMI/NMI 含む） |
| `korea-macro` | FinanceDataReader BOK ECOS-KEYSTAT — 54 指標 / 13 group（月次 industry activity layer 含む） |
| `china-macro` | NBS new-SPA API + PBOC/Caixin via akshare + FRED + yfinance — 36 指標（Caixin + NBS 二系統 PMI 含む） |
| `us-stock-snapshot` | yfinance price/valuation + SEC EDGAR 10-K/10-Q/8-K + XBRL facts + Item-section narrative |
| `taiwan-stock-snapshot` | MOPS JSON + TWSE/TPEx OpenAPI Tier A primary、FinMind Tier 2 fallback（三大法人 / 月營收 / 融資融券 / 董監持股 / 重大訊息） |
| `japan-stock-snapshot` | EDINET v2 + TDnet (Yanoshin) + yfinance `.T` — dual-mode（`EDINET_API_KEY` あり → Tier A、なし → yfinance financials Tier 2 fallback） |
| `technical-snapshot` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200（OHLCV から計算） |

### Aggregation layer

| Skill | 説明 |
|-------|-------------|
| `macro-regime-snapshot` | 5 か国 IC + Hedgeye GIP regime call + Rate Stress Dashboard（real rate + swap spread）; 5×9 cross-country coverage grid |
| `stock-screener` | User 指定 ticker list 上の合成 score screener（preset 8 種：value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced） |
| `dcf-valuation` | 3-stage DCF（Damodaran 2012 Ch.12）+ 3×3 sensitivity table + Graham/Klarman verdict |
| `invest-portfolio` | Holdings parser + batch price fetch + macro overlay + position P&L |

### Delegation layer

| Skill | 説明 |
|-------|-------------|
| `investment-memo-writer` | フル memo pipeline: data-fetcher agent → macro-regime-snapshot → `domain-teams:investing-team`（Deep Equity Research Memo protocol + 2 MUST + 4 SHOULD + 1 MAY gate）→ オプション `domain-teams:docs-team` |

### Router

| Skill | 説明 |
|-------|-------------|
| `using-investing-toolkit` | Entry point — 14 skill の intent routing |

## Architecture

```
slash command           skill                       agent / delegate           data source
─────────────           ─────                       ────────────────           ───────────
/invest-memo NVDA   →   investment-memo-writer  →   data-fetcher (haiku)   →   yfinance, FRED, ...
                                                ↘   macro-regime-snapshot
                                                ↘   domain-teams:investing-team   (analysis + gate)
                                                ↘   domain-teams:docs-team        (任意)
```

Adapter の SSOT は [`scripts/`](scripts/) に置きます。各 `*_client.py` は 3 通りで呼び出し可能：任意の skill から `uv run` subprocess、[`servers/mcp_server.py`](servers/mcp_server.py) に登録された MCP tool（18 client / 29 tool）、Python module 直接 import。Subprocess と MCP どちらも byte 単位で同一の JSON を返し、CI guard（`tests/test_mcp_equivalence_auto.py`）が drift しないか確認します。

`skills/*/scripts/` 配下の skill ローカルコピーは canonical な `scripts/` から [`sync-scripts.sh`](scripts/sync-scripts.sh) で同期し、CI 上で [`sync-check.sh`](scripts/sync-check.sh) が検証します。

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
|----------|-------------|------------|
| `FRED_API_KEY` | US の rate limit 緩和（匿名でも動作） | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FINMIND_API_TOKEN` | 台湾の rate limit 緩和（匿名でも動作） | [finmindtrade.com](https://finmindtrade.com/) |
| `EDINET_API_KEY` | JP Tier A 財務データ（無しなら yfinance financials Tier 2 fallback） | [disclosure2dl.edinet-fsa.go.jp](https://disclosure2dl.edinet-fsa.go.jp/) — 5 分の無料 self-service 登録 |

詳細な troubleshooting と Cowork retrospective は [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

## Data source

Adapter は [`scripts/`](scripts/) に集約 — 可能な限り primary source、無料 tier のみ。

| 地域 | Adapter | Source |
|--------|---------|--------|
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

investing-toolkit は data layer、分析は `domain-teams:investing-team` に置きます。Delegation は path と構造化 seed context のみ渡し、ファイル content は渡しません。委譲先 skill は自前の gate を enforcement します。

```
investing-toolkit                    domain-teams:investing-team
  investment-memo-writer    ───→     Deep Equity Research Memo protocol
                                       2 MUST gate
                                       4 SHOULD gate
                                       1 MAY gate（Taiwan Local Rigor）
                                     verdict: BUY / HOLD / SELL  ───→ caller に返却
                                       ↓（任意）
                                     domain-teams:docs-team
                                       formatting 仕上げ
```

Contract は [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract に明記。Toolkit skill は `investing-team` standards を複製しない、gate logic を local 実行しない、ファイル content の代わりに path 参照を渡す。`data-fetcher` agent は I/O 専任で分析しません。

## Cross-country 参考 doc

- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design 原則（v1.14.0 + v1.16.3 の hypothesis-vs-reality miss から得た教訓）
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — 5 市場の sector coverage + release cadence 比較
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install / troubleshooting / Cowork sandbox retrospective / MCP vs subprocess token・latency trade-off
- 各 skill 内の deep reference: `skills/{country}-macro/references/`、`skills/{country}-macro/docs/`（BOK ECOS catalogue、NBS 2908-leaf tree、JGBi auction 履歴 等）

## Version 履歴

完全な version 履歴（v1.0.0 → v1.16.5）と v2.0.0 への roadmap（backtesting + factor model）は [`ROADMAP.md`](ROADMAP.md) を参照。直近の release: v1.16.5（Phase 3 を investing-team に retarget）、v1.16.4（TWSE `/rwd/` 配線 + design-principles doc）、v1.16.3（empirical yfinance 検証）。

## Contributing

- Bug 報告と PR: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- Cowork 関連の issue は先に [`docs/mcp-setup.md`](docs/mcp-setup.md) を確認 — ほぼ確実に doc 化済みの sandbox 制約であり、plugin の bug ではありません
- 新規 data adapter の PR を歓迎します。既存の `*_client.py` pattern（`register_mcp_tools()` + subprocess CLI + cache TTL header）に従い、contract test fixture を追加してください

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。
