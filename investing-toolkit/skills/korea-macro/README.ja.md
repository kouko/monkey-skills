# korea-macro

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

investing-toolkit 向けの韓国マクロ経済データ skill。
한국 매크로 경제 데이터 스킬. 韓國宏觀經濟資料技能。

## 概要

FinanceDataReader を介して Bank of Korea（BOK）Economic Statistics System（ECOS）から **54 項目の韓国マクロ経済指標** を取得し、**13 の指標 group**（rates、inflation、growth、industry、labor、trade、money、sentiment、cycle、markets、fx、realestate、demographics）にまとめた構造化 JSON を返します。

**Catalog**：BOK ECOS KEYSTAT の全 98 コード catalog は `docs/bok-ecos-keystat-catalog.md` を参照（54 が preset、~40 が残りの Tier-B 候補、7 はスキップ）。完全な BOK ECOS catalog（10,000+ series）は API key が必要 — v1.9.0 に延期。

**月次 GDP proxy**：`coincident-cycle`（K253、동행지수순환변동치）+ `leading-cycle`（K254、선행지수순환변동치）の pair が合わせて月次 GDP モメンタムの proxy を構成し、us-macro の `nowcast` group、japan-macro の景気動향指数 CI 三本柱、china-macro の三大数据と並列の位置付けです。Statistics Korea（통계청）が BOK ECOS 経由で事前集計済みの CI 値を公表しているため、合成は不要です。lagging CI（후행지수）は Statistics Korea には存在しますが BOK ECOS KEYSTAT 経由では公開されていません（K255/K256 を probe — 両方とも別 series にマップ）。

## データソース（1 つの script）

| Script | ソース | 指標数 | 役割 |
|--------|--------|-----------|------|
| `fdr_client.py` | BOK ECOS-KEYSTAT を FinanceDataReader 経由 | 53（+ 1 FRED） | **Primary** — マクロ指標すべて |

### なぜ単一 script なのか

FinanceDataReader は BOK ECOS の内部エンドポイントを clean な Python API でラップします。53 個の ECOS-KEYSTAT コードはすべて同じ `fdr.DataReader()` 呼び出しを通ります。他国 skill との対称性のため、KRW/USD（`krw-usd`）のみ FRED CSV を fallback として利用しています（K152 が BOK 公式の KRW/USD 代替；catalog 参照）。

## 指標（54、v1.8.1）

### コア（group 別）

| Group | 数 | 指標 | 頻度 |
|-------|-------|-----------|-----------|
| rates | 7 | 기준금리、콜금리、CD 91일、KORIBOR 3M、국고채 3Y/5Y、회사채 AA- | 日次 |
| inflation | 5 | CPI、Core CPI、PPI、수입물가、수출물가 | 月次 |
| growth | 7 | GDP QoQ + 명목、전산업/제조업 생산、민간소비、설비/건설투자 | 四半期/月次 |
| industry | 11 | 제조업 재고/출하/가동률、서비스업 생산、소매판매、도소매、카드이용、기계수주、자본재 생산、건설기성/수주 | 月次 |
| labor | 2 | 실업률、고용률 | 月次 |
| trade | 3 | 경상수지、교역조건、재화수출（national accounts） | 月次/四半期 |
| money | 4 | M1、M2、Lf、가계신용 | 月次/四半期 |
| sentiment | 2 | 소비자심리지수、경제심리지수 | 月次 |
| cycle | 2 | 선행 / 동행 순환변동치（月次 GDP proxy CI pair） | 月次 |
| markets | 2 | KOSPI、KOSDAQ | 日次 |
| fx | 5 | KRW/USD（FRED）、KRW/JPY/EUR/CNY、외환보유액 | 日次/月次 |
| realestate | 1 | 주택매매가격지수 | 月次 |
| demographics | 3 | 추계인구、고령인구비율、합계출산율 | 年次 |

### 安定性に関する注記

- **FinanceDataReader + ECOS-KEYSTAT**：BOK の内部エンドポイント（`ecos.bok.or.kr/serviceEndpoint`）を使用。文書化された公開 API ではありませんが、FinanceDataReader（GitHub 1.5k stars）は活発に保守され、韓国の金融・データサイエンスコミュニティで広く利用されています。
- **FRED CSV（krw-usd のみ）**：Federal Reserve 公式データ — **非常に安定**。

## アーキテクチャ

```
korea-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── fdr_client.py                      ← BOK ECOS via FDR（53 preset + 1 FRED）
│   └── setup.sh
├── docs/                                   ← 開発者向け参考資料（v1.8.0）
│   ├── README.md
│   ├── bok-ecos-keystat-catalog.md        ← 完全な 98 コード KEYSTAT catalog
│   ├── bok-ecos-keystat.json              ← 生の probe 出力
│   └── tools/probe-keystat.py             ← 再 probe 用 script
└── references/
    ├── indicator-index.md                 ← 54 指標 三言語インデックス
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md               ← 四半期 national accounts
    ├── indicators-industry.md             ← 月次 sector activity（v1.8.1）
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-sentiment.md            ← CSI / ESI（survey-based）
    ├── indicators-cycle.md                ← CI pair（月次 GDP proxy）
    ├── indicators-demographics.md         ← 人口 / 高齢化 / 出生率
    ├── indicators-other.md                ← markets / FX / money / 不動産
    └── sources.md
```

## セットアップ

API key 不要。FinanceDataReader が内部で BOK ECOS にアクセスします。

```bash
uv run scripts/fdr_client.py --preset policy-rate
uv run scripts/fdr_client.py --preset cpi,unemployment
uv run scripts/fdr_client.py --preset all
```

## 検証

```bash
cd investing-toolkit/scripts

# 全 54 preset
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

### 最新の検証

**日付**：2026-04-18 — **54 指標** すべて ACTIVE。53 が ECOS-KEYSTAT 経由 + 1 が FRED DEXKOUS 経由。

**v1.7.3 追加**（2 件タグ付け）：`leading-cycle` + `coincident-cycle` を月次 GDP proxy 構成要素としてタグ付け。

**v1.8.0 追加**（新 preset 15 件）：`koribor-3m`、`private-consumption`、`equipment-investment`、`construction-investment`、`goods-exports`、`m1`、`lf`、`krw-jpy`、`krw-eur`、`krw-cny`、`fx-reserves`、`population`、`aging-ratio`、`fertility-rate`、および `sentiment` → `sentiment` + `cycle` リファクタ + 新 `demographics` group。

**v1.8.1 追加**（新 preset 11 件、新 `industry` group）：`manufacturing-inventory`、`manufacturing-shipment`、`manufacturing-operating-rate`、`services-production`、`retail-sales`、`wholesale-retail`、`credit-card-usage`、`machinery-orders`、`capital-goods-output`、`construction-completion`、`construction-orders`。JP/TW/CN との月次 sector-activity ギャップを解消。

**v1.9.0 候補**：完全な BOK ECOS API 統合（無料 API key の登録が必要）— `docs/bok-ecos-keystat-catalog.md` で特定された ~40 個の Tier-B 候補と lagging CI（후행지수）が解放される。
