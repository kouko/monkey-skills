# investing-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork 互換性**：Claude Code CLI / Code tab のみ動作。Cowork tab は sandbox の URL allowlist により外部 data fetch がブロックされる。詳細な retrospective は [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

**Version**：1.16.5
**所属**：[monkey-skills](https://github.com/kouko/monkey-skills)

投資リサーチ toolkit — **5 か国 macro データ**（US / JP / TW / KR / CN）、
個別株 snapshot（US / TW / JP）、technical indicator、DCF valuation、stock screener、
portfolio レビュー、そして `domain-teams:investing-team` を通じた完全な
investment memo pipeline。

データ専用層：本 toolkit はデータの取得と構造化のみを担当。分析、regime
判定、quality gate を経た memo は `domain-teams:investing-team` で行われる。

## Monthly GDP Proxy フレームワーク

v1.7.3 以降、5 つの country-macro skill は一貫した monthly
GDP proxy 規約を共有：

| 市場 | Proxy 種別 | 指標 |
|--------|-----------|------------|
| US | 集計済み Fed nowcast | `nowcast` group：`GDPNOW`、`CFNAI`、`WEI`、`USALOLITOAASTSAM`（OECD CLI） |
| JP | 集計済み内閣府 composite | 景気動向指数 CI トリオ：`coincident-index`（proxy 本体）、`leading-index`、`lagging-index` |
| TW | 集計済み NDC + DGBAS | `signal`（五色景氣燈號 — Taiwan 独自）、`leading-index`、`coincident-index` |
| KR | 集計済み BOK ECOS | `cycle` group：`coincident-cycle` K253（proxy 本体）、`leading-cycle` K254（KEYSTAT に lagging なし） |
| CN | 生コンポーネント（合意済み composite なし） | 三大数据：`industrial-yoy`、`retail-yoy`、`fai-yoy` + `services-production-yoy` |

US / JP / TW / KR はそれぞれの統計機関（Fed / 内閣府 / NDC+DGBAS / BOK ECOS）
から **集計済み** の値を提供する。China はコンポーネントを生のまま保持
する — 統合 composite に市場コンセンサスが存在しない（克強指数は陳腐化、
SF Fed CAT は四半期、Goldman / Bloomberg は独自）ため。Composite の合成は
分析責任を伴う方法論選択であるため、`domain-teams:investing-team` の
領分とする。

## Slash Commands

| Command | 機能 | Status |
|---------|-------------|--------|
| `/invest` | 適切な skill にルーティング | v1.0.0 |
| `/invest-macro [--region us\|japan\|global]` | IC + FRED/BOJ regime コール | v1.0.0 |
| `/invest-memo {ticker} [--scope deep\|quick]` | 完全 memo pipeline → investing-team | v1.0.0 |
| `/invest-screen {tickers} [--pe-max N] [--above-sma200]` | バッチ screener + 総合ランキング | v1.2.0 |
| `/invest-portfolio [holdings.csv]` | Portfolio レビュー + リバランス | v1.2.0 |

## Skills

Skill は 3 層構造（`using-investing-toolkit` router を反映）：

- **data** — 外部ソースから生の時系列を取得する、分析なし
- **aggregation** — データを結合 / スコアリング / 変換し単目的の出力にする
- **delegation** — `domain-teams:investing-team` への橋渡し（完全リサーチ用）

| Skill | Layer | 目的 | Status |
|-------|-------|---------|--------|
| `us-macro` | data | US macro（FRED 経由、約 31 series、14 group、新規 `pmi` [OECD CLI] + 新規 `swap-spreads` [T-SOFR 3M] を含む） | v1.10.0 |
| `japan-macro` | data | Japan macro（BOJ + e-Stat + ECB + MoF auction 経由、27 preset / 10 group、新規 `real-rates` group を含む、C+D+E マルチソース） | v1.10.0 |
| `taiwan-macro` | data | Taiwan macro（stat.gov.tw + CBC + DGBAS + NDC 経由、32 指標、新規 `pmi` group — CIER PMI/NMI を NDC 政府資料開放 dataset 6100 経由で取得） | v1.11.0 |
| `korea-macro` | data | Korea macro（FinanceDataReader BOK ECOS-KEYSTAT 経由、**54 指標、13 group**、月次 `industry` activity layer を含む；完全 98-code カタログは `docs/`） | v1.8.1 |
| `china-macro` | data | China macro（NBS new-SPA API + PBOC + FRED + yfinance 経由、36 指標、新規 `pmi` group — Caixin mfg/svc を akshare 経由 + NBS mfg/non-mfg/composite を nbs_client 経由；primary-source 優先） | v1.11.0 |
| `us-stock-snapshot` | data | yfinance 株価 + info + **SEC EDGAR Tier A fundamentals**（XBRL + Item セクション） | v1.13.0 |
| `taiwan-stock-snapshot` | data | **MOPS + TWSE/TPEx OpenAPI Tier A primary**（公司揭露 + 交易）；FinMind Tier 2 fallback | v1.13.0 |
| `japan-stock-snapshot` | data | **EDINET v2 Tier A fundamentals**（有報/四半期/臨時/大量保有）+ TDnet 当日 index + yfinance Tier 2 fallback — `EDINET_API_KEY` による dual-mode routing | v1.15.0 |
| `technical-snapshot` | data | RSI / MACD / Bollinger / ATR / SMA を `ta_client.py` 経由で計算 | v1.2.0 |
| `macro-regime-snapshot` | aggregation | 5 か国 IC + GIP（US/JP/TW/KR/CN）+ Rate Stress Dashboard + v1.11.0 クロスカントリー一貫性更新（Block 1 PMI 3/5 live；5×9 coverage grid；2026-Q2 grounding） | v1.11.0 |
| `stock-screener` | aggregation | バッチ screener — バリュエーション + モメンタム + トレンドの総合スコア | v1.2.0 |
| `dcf-valuation` | aggregation | 3 段階 DCF + 感度テーブル | v1.0.0 |
| `invest-portfolio` | aggregation | Portfolio レビュー — 損益 + regime overlay + リバランス | v1.2.0 |
| `investment-memo-writer` | delegation | 完全 memo pipeline — `domain-teams:investing-team` に委譲 | v1.0.0 |
| `using-investing-toolkit` | router | ルーティング用エントリ skill | v1.0.0 |

## アーキテクチャ

```
investing-toolkit/
├── README.md
├── ROADMAP.md
├── scripts/                        # Source of truth（ここでのみ編集）
│   ├── yfinance_client.py          #   US + 全世界 equity snapshot
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
│   ├── sync-scripts.sh             #   Source → skill ディレクトリへコピー
│   └── sync-check.sh               #   CI：コピー一致を検証
├── agents/data-fetcher.md          # 共通 I/O agent 仕様
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
│   │   └──→ domain-teams:docs-team（フォーマット、任意）
│   └── using-investing-toolkit/    # router
└── commands/                       # /invest-* slash command
```

各 skill は **自己完結型** で、自身の `scripts/` と `references/` を持つ。
plugin 層の `scripts/` ディレクトリが SSOT（信頼できる唯一の情報源） —
編集後は `sync-scripts.sh` を実行し、`sync-check.sh` で検証する。

## セットアップ

```bash
# Step 1 — uv をインストール（Homebrew 優先、curl fallback、既にあればスキップ）
sh investing-toolkit/scripts/setup.sh

# Step 2（任意）— FRED API key で rate limit を引き上げ（無料）
# https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY=your_key_here

# Step 3（任意）— Taiwan stocks 用 FinMind token（無料登録）
# https://finmindtrade.com
export FINMIND_API_TOKEN=your_token_here
```

その他のデータソース（NBS、BOJ、e-Stat、stat.gov.tw、CBC、DGBAS、NDC、
akshare 経由の PBOC/SHIBOR、FinanceDataReader BOK ECOS、yfinance）は
**API key 不要**。Scripts は `uv run` を inline 依存で使用 — Step 1 以降
`pip install` は不要。

## データソース

| ソース | データ | 認証 | 経由 |
|--------|------|------|-----|
| yfinance | US + 全世界 equity 株価/info；China/HK 指数 | なし | `yfinance_client.py` |
| FRED | US macro（金利/インフレ/GDP/nowcast）；CN FX | 任意 | `fred_client.py` |
| SEC EDGAR | US 財務（手動 URL） | なし | — |
| FinMind | Taiwan 三大法人 / 月營收 / 融資融券 / 董監持股 / 財報 | 任意 | `finmind_client.py` |
| CasualMarket MCP | Taiwan リアルタイム気配（任意） | なし | MCP |
| BOJ Time-Series API | Japan 政策金利、JGB、マネー、TANKAN、為替 | なし | `boj_client.py` |
| 統計ダッシュボード (e-Stat) | Japan CPI、GDP、IP、失業率、景気動向指数 CI トリオ | なし | `estat_client.py` |
| stat.gov.tw | Taiwan CPI、失業率、貿易ほか（hidden chart JSON） | なし | `statgov_client.py` |
| CBC Open Data API | Taiwan 政策金利、外貨準備、M1B/M2 | なし | `cbc_client.py` |
| DGBAS | Taiwan GDP、IP、景氣燈號（Excel .xls） | なし | `dgbas_client.py` |
| NDC | Taiwan 景氣對策信號 + composite index（ZIP/CSV） | なし | `ndc_client.py` |
| FinanceDataReader BOK ECOS | Korea 28 指標（KEYSTAT preset） | なし | `fdr_client.py` |
| NBS new-SPA API | China macro 直接（`data.stats.gov.cn`）— 21 指標 | なし | `nbs_client.py` |
| PBOC（chinamoney）via akshare | China LPR / RRR / 社融増量 / new loans | なし | `akshare_client.py` |
| SHIBOR（shibor.org）via akshare | China インターバンク金利 | なし | `akshare_client.py` |

## Cross-Plugin Delegation

`investment-memo-writer` は本 repo 初の cross-plugin delegation skill：

```
investing-toolkit:investment-memo-writer
  ├── data-fetcher agent (I/O)
  ├── macro-regime-snapshot（regime コンテキスト）
  ├── domain-teams:investing-team（分析 + gates）   ← cross-plugin
  └── domain-teams:docs-team（フォーマット、任意）  ← cross-plugin
```

規約は `CLAUDE.md` §Cross-Plugin Delegation Contract を参照。
データ層は本 toolkit に存在し、分析 / 判定 / quality gate は
`domain-teams:investing-team` に存在する。

## クロスカントリー参照ドキュメント

plugin 層のクロス市場参照（各 skill の references を補完）：

- [Industry Indicator Cadence](docs/industry-indicator-cadence.md) — 5 か国（US/JP/TW/KR/CN）の業界レベル指標カバレッジ、リリース頻度（daily → annual の各 tier）、公表ラグ、投資ホライゾンとのマッチングガイド
- [Design Principles](docs/design-principles.md) — 本 plugin のアーキテクチャ用メタ規約。**empirical-first design** ルールを含む（v1.14.0 + v1.16.3 の「仮説 vs 現実」事後検証から獲得）
- [MCP Setup](docs/mcp-setup.md) — インストールパス + Cowork sandbox 制約の率直な記載

## バージョンハイライト

### v1.16.5 (2026-04-20) — investment-memo-writer Phase 3 を investing-team に再ターゲット

v1.16.4 が v1.12.0 から継承していた古いルーティングを修正：
memo Phase 3 は `investing-team` を「v5.0.0-v5.1.0 一時的」と
誤認した前提で `domain-teams:research-team` にディスパッチしていた。
Git log によると investing-team は v5.0.0 以降恒常的に存在し、
完全な standards/protocols/rubrics スタックを備える；research-team
自身の SKILL.md も投資業務を investing-team に戻すリダイレクトを
持つため、従前のルーティングは無駄な間接化であり、CLAUDE.md
の Cross-Plugin Delegation Contract canonical target にも違反していた。

- `skills/investment-memo-writer/SKILL.md`：Phase 3 の見出し + 本文 +
  description + 解説 + Cross-Plugin Delegation Contract §
  を research-team → investing-team に再ターゲット。
- Gate 表を **実際の** investing-team gate スタックに置換
  （以前は 7 個の捏造「research-team gate」を列挙していた；
  現在は investing-team rubrics/ にある本物の 2 MUST + 4 SHOULD + 1 MAY）。
- audit trail として履歴ノートを残し、v1.12.0 の誤前提と
  v1.16.5 の修正を遡及的に説明。

code / script / test の変更なし。Regression suite 不変（26/26 pass）。

### v1.16.4 (2026-04-19) — taiwan-stock-snapshot に TWSE `/rwd/` を結線 + design-principles ドキュメント

v1.16.3 から残っていた 2 つの懸案を解消：

- **A1 — TWSE `/rwd/` stock-day-history が孤立しない**：
  taiwan-stock-snapshot Phase 1 は memo が規制機関引用（ISQ Narrative Anchor）
  を必要とする際、`.TW` ticker を Tier A 生株価エンドポイント
  経由で明示的にルーティングする。technical-snapshot 既存の
  yfinance-primary 既定を補完 — 生株価と調整後株価が
  明文化された別々の利用者を持つ形に。
- **A3 — `docs/design-principles.md`**：v1.14.0（MCP Cowork 前提失敗）+
  v1.16.3（yfinance TW カバレッジ仮定失敗）から得た
  empirical-first design ルールを成文化。2 件のインシデントを
  再利用可能な事前設計の探査 checklist に転化。

code 変更なし、SKILL.md / docs のみ。Regression test 不変
（v1.16.3 と同じ 26/26 pass）。

### v1.16.3 (2026-04-19) — TWSE `/rwd/` 過去 OHLCV action（Tier A、memo-citation モード）

ユーザーから `technical-snapshot` / `stock-screener` が OHLCV を
`yfinance_client.py` にハードコードしており、TW/KR/CN の
カバレッジに穴がある可能性が指摘された。`.TW` 用の
Tier A TWSE 過去エンドポイントを追加。続いて TSMC 2330.TW（243 行 / 1y、
完全 info、SMA-200 計算可能）+ 3105.TWO WIN Semi で yfinance を実証検証 —
**yfinance は TW を split-adjusted 株価（TA 標準）で問題なくカバーしている**
ことが判明。最終的なルーティングは **yfinance を全市場の既定** とし、
TWSE `/rwd/` エンドポイントを *explicit-request* モードとして公開、
caller が memo の primary-source 引用に規制機関の生株価が必要な
場合に利用する。

- **`scripts/twse_openapi_client.py::stock-day-history`**（新 action）：
  TWSE 公開 stock-day.html ページの裏側にある
  `https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY` をラップ。
  Tier A primary-source、約 16 年分の履歴、月次粒度（client が内部で
  N か月ループ）。過去月は 30 日 cache、当月は 1 日。標準化出力は
  ta_client の入力契約に整合：西暦日付、小文字 `open/high/low/close/volume`、
  パース済み float（千位区切り除去）。
- **`scripts/ta_client.py` の堅牢化**：source が top level に
  `latest_date` / `latest_close` を返さない場合、`data[]` から自動算出。
  ta_client が yfinance + FinMind + TWSE `/rwd/` 間でソース別 shim ゼロで
  ポータブルに。
- **`technical-snapshot` SKILL.md Phase 1**：yfinance は全市場
  （`.TW` / `.TWO` を含む）の既定を維持。TWSE `/rwd/`
  action は生 primary-source 株価用の Advanced / memo-citation モードとして文書化。
- **`stock-screener` SKILL.md Phase 1**：完全 ticker リストに対し
  単一の yfinance バッチ呼び出し（v1.16.3 以前の形を維持）。
  taiwan-stock-snapshot memo コンテキスト向けに TWSE `/rwd/` への
  ポインタを記載。
- **2026-04-19 の実証検証**：
  - TSMC 2330.TW を yfinance 1y 経由 → 243 行、SMA-200 計算可能、
    通貨 TWD、完全 info（sector/PE/PB/yield）；TWSE `/rwd/`
    終値と完全一致（2030.0 @ 2026-04-17）。
  - 3105.TWO（WIN Semi、上櫃）を yfinance 3mo 経由 → 55 行、終値 539.0。
  - yfinance 株価は split/dividend-adjusted（TA の業界標準）；
    TWSE `/rwd/` は生株価（規制機関引用用途）。
- **Regression**：MCP 契約テスト 26/26。US / JP / 既存 TW / TWO ユーザーに対して
  v1.16.2 比で挙動変化なし。

注意点：
- TWSE `/rwd/` エンドポイントは openapi.twse.com.tw に未掲載。
  Tier A（TWSE 自家発行）だが文書化なし — 既定経路ではなく
  explicit-request action として保持。
- TPEx（.TWO）には /rwd/ 相当なし — yfinance を推奨既定とし、
  FinMind TaiwanStockPrice は `taiwan-stock-snapshot` memo コンテキストでの
  明示的 Tier 2 fallback として引き続き利用可能。

### v1.16.2 (2026-04-19) — mops_fetch 必須パラメータ検証（ユーザー報告 bug 修正）

`mops_fetch` が必須パラメータ無しで呼ばれた際の不可解な runtime エラーを修正。
例：`mops_fetch(action="director-holdings", ticker="6741")` —
`year`/`month` 欠落時に
`unsupported format string passed to NoneType.__format__`（下流の f-string
が `None` に作用）で crash していた。現在は以下を返す：

```json
{"error": "action 'director-holdings' requires: --year, --month. (ROC calendar for --year: 西元 - 1911; e.g. 2026 → 115)", "action": "director-holdings"}
```

- **scripts/mops_client.py**：`_REQUIRED_PARAMS` テーブル（action → 必須
  パラメータ名）+ `_validate_action_params(args)` ヘルパーを追加し、
  `_run_action()` 冒頭で呼び出す。欠落パラメータは明確な flag リストと
  共に `SystemExit` を raise；既存の `mops_fetch` SystemExit handler が
  読みやすい error dict に変換する。5 カテゴリ 13 action が検証対象に。
- **mops_fetch docstring**：action ごとに明示的な `[required, params]`
  記法で書き直し — 従来の曖昧な「Insider / governance (ticker,
  year [+ month])」記法を置き換え、どのパラメータが必須か LLM caller を
  誤導しないように。
- **tests/test_mcp_equivalence_auto.py**：6 つのパラメータ化された
  negative-case regression テストを追加し、director-holdings、monthly-revenue、
  day-announcements、balance-sheet、insider-trades のパラメータ欠落パスをカバー。

MCP と CLI の両経路を修正（共に `_run_action` を経由）。
姉妹 client（twse/edinet/sec_edgar）は元々安全 — mops のみ
top-level 検証なしの dispatcher-pattern client だった。

### v1.16.1 (2026-04-19) — Cowork sandbox 事後検証 + メンテナンス自動化

**事後検証**：v1.14.0 の中核前提 — plugin インストールの stdio
MCP server が Claude Desktop Cowork sandbox の URL allowlist を
迂回する — は誤りだった。v1.16.1 の実証テストにより、plugin-MCP は
plugin-subprocess と **同じ** sandbox 内で動作し、両経路とも
Cowork で同様にブロックされることが確認された。Anthropic 自身の
plugin がすべて remote `type: http` MCP を採用しているのは
まさにこの理由であり、私たちはそのシグナルを読み違えていた。

**意味するところ**：
- Claude Code CLI / Desktop Code タブ：subprocess も MCP も
  問題なく動作；subprocess の方が安価な既定（token オーバーヘッドゼロ）。
- Claude Desktop Cowork タブ：URL fetch を行う script では
  どちらの経路も動かない。本 plugin は Claude Code CLI に切り替えること。

**v1.16.1 で何が変わるか**：
- `docs/mcp-setup.md` を率直な事後検証 + Code CLI vs Cowork ガイダンス +
  token/レイテンシのトレードオフ表で書き直し。
- 9 つの SKILL.md MCP-aware 引用ブロックを「prefer MCP」から
  「Claude はどちらでも使用可；両者は同一 JSON を返す」に中立化；
  Cowork 注意事項を明示；skill ごとの tool 名列挙は
  `docs/mcp-setup.md` の単一権威カタログへ集約。
- **新規 `tests/test_mcp_equivalence_auto.py`** — 全公開 client にまたがる
  14 fixture をカバーするパラメータ化 MCP↔CLI drift guard。
  action ヘルパーが変わった際に静かな乖離を検出。
- **新規 `tests/test_skill_md_sync.py`** — canonical な事後検証文言を強制し、
  SKILL.md 内の古い MCP tool 参照をフラグする。
- **新規 `tools/validate_mcp_tools.py`** — schema + description の linter；
  現在 29 tool すべて pass。

**MCP インフラのロールバックはなし** — Code CLI で問題なく動作し、
将来の remote-HTTP-MCP 移行のオプショナリティを保持し、
v1.16.1 で約 1 日かけた CI 自動化投資により、今後のメンテナンスが
~3.5-6.5 h/6mo から <1 h/6mo に短縮される。

### v1.16.0 (2026-04-19) — MCP tool surface 完成

v1.14.0 で延期された残り 8 個のデータ取得 script を
MCP tool としてラップ、Cowork ユーザーが macro / regime 業務で
詰まらないようにした。本 toolkit のすべての primary データ adapter が
MCP からアドレッサブルに。

- **JP macro MCP tool**（Commit 1）：`boj_fetch`、`boj_tankan_inflation_outlook`、
  `ecb_series`、`estat_fetch`、`estat_search`。
- **TW macro MCP tool**（Commit 2）：`cbc_fetch`、`dgbas_fetch`、
  `ndc_fetch`、`statgov_fetch`。
- **KR macro MCP tool**（Commit 3）：`fdr_fetch`（BOK ECOS-KEYSTAT 54
  指標 / 13 group）。
- **中央 registry**（Commit 4）：`servers/mcp_server.py` が 18
  client をインポートし 29 tool を公開。契約テスト更新；3 個 pass。
- **Session token コスト**：~4.4K（29 × 150）— v1.14.0 の 5K-split
  しきい値以下；core/extras MCP 分割は引き続き延期。

**既知の非目標**：`ta_client.py` はラップ**しない** — 外部データを
取得するのではなく OHLCV をローカル変換するため（MCP caller が必要なら
`yfinance_history` と組み合わせ CLI 変換を実行する）。

### v1.15.0 (2026-04-19) — Japan 個別株 skill（Path γ 完了）

v1.13.0 から積み残された stacked PR を完了：
Japan が US + TW に並び、専用個別株データ skill を持つ 3 つ目の市場に。

- **scripts/edinet_client.py**（739 行）：金融庁 EDINET v2 REST API
  Tier A primary-source adapter。7 種の様式（有報 120 / 四半期 140 /
  半期 160 / 臨時 180 / 自己株買付 220 / 大量保有 350 + 訂正版）。CSV
  type=5（FSA が 2024-04 に追加）を MVP パスとして採用 — iXBRL-flatten された
  BS/PL/CF を sec_edgar / mops と同形状の canonical key_metrics dict に
  パース。Ticker → EDINET code 解決は無料公開の
  Edinetcode.zip ダウンロード経由（key 不要）。PDL 1.0 ライセンス —
  「出典：金融庁 EDINET」帰属表示で再配布可。

- **scripts/tdnet_client.py**：当日適時開示情報 index、
  Yanoshin WEB-API 経由。決算短信 / 業績予想 / 配当予想 / 自己株
  買付 / 株主総会 / 役員異動 をカバー — これらは EDINET 臨時報告書では
  約 45 日後にしか出てこない事象。Index-only ポインタ方式；本文は
  JPX（release.tdnet.info）から取得。

- **yfinance_client.py --action financials**（新規）：JP（およびクロス市場）の
  Tier 2 BS/PL/CF fallback を Yahoo Finance で提供。Provenance は
  `data_tier: "tier_2"` と警告付きで明示。Toyota FY2025-03-31 で
  EDINET と突き合わせ検証 — revenue / operating / net
  income / total assets / operating CF が円単位まで一致。

- **skills/japan-stock-snapshot/**：Dual-mode tier routing の SKILL.md。
  `EDINET_API_KEY` 設定済み → Tier A モード；未設定 → Tier 2 yfinance
  fallback、目立つアップグレード推奨プロンプト付き。既知のギャップを
  明示記載（信用取引残高 per-stock / 空売り / daily 投資部門別 — すべて
  J-Quants Standard 有料 tier の背後または無料では真に取得不可）。

- **investment-memo-writer**：Phase 1 を拡張して 4 桁 JP
  ticker（`^\d{4}(\.T|\.TO)?$`）を新 skill にルーティング。Output 形状は
  US/TW snapshot と同一で、`domain-teams:research-team` が
  市場非依存の fixture を受け取れる。

- **MCP surface**：13 → 19 tool（+4 edinet、+1 tdnet、+1
  yfinance_financials）。`--self-check` は 10 client を返す。契約
  テスト更新；3 個 pass。

### v1.14.0 (2026-04-19) — MCP migration（Claude Desktop Cowork 解除）

8 個のデータ取得 script を、plugin 層の単一 MCP server を介して
**13 個の MCP tool** として公開。Claude Code と Claude Cowork は
plugin インストール時に自動アクティブ化；MCP プロセスは
Claude Desktop sandbox の外で動くため、従来 Cowork 内のすべての
データ取得呼び出しをブロックしていた URL 制限が
アーキテクチャ的にバイパスされる。

- **servers/mcp_server.py**：FastMCP エントリ、8 client モジュールを
  すべてインポート。合計 13 tool（yfinance × 3、sec_edgar × 4、fred / mops /
  twse_openapi / finmind / akshare_china_macro / nbs_china_macro × 各 1）。
  `--self-check` flag で MCP loop に入らずに uv cache + 依存を
  事前ウォーム。

- **.mcp.json + servers/mcp_bootstrap.sh**：plugin 自動登録。
  二経路ルーター：FAST PATH（marker + uv 準備済 → 真の server を
  3 秒未満で exec）、BOOTSTRAP PATH（バックグラウンドで setup.sh を spawn し、
  Claude Desktop の 60 秒 handshake timeout 内に即応する stdlib
  wrapper を exec — 2026-04-19 に実証探査）。

- **servers/setup.sh**：silent-auto の段階的インストール（Homebrew → curl
  astral.sh/uv/install.sh）、続いて `--self-check` で 66 wheel を
  事前ウォーム、plugin バージョン marker を書き込み。非開発者ユーザーは
  Terminal を開く必要なし。

- **servers/mcp_wrapper.py**：stdlib JSON-RPC；プロビジョニング期間中に
  `investing_toolkit_status` を公開し、Claude が
  setup の進捗をリアルタイムで報告し、準備完了時に再起動を依頼できる。

- **Dual-mode scripts**：8 client script すべてに `register_mcp_tools()` を追加；
  `uv run scripts/xxx.py` の CLI 経路は不変 — MCP と CLI が
  同一 JSON を返す（`tests/test_mcp_contract.py` で強制）。

- **SKILL.md MCP-aware 文章**：8 skill に注釈を加え、MCP tool が
  登録されていればそれを優先；subprocess command は canonical fallback。

- **docs/mcp-setup.md**：ユーザー向けインストールガイド — Claude Code CLI、
  Claude Cowork（Team プライベート fork）、Pro/Max 制約説明、
  troubleshooting。

インストールパスは [`docs/mcp-setup.md`](docs/mcp-setup.md) を参照。

### v1.13.0 (2026-04-19) — 個別株 fundamentals（US + TW）

Pattern C NVDA demo の 4 つのデータギャップ（SEC EDGAR 欠落 / forward
guidance / consensus / peer）を US + TW 市場で解消：

- **sec_edgar_client.py**：JSON API で 7 種の SEC 様式（10-K /
  10-Q / 8-K / Form 4 / 13F / S-1 / DEF 14A）をカバー。XBRL 構造化 fact +
  HTML 文章 Item セクション parser。User-Agent 必須、10 req/sec
  コンプライアンス組み込み、tiered cache TTL。

- **mops_client.py**：新 MOPS JSON API（mops.twse.com.tw に 2025-02 ローンチ）
  経由で 16 エンドポイント。公司基本資料 + 財報 BS/IS/CF +
  月營收 + 持股 + 股利 + 重大訊息 + 株主総会をカバー。履歴の深さ：IFRS
  財報 13 年（2013+）、歴史重大訊息 30 年（1996+）。auth/cookie/CSRF なし。
  Primary-source Tier A（金管會法定揭露）。

- **twse_openapi_client.py**：TWSE/TPEx 公開 OpenAPI、交易資料用
  （日行情 / 融資融券 / 三大法人 snapshot / 業界 EPS / 除權息日曆）。
  MOPS はこれをカバーしない — 設計上の分担。

- **taiwan-stock-snapshot 再構築**：MOPS + TWSE OpenAPI Tier 1
  primary；FinMind Tier 2 自動 fallback（Pattern A+B）。既知の Tier 1
  ギャップ（daily T86 per-stock flow、歴史 STOCK_DAY）は警告ログ付きで
  既定で FinMind にルート。

- **dcf-valuation 有効化**：以前は財務諸表欠落で構造的に動かなかったが、
  SEC EDGAR（US）または MOPS（TW）から自動取得するように。

- **investment-memo-writer Phase 1 更新**：SEC EDGAR + MOPS + TWSE
  OpenAPI command を追加；FinMind は Tier 2 fallback パスとして残置。

JP 個別株 skill は v1.14.0 stacked PR（Path γ
アーキ決定）に延期。

Pattern C 再実行時の期待：v1.13.0 merge 後、NVDA と 2330.TW で ISQ
verdict が `PASS`（`PASS_WITH_NOTES` ではなく）。

### v1.12.0 (2026-04-19) — Pattern C UX（ファイル書き込み + 可視性）

v1.11.0 NVDA Pattern C demo で露呈した 3 つの UX 問題を修正：

- **investment-memo-writer Phase 5**：ファイル書き込みを既定に —
  `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
  で deep/quick モード別ファイル名（同モード再実行で上書き）。Obsidian
  モード自動検出：`$OBSIDIAN_VAULT_PATH` 環境変数または
  `~/kouko-obsidian-vault/` 等を probe；vault `CLAUDE.md` を読みフォルダ規約を
  取得；`obsidian:obsidian-markdown` skill 経由でルーティング。
  Chat 配信は executive summary + gate verdict + ファイルリンクのみ
  （完全 memo はファイル内、chat には反復しない）。

- **investment-memo-writer Phase 3 ターゲット修正**：
  `domain-teams:investing-team` 参照を
  `domain-teams:research-team` に置換（research-team の「投資もしくは
  macro 分析」スコープに従う）。歴史ノートは保持。

- **skill-team Visibility Convention（domain-teams v5.2.0）**：7 つの
  workflow skill（research / code / design / docs / devops / qa /
  planning）に compliance ブロックを追加し、3 段階で `TaskUpdate` を
  発行することを要求：phase 遷移 + マイルストーン + heartbeat（最大
  60 秒沈黙）。Narration Convention（軸 1）を investment-memo-writer に
  追加し、ディスパッチ前の期待値設定に使う。

アーキ代替案（軸 3 phase-split）は軸 1+2 が不十分なら v1.13.0+ に
延期。確率的 vs 構造的保証のトレードオフは
skill-team SKILL.md §Visibility Convention に記載。

クロス plugin PR：investing-toolkit（1.11.0 → 1.12.0）+ domain-teams
（5.1.0 → 5.2.0）。3-commit スタック、~3.5 日のスコープ。

### v1.11.0 (2026-04-19) — クロスカントリー一貫性更新

v1.10.0 の PMI 非対称性 + grounding vintage drift に対処：
- **china-macro**：新 `pmi` group（Caixin mfg/svc を akshare 経由 + NBS
  公式 mfg/non-mfg/composite を既存 nbs_client 経由 — primary-source
  優先）。Block 1 CN PMI ギャップを充填。
- **taiwan-macro**：新 `pmi` group（PMI/NMI を NDC data.gov.tw CSV 経由 —
  v1.11.0 APAC 探査中に予期せず発見した無料 tier アクセス；
  ライセンス：政府資料開放授權條款-第1版、CC BY 相当）
- **japan-macro / korea-macro**：PMI URL のみの参照を正式化
  （au Jibun Bank / S&P Global Korea 有償 — 無料 tier パスなし）
- **macro-regime-snapshot**：Block 1 PMI 行カバレッジを 1/5 → 3/5 live に
  改善（+CN +TW）；Data Source Architecture セクションを 5×9
  クロスカントリーカバレッジグリッドで拡充
- **grounding 更新**：CN + JP を 2026-Q2 vintage に完全再監査
  （CN 2026 政府工作報告 GDP 4.5-5% レンジ；BOJ は 2026-01/03 で 0.75% 据え置き）；
  US + TW + KR は差分追補（FOMC SEP r* 3.0→3.1%；CBC 2.00% 据え置き；
  BOK 7 連続据え置き）。合計 16 🔴 + 17 ⚠️ 修正。
- **research/grounding-v1.11.0.md**：299 行の audit trail を統合

JGBi YTM solver（v1.11.0 で当初検討）は架構的一貫性のため
意図的に却下 — JP のみが 5 country-macro skill 中で唯一の
bond-math 国家になり、「country-macro = 純粋データ層」規律に違反する。
ブレインストーミング監査で再確認。

### v1.10.0 (2026-04-19) — PMI + JP real rates + swap spread

v1.9.0 の延期リストから 3 つのデータカバレッジギャップを解消：
- **us-macro**：新 `pmi` group（OECD CLI USALOLITOAASTSAM を FRED-available
  proxy として — ISM/S&P Global は St. Louis Fed blog によると 2016 に FRED から削除）
  + 新 `swap-spreads` group（Treasury-SOFR 3M スプレッドをマネーマーケット
  流動性 proxy として — ポスト LIBOR の FRED にはきれいな term swap series がない）
- **japan-macro**：新 `real-rates` group、C+D+E マルチソースフレームワーク経由
  （MoF JGBi auction アンカー + ECB 月次 ex-post + BOJ Tankan 1Y/3Y/5Y
  期待インフレ）。JSDA YTM solver は探査により JSDA が JGBi 利回りを
  マスクしている（999.999 sentinel）と確認されたため v1.11.0 に延期。
  `ecb_client.py` を追加、Tankan のため `boj_client.py` を拡張。
- **macro-regime-snapshot**：Block 1 に各国 PMI 行（US は取得；
  JP/TW/KR/CN は URL のみ）。Block 3 を「Rate Stress Dashboard」に改名し、
  JP real-rate サブブロックと US swap spread サブブロックを追加。
- **research**：新 `grounding-v1.10.0.md` を追加、3 つの新 JP データソース
  （MoF auction / ECB SDMX / BOJ Tankan）の primary-source 検証を記載、
  JSDA / JBTS パスの却下理由も含む。

- **v1.9.0** — macro-regime-snapshot 5 か国更新（US/JP/TW/KR/CN）+ LSEG-style 5-block dashboard（Macro Summary / Yield Curve / Real Rate / IC+GIP Regime / Asset-Class Tilts）+ us-macro に新 US `real-rates` group（T5YIE / T10YIE / DFII5 / DFII10 — real-rate 分解ブロック）。signal-label セマンティクスを追加（Expansion/Contraction、Accommodative/Restrictive ほか）
- **v1.8.1** — Korea-macro 月次産業活動層（43 → 54 指標；新 `industry` group：K201-K217 業種活動 — manufacturing inventory/shipment/operating-rate、services production、retail sales、wholesale-retail、credit-card usage、machinery orders、capital-goods output、construction completion/orders）
- **v1.8.0** — Korea-macro カタログ + 構造的 refactoring + 15 Tier-B preset（28 → 43 指標）
- **v1.7.3** — Taiwan + Korea 月次 GDP proxy タグ付け（5 市場フレームワーク完成）
- **v1.7.2** — Router 同期 + Layer カラム
- **v1.7.1** — China 月次 GDP proxy タグ付け（US/JP との Tier 2 同等性）
- **v1.7.0** — US（nowcast group）+ JP（CI トリオ）の月次 GDP proxy
- **v1.6.0** — China macro（NBS direct + PBOC + FRED + yfinance 経由 34 指標）
- **v1.5.0** — Korea macro（FinanceDataReader 経由 28 指標）
- **v1.4.0** — Taiwan macro（30 指標、4 つの政府ソース）
- **v1.3.0** — US + Japan macro skill
- **v1.2.0** — stock-screener、technical-snapshot、invest-portfolio
- **v1.1.0** — Taiwan stock データを FinMind 経由
- **v1.0.0** — コア：macro-regime-snapshot、us-stock-snapshot、DCF、memo writer

完全な履歴と v2.0.0 Quantitative Layer 計画は [ROADMAP.md](ROADMAP.md) を参照。
