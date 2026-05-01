# investing-toolkit Scripts — canonical client adapter

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

用於擷取市場與總經資料的 Python data adapter。

## 在 v2.0.0 架構中的角色

這個 `scripts/` 目錄是所有共用 client adapter（`yfinance_client.py`、`fred_client.py`、`nbs_client.py`、`akshare_client.py` 等）的 **canonical home**。在 v2.0.0 三層架構下，每個 `data-{country}` skill 在自己的 `scripts/` 內持有它需要的 client 的 **functional copy**。依 Anthropic 的 skill-folder rule，這些副本必須實體放在使用它們的 skill 內 — 但和 canonical 維持 MD5 一致。

- **Canonical SoT（single source of truth）**：`investing-toolkit/scripts/*_client.py`
- **Functional copy**：`investing-toolkit/skills/data-{us,jp,tw,kr,cn}/scripts/*_client.py`
- **Sync 工具**：`bash scripts/sync-clients.sh` 把 canonical 推送到所有副本；加 `--check` 只回報 drift，有 drift 則 exit 1
- **CI guard**：`.github/workflows/check-script-sync.yml` 強制檢查 MD5 一致；v2.0.0 起，drift 即 CI block
- **架構決策**：[`../docs/adr/0001-data-analysis-report-layers.md`](../docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications

如果你修改了這裡的 client，commit 前請先跑 `bash scripts/sync-clients.sh`。如果你新增的 client 由新的 `data-{country}` skill 使用，請把該 skill 加入 `sync-clients.sh` 對應的 `*_TARGETS` 陣列，**同時** 在 `.github/workflows/check-script-sync.yml` 內鏡射對應條目。

## 安裝

**Step 1 — 安裝 uv**（一次性，自動偵測 Homebrew）：

```bash
sh investing-toolkit/scripts/setup.sh
```

就這樣。Scripts 使用 `uv run` 搭配 inline 相依套件 — 不需手動 `pip install`。

<details>
<summary>手動安裝選項</summary>

```bash
# macOS with Homebrew
brew install uv

# macOS / Linux 不使用 Homebrew
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

## Scripts

### yfinance_client.py

透過 yfinance（非官方）擷取美股價格歷史與公司資訊。

**Auth**：不需要。
**Cache**：`~/.cache/investing-toolkit/yfinance/` — 1h TTL。

```bash
# OHLCV 價格歷史
uv run yfinance_client.py --ticker AAPL --period 1y
uv run yfinance_client.py --ticker NVDA --period 6mo --interval 1wk

# 公司資訊（PE、PB、市值、EV — 不含財報）
uv run yfinance_client.py --ticker MSFT --action info

# 跳過 cache
uv run yfinance_client.py --ticker TSLA --period 1y --no-cache
```

**警告**：yfinance 是非官方爬蟲。它**僅提供價格資料**。請勿用於財務報表（損益表、資產負債表、現金流量表）。美國財報請直接使用 SEC EDGAR。

**yfinance 不支援台灣財報**。台灣財報請使用 FinMind（v1.1.0 起內建於 investing-toolkit）。

---

### fred_client.py

從 Federal Reserve Economic Data (FRED) 擷取總經資料。

**Auth**：設定 `FRED_API_KEY` 環境變數可取得較高 rate limit（API key 免費）。
未設 key：每天約 100 requests 後會 429 throttle。
**Cache**：`~/.cache/investing-toolkit/fred/` — 24h TTL。

```bash
# 單一 series
uv run fred_client.py --series T10Y2Y --periods 24

# 多個 series（逗號分隔）
uv run fred_client.py --series DGS10,DGS2,CPIAUCSL,GDPC1 --periods 12

# 跳過 cache
uv run fred_client.py --series FEDFUNDS --periods 24 --no-cache
```

**用於 macro regime 診斷的關鍵 series**：

| Series | 衡量內容 |
|--------|-----------------|
| `T10Y2Y` | 10Y–2Y 殖利率利差（殖利率倒掛訊號） |
| `DGS10` | 10 年期公債殖利率 |
| `DGS2` | 2 年期公債殖利率 |
| `CPIAUCSL` | 全體都市消費者 CPI（年增率反映通膨方向） |
| `CPILFESL` | 核心 CPI（排除食品與能源） |
| `GDPC1` | 實質 GDP（季頻） |
| `INDPRO` | 工業生產指數 |
| `FEDFUNDS` | 聯邦資金利率 |
| `UNRATE` | 失業率 |

申請免費的 FRED API key：https://fred.stlouisfed.org/docs/api/api_key.html

---

## 輸出格式

所有 scripts 皆**輸出 JSON 至 stdout**。錯誤訊息亦以 JSON 輸出，含 `"error"` key，並以 exit code 1 結束。

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

## CasualMarket MCP（台灣即時行情 — 外部）

台灣即時行情請另外安裝 CasualMarket：

```bash
claude plugin add casualmarket
```

CasualMarket 並未內建於 investing-toolkit。它以 MCP server 形式運作，提供即時 TWSE/OTC 報價、外資動向，以及估值倍數。
參見：https://github.com/sacahan/CasualMarket

---

### finmind_client.py

從 FinMind API 擷取台股資料。

**Auth**：設定 `FINMIND_API_TOKEN` 環境變數可取得較高 rate limit（免費註冊）。
未設 token：300 req/hr。設 token：600 req/hr。
**Cache**：`~/.cache/investing-toolkit/finmind/` — 6h TTL。

```bash
# 台股股價（日 OHLCV）— ticker = 4 碼代號
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01

# 三大法人買賣超（近 3 個月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start 2026-01-01

# 月營收（近 12 個月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMonthRevenue --date-start 2025-01-01

# 董監持股 + 質押率
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockHoldingSharesPer --date-start 2025-01-01

# 融資融券（近 3 個月）
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMarginPurchaseShortSale --date-start 2026-01-01

# 一次擷取多個 dataset
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice,TaiwanStockMonthRevenue --date-start 2025-01-01

# 跳過 cache
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01 --no-cache
```

**Ticker 格式**：僅 4 碼代號。`.TW` 與 `.TWO` 後綴會自動移除。

**支援的 datasets**：

| Dataset ID | 內容 | 公布延遲 |
|-----------|---------|-----------------|
| `TaiwanStockPrice` | 日 OHLCV | ~15 分鐘（T+0） |
| `TaiwanStockInstitutionalInvestorsBuySell` | 三大法人買賣超 | T+1 18:00 後 |
| `TaiwanStockMonthRevenue` | 月營收 | 次月 10 日前 |
| `TaiwanStockHoldingSharesPer` | 董監持股 + 質押率 | 季頻 |
| `TaiwanStockMarginPurchaseShortSale` | 融資融券餘額 | T+1 18:00 後 |
| `TaiwanStockFinancialStatements` | 財務報表（季頻）| 季頻 |
| `TaiwanStockProfitLossStatement` | 損益表（季頻） | 季頻 |

申請免費的 FinMind API token：https://finmindtrade.com

---
