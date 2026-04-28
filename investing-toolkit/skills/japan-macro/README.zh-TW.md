# japan-macro

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

investing-toolkit 的日本總經資料 skill。
日本マクロ経済データスキル。日本宏觀經濟資料技能。

## 概覽

從兩個政府資料來源擷取日本總經指標 — Bank of Japan（日本銀行）Time-Series API 與 Statistics Dashboard（統計ダッシュボード）API — 並回傳依 rates、inflation、growth、money、tankan、forex、balance group 分類的結構化 JSON。這是純資料 skill — 不分析、不對應 regime、不產出投資判定。

**月度 GDP proxy**：日本官方 GDP 為季頻（統計DB）。內閣府每月公布的景気動向指数 CI 三件組（先行 / 一致 / 遅行）是業界標準的月度 GDP proxy，其中一致指数（`coincident-index`）是定義經濟現況的關鍵讀數，與 us-macro 的 `nowcast` group 與 china-macro 的三大数据對應。

日本銀行の時系列統計APIと統計ダッシュボードAPIから日本マクロ指標を取得し、グループ別の構造化JSONを返す。データ取得のみで、分析やレジーム判定は行わない。

## 資料來源

### BOJ Time-Series API（日本銀行 時系列統計）

- **URL**：`https://www.stat-search.boj.or.jp/api/v1/`
- **Auth**：不需
- **涵蓋**：Call rate、CGPI、money stock M2、TANKAN DI、USD/JPY、REER、經常收支
- **更新**：每日 JST 上午 8:50（UTC 前一日 23:50）
- **Docs**：https://www.stat-search.boj.or.jp/info/api_guide_en.html

### 統計ダッシュボード API（Statistics Dashboard）

- **API Endpoint**：`https://dashboard.e-stat.go.jp/api/1.0/`
- **API Docs**：https://dashboard.e-stat.go.jp/static/api
- **Auth**：不需
- **涵蓋**：CPI、core CPI、工業生產、失業率、GDP、10 年 JGB 殖利率
- **更新**：依指標與主管機關而定

### 為何需要兩個來源？

日本各經濟統計分屬不同主管機關，無單一 API 涵蓋全部指標：

| 機關 | 指標 |
|--------|-----------|
| 日本銀行（Bank of Japan） | 利率、CGPI、貨幣供給、TANKAN、外匯 |
| 総務省（MIC, Statistics Bureau） | CPI、失業率 |
| 内閣府（Cabinet Office） | GDP |
| 経済産業省（METI） | 工業生產 |
| 財務省（MOF） | JGB 殖利率、經常收支（與 BOJ 共同管理） |

BOJ API 提供日銀自行收集的資料；其餘皆透過 e-Stat 系統（統計ダッシュボード）— 它將多個部會的資料彙整為單一 API。

### 為何不用 FRED？

FRED 也載有部分日本 series，但限制嚴重：

- 日本 CPI 在 FRED 上**僅年頻**（最新資料點：2024）
- 日本工業生產在 FRED 上**過時 2 年以上**
- 日本政府 API 提供**月頻資料更新至 2026-02/03**

直接使用來源 API 才能得到月頻顆粒度與即時資料。

## 指標

### Tier 1：核心指標（16）

| 日本語 | English | 來源 | 頻率 | 一般延遲 |
|--------|---------|--------|-----------|-------------|
| 無担保コールO/N物レート | Call Rate, Uncollateralized O/N | BOJ (FM01) | 日頻 | 1 個營業日 |
| 基準割引率・基準貸付利率 | Basic Discount / Loan Rate | BOJ (IR01) | 不定期 | 當日 |
| 消費者物価指数 CPI | Consumer Price Index | 統計DB | 月頻 | ~3-4 週 |
| コアCPI | Core CPI（不含生鮮食品） | 統計DB | 月頻 | ~3-4 週 |
| 企業物価指数 CGPI | Corporate Goods Price Index | BOJ (PR01) | 月頻 | ~2 週 |
| 国内総生産 GDP | Gross Domestic Product | 統計DB | 季頻 | ~6 週 |
| マネーストック M2 | Money Stock M2 | BOJ (MD02) | 月頻 | ~2 週 |
| 鉱工業生産指数 | Industrial Production Index | 統計DB | 月頻 | ~6 週 |
| 完全失業率 | Unemployment Rate | 統計DB | 月頻 | ~4 週 |
| 新発10年国債利回り | 10-Year JGB Yield | 統計DB | 月頻 | ~1 週 |
| 短観 業況判断DI | TANKAN Business Conditions DI | BOJ (CO) | 季頻 | ~1 週 |
| USD/JPY 為替レート | USD/JPY Exchange Rate | BOJ (FM08) | 日頻 | 1-2 個營業日 |
| 実効為替レート | Effective Exchange Rate (REER) | BOJ (FM09) | 月頻 | 1-2 個營業日 |
| 景気動向指数 CI 一致指数 | Composite Coincident Index（**月度 GDP proxy**） | 統計DB | 月頻 | ~6-8 週 |
| 景気動向指数 CI 先行指数 | Composite Leading Index | 統計DB | 月頻 | ~6-8 週 |
| 景気動向指数 CI 遅行指数 | Composite Lagging Index | 統計DB | 月頻 | ~6-8 週 |

