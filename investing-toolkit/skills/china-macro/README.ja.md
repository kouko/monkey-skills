# china-macro

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

investing-toolkit 向けの中国マクロ経済データ skill。
中国宏观经济数据技能。中國宏觀經濟資料技能。

## 概要

4 つのソースから 34 項目の中国マクロ経済指標を取得します：NBS（リバースエンジニアリングした new-SPA API 経由で直接取得、2026-04 移行）、PBOC/SHIBOR は akshare 経由、FRED（CNY/USD + 外貨準備）、および yfinance（5 つの equity 指数）。12 の指標 group ごとに整理された構造化 JSON を返します。

**月次 GDP proxy**：三大数据（`industrial-yoy` / `retail-yoy` / `fai-yoy`）+ `services-production-yoy` が合わせて月次 GDP モメンタムの proxy となり、us-macro の `nowcast` group や japan-macro の景気動向指数 CI 三本柱と並列の位置付けです。中国には**権威ある月次 composite index が存在せず** — 李克強指数 / SF Fed CAT / Goldman CAI / 学術 DFM の各方法論は収束していません。本 skill は意図的に 4 つの構成要素を生のまま保持し、合成は分析層（investing-team）に委ねます。

## データソース（4 つの scripts）

| Script | ソース | 指標数 | 役割 |
|--------|--------|-----------|------|
| `nbs_client.py` | NBS new-SPA API（`data.stats.gov.cn/dg/website/publicrelease/web/external/*`） | **21** | **Primary source** — NBS 月次 + 四半期データすべて |
| `akshare_client.py` | PBOC（chinamoney）+ SHIBOR（shibor.org）を akshare 経由 | 6 | PBOC のみ：LPR×2、RRR、SHIBOR、社融増量、新規貸出 |
| `fred_client.py` | FRED CSV | 2 | CNY/USD（`DEXCHUS`）+ 外貨準備（`TRESEGCNM052N`） |
| `yfinance_client.py` | Yahoo Finance | 5 | CSI300、SSEC、ChiNext、HSI、HSCEI |

### なぜ 3 つの script なのか

- **akshare** — NBS `data.stats.gov.cn` の WAF が中国本土以外の IP をブロックします（403 `reason:UrlACL`）。akshare は到達可能なミラー（eastmoney、investing.com、chinamoney.com.cn、shibor.org）から同等のデータを集約します。
- **FRED** — akshare の `macro_china_foreign_exchange_gold` は上流側が壊れており、FRED `TRESEGCNM052N` が IMF パイプライン経由で同じ SAFE データを提供します。CNY/USD（`DEXCHUS`）は Federal Reserve Board が公表する標準日次レートです。
- **yfinance** — 既に toolkit の依存関係であり、追加パッケージなしで中国・香港の benchmark 指数 5 つすべてをカバーします。

## 指標（34）

### コア（group ごと）

| Group | 数 | 指標 | 頻度 |
|-------|-------|-----------|-----------|
| inflation | 3 | CPI YoY、Core CPI、PPI YoY | 月次 |
| growth | 4 | GDP YoY、鉱工業生産 YoY、小売売上高 YoY、FAI YoY | 四半期/月次 |
| trade | 3 | 輸出 YoY、輸入 YoY、貿易収支 | 月次 |
| labor | 1 | 都市調査失業率 | 月次 |
| sentiment | 3 | 製造業 / 非製造業 / 総合 PMI（NBS 公式） | 月次 |
| realestate | 4 | 投資 / 販売面積 / 販売額 / 資金調達 | 月次 |
| services | 1 | 服務業生産指数 | 月次 |
| rates | 4 | LPR 1Y、LPR 5Y、RRR、SHIBOR 3M | 日次/月次/イベント |
| money | 2 | M1 YoY、M2 YoY | 月次 |
| credit | 2 | 社融（社会融資総量）、新規人民元貸出 | 月次 |
| markets | 5 | CSI 300、上海総合、ChiNext、HSI、HSCEI | 日次 |
| fx | 2 | CNY/USD、外貨準備（金除く） | 日次/月次 |

### 安定性に関する注記

- **`nbs_client.py` 経由の NBS 直接取得** — primary source。台湾 + Anthropic の IP から到達可能。WAF は大量走査（100+ requests）で発動するため、すべての `(cid, indicator_id)` ペアは静的に固定し、ランタイムでの discovery は行いません。基準期間の改定は概ね 5 年に一度発生し、その都度 catalog の更新が必要です。`docs/tools/README.md` を参照。
- **akshare PBOC presets**：chinamoney（CFETS）と shibor.org に依拠。約 1 ヶ月以内の鮮度。
- **FRED `DEXCHUS`、`TRESEGCNM052N`**：Fed / IMF の公式データ — 非常に安定。
- **yfinance**：標準的な日次 feed。
- **Caixin PMI** preset は 2026-04-18 に削除（ミラーが古く、新しいソースなし）。SKILL.md の「Deliberately excluded indicators」を参照。
- **70 都市住宅価格指数**は未収録 — NBS が `queryIndexTreeAsync` で公開していない（PDF 公表のみ）。延期。

## アーキテクチャ

```
china-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── nbs_client.py          ← 21 個の preset（NBS new-SPA API 経由、PRIMARY）
│   ├── akshare_client.py      ← 6 個の PBOC preset
│   ├── fred_client.py         ← 中国 FX series 2 つ
│   ├── yfinance_client.py     ← 指数 5 件
│   └── setup.sh
├── docs/                       ← 開発者向け参考資料
│   ├── nbs-indicator-catalog.md
│   ├── china-macro-research-frameworks.md
│   ├── nbs-tree-*.md + nbs-indicators-*.{json,md}
│   └── tools/（probe scripts）
└── references/
    ├── indicator-index.md     ← 34 指標 三言語インデックス
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

## セットアップ

API key は不要です。NBS、FRED、Yahoo Finance、akshare のエンドポイントはすべて認証不要です。

```bash
# NBS 直接取得（primary source、21 指標）
uv run scripts/nbs_client.py --preset cpi-yoy
uv run scripts/nbs_client.py --preset industrial-yoy,exports-yoy,trade-balance
uv run scripts/nbs_client.py --preset all

# PBOC を akshare 経由で（6 指標）
uv run scripts/akshare_client.py --preset lpr-1y,shibor-3m,new-loans
uv run scripts/akshare_client.py --preset all

# FRED（2）+ yfinance（5）
uv run scripts/fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 12
uv run scripts/yfinance_client.py --tickers "000300.SS,^HSI,^HSCE"
```

## 検証

```bash
cd investing-toolkit/scripts

# 全 21 個の akshare preset
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

### 最新の検証

**日付**：2026-04-17 — 28 指標すべて ACTIVE。21 件は akshare 経由、2 件は FRED 経由、5 件は yfinance 経由。古い指標（industrial-yoy、exports/imports/trade-balance、caixin PMIs）は SKILL.md の Limitations セクションでフラグ付け済み。
