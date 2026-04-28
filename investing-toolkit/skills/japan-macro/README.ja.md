# japan-macro

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

investing-toolkit 向けの日本マクロ経済データ skill。
日本マクロ経済データスキル。日本宏觀經濟資料技能。

## 概要

2 つの政府データソース — Bank of Japan（日本銀行）Time-Series API と Statistics Dashboard（統計ダッシュボード）API — から日本のマクロ経済指標を取得し、rates、inflation、growth、money、tankan、forex、balance に group 分けされた構造化 JSON を返します。本 skill はデータ取得のみで、分析・regime マッピング・投資判定の生成は行いません。

**月次 GDP proxy**：日本の公式 GDP は四半期（統計DB）です。内閣府が月次で公表する景気動向指数 CI 三本柱（先行 / 一致 / 遅行）は業界標準の月次 GDP proxy であり、一致指数（`coincident-index`）が「いま景気はどうなっているか」を示す決定的な値で、us-macro の `nowcast` group や china-macro の三大数据と並列の位置付けです。

日本銀行の時系列統計APIと統計ダッシュボードAPIから日本マクロ指標を取得し、グループ別の構造化JSONを返す。データ取得のみで、分析やレジーム判定は行わない。

## データソース

### BOJ Time-Series API（日本銀行 時系列統計）

- **URL**：`https://www.stat-search.boj.or.jp/api/v1/`
- **Auth**：不要
- **対象**：Call rate、CGPI、money stock M2、TANKAN DI、USD/JPY、REER、経常収支
- **更新**：毎日 JST 8:50（前日 UTC 23:50）
- **Docs**：https://www.stat-search.boj.or.jp/info/api_guide_en.html

### 統計ダッシュボード API（Statistics Dashboard）

- **API Endpoint**：`https://dashboard.e-stat.go.jp/api/1.0/`
- **API Docs**：https://dashboard.e-stat.go.jp/static/api
- **Auth**：不要
- **対象**：CPI、core CPI、鉱工業生産、失業率、GDP、10 年国債利回り
- **更新**：指標と所管機関により異なる

### なぜ 2 ソースなのか

日本の経済統計はそれぞれの所管機関が管理しており、すべての指標を 1 つの API でカバーすることはできません：

| 機関 | 指標 |
|--------|-----------|
| 日本銀行（Bank of Japan） | 金利、CGPI、money supply、TANKAN、forex |
| 総務省（MIC, Statistics Bureau） | CPI、失業率 |
| 内閣府（Cabinet Office） | GDP |
| 経済産業省（METI） | 鉱工業生産 |
| 財務省（MOF） | JGB 利回り、経常収支（BOJ と共同） |

BOJ API は日本銀行自身が収集するデータを提供します。その他はすべて e-Stat システム（統計ダッシュボード）を経由し、複数省庁のデータを 1 つの API に集約します。

### なぜ FRED ではないのか

FRED も日本の series を一部扱っていますが、深刻な制約があります：

- FRED の日本 CPI は**年次のみ**（最新データ点：2024）
- FRED の日本鉱工業生産は**2 年以上古い**
- 日本政府 API は **2026-02/03 まで月次データ**を提供

ソース API を直接使うことで、月次の粒度とタイムリーなデータが得られます。

## 指標

### Tier 1：コア指標（16）