### Tier 2：擴充（30+）

更深入分析所用的額外 BOJ database series — 利率（IR02-IR04）、貨幣市場利率（FM02-FM07）、貨幣總計量（MD01、MD03-MD14）、貸款（LA01-LA05）、資產負債表（BS01-BS02）、資金循環（FF）、服務價格（PR02-PR04）。

完整雙語文件參見 `references/japan-macro-indicators.md`。

### Tier 3：完整 BOJ DB Catalog（40+）

透過 BOJ Time-Series API 可取用的所有 database，包含公共財政（PF01-PF02）、BIS 國際銀行業（BIS）、衍生性商品（DER）、結算系統（PS01-PS02）。

完整對照表參見 `references/japan-boj-db-catalog.md`。

## 架構

```
japan-macro skill
├── SKILL.md                           <- Claude 讀取此檔
├── scripts/
│   ├── boj_client.py                  <- BOJ API adapter
│   ├── estat_client.py                <- 統計ダッシュボード adapter
│   └── setup.sh                       <- 自動安裝 uv
└── references/
    ├── japan-macro-indicators.md      <- Tier 1+2 雙語參考
    └── japan-boj-db-catalog.md        <- Tier 3 完整 DB catalog
```

Scripts 為從 `investing-toolkit/scripts/` 透過 `sync-scripts.sh` 同步的副本。Skill 目錄自包含，Claude Code 會以 skill 根目錄為基準解析所有路徑。

## 運作方式

1. **解析 series 清單** — `--indicators` 參數（預設 `all`）對應到 BOJ database/code pair 與統計DB presets。例如 `--indicators inflation` 會解析為 BOJ PR01（CGPI）加上統計DB presets `cpi` 與 `core-cpi`。

2. **為 BOJ series launch data-fetcher** — Skill 將 fetch requests 派送至 `data-fetcher` agent，agent 透過 `uv run` 執行 `boj_client.py`。對於標註「(discover via getMetadata)」的 series，agent 會先呼叫 BOJ `getMetadata` endpoint 找出當前有效的 series code（基期改版時 code 會變動），再擷取資料。

3. **為統計DB series launch data-fetcher** — 第二批 fetch requests 以 preset 名稱（如 `--preset cpi`）執行 `estat_client.py`。GDP 使用 `--cycle quarterly`，因為其無月頻版本。

4. **合併為統一輸出** — BOJ 與統計DB 結果合成單一 JSON 結構，依指標 group 分類。每個資料點保留 `"_source"` tag（`"boj"` 或 `"estat_dashboard"`）以便追溯。

## 輸出 contract

```json
{
  "fetched_at": "2026-04-16T08:50:00Z",
  "groups": {
    "rates": {
      "call_rate_on": {
        "latest": { "date": "2026-04-15", "value": 0.479 },
        "prior":  { "date": "2026-04-14", "value": 0.478 },
        "direction": "Rising",
        "_source": "boj"
      },
      "jgb10y": {
        "latest": { "date": "2026-03", "value": 1.520 },
        "prior":  { "date": "2026-02", "value": 1.380 },
        "direction": "Rising",
        "_source": "estat_dashboard"
      }
    },
    "inflation": {
      "cgpi":     { "...": "...", "_source": "boj" },
      "cpi":      { "...": "...", "_source": "estat_dashboard" },
      "core_cpi": { "...": "...", "_source": "estat_dashboard" }
    },
    "growth":  { "ip": { "..." }, "unemployment": { "..." }, "gdp": { "..." } },
    "money":   { "m2": { "...", "_source": "boj" } },
    "tankan":  { "tankan_di": { "...", "_source": "boj" } },
    "forex":   { "usdjpy": { "...", "_source": "boj" }, "reer": { "...", "_source": "boj" } },
    "balance": { "current_account": { "...", "_source": "boj" } }
  }
}
```

`_source` 欄位區分 BOJ 來源與統計DB 來源。請務必檢查 `latest.date` 確認參考期間。

## 日本特定情境

指標參考文件中記載的關鍵情境，會影響解讀：

