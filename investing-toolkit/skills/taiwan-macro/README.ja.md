# taiwan-macro

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

investing-toolkit 向けの台湾マクロ経済データ skill。
台灣宏觀經濟資料技能。台湾マクロ経済データスキル。

## 概要

4 つの政府データソースから 30 項目の台湾マクロ経済指標を取得し、8 つの指標 group（rates、inflation、growth、labor、trade、cycle、forex、money）にまとめた構造化 JSON を返します。

**月次 GDP proxy**：`signal`（景氣對策信號）+ `leading-index` + `coincident-index` の三本柱が月次 GDP モメンタムの proxy を構成し、us-macro の `nowcast` group、japan-macro の景気動向指数 CI 三本柱、china-macro の三大数据と並列です。NDC/DGBAS は事前集計済みの CI 値を公表しているため、合成は不要です。台湾固有の **五色景氣燈號** ダッシュボード（紅/黃紅/綠/黃藍/藍）は `signal` 経由で取得でき、他国にはない NDC の特色です。

## データソース（4 つの scripts）

| Script | ソース | 指標数 | 役割 |
|--------|--------|-----------|------|
| `statgov_client.py` | stat.gov.tw 隠し chart JSON | 17 | **Primary** — trade、growth、labor、finance |
| `cbc_client.py` | CBC Open Data API | 5 | **Primary** — 金融政策、FX |
| `dgbas_client.py` | DGBAS Excel（.xls） | 6 | **Primary** — 物価指数（CPI/PPI） |
| `ndc_client.py` | NDC ZIP（ws.ndc.gov.tw） | 6 | **Primary** — 景氣燈號、signal 構成要素 |

### なぜこの分割なのか

それぞれの script は他では提供できない指標について primary です：

| Script | 代替不可能な指標 |
|--------|------------------------|
| statgov | 外銷訂單金額、出口/進口金額、TAIEX、外匯存底 |
| CBC | 重貼現率、TWD/USD 日次、準備貨幣 |
| DGBAS Excel | CPI/核心CPI 指数値（年増率ではない）、進出口物価指数 |
| NDC | 景氣燈號の色、9 つの構成項目明細、先行指標構成項目 |

## 指標（30）

### コア（group 別）

| Group | 指標 | Primary Source |
|-------|-----------|---------------|
| rates (2) | 重貼現率、央行利率 | CBC |
| inflation (3) | CPI、核心CPI、PPI | DGBAS Excel |
| growth (4) | GDP YoY%、IPI YoY%、製造業 YoY%、零售業 YoY% | statgov |
| labor (2) | 失業率、季調失業率 | statgov |
| trade (7) | 外銷訂單、出口/進口金額、出口/進口 YoY%、進出口物價指數 | statgov + DGBAS |
| cycle (5) | 景氣燈號（分數+色）、構成項目、先行/一致指標 | NDC + statgov |
| forex (2) | TWD/USD、外匯存底 | CBC + statgov |
| money (4) | M2、準備貨幣、M2 YoY%、TAIEX | CBC + statgov |

### 安定性に関する注記

- **stat.gov.tw**：Highcharts の隠しフィールドから抽出 — 機能はするが**文書化された API ではない**。ページのリデザインで壊れる可能性あり。
- **CBC API**：文書化された公式 API — **最も安定**。
- **DGBAS Excel**：URL 固定、フォーマット安定 — **非常に安定**。
- **NDC ZIP**：2016 年以降ファイル構造が一貫 — **安定**。

## アーキテクチャ

```
taiwan-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── statgov_client.py      ← stat.gov.tw（17 preset）
│   ├── cbc_client.py          ← CBC API（5 preset）
│   ├── dgbas_client.py        ← DGBAS Excel/xlrd（6 preset）
│   ├── ndc_client.py          ← NDC ZIP/CSV（6 preset）
│   └── setup.sh
└── references/
    ├── indicator-index.md     ← 30 指標 三言語インデックス
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-cycle.md
    ├── indicators-other.md
    └── sources.md
```

## セットアップ

API key 不要。すべてのソースが無料・認証不要です。

```bash
uv run scripts/statgov_client.py --preset export-orders
uv run scripts/cbc_client.py --preset rediscount-rate
uv run scripts/dgbas_client.py --preset cpi
uv run scripts/ndc_client.py --preset signal
```

## 検証

```bash
cd investing-toolkit/scripts

# statgov（17）
for p in export-orders exports imports exports-yoy imports-yoy ipi \
  manufacturing-yoy retail-yoy gdp-yoy unemployment unemployment-sa \
  fx-reserves taiex m2-yoy leading-index coincident-index signal-score; do
  uv run statgov_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# CBC（5）
for p in rediscount-rate m2 twdusd reserve-money financial-sa; do
  uv run cbc_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# DGBAS Excel（6）
for p in cpi core-cpi cpi-sa ppi import-pi export-pi; do
  uv run dgbas_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# NDC（signal）
uv run ndc_client.py --preset signal --no-cache 2>&1 | python3 -c "
import json,sys;d=json.load(sys.stdin)
s=d.get('score',{}).get('latest',{});c=d.get('color',{}).get('latest',{})
print(f'signal-score           {s.get(\"date\",\"?\")} {s.get(\"value\",\"?\")}')
print(f'signal-color           {c.get(\"date\",\"?\")} {c.get(\"value\",\"?\")}')
"
```

### 最新の検証

**日付**：2026-04-17 — 30 指標が 4 ソース横断ですべて ACTIVE。