| 日本語 | English | ソース | 頻度 | 標準ラグ |
|--------|---------|--------|-----------|-------------|
| 無担保コールO/N物レート | Call Rate, Uncollateralized O/N | BOJ (FM01) | 日次 | 1 営業日 |
| 基準割引率・基準貸付利率 | Basic Discount / Loan Rate | BOJ (IR01) | 不定期 | 当日 |
| 消費者物価指数 CPI | Consumer Price Index | 統計DB | 月次 | ~3-4 週 |
| コアCPI | Core CPI（生鮮食品除く） | 統計DB | 月次 | ~3-4 週 |
| 企業物価指数 CGPI | Corporate Goods Price Index | BOJ (PR01) | 月次 | ~2 週 |
| 国内総生産 GDP | Gross Domestic Product | 統計DB | 四半期 | ~6 週 |
| マネーストック M2 | Money Stock M2 | BOJ (MD02) | 月次 | ~2 週 |
| 鉱工業生産指数 | Industrial Production Index | 統計DB | 月次 | ~6 週 |
| 完全失業率 | Unemployment Rate | 統計DB | 月次 | ~4 週 |
| 新発10年国債利回り | 10-Year JGB Yield | 統計DB | 月次 | ~1 週 |
| 短観 業況判断DI | TANKAN Business Conditions DI | BOJ (CO) | 四半期 | ~1 週 |
| USD/JPY 為替レート | USD/JPY Exchange Rate | BOJ (FM08) | 日次 | 1-2 営業日 |
| 実効為替レート | Effective Exchange Rate (REER) | BOJ (FM09) | 月次 | 1-2 営業日 |
| 景気動向指数 CI 一致指数 | Composite Coincident Index（**月次 GDP proxy**） | 統計DB | 月次 | ~6-8 週 |
| 景気動向指数 CI 先行指数 | Composite Leading Index | 統計DB | 月次 | ~6-8 週 |
| 景気動向指数 CI 遅行指数 | Composite Lagging Index | 統計DB | 月次 | ~6-8 週 |

### Tier 2：拡張（30+）

より深い分析のための追加 BOJ database series — 金利（IR02-IR04）、コール市場金利（FM02-FM07）、マネタリーアグリゲート（MD01、MD03-MD14）、貸出（LA01-LA05）、バランスシート（BS01-BS02）、資金循環（FF）、サービス価格（PR02-PR04）。

完全なバイリンガル文書は `references/japan-macro-indicators.md` を参照。

### Tier 3：完全 BOJ DB Catalog（40+）

BOJ Time-Series API を通じて利用可能なすべての database。財政（PF01-PF02）、BIS 国際銀行業（BIS）、デリバティブ（DER）、決済システム（PS01-PS02）を含みます。

完全な対応表は `references/japan-boj-db-catalog.md` を参照。

## アーキテクチャ

```
japan-macro skill
├── SKILL.md                           <- Claude が読むファイル
├── scripts/
│   ├── boj_client.py                  <- BOJ API adapter
│   ├── estat_client.py                <- 統計ダッシュボード adapter
│   └── setup.sh                       <- uv を自動インストール
└── references/
    ├── japan-macro-indicators.md      <- Tier 1+2 バイリンガルリファレンス
    └── japan-boj-db-catalog.md        <- Tier 3 完全 DB catalog
```

scripts は `investing-toolkit/scripts/` から `sync-scripts.sh` で同期されたコピーです。skill ディレクトリは自己完結しており、Claude Code が skill ルートを基準にすべてのパスを解決できます。

## 動作の仕組み

1. **series リストを解決** — `--indicators` パラメータ（既定値：`all`）は BOJ database/code ペアと統計DB の preset にマッピングされます。例えば `--indicators inflation` は BOJ PR01（CGPI）+ 統計DB の `cpi` および `core-cpi` preset に解決されます。

2. **BOJ series 用に data-fetcher を起動** — skill は fetch リクエストを `data-fetcher` agent に dispatch し、agent は `uv run` 経由で `boj_client.py` を実行します。「(discover via getMetadata)」とマークされた series については、agent はまず BOJ の `getMetadata` エンドポイントを照会して現行の有効な series code（基準年改定で変わる）を見つけ、その後データを取得します。

3. **統計DB series 用に data-fetcher を起動** — 2 セット目の fetch リクエストが preset 名（例：`--preset cpi`）で `estat_client.py` を実行します。GDP は月次で利用できないため `--cycle quarterly` を使います。

4. **統合出力にマージ** — BOJ と統計DB の結果は、指標 group ごとに整理された 1 つの JSON 構造に結合されます。各データポイントは `"_source"` タグ（`"boj"` または `"estat_dashboard"`）を保持します。

## 出力 contract

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

`_source` フィールドは BOJ 由来のデータと統計DB 由来のデータを区別します。参照期間を確認するため、必ず `latest.date` をチェックしてください。

## 日本固有のコンテキスト

指標 reference 文書に記載されている、解釈に影響する重要なコンテキスト：

- **マイナス金利政策（Negative Interest Rate Policy, 2016-2024）** — Call rate は 8 年間 -0.1% 付近に固定されていました。プラスの読みはすべて歴史的に意味を持ちます。BOJ は 2024 年 3 月に NIRP を終了しました。

