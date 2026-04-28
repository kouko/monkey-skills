# taiwan-macro

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

investing-toolkit 的台灣總經資料 skill。
台灣宏觀經濟資料技能。台湾マクロ経済データスキル。

## 概覽

從四個政府資料來源擷取 30 項台灣總經指標，回傳依 8 個指標 group 分類的結構化 JSON：rates、inflation、growth、labor、trade、cycle、forex、money。

**月度 GDP proxy**：`signal`（景氣對策信號）+ `leading-index` + `coincident-index` 三件組共同構成月度 GDP 動能 proxy，與 us-macro 的 `nowcast` group、japan-macro 的景気動向指数 CI 三件組、china-macro 的三大数据對應。NDC/DGBAS 公布預先彙總的 CI 數值 — 無需自行合成。台灣獨有的 **五色景氣燈號**（紅/黃紅/綠/黃藍/藍）儀表板透過 `signal` 提供，是 NDC 的特色，他國無此項。

## 資料來源（4 個 scripts）

| Script | 來源 | 指標數 | 角色 |
|--------|--------|-----------|------|
| `statgov_client.py` | stat.gov.tw 隱藏 chart JSON | 17 | **Primary** — trade、growth、labor、finance |
| `cbc_client.py` | CBC Open Data API | 5 | **Primary** — 貨幣政策、FX |
| `dgbas_client.py` | DGBAS Excel（.xls） | 6 | **Primary** — 物價指數（CPI/PPI） |
| `ndc_client.py` | NDC ZIP（ws.ndc.gov.tw） | 6 | **Primary** — 景氣燈號、signal 構成項目 |

### 為何如此切分？

各 script 對其他 script 無法提供的指標而言皆為 primary：

| Script | 不可替代的指標 |
|--------|------------------------|
| statgov | 外銷訂單金額、出口/進口金額、TAIEX、外匯存底 |
| CBC | 重貼現率、TWD/USD 日頻、準備貨幣 |
| DGBAS Excel | CPI/核心CPI 指數值（非年增率）、進出口物價指數 |
| NDC | 景氣燈號顏色、9 個構成項目明細、領先指標構成項目 |

## 指標（30）

### 核心（依 group 分類）

| Group | 指標 | Primary Source |
|-------|-----------|---------------|
| rates (2) | 重貼現率、央行利率 | CBC |
| inflation (3) | CPI、核心CPI、PPI | DGBAS Excel |
| growth (4) | GDP YoY%、IPI YoY%、製造業 YoY%、零售業 YoY% | statgov |
| labor (2) | 失業率、季調失業率 | statgov |
| trade (7) | 外銷訂單、出口/進口金額、出口/進口 YoY%、進出口物價指數 | statgov + DGBAS |
| cycle (5) | 景氣燈號（分數+顏色）、構成項目、領先/同時指標 | NDC + statgov |
| forex (2) | TWD/USD、外匯存底 | CBC + statgov |
| money (4) | M2、準備貨幣、M2 YoY%、TAIEX | CBC + statgov |

### 穩定性說明

- **stat.gov.tw**：從 Highcharts 隱藏欄位中擷取 — 可運作但**並非已文件化的 API**。頁面改版可能造成中斷。
- **CBC API**：已文件化的官方 API — **最穩定**。
- **DGBAS Excel**：URL 固定、格式穩定 — **非常穩定**。
- **NDC ZIP**：自 2016 年起檔案結構一致 — **穩定**。

## 架構

```
taiwan-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── statgov_client.py      ← stat.gov.tw（17 個 preset）
│   ├── cbc_client.py          ← CBC API（5 個 preset）
│   ├── dgbas_client.py        ← DGBAS Excel/xlrd（6 個 preset）
│   ├── ndc_client.py          ← NDC ZIP/CSV（6 個 preset）
│   └── setup.sh
└── references/
    ├── indicator-index.md     ← 30 項指標三語索引
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-cycle.md
    ├── indicators-other.md
    └── sources.md
```

## 安裝

不需 API key。所有來源皆免費且免驗證。

```bash
uv run scripts/statgov_client.py --preset export-orders
uv run scripts/cbc_client.py --preset rediscount-rate
uv run scripts/dgbas_client.py --preset cpi
uv run scripts/ndc_client.py --preset signal
```

## 驗證

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

### 最近一次驗證

**日期**：2026-04-17 — 30 項指標跨 4 個來源，全部 ACTIVE。
