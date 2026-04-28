# korea-macro

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

investing-toolkit 的韓國總經資料 skill。
한국 매크로 경제 데이터 스킬. 韓國宏觀經濟資料技能。

## 概覽

透過 FinanceDataReader 從 Bank of Korea（BOK）Economic Statistics System（ECOS）擷取 **54 項韓國總經指標**，回傳依 **13 個指標 group** 分類的結構化 JSON：rates、inflation、growth、industry、labor、trade、money、sentiment、cycle、markets、fx、realestate、demographics。

**Catalog**：完整 98 個 BOK ECOS KEYSTAT 代碼參見 `docs/bok-ecos-keystat-catalog.md`（54 個作為 preset + ~40 個 Tier-B 候選 + 7 個跳過）。完整 BOK ECOS catalog（10,000+ series）需要 API key — 延後至 v1.9.0。

**月度 GDP proxy**：`coincident-cycle`（K253，동행지수순환변동치）+ `leading-cycle`（K254，선행지수순환변동치）pair 共同構成月度 GDP 動能 proxy，與 us-macro 的 `nowcast` group、japan-macro 的景気動향指数 CI 三件組、china-macro 的三大数据對應。Statistics Korea（통계청）透過 BOK ECOS 公布預先彙總的 CI 數值 — 無需自行合成。Lagging CI（후행지수）存在於 Statistics Korea 但未透過 BOK ECOS KEYSTAT 公開（已嘗試 K255/K256 — 兩者皆對應其他 series）。

## 資料來源（1 個 script）

| Script | 來源 | 指標數 | 角色 |
|--------|--------|-----------|------|
| `fdr_client.py` | BOK ECOS-KEYSTAT 透過 FinanceDataReader | 53（+ 1 FRED） | **Primary** — 全部總經指標 |

### 為何單一 script？

FinanceDataReader 將 BOK ECOS 的內部 endpoint 包裝成乾淨的 Python API。所有 53 個 ECOS-KEYSTAT 代碼皆走同一個 `fdr.DataReader()` 呼叫。僅 KRW/USD（`krw-usd`）使用 FRED CSV 作為 fallback，與其他國家 skill 對稱（K152 為 BOK 官方 KRW/USD 替代；參見 catalog）。

## 指標（54，v1.8.1）

### 核心（依 group 分類）

| Group | 數量 | 指標 | 頻率 |
|-------|-------|-----------|-----------|
| rates | 7 | 기준금리、콜금리、CD 91일、KORIBOR 3M、국고채 3Y/5Y、회사채 AA- | 日頻 |
| inflation | 5 | CPI、Core CPI、PPI、수입물가、수출물가 | 月頻 |
| growth | 7 | GDP QoQ + 명목、전산업/제조업 생산、민간소비、설비/건설투자 | 季頻/月頻 |
| industry | 11 | 제조업 재고/출하/가동률、서비스업 생산、소매판매、도소매、카드이용、기계수주、자본재 생산、건설기성/수주 | 月頻 |
| labor | 2 | 실업률、고용률 | 月頻 |
| trade | 3 | 경상수지、교역조건、재화수출（national accounts） | 月頻/季頻 |
| money | 4 | M1、M2、Lf、가계신용 | 月頻/季頻 |
| sentiment | 2 | 소비자심리지수、경제심리지수 | 月頻 |
| cycle | 2 | 선행 / 동행 순환변동치（月度 GDP proxy CI pair） | 月頻 |
| markets | 2 | KOSPI、KOSDAQ | 日頻 |
| fx | 5 | KRW/USD（FRED）、KRW/JPY/EUR/CNY、외환보유액 | 日頻/月頻 |
| realestate | 1 | 주택매매가격지수 | 月頻 |
| demographics | 3 | 추계인구、고령인구비율、합계출산율 | 年頻 |

### 穩定性說明

