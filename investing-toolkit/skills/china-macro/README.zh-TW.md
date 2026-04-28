# china-macro

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

investing-toolkit 的中國總經資料 skill。
中国宏观经济数据技能。中國宏觀經濟資料技能。

## 概覽

從四個來源擷取 34 項中國總經指標：NBS（透過逆向工程的 new-SPA API 直接取得，2026-04 已遷移）、PBOC/SHIBOR 透過 akshare、FRED（CNY/USD + 外匯存底），以及 yfinance（5 檔股票指數）。回傳依 12 個指標 group 分類的結構化 JSON。

**月度 GDP proxy**：三大數據（`industrial-yoy` / `retail-yoy` / `fai-yoy`）+ `services-production-yoy` 共同構成月度 GDP 動能 proxy，與 us-macro 的 `nowcast` group 及 japan-macro 的景気動向指数 CI 三件組對應。中國**沒有權威的月度綜合指標** — 李克強指數 / SF Fed CAT / Goldman CAI / 學術 DFM 等方法論並未收斂。本 skill 刻意保留 4 個原始構成項目；綜合判斷交由分析層（investing-team）處理。

## 資料來源（4 個 scripts）

| Script | 來源 | 指標數 | 角色 |
|--------|--------|-----------|------|
| `nbs_client.py` | NBS new-SPA API（`data.stats.gov.cn/dg/website/publicrelease/web/external/*`） | **21** | **Primary source** — 所有 NBS 月頻 + 季頻資料 |
| `akshare_client.py` | PBOC（chinamoney）+ SHIBOR（shibor.org）透過 akshare | 6 | 僅 PBOC：LPR×2、RRR、SHIBOR、社融增量、新增貸款 |
| `fred_client.py` | FRED CSV | 2 | CNY/USD（`DEXCHUS`）+ 外匯存底（`TRESEGCNM052N`） |
| `yfinance_client.py` | Yahoo Finance | 5 | CSI300、SSEC、ChiNext、HSI、HSCEI |

### 為何使用三個 scripts？

- **akshare** — NBS `data.stats.gov.cn` WAF 會封鎖中國以外 IP（403 `reason:UrlACL`）。akshare 從可達的鏡像來源（eastmoney、investing.com、chinamoney.com.cn、shibor.org）匯總等價資料。
- **FRED** — akshare 的 `macro_china_foreign_exchange_gold` 上游已壞；FRED `TRESEGCNM052N` 透過 IMF 管道提供同樣的 SAFE 資料。CNY/USD（`DEXCHUS`）是 Federal Reserve Board 的標準日頻匯率。
- **yfinance** — 已是 toolkit 的相依套件；涵蓋全部 5 檔中國與香港 benchmark 指數，無需額外套件。

## 指標（34）

### 核心（依 group 分類）

| Group | 數量 | 指標 | 頻率 |
|-------|-------|-----------|-----------|
| inflation | 3 | CPI YoY、Core CPI、PPI YoY | 月頻 |
| growth | 4 | GDP YoY、工業生產 YoY、零售銷售 YoY、FAI YoY | 季頻/月頻 |
| trade | 3 | 出口 YoY、進口 YoY、貿易差額 | 月頻 |
| labor | 1 | 城鎮調查失業率 | 月頻 |
| sentiment | 3 | 製造業 / 非製造業 / 綜合 PMI（NBS 官方） | 月頻 |
| realestate | 4 | 投資 / 銷售面積 / 銷售金額 / 資金來源 | 月頻 |
| services | 1 | 服務業生產指數 | 月頻 |
| rates | 4 | LPR 1Y、LPR 5Y、RRR、SHIBOR 3M | 日頻/月頻/事件 |
| money | 2 | M1 YoY、M2 YoY | 月頻 |
| credit | 2 | 社融（社會融資規模）、人民幣新增貸款 | 月頻 |
| markets | 5 | CSI 300、上證綜指、ChiNext、HSI、HSCEI | 日頻 |
| fx | 2 | CNY/USD、外匯存底（不含黃金） | 日頻/月頻 |

### 穩定性說明

- **NBS 透過 `nbs_client.py` 直接取得** — primary source。可從台灣 + Anthropic IP 連線。WAF 會在大量遍歷時觸發（100+ requests），因此所有 `(cid, indicator_id)` pair 皆靜態固定；無 runtime discovery。基期修訂約每 5 年發生一次，屆時需更新 catalog；參見 `docs/tools/README.md`。
- **akshare PBOC presets**：背靠 chinamoney（CFETS）與 shibor.org。延遲約 1 個月以內。
- **FRED `DEXCHUS`、`TRESEGCNM052N`**：Fed / IMF 官方資料 — 非常穩定。
- **yfinance**：標準日頻 feed。
- **Caixin PMI** presets 已於 2026-04-18 移除（鏡像過期，無新鮮來源）。參見 SKILL.md 「Deliberately excluded indicators」。
- **70 城房價指數**未納入 — NBS 並未透過 `queryIndexTreeAsync` 公開（僅 PDF 公布）。延後處理。

## 架構

```
china-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── nbs_client.py          ← 21 個 presets，透過 NBS new-SPA API（PRIMARY）
│   ├── akshare_client.py      ← 6 個 PBOC presets
│   ├── fred_client.py         ← 2 個中國 FX series
│   ├── yfinance_client.py     ← 5 檔指數
│   └── setup.sh
├── docs/                       ← 開發者參考資料
│   ├── nbs-indicator-catalog.md
│   ├── china-macro-research-frameworks.md
│   ├── nbs-tree-*.md + nbs-indicators-*.{json,md}
│   └── tools/（probe scripts）
└── references/
    ├── indicator-index.md     ← 34 項指標三語索引
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-trade.md
    ├── indicators-labor.md
    ├── indicators-sentiment.md
    ├── indicators-rates.md
    ├── indicators-money.md
    ├── indicators-realestate.md
    ├── indicators-services.md
    ├── indicators-markets.md
    ├── indicators-fx.md
    └── sources.md
```

## 安裝

不需 API key。NBS、FRED、Yahoo Finance、akshare 端點皆無需驗證。

```bash
# NBS 直接取得（primary source，21 項指標）
uv run scripts/nbs_client.py --preset cpi-yoy
uv run scripts/nbs_client.py --preset industrial-yoy,exports-yoy,trade-balance
uv run scripts/nbs_client.py --preset all

# PBOC 透過 akshare（6 項指標）
uv run scripts/akshare_client.py --preset lpr-1y,shibor-3m,new-loans
uv run scripts/akshare_client.py --preset all

# FRED（2）+ yfinance（5）
uv run scripts/fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 12
uv run scripts/yfinance_client.py --tickers "000300.SS,^HSI,^HSCE"
```

## 驗證

```bash
cd investing-toolkit/scripts

# 全部 21 個 akshare presets
uv run akshare_client.py --preset all --no-cache 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d['indicators'].items():
    if 'error' in v:
        print(f'!!! {k}: {v[\"error\"]}')
    else:
        L = v.get('latest') or {}
        stale = v.get('_provenance',{}).get('staleness_days')
        print(f'OK {k:27s} latest={L.get(\"date\")} = {L.get(\"value\")} stale={stale}d')
"
```

### 最近一次驗證

**日期**：2026-04-17 — 28 項指標，全部 ACTIVE。21 透過 akshare + 2 透過 FRED + 5 透過 yfinance。Stale 指標（industrial-yoy、exports/imports/trade-balance、caixin PMIs）已於 SKILL.md Limitations 段落標註。
