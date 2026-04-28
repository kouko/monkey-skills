# us-macro

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

investing-toolkit 的美國總經與產業層級資料 skill。

## 概覽

從 FRED（Federal Reserve Economic Data）擷取 25 項美國總經與產業層級指標，回傳依 11 個指標 group 分類的結構化 JSON：rates、inflation、growth、nowcast（核心總經），加上 housing、industrials、energy、financials、consumer、tech、ppi（產業層級）。產業 group 對應產業 ETF 用於投資分析。本 skill 為純資料 skill — 不分析、不對應 regime、不產出投資判定。

**月度 GDP proxy**：美國官方 GDP 為季頻（`GDPC1`）。`nowcast` group（GDPNow、CFNAI、WEI、OECD CLI）共同構成即時 GDP 動能 proxy，與 china-macro 的三大數據及 japan-macro 的景気動向指数 CI 三件組對應。

## 資料來源

**FRED CSV endpoint** — 不需 API key。Script 直接從 St. Louis Fed 公開 endpoint 下載 CSV 資料：

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES}&cosd={START}
```

可選的 JSON API mode（`--use-api`）支援更彈性的查詢，但需要 `FRED_API_KEY` 環境變數。本 skill 預設的 CSV mode 已涵蓋全部用例。

## 指標

### 核心總經

| Series | 名稱 | Group | 頻率 | 一般延遲 |
|--------|------|-------|-----------|-------------|
| T10Y2Y | 10Y-2Y 公債利差 | rates | 日頻 | 1 個營業日 |
| DGS10 | 10 年期公債殖利率 | rates | 日頻 | 1 個營業日 |
| DGS2 | 2 年期公債殖利率 | rates | 日頻 | 1 個營業日 |
| FEDFUNDS | 有效聯邦資金利率 | rates | 月頻 | 月底後 ~1 週 |
| CPIAUCSL | 全項 CPI（All Items） | inflation | 月頻 | ~2-3 週 |
| CPILFESL | 核心 CPI（不含食品與能源） | inflation | 月頻 | ~2-3 週 |
| GDPC1 | 實質 GDP | growth | 季頻 | ~1 個月（advance est.） |
| INDPRO | 工業生產指數 | growth | 月頻 | ~3-4 週 |
| GDPNOW | Atlanta Fed GDPNow（SAAR %） | nowcast | 季頻 snapshot | 當季每月更新 6-7 次 |
| CFNAI | Chicago Fed National Activity Index | nowcast | 月頻 | ~2-3 個月 |
| WEI | NY Fed Weekly Economic Index | nowcast | 週頻 | ~1 週 |
| USALOLITOAASTSAM | OECD Composite Leading Indicator（USA） | nowcast | 月頻 | ~1 個月 |

### 產業層級

| Series | 名稱 | Group | 頻率 | 一般延遲 |
|--------|------|-------|-----------|-------------|
| PERMIT | 建築許可 | housing | 月頻 | ~2-3 週 |
| HOUST | 新建房屋開工 | housing | 月頻 | ~2-3 週 |
| CSUSHPISA | Case-Shiller 房價指數 | housing | 月頻 | ~2 個月 |
| MORTGAGE30US | 30 年期房貸利率 | housing | 週頻 | ~1 週 |
| DGORDER | 耐久財訂單 | industrials | 月頻 | ~4 週 |
| DCOILWTICO | WTI 原油價格 | energy | 日頻 | 1 個營業日 |
| DHHNGSP | Henry Hub 天然氣價格 | energy | 日頻 | 1 個營業日 |
| BAMLH0A0HYM2 | 高收益債信用利差 | financials | 日頻 | 1 個營業日 |
| RSAFS | 預估零售銷售 | consumer | 月頻 | ~2 週 |
| UMCSENT | 消費者信心（UMich） | consumer | 月頻 | ~2-4 週 |
| CES3133440001 | 半導體就業 | tech | 月頻 | ~3-4 週 |
| PCUAINFOAINFO | PPI：資訊服務 | tech | 月頻 | ~2-3 週 |
| PCUOMFGOMFG | PPI：總製造業 | ppi | 月頻 | ~2-3 週 |

組織為 11 個 group：

- **rates**：T10Y2Y、DGS10、DGS2、FEDFUNDS
- **inflation**：CPIAUCSL、CPILFESL
- **growth**：GDPC1、INDPRO
- **nowcast**：GDPNOW、CFNAI、WEI、USALOLITOAASTSAM
- **housing**：PERMIT、HOUST、CSUSHPISA、MORTGAGE30US
- **industrials**：DGORDER
- **energy**：DCOILWTICO、DHHNGSP
- **financials**：BAMLH0A0HYM2
- **consumer**：RSAFS、UMCSENT
- **tech**：CES3133440001、PCUAINFOAINFO
- **ppi**：PCUOMFGOMFG

## 產業 ETF 對應

| Group | 主要 ETF | 備註 |
|-------|-------------|-------|
| housing | XLRE、XHB | MORTGAGE30US 亦為 XLF 訊號 |
| industrials | XLI | INDPRO（growth group）亦相關 |
| energy | XLE | 油價影響航空、消費支出、通膨 |
| financials | XLF | T10Y2Y（rates group）驅動銀行利差 |
| consumer | XLY、XLP | 零售銷售驅動非必需品 vs 必需品輪動 |
| tech | XLK | 半導體就業反映供應鏈 |
| ppi | （跨產業） | 領先 CPI 3-6 個月；毛利壓力訊號 |

## 架構

```
us-macro skill
├── SKILL.md                    <- Claude 讀取此檔
├── scripts/
│   ├── fred_client.py          <- FRED CSV adapter（不需 API key）
│   └── setup.sh                <- 自動安裝 uv
└── references/
    └── us-macro-indicators.md  <- 25 項指標條目 + 解讀