- **FinanceDataReader + ECOS-KEYSTAT**：使用 BOK 內部 endpoint（`ecos.bok.or.kr/serviceEndpoint`）。並非已文件化的公開 API，但 FinanceDataReader（GitHub 1.5k stars）持續維護，且在韓國金融/資料科學社群被廣泛使用。
- **FRED CSV（僅 krw-usd）**：Federal Reserve 官方資料 — **非常穩定**。

## 架構

```
korea-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── fdr_client.py                      ← BOK ECOS via FDR（53 個 preset + 1 FRED）
│   └── setup.sh
├── docs/                                   ← 開發者參考資料（v1.8.0）
│   ├── README.md
│   ├── bok-ecos-keystat-catalog.md        ← 完整 98 代碼 KEYSTAT catalog
│   ├── bok-ecos-keystat.json              ← 原始 probe 輸出
│   └── tools/probe-keystat.py             ← 重新探測 script
└── references/
    ├── indicator-index.md                 ← 54 項指標三語索引
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md               ← 季頻 national accounts
    ├── indicators-industry.md             ← 月頻 sector activity（v1.8.1）
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-sentiment.md            ← CSI / ESI（survey-based）
    ├── indicators-cycle.md                ← CI pair（月度 GDP proxy）
    ├── indicators-demographics.md         ← 人口 / 高齡化 / 生育率
    ├── indicators-other.md                ← markets / FX / money / 房地產
    └── sources.md
```

## 安裝

不需 API key。FinanceDataReader 內部存取 BOK ECOS。

```bash
uv run scripts/fdr_client.py --preset policy-rate
uv run scripts/fdr_client.py --preset cpi,unemployment
uv run scripts/fdr_client.py --preset all
```

## 驗證

```bash
cd investing-toolkit/scripts

# 全部 54 個 preset
for p in policy-rate call-rate cd-91d koribor-3m treasury-3y treasury-5y corp-bond-3y \
  cpi core-cpi ppi import-pi export-pi \
  gdp-qoq gdp-nominal ipi manufacturing private-consumption equipment-investment construction-investment \
  manufacturing-inventory manufacturing-shipment manufacturing-operating-rate services-production retail-sales wholesale-retail credit-card-usage machinery-orders capital-goods-output construction-completion construction-orders \
  unemployment employment-rate \
  current-account terms-of-trade goods-exports \
  m1 m2 lf household-credit \
  consumer-sentiment economic-sentiment leading-cycle coincident-cycle \
  kospi kosdaq \
  krw-usd krw-jpy krw-eur krw-cny fx-reserves \
  housing-price \
  population aging-ratio fertility-rate; do
  uv run fdr_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:28} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done
```

### 最近一次驗證

**日期**：2026-04-18 — **54 項指標**全部 ACTIVE。53 透過 ECOS-KEYSTAT + 1 透過 FRED DEXKOUS。

**v1.7.3 新增**（標記 2 項）：`leading-cycle` + `coincident-cycle` 標記為月度 GDP proxy 構成項目。

**v1.8.0 新增**（15 個新 preset）：`koribor-3m`、`private-consumption`、`equipment-investment`、`construction-investment`、`goods-exports`、`m1`、`lf`、`krw-jpy`、`krw-eur`、`krw-cny`、`fx-reserves`、`population`、`aging-ratio`、`fertility-rate`，以及 `sentiment` → `sentiment` + `cycle` 重構 + 新增 `demographics` group。

**v1.8.1 新增**（11 個新 preset，新 `industry` group）：`manufacturing-inventory`、`manufacturing-shipment`、`manufacturing-operating-rate`、`services-production`、`retail-sales`、`wholesale-retail`、`credit-card-usage`、`machinery-orders`、`capital-goods-output`、`construction-completion`、`construction-orders`。補齊與 JP/TW/CN 之間月頻 sector-activity 的缺口。

**v1.9.0 候選**：完整 BOK ECOS API 整合（需免費 API key 註冊）— 將解鎖 `docs/bok-ecos-keystat-catalog.md` 中標識的 ~40 個 Tier-B 候選，以及 lagging CI（후행지수）。
