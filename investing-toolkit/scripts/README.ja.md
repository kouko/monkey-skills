# investing-toolkit Scripts — canonical client adapter

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

市場およびマクロ経済データを取得するための Python data adapter。

## v2.0.0 アーキテクチャでの位置付け

この `scripts/` ディレクトリは共有 client adapter（`yfinance_client.py`、`fred_client.py`、`nbs_client.py`、`akshare_client.py` ほか）すべての **canonical home** です。v2.0.0 の three-layer architecture では、各 `data-{country}` skill が自身の `scripts/` 配下に必要な client の **functional copy** を保持します。Anthropic の skill-folder rule に従い、これらのコピーは消費する skill 内に物理的に存在しなければなりませんが、canonical と MD5 一致を保ちます。

- **Canonical SoT（single source of truth）**: `investing-toolkit/scripts/*_client.py`
- **Functional copy**: `investing-toolkit/skills/data-{us,jp,tw,kr,cn}/scripts/*_client.py`
- **Sync helper**: `bash scripts/sync-clients.sh` が canonical → 全コピーへ伝播。`--check` は drift を報告し、検出時 exit 1
- **CI guard**: `.github/workflows/check-script-sync.yml` が MD5 一致を強制。v2.0.0 から drift は CI ブロック対象
- **アーキテクチャ決定**: [`../docs/adr/0001-data-analysis-report-layers.md`](../docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications

ここの client を変更したら commit 前に `bash scripts/sync-clients.sh` を実行してください。新しい client を新規 `data-{country}` skill が使う場合、その skill を `sync-clients.sh` の該当 `*_TARGETS` 配列に追加し、**同時に** `.github/workflows/check-script-sync.yml` にもミラーしてください。

## セットアップ

**Step 1 — uv をインストール**（一回のみ、Homebrew を自動検出）：

```bash
sh investing-toolkit/scripts/setup.sh
```

以上です。各 script は inline 依存パッケージを伴う `uv run` を使うため、手動の `pip install` は不要です。

<details>
<summary>手動インストールの選択肢</summary>

```bash
# macOS with Homebrew
brew install uv

# macOS / Linux（Homebrew なし）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

## Scripts

### yfinance_client.py

yfinance（非公式）経由で米国株の価格履歴と企業情報を取得します。

**Auth**：不要。
**Cache**：`~/.cache/investing-toolkit/yfinance/` — 1h TTL。

```bash
# OHLCV 価格履歴
uv run yfinance_client.py --ticker AAPL --period 1y
uv run yfinance_client.py --ticker NVDA --period 6mo --interval 1wk

# 企業情報（PE、PB、時価総額、EV — 財務諸表は含まない）
uv run yfinance_client.py --ticker MSFT --action info

# cache をバイパス
uv run yfinance_client.py --ticker TSLA --period 1y --no-cache
```

**警告**：yfinance は非公式スクレイパーです。**価格データのみ**を提供します。財務諸表（損益計算書、貸借対照表、キャッシュフロー計算書）には使用しないでください。米国の財務報告は SEC EDGAR を直接利用してください。

**yfinance は台湾の財務諸表をサポートしていません**。台湾の財務には FinMind を使用してください（investing-toolkit v1.1.0 から利用可能）。

---

### fred_client.py

Federal Reserve Economic Data (FRED) からマクロ経済データを取得します。

**Auth**：`FRED_API_KEY` 環境変数を設定すると rate limit が緩和されます（無料 API key）。
key 未設定時：429 throttle 前に 1 日約 100 requests。
**Cache**：`~/.cache/investing-toolkit/fred/` — 24h TTL。

```bash
# 単一 series
uv run fred_client.py --series T10Y2Y --periods 24

# 複数 series（カンマ区切り）
uv run fred_client.py --series DGS10,DGS2,CPIAUCSL,GDPC1 --periods 12

# cache をバイパス
uv run fred_client.py --series FEDFUNDS --periods 24 --no-cache
```

**macro regime 診断に使う主要 series**：

| Series | 計測内容 |
|--------|-----------------|
| `T10Y2Y` | 10Y–2Y 利回りスプレッド（逆イールドのシグナル） |
| `DGS10` | 10 年米国債利回り |
| `DGS2` | 2 年米国債利回り |
| `CPIAUCSL` | 全都市消費者 CPI（YoY でインフレ方向を測る） |
| `CPILFESL` | コア CPI（食品・エネルギー除く） |
| `GDPC1` | 実質 GDP（四半期） |
| `INDPRO` | 鉱工業生産指数 |
| `FEDFUNDS` | フェデラル・ファンド・レート |
| `UNRATE` | 失業率 |

無料 FRED API key の取得：https://fred.stlouisfed.org/docs/api/api_key.html

---

## 出力フォーマット

すべての script は **stdout に JSON を出力**します。エラーも `"error"` キーを含む JSON で出力され、exit code 1 で終了します。

```json
{
  "ticker": "AAPL",
  "period": "1y",
  "fetched_at": "2026-04-16T10:00:00Z",
  "_cache": "miss",
  "latest_close": 195.42,
  "latest_date": "2026-04-15",
  "rows": 252,
  "data": [...]
}
```

## CasualMarket MCP（台湾リアルタイム — 外部）

台湾のリアルタイム市場データには CasualMarket を別途インストールしてください：

```bash
claude plugin add casualmarket
```

CasualMarket は investing-toolkit に同梱されていません。MCP server として動作し、TWSE/OTC のライブ気配、外資動向、バリュエーション倍率を提供します。
参照：https://github.com/sacahan/CasualMarket

---

### finmind_client.py

FinMind API から台湾株式データを取得します。

**Auth**：`FINMIND_API_TOKEN` 環境変数を設定すると rate limit が緩和されます（無料登録）。
token 未設定時：300 req/hr。設定時：600 req/hr。
**Cache**：`~/.cache/investing-toolkit/finmind/` — 6h TTL。

```bash
# 台湾株価（日次 OHLCV）— ticker は 4 桁コード
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01

# 三大法人買賣超（直近 3 ヶ月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start 2026-01-01

# 月營收（直近 12 ヶ月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMonthRevenue --date-start 2025-01-01

# 董監持股 + 質押率
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockHoldingSharesPer --date-start 2025-01-01

# 融資融券（直近 3 ヶ月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMarginPurchaseShortSale --date-start 2026-01-01

# 1 回の呼び出しで複数 dataset
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice,TaiwanStockMonthRevenue --date-start 2025-01-01

# cache をバイパス
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01 --no-cache
```

**Ticker 形式**：4 桁コードのみ。`.TW` および `.TWO` のサフィックスは自動的に除去されます。

**サポートされている datasets**：

| Dataset ID | 内容 | 公表ラグ |
|-----------|---------|-----------------|
| `TaiwanStockPrice` | 日次 OHLCV | ~15 分（T+0） |
| `TaiwanStockInstitutionalInvestorsBuySell` | 三大法人買賣超 | T+1 18:00 以降 |
| `TaiwanStockMonthRevenue` | 月營收 | 翌月 10 日まで |
| `TaiwanStockHoldingSharesPer` | 董監持股 + 質押率 | 四半期 |
| `TaiwanStockMarginPurchaseShortSale` | 融資融券残高 | T+1 18:00 以降 |
| `TaiwanStockFinancialStatements` | 財務報表（四半期）| 四半期 |
| `TaiwanStockProfitLossStatement` | 損益計算書（四半期） | 四半期 |

無料 FinMind API token の取得：https://finmindtrade.com

---