```

Scripts 為從 `investing-toolkit/scripts/` 透過 `sync-scripts.sh` 同步的副本。Skill 目錄自包含，Claude Code 會以 skill 根目錄為基準解析所有路徑。

## 運作方式

1. **解析 series 清單** — `--indicators` 參數（預設 `all`）對應到 FRED series ID。例如 `--indicators rates` 會解析為 T10Y2Y、DGS10、DGS2、FEDFUNDS。

2. **Launch data-fetcher agent** — Skill 將 fetch requests 派送至 `data-fetcher` agent，agent 透過 `uv run` 執行 `fred_client.py`。Requests 依頻率分組，使用適當的 period 數（如日頻/月頻 24 期、季頻 12 期）。

3. **構造輸出** — 對每個 series，skill 取出最新與前一筆觀測值，計算方向（Rising / Falling / Flat），並依其指標 group key 分類。

## 輸出 contract

```json
{
  "fetched_at": "2026-04-16T08:00:00Z",
  "groups": {
    "rates": {
      "T10Y2Y": {
        "latest": { "date": "2026-04-15", "value": 0.42 },
        "prior":  { "date": "2026-04-14", "value": 0.38 },
        "direction": "Rising"
      },
      "DGS10":    { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "DGS2":     { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "FEDFUNDS": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "inflation": {
      "CPIAUCSL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "CPILFESL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "growth": {
      "GDPC1":  { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "INDPRO": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "nowcast": {
      "GDPNOW":           { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "CFNAI":            { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "WEI":              { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "USALOLITOAASTSAM": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "housing": { "PERMIT": { "..." }, "HOUST": { "..." }, "CSUSHPISA": { "..." }, "MORTGAGE30US": { "..." } },
    "industrials": { "DGORDER": { "..." } },
    "energy": { "DCOILWTICO": { "..." }, "DHHNGSP": { "..." } },
    "financials": { "BAMLH0A0HYM2": { "..." } },
    "consumer": { "RSAFS": { "..." }, "UMCSENT": { "..." } },
    "tech": { "CES3133440001": { "..." }, "PCUAINFOAINFO": { "..." } },
    "ppi": { "PCUOMFGOMFG": { "..." } }
  }
}
```

所有條目的 `_provenance` 隱含為 FRED。請檢查 `latest.date` 確認參考期間，因為各 series 的公布延遲不同。

## 跨 plugin 使用

```
us-macro（本 skill）-> macro-regime-snapshot -> domain-teams:investing-team
```

1. **us-macro** — 擷取 FRED 資料，回傳結構化 JSON
2. **macro-regime-snapshot** — 對應 Investment Clock phase + Growth-Inflation Positioning（GIP）象限，輸出 regime 判定
3. **domain-teams:investing-team** — 完整分析、conviction scoring、portfolio implications

啟動 `macro-regime-snapshot` 時，將輸出 JSON 原文作為 `### Input` 段傳入。

## 安裝

僅需 `uv`（Python package runner）。`setup.sh` script 在找不到 `uv` 時會自動安裝。預設的 CSV endpoint 不需 API key。

```bash
# 手動測試
uv run scripts/fred_client.py --series T10Y2Y,DGS10 --periods 24
```

## 維運與驗證

### 驗證所有 series 都能回傳資料

```bash
cd investing-toolkit/scripts

for series in T10Y2Y DGS10 DGS2 FEDFUNDS CPIAUCSL CPILFESL GDPC1 INDPRO GDPNOW CFNAI WEI USALOLITOAASTSAM PERMIT HOUST CSUSHPISA MORTGAGE30US DGORDER DCOILWTICO DHHNGSP BAMLH0A0HYM2 RSAFS UMCSENT CES3133440001 PCUAINFOAINFO PCUOMFGOMFG; do
  uv run fred_client.py --series "$series" --periods 3 --no-cache 2>&1 | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
l = d.get('latest') or {}
pv = d.get('_provenance') or {}
err = d.get('error', '')
if err:
    print(f'$series: ERROR - {err}')
else:
    print(f'$series: date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  staleness={pv.get(\"staleness_days\",\"?\")}d')
"
done
```

**各頻率預期 staleness：**

| 頻率 | Series | 預期 staleness |
|-----------|--------|-------------------|
| 日頻 | T10Y2Y、DGS10、DGS2、DCOILWTICO、DHHNGSP、BAMLH0A0HYM2 | < 5 天 |
| 週頻 | MORTGAGE30US、WEI | < 10 天 |
| 月頻 | FEDFUNDS、CPIAUCSL、CPILFESL、INDPRO、PERMIT、HOUST、DGORDER、RSAFS、UMCSENT、CES3133440001、PCUOMFGOMFG、PCUAINFOAINFO、USALOLITOAASTSAM | < 60 天 |
| 月頻（lagging） | CSUSHPISA、CFNAI | < 90 天 |
| 季頻 | GDPC1、GDPNOW | < 200 天 |

### 驗證 FRED CSV endpoint

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10" | tail -3
```

### 驗證 series ID 仍為有效

FRED 偶爾會停用或更名 series：

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}" | head -3
```

若已停用，請於此處查找後繼：`https://fred.stlouisfed.org/series/{SERIES_ID}`

### 新增 FRED series

1. 至 https://fred.stlouisfed.org 找到 series ID
2. 驗證：`uv run fred_client.py --series {ID} --periods 12 --no-cache`
3. 更新 `SKILL.md`（加入 group）+ `references/us-macro-indicators.md`（加入條目）
4. 不需修改 `fred_client.py`（接受任何 FRED series ID）

### 最近一次驗證

**日期**：2026-04-18 — 全部 25 個 series ACTIVE，透過 CSV endpoint 回傳 2026 資料。新增 `nowcast` group（GDPNOW、CFNAI、WEI、USALOLITOAASTSAM）作為月度 GDP proxy。