- **マイナス金利政策（Negative Interest Rate Policy, 2016-2024）** — Call rate 在這 8 年期間被釘在 -0.1% 附近。任何正值在歷史上都具意義。BOJ 於 2024 年 3 月結束 NIRP。

- **YCC イールドカーブコントロール（Yield Curve Control, 2016-2024）** — 期間內 10Y JGB 殖利率為行政管制利率，並非市場出清利率。後 YCC 時代殖利率正逐步正常化，但仍因 BOJ 持有約 50% JGB 而受到壓抑。

- **CGPI 與 CPI 不同** — CGPI（企業物価，BOJ 管理）衡量 B2B 商品價格；CPI（消費者物価，総務省管理）衡量消費者價格。CGPI 領先 CPI 3-6 個月。日本「core CPI」意指「不含生鮮食品」，並非美國的「不含食品與能源」。

- **短観 DI 解讀** — DI > 0 表示回報「favorable」的廠商多於「unfavorable」。下降中但仍為正值的 DI 代表景氣轉差但尚未轉負。Large Manufacturers DI 是頭條數字。

- **経常収支 結構** — 日本自 2011 年福島事故起呈結構性貿易逆差，但海外投資帶來巨額一次所得盈餘。淨經常帳通常仍為正值，但因海外所得多再投資於海外，對 FX 影響較有限。

## 跨 plugin 使用

```
japan-macro（本 skill）-> macro-regime-snapshot -> domain-teams:investing-team
```

1. **japan-macro** — 擷取 BOJ + 統計DB 資料，回傳結構化 JSON
2. **macro-regime-snapshot** — 對應 Investment Clock phase + Growth-Inflation Positioning（GIP）象限，輸出 regime 判定
3. **domain-teams:investing-team** — 完整分析、conviction scoring、portfolio implications

啟動 `macro-regime-snapshot` 時，將輸出 JSON 原文作為 `### Input` 段傳入。

## 安裝

僅需 `uv`（Python package runner）。`setup.sh` script 在找不到 `uv` 時會自動安裝。兩個來源皆免費且免驗證，無需 API key。

```bash
# 手動測試 — BOJ call rate
uv run scripts/boj_client.py --db FM01 --code STRDCLUCON --start-date 202501

# 手動測試 — e-Stat CPI
uv run scripts/estat_client.py --preset cpi
```

## 維運與驗證

### 驗證所有 preset 為 active 並能回傳資料

**e-Stat presets（批次檢查）：**

```bash
cd investing-toolkit/scripts

for p in cpi core-cpi core-core-cpi unemployment ip jgb10y \
  coincident-index leading-index lagging-index \
  machine-orders real-wages job-ratio \
  tertiary-index retail-sales service-sales; do
  uv run estat_client.py --preset "$p" --no-cache 2>&1 | \
    python3 -c "
import json,sys
p='$p'
d=json.load(sys.stdin)
l=d.get('latest') or {}
s=(d.get('_provenance') or {}).get('staleness_days','?')
print(f'{p:20} date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  stale={s}d')
"
done
```

**BOJ series：**

```bash
uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202601
```

### 驗證 preset 是否未停用

使用 `getIndicatorInfo` API 檢查 `toDate`：

```bash
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode={CODE}"
```

- `toDate = 99991200` → ACTIVE
- `toDate = 20241200` → DISCONTINUED — 找替代品（見下）

### 調查停止時的處理

1. 在 e-Stat API metadata PDF 內查舊/新 StatCode：https://dashboard.e-stat.go.jp/static/api
2. 以新 StatCode 搜尋：`getIndicatorInfo?StatCode={NEW_CODE}`
3. 找出月頻 + 全日本版本
4. 更新 `estat_client.py` 中的 `PRESETS` + `INDICATOR_NAMES`
5. 執行 `sync-scripts.sh` + `sync-check.sh`

### 新增指標

1. 搜尋：`uv run estat_client.py --search "keyword"`（僅英文）
2. 或依 Category：`getIndicatorInfo?Category={CODE}`（見 API metadata PDF）
3. 驗證：`uv run estat_client.py --indicator {CODE} --no-cache`
4. 加入 `PRESETS` dict + `INDICATOR_NAMES` dict + `SKILL.md` + 指標參考檔

### 最近一次驗證

**日期**：2026-04-18 — 全部 16 項指標（1 BOJ + 15 e-Stat）ACTIVE + 月頻 + 2026 資料。
**v1.7.0 新增**：`leading-index` + `lagging-index` 補齊景気動向指数 CI 三件組（先行 / 一致 / 遅行），作為日本月度 GDP proxy 套件。
**已套用修正**：`service-sales`（舊調查 2024-12 停止，已替換為新 StatCode）、`job-ratio`（舊代碼為年度頻率，已替換為月頻代碼）。