- **YCC イールドカーブコントロール（Yield Curve Control, 2016-2024）** — 同期間中、10 年 JGB 利回りは市場clearing rate ではなく管理金利でした。YCC 終了後も BOJ が JGB の約 50% を保有しているため、利回りは正常化しつつも依然として抑制されています。

- **CGPI と CPI は別物** — CGPI（企業物価、BOJ 管理）は B2B 商品の価格を、CPI（消費者物価、総務省管理）は消費者価格を測定します。CGPI は CPI に 3-6 ヶ月先行します。日本の「core CPI」は米国のような「食料・エネルギー除く」ではなく「生鮮食品除く」を意味します。

- **短観 DI の解釈** — DI > 0 は「良い」と回答した企業が「悪い」を上回ることを意味します。プラスの DI が下落しているのは、状況が悪化中ながらまだマイナスではないことを示します。大企業製造業 DI がヘッドライン数値です。

- **経常収支の構造** — 日本は 2011 年の福島事故以来構造的な貿易赤字を抱えますが、海外投資からの第一次所得収支は巨額の黒字です。経常収支ネットは通常プラスを維持しますが、海外で再投資されることが多いため FX への影響は限定的です。

## クロス plugin 利用

```
japan-macro（本 skill）-> macro-regime-snapshot -> domain-teams:investing-team
```

1. **japan-macro** — BOJ + 統計DB のデータを取得し、構造化 JSON を返す
2. **macro-regime-snapshot** — Investment Clock phase + Growth-Inflation Positioning（GIP）象限にマッピングし、regime 判定を出力
3. **domain-teams:investing-team** — フル分析、conviction scoring、portfolio implications

`macro-regime-snapshot` を起動するときは、出力 JSON をそのまま `### Input` セクションとして渡します。

## セットアップ

`uv`（Python パッケージランナー）のみ必要。`setup.sh` script が見つからなければ自動でインストールします。BOJ API も統計ダッシュボード API も無料・認証不要のため、API key は不要です。

```bash
# 手動テスト — BOJ call rate
uv run scripts/boj_client.py --db FM01 --code STRDCLUCON --start-date 202501

# 手動テスト — e-Stat CPI
uv run scripts/estat_client.py --preset cpi
```

## メンテナンスと検証

### すべての preset が active でデータを返すか検証

**e-Stat preset（バッチチェック）：**

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

### preset が discontinued でないか検証

`getIndicatorInfo` API を使い `toDate` をチェック：

```bash
curl -sS "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo?Lang=EN&IndicatorCode={CODE}"
```

- `toDate = 99991200` → ACTIVE
- `toDate = 20241200` → DISCONTINUED — 後継を探す（下記参照）

### 調査が discontinued になったとき

1. e-Stat API metadata PDF で旧/新 StatCode をチェック：https://dashboard.e-stat.go.jp/static/api
2. 新 StatCode で検索：`getIndicatorInfo?StatCode={NEW_CODE}`
3. 月次 + 全国版を見つける
4. `estat_client.py` の `PRESETS` + `INDICATOR_NAMES` を更新
5. `sync-scripts.sh` + `sync-check.sh` を実行

### 新しい指標を追加

1. 検索：`uv run estat_client.py --search "keyword"`（英語のみ）
2. または Category 経由：`getIndicatorInfo?Category={CODE}`（API metadata PDF 参照）
3. 検証：`uv run estat_client.py --indicator {CODE} --no-cache`
4. `PRESETS` dict + `INDICATOR_NAMES` dict + `SKILL.md` + 指標 reference ファイルに追加

### 最新の検証

**日付**：2026-04-18 — 全 16 指標（1 BOJ + 15 e-Stat）ACTIVE + 月次 + 2026 データ。
**v1.7.0 追加**：`leading-index` + `lagging-index` を加えて景気動向指数 CI 三本柱（先行 / 一致 / 遅行）を完成させ、日本の月次 GDP proxy パッケージとした。
**適用済み修正**：`service-sales`（旧調査が 2024-12 で discontinued、新 StatCode に置換）、`job-ratio`（旧コードは年度のみ、月次コードに置換）。
